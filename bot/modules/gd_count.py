from ..helper.ext_utils.bot_utils import sync_to_async, new_task
from ..helper.ext_utils.links_utils import is_gdrive_link
from ..helper.ext_utils.status_utils import get_readable_file_size
from ..helper.mirror_leech_utils.gdrive_utils.count import GoogleDriveCount
from ..helper.telegram_helper.message_utils import delete_message, send_message


@new_task
async def count_node(_, message):
    args = message.text.split()
    user = message.from_user or message.sender_chat
    if username := user.username:
        tag = f"@{username}"
    else:
        tag = message.from_user.mention

    link = args[1] if len(args) > 1 else ""
    if len(link) == 0 and (reply_to := message.reply_to_message):
        link = reply_to.text.split(maxsplit=1)[0].strip()

    if is_gdrive_link(link):
        msg = await send_message(message, f"正在计算: <code>{link}</code>")
        name, mime_type, size, files, folders = await sync_to_async(
            GoogleDriveCount().count, link, user.id
        )
        if mime_type is None:
            await send_message(message, name)
            return
        await delete_message(msg)
        msg = f"<b>名称: </b><code>{name}</code>"
        msg += f"\n\n<b>大小: </b>{get_readable_file_size(size)}"
        msg += f"\n\n<b>类型: </b>{mime_type}"
        if mime_type == "Folder":
            msg += f"\n<b>子文件夹: </b>{folders}"
            msg += f"\n<b>文件: </b>{files}"
        msg += f"\n\n<b>cc: </b>{tag}"
    else:
        msg = (
            "请将 Gdrive 链接与命令一起发送，或通过命令回复链接"
        )

    await send_message(message, msg)



