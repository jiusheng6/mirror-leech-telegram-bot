from time import time
from re import search as research
from asyncio import gather
from aiofiles.os import path as aiopath
from psutil import (
    disk_usage,
    cpu_percent,
    swap_memory,
    cpu_count,
    virtual_memory,
    net_io_counters,
    boot_time,
)

from .. import bot_start_time
from ..helper.ext_utils.status_utils import get_readable_file_size, get_readable_time
from ..helper.ext_utils.bot_utils import cmd_exec, new_task
from ..helper.telegram_helper.message_utils import send_message

commands = {
    "aria2": (["aria2c", "--version"], r"aria2 version ([\d.]+)"),
    "qBittorrent": (["qbittorrent-nox", "--version"], r"qBittorrent v([\d.]+)"),
    "SABnzbd+": (["sabnzbdplus", "--version"], r"sabnzbdplus-([\d.]+)"),
    "python": (["python3", "--version"], r"Python ([\d.]+)"),
    "rclone": (["rclone", "--version"], r"rclone v([\d.]+)"),
    "yt-dlp": (["yt-dlp", "--version"], r"([\d.]+)"),
    "ffmpeg": (["ffmpeg", "-version"], r"ffmpeg version ([\d.]+(-\w+)?).*"),
    "7z": (["7z", "i"], r"7-Zip ([\d.]+)"),
}


@new_task
async def bot_stats(_, message):
    total, used, free, disk = disk_usage("/")
    swap = swap_memory()
    memory = virtual_memory()
    stats = f"""
<b>提交日期:</b> {commands["commit"]}

<b>机器人运行时间:</b> {get_readable_time(time() - bot_start_time)}
<b>系统运行时间:</b> {get_readable_time(time() - boot_time())}

<b>总磁盘空间:</b> {get_readable_file_size(total)}
<b>已用:</b> {get_readable_file_size(used)} | <b>空闲:</b> {get_readable_file_size(free)}

<b>上传:</b> {get_readable_file_size(net_io_counters().bytes_sent)}
<b>下载:</b> {get_readable_file_size(net_io_counters().bytes_recv)}

<b>CPU:</b> {cpu_percent(interval=0.5)}%
<b>内存:</b> {memory.percent}%
<b>磁盘:</b> {disk}%

<b>物理核心:</b> {cpu_count(logical=False)}
<b>总核心数:</b> {cpu_count()}
<b>交换空间:</b> {get_readable_file_size(swap.total)} | <b>已用:</b> {swap.percent}%

<b>总内存:</b> {get_readable_file_size(memory.total)}
<b>空闲内存:</b> {get_readable_file_size(memory.available)}
<b>已用内存:</b> {get_readable_file_size(memory.used)}

<b>python:</b> {commands["python"]}
<b>aria2:</b> {commands["aria2"]}
<b>qBittorrent:</b> {commands["qBittorrent"]}
<b>SABnzbd+:</b> {commands["SABnzbd+"]}
<b>rclone:</b> {commands["rclone"]}
<b>yt-dlp:</b> {commands["yt-dlp"]}
<b>ffmpeg:</b> {commands["ffmpeg"]}
<b>7z:</b> {commands["7z"]}
"""
    await send_message(message, stats)


async def get_version_async(command, regex):
    try:
        out, err, code = await cmd_exec(command)
        if code != 0:
            return f"错误: {err}"
        match = research(regex, out)
        return match.group(1) if match else "未找到版本"
    except Exception as e:
        return f"异常: {str(e)}"


@new_task
async def get_packages_version():
    tasks = [get_version_async(command, regex) for command, regex in commands.values()]
    versions = await gather(*tasks)
    for tool, version in zip(commands.keys(), versions):
        commands[tool] = version
    if await aiopath.exists(".git"):
        last_commit = await cmd_exec(
            "git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True
        )
        last_commit = last_commit[0]
    else:
        last_commit = "没有上游仓库"
    commands["commit"] = last_commit
