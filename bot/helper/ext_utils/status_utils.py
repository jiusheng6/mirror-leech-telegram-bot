from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage
from time import time
from asyncio import iscoroutinefunction, gather

from ... import task_dict, task_dict_lock, bot_start_time, status_dict, DOWNLOAD_DIR
from ...core.config_manager import Config
from ..telegram_helper.button_build import ButtonMaker

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


class MirrorStatus:
    STATUS_UPLOAD = "上传"
    STATUS_DOWNLOAD = "下载"
    STATUS_CLONE = "克隆"
    STATUS_QUEUEDL = "下载队列"
    STATUS_QUEUEUP = "上传队列"
    STATUS_PAUSED = "暂停"
    STATUS_ARCHIVE = "压缩"
    STATUS_EXTRACT = "解压"
    STATUS_SPLIT = "分割"
    STATUS_CHECK = "检查"
    STATUS_SEED = "做种"
    STATUS_SAMVID = "视频采样"
    STATUS_CONVERT = "转换"
    STATUS_FFMPEG = "FFmpeg"


STATUSES = {
    "ALL": "全部",
    "DL": MirrorStatus.STATUS_DOWNLOAD,
    "UP": MirrorStatus.STATUS_UPLOAD,
    "QD": MirrorStatus.STATUS_QUEUEDL,
    "QU": MirrorStatus.STATUS_QUEUEUP,
    "AR": MirrorStatus.STATUS_ARCHIVE,
    "EX": MirrorStatus.STATUS_EXTRACT,
    "SD": MirrorStatus.STATUS_SEED,
    "CL": MirrorStatus.STATUS_CLONE,
    "CM": MirrorStatus.STATUS_CONVERT,
    "SP": MirrorStatus.STATUS_SPLIT,
    "SV": MirrorStatus.STATUS_SAMVID,
    "FF": MirrorStatus.STATUS_FFMPEG,
    "PA": MirrorStatus.STATUS_PAUSED,
    "CK": MirrorStatus.STATUS_CHECK,
}


async def get_task_by_gid(gid: str):
    async with task_dict_lock:
        for tk in task_dict.values():
            if hasattr(tk, "seeding"):
                await tk.update()
            if tk.gid() == gid:
                return tk
        return None


