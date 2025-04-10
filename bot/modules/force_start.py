from .. import (
    task_dict,
    task_dict_lock,
    user_data,
    queued_up,
    queued_dl,
    queue_dict_lock,
)
from ..core.config_manager import Config
from ..helper.ext_utils.bot_utils import new_task
from ..helper.ext_utils.status_utils import get_task_by_gid
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.telegram_helper.message_utils import send_message
from ..helper.ext_utils.task_manager import start_dl_from_queued, start_up_from_queued


@new_task
async def remove_from_queue(_, message):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    msg = message.text.split()
    status = msg[1] if len(msg) > 1 and msg[1] in ["fd", "fu"] else ""
    if status and len(msg) > 2 or not status and len(msg) > 1:
        gid = msg[2] if status else msg[1]
        task = await get_task_by_gid(gid)
        if task is None:
            await send_message(message, f"GID: <code>{gid}</code> 未找到.")
            return
    elif reply_to_id := message.reply_to_message_id:
        async with task_dict_lock:
            task = task_dict.get(reply_to_id)
        if task is None:
            await send_message(message, "这不是一个活动任务!")
            return
    elif len(msg) in {1, 2}:
        msg = f"""回复用于启动下载/上传的活动命令消息。
<code>/{BotCommands.ForceStartCommand[0]}</code> fd (从下载队列中移除) 或 fu (从上传队列中移除) 或不带参数来同时从下载和上传队列中移除。
也可以发送 <code>/{BotCommands.ForceStartCommand[0]} GID</code> fu|fd 或只发送 gid 来强制开始，从队列中移除任务！
示例：
<code>/{BotCommands.ForceStartCommand[1]}</code> GID fu (强制上传)
<code>/{BotCommands.ForceStartCommand[1]}</code> GID (强制下载和上传)
通过回复任务命令：
<code>/{BotCommands.ForceStartCommand[1]}</code> (强制下载和上传)
<code>/{BotCommands.ForceStartCommand[1]}</code> fd (强制下载)
"""
        await send_message(message, msg)
        return
    if (
        Config.OWNER_ID != user_id
        and task.listener.user_id != user_id
        and (user_id not in user_data or not user_data[user_id].get("SUDO"))
    ):
        await send_message(message, "这个任务不是为你的!")
        return
    listener = task.listener
    msg = ""
    async with queue_dict_lock:
        if status == "fu":
            listener.force_upload = True
            if listener.mid in queued_up:
                await start_up_from_queued(listener.mid)
                msg = "任务已被强制开始上传!"
            else:
                msg = "已为此任务启用强制上传!"
        elif status == "fd":
            listener.force_download = True
            if listener.mid in queued_dl:
                await start_dl_from_queued(listener.mid)
                msg = "任务已被强制开始下载!"
            else:
                msg = "此任务不在下载队列中!"
        else:
            listener.force_download = True
            listener.force_upload = True
            if listener.mid in queued_up:
                await start_up_from_queued(listener.mid)
                msg = "任务已被强制开始上传!"
            elif listener.mid in queued_dl:
                await start_dl_from_queued(listener.mid)
                msg = "任务已被强制开始下载，下载完成后将开始上传!"
            else:
                msg = "此任务不在队列中!"
    if msg:
        await send_message(message, msg)
