from aiofiles.os import remove, path as aiopath
from asyncio import iscoroutinefunction

from .. import (
    task_dict,
    task_dict_lock,
    user_data,
    LOGGER,
    sabnzbd_client,
)
from ..core.config_manager import Config
from ..core.torrent_manager import TorrentManager
from ..helper.ext_utils.bot_utils import (
    bt_selection_buttons,
    new_task,
)
from ..helper.ext_utils.status_utils import get_task_by_gid, MirrorStatus
from ..helper.telegram_helper.message_utils import (
    send_message,
    send_status_message,
    delete_message,
)


@new_task
async def select(_, message):
    if not Config.BASE_URL:
        await send_message(message, "Base URL not defined!")
        return
    user_id = message.from_user.id
    msg = message.text.split()
    if len(msg) > 1:
        gid = msg[1]
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
    elif len(msg) == 1:
        msg = (
            "回复一个用于启动下载的活动 /cmd 命令，或在命令中添加 gid\n\n"
            + "该命令主要用于选择已添加的种子/nzb 中的文件。 "
            + "但您也可以始终在下载开始前使用带有参数 `s` 的 /cmd 来选择文件。"
        )
        await send_message(message, msg)
        return
    if (
        Config.OWNER_ID != user_id
        and task.listener.user_id != user_id
        and (user_id not in user_data or not user_data[user_id].get("SUDO"))
    ):
        await send_message(message, "这个任务不是为你的!")
        return
    if not iscoroutinefunction(task.status):
        await send_message(message, "任务已完成下载阶段!")
        return
    if await task.status() not in [
        MirrorStatus.STATUS_DOWNLOAD,
        MirrorStatus.STATUS_PAUSED,
        MirrorStatus.STATUS_QUEUEDL,
    ]:
        await send_message(
            message,
            "任务应处于下载或暂停（如果消息被错误删除）或队列状态（如果您使用了种子或 nzb 文件）!",
        )
        return
    if task.name().startswith("[METADATA]") or task.name().startswith("Trying"):
        await send_message(message, "在元数据下载完成后再尝试!")
        return

    try:
        if not task.queued:
            await task.update()
            id_ = task.gid()
            if task.listener.is_nzb:
                await sabnzbd_client.pause_job(id_)
            elif task.listener.is_qbit:
                id_ = task.hash()
                await TorrentManager.qbittorrent.torrents.stop([id_])
            else:
                try:
                    await TorrentManager.aria2.forcePause(id_)
                except Exception as e:
                    LOGGER.error(
                        f"{e} Error in pause, this mostly happens after abuse aria2"
                    )
        task.listener.select = True
    except:
        await send_message(message, "这不是一个 BitTorrent 或 Sabnzbd 任务!")
        return

    SBUTTONS = bt_selection_buttons(id_)
    msg = "您的下载已暂停。选择文件然后点击“选择完成”按钮恢复下载。"
    await send_message(message, msg, SBUTTONS)


@new_task
async def confirm_selection(_, query):
    user_id = query.from_user.id
    data = query.data.split()
    message = query.message
    task = await get_task_by_gid(data[2])
    if task is None:
        await query.answer("这个任务已被取消!", show_alert=True)
        await delete_message(message)
        return
    if user_id != task.listener.user_id:
        await query.answer("这个任务不是为你的!", show_alert=True)
    elif data[1] == "pin":
        await query.answer(data[3], show_alert=True)
    elif data[1] == "done":
        await query.answer()
        id_ = data[3]
        if hasattr(task, "seeding"):
            if task.listener.is_qbit:
                tor_info = (
                    await TorrentManager.qbittorrent.torrents.info(hashes=[id_])
                )[0]
                path = tor_info.content_path.rsplit("/", 1)[0]
                res = await TorrentManager.qbittorrent.torrents.files(id_)
                for f in res:
                    if f.priority == 0:
                        f_paths = [f"{path}/{f.name}", f"{path}/{f.name}.!qB"]
                        for f_path in f_paths:
                            if await aiopath.exists(f_path):
                                try:
                                    await remove(f_path)
                                except:
                                    pass
                if not task.queued:
                    await TorrentManager.qbittorrent.torrents.start([id_])
            else:
                res = await TorrentManager.aria2.getFiles(id_)
                for f in res:
                    if f["selected"] == "false" and await aiopath.exists(f["path"]):
                        try:
                            await remove(f["path"])
                        except:
                            pass
                if not task.queued:
                    try:
                        await TorrentManager.aria2.unpause(id_)
                    except Exception as e:
                        LOGGER.error(
                            f"{e} Error in resume, this mostly happens after abuse aria2. Try to use select cmd again!"
                        )
        elif task.listener.is_nzb:
            await sabnzbd_client.resume_job(id_)
        await send_status_message(message)
        await delete_message(message)
    else:
        await delete_message(message)
        await task.cancel_task()