async def get_specific_tasks(status, user_id):
    if status == "全部":
        if user_id:
            return [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        else:
            return list(task_dict.values())
    tasks_to_check = (
        [tk for tk in task_dict.values() if tk.listener.user_id == user_id]
        if user_id
        else list(task_dict.values())
    )
    coro_tasks = []
    coro_tasks.extend(tk for tk in tasks_to_check if iscoroutinefunction(tk.status))
    coro_statuses = await gather(*[tk.status() for tk in coro_tasks])
    result = []
    coro_index = 0
    for tk in tasks_to_check:
        if tk in coro_tasks:
            st = coro_statuses[coro_index]
            coro_index += 1
        else:
            st = tk.status()
        if (st == status) or (
            status == MirrorStatus.STATUS_DOWNLOAD and st not in STATUSES.values()
        ):
            result.append(tk)
    return result


async def get_all_tasks(req_status: str, user_id):
    async with task_dict_lock:
        return await get_specific_tasks(req_status, user_id)


def get_readable_file_size(size_in_bytes):
    if not size_in_bytes:
        return "0B"

    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1

    return f"{size_in_bytes:.2f}{SIZE_UNITS[index]}"


def get_readable_time(seconds: int):
    periods = [("天", 86400), ("小时", 3600), ("分钟", 60), ("秒", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result


def time_to_seconds(time_duration):
    try:
        parts = time_duration.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = map(float, parts)
        elif len(parts) == 1:
            hours = 0
            minutes = 0
            seconds = float(parts[0])
        else:
            return 0
        return hours * 3600 + minutes * 60 + seconds
    except:
        return 0


def speed_string_to_bytes(size_text: str):
    size = 0
    size_text = size_text.lower()
    if "k" in size_text:
        size += float(size_text.split("k")[0]) * 1024
    elif "m" in size_text:
        size += float(size_text.split("m")[0]) * 1048576
    elif "g" in size_text:
        size += float(size_text.split("g")[0]) * 1073741824
    elif "t" in size_text:
        size += float(size_text.split("t")[0]) * 1099511627776
    elif "b" in size_text:
        size += float(size_text.split("b")[0])
    return size


def get_progress_bar_string(pct):
    pct = float(pct.strip("%"))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = "■" * cFull
    p_str += "□" * (12 - cFull)
    return f"[{p_str}]"


async def get_readable_message(sid, is_user, page_no=1, status="全部", page_step=1):
    msg = ""
    button = None

    tasks = await get_specific_tasks(status, sid if is_user else None)

    STATUS_LIMIT = Config.STATUS_LIMIT
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
        status_dict[sid]["page_no"] = page_no
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
        status_dict[sid]["page_no"] = page_no
    start_position = (page_no - 1) * STATUS_LIMIT

    for index, task in enumerate(
        tasks[start_position : STATUS_LIMIT + start_position], start=1
    ):
        if status != "全部":
            tstatus = status
        elif iscoroutinefunction(task.status):
            tstatus = await task.status()
        else:
            tstatus = task.status()
        if task.listener.is_super_chat:
            msg += f"<b>{index + start_position}.<a href='{task.listener.message.link}'>{tstatus}</a>: </b>"
        else:
            msg += f"<b>{index + start_position}.{tstatus}: </b>"
        msg += f"<code>{escape(f'{task.name()}')}</code>"
        if task.listener.subname:
            msg += f"\n<i>{task.listener.subname}</i>"
        if (
            tstatus not in [MirrorStatus.STATUS_SEED, MirrorStatus.STATUS_QUEUEUP]
            and task.listener.progress
        ):
            progress = task.progress()
            msg += f"\n{get_progress_bar_string(progress)} {progress}"
            if task.listener.subname:
                subsize = f"/{get_readable_file_size(task.listener.subsize)}"
                ac = len(task.listener.files_to_proceed)
                count = f"{task.listener.proceed_count}/{ac or '?'}"
            else:
                subsize = ""
                count = ""
            msg += f"\n<b>已处理:</b> {task.processed_bytes()}{subsize}"
            if count:
                msg += f"\n<b>数量:</b> {count}"
            msg += f"\n<b>大小:</b> {task.size()}"
            msg += f"\n<b>速度:</b> {task.speed()}"
            msg += f"\n<b>剩余时间:</b> {task.eta()}"
            if (
                tstatus == MirrorStatus.STATUS_DOWNLOAD
                and task.listener.is_torrent
                or task.listener.is_qbit
            ):
                try:
                    msg += f"\n<b>做种者:</b> {task.seeders_num()} | <b>下载者:</b> {task.leechers_num()}"
                except:
                    pass
        elif tstatus == MirrorStatus.STATUS_SEED:
            msg += f"\n<b>大小: </b>{task.size()}"
            msg += f"\n<b>速度: </b>{task.seed_speed()}"
            msg += f"\n<b>已上传: </b>{task.uploaded_bytes()}"
            msg += f"\n<b>分享率: </b>{task.ratio()}"
            msg += f" | <b>时间: </b>{task.seeding_time()}"
        else:
            msg += f"\n<b>大小: </b>{task.size()}"
        msg += f"\n<b>Gid: </b><code>{task.gid()}</code>\n\n"

    if len(msg) == 0:
        if status == "全部":
            return None, None
        else:
            msg = f"没有活跃的{status}任务！\n\n"
    buttons = ButtonMaker()
    if not is_user:
        buttons.data_button("📜", f"status {sid} ov", position="header")
    if len(tasks) > STATUS_LIMIT:
        msg += f"<b>页码:</b> {page_no}/{pages} | <b>任务:</b> {tasks_no} | <b>步长:</b> {page_step}\n"
        buttons.data_button("<<", f"status {sid} pre", position="header")
        buttons.data_button(">>", f"status {sid} nex", position="header")
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15]:
                buttons.data_button(i, f"status {sid} ps {i}", position="footer")
    if status != "全部" or tasks_no > 20:
        for label, status_value in list(STATUSES.items()):
            if status_value != status:
                buttons.data_button(label, f"status {sid} st {status_value}")
    buttons.data_button("♻️", f"status {sid} ref", position="header")
    button = buttons.build_menu(8)
    msg += f"<b>CPU:</b> {cpu_percent()}% | <b>可用空间:</b> {get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)}"
    msg += f"\n<b>内存:</b> {virtual_memory().percent}% | <b>运行时间:</b> {get_readable_time(time() - bot_start_time)}"
    return msg, button
