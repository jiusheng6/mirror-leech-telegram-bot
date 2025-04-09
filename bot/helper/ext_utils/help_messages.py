from ..telegram_helper.bot_commands import BotCommands
from ...core.mltb_client import TgClient

mirror = """<b>发送链接及命令行或</b>

/cmd 链接

<b>通过回复链接/文件</b>:

/cmd -n 新名称 -e -up 上传目的地

<b>注意:</b>
1. 以 <b>qb</b> 开头的命令仅适用于种子文件。"""

yt = """<b>发送链接及命令行</b>:

/cmd 链接
<b>通过回复链接</b>:
/cmd -n 新名称 -z 密码 -opt x:y|x1:y1

查看所有支持的<a href='https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md'>网站</a>
从这个<a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L212'>文件</a>中查看所有 yt-dlp API 选项，或使用这个<a href='https://t.me/mltb_official_channel/177'>脚本</a>将命令行参数转换为 API 选项。"""

clone = """发送 Gdrive|Gdot|Filepress|Filebee|Appdrive|Gdflix 链接或 rclone 路径，与命令一起发送或通过命令回复链接/rc_路径。
使用 -sync 在 rclone 中使用同步方法。例如：/cmd rcl/rclone_path -up rcl/rclone_path/rc -sync"""

new_name = """<b>新文件名</b>: -n

/cmd 链接 -n 新名称
注意：不适用于种子文件"""

multi_link = """<b>多链接仅通过回复第一个链接/文件</b>: -i

/cmd -i 10(链接/文件数量)"""

same_dir = """<b>将文件/文件夹移动到新文件夹</b>: -m

您还可以使用此参数将多个链接/种子内容移动到同一目录，这样所有链接将作为一个任务一起上传

/cmd 链接 -m 新文件夹 (仅一个链接在新文件夹内)
/cmd -i 10(链接/文件数量) -m 文件夹名称 (所有链接内容在一个文件夹中)
/cmd -b -m 文件夹名称 (回复批量消息/文件(每行一个链接))

使用批量时，也可以在消息或文件批处理中的链接旁使用此参数，并指定不同的文件夹名称
例如:
链接1 -m 文件夹1
链接2 -m 文件夹1
链接3 -m 文件夹2
链接4 -m 文件夹2
链接5 -m 文件夹3
链接6
这样，链接1和链接2的内容将从同一个文件夹上传，即文件夹1
链接3和链接4的内容将从同一个文件夹上传，即文件夹2
链接5将单独上传到名为文件夹3的新文件夹中
链接6将正常单独上传
"""

thumb = """<b>当前任务的缩略图</b>: -t

/cmd 链接 -t tg-消息链接 (文档或照片) 或 none (无缩略图的文件)"""

split_size = """<b>当前任务的分割大小</b>: -sp

/cmd 链接 -sp (500mb 或 2gb 或 4000000000)
注意: 仅支持 mb 和 gb 单位，或以字节为单位直接写入数字!"""

upload = """<b>上传目的地</b>: -up

/cmd 链接 -up rcl/gdl (rcl: 选择 rclone 配置、远程和路径 | gdl: 选择 token.pickle、gdrive id) 使用按钮
您可以直接添加上传路径: -up remote:dir/subdir 或 -up Gdrive_id 或 -up id/username (telegram) 或 -up id/username|topic_id (telegram)
如果 DEFAULT_UPLOAD 是 `rc`，则可以传递 up: `gd` 使用 gdrive 工具上传到 GDRIVE_ID。
如果 DEFAULT_UPLOAD 是 `gd`，则可以传递 up: `rc` 上传到 RCLONE_PATH。

如果您想从配置/令牌手动添加路径或 gdrive (从用户设置上传)，在路径/gdrive_id 前添加 mrcc: 表示 rclone，添加 mtp: 表示路径/gdrive_id，不带空格。
/cmd 链接 -up mrcc:main:dump 或 -up mtp:gdrive_id <strong>或者您可以简单地从所有者/用户令牌/配置中编辑上传，无需在上传路径/id 前添加 mtp: 或 mrcc:</strong>

添加下载目的地:
-up id/@username/pm
-up b:id/@username/pm (b: 表示通过机器人下载) (聊天的 id 或用户名，或写 pm 表示私人消息，机器人将私下发送文件给您)
何时应该使用 b:(通过机器人下载)? 当您的默认设置是通过用户下载，但您想为特定任务通过机器人下载时。
-up u:id/@username(u: 表示通过用户下载) 这种情况下 OWNER 添加了 USER_STRING_SESSION。
-up h:id/@username(混合下载) h: 根据文件大小通过机器人和用户上传文件。
-up id/@username|topic_id(在特定聊天和主题中下载) 添加 | 不带空格，并在聊天 id 或用户名后写入主题 id。

如果您想指定是使用 token.pickle 还是服务帐户，可以添加 tp:gdrive_id (使用 token.pickle) 或 sa:gdrive_id (使用服务帐户) 或 mtp:gdrive_id (使用从用户设置上传的 token.pickle)。
DEFAULT_UPLOAD 不影响下载命令。
"""

user_download = """<b>用户下载</b>: 链接

/cmd tp:链接 使用所有者 token.pickle 下载，适用于已启用服务帐户的情况。
/cmd sa:链接 使用服务帐户下载，适用于已禁用服务帐户的情况。
/cmd tp:gdrive_id 使用 token.pickle 和文件 ID 下载，适用于已启用服务帐户的情况。
/cmd sa:gdrive_id 使用服务帐户和文件 ID 下载，适用于已禁用服务帐户的情况。
/cmd mtp:gdrive_id 或 mtp:链接 使用从用户设置上传的用户 token.pickle 下载
/cmd mrcc:remote:path 使用从用户设置上传的用户 rclone 配置下载
您可以简单地从所有者/用户令牌/配置中编辑上传，无需在路径/id 前添加 mtp: 或 mrcc:"""

rcf = """<b>Rclone 标志</b>: -rcf

/cmd 链接|路径|rcl -up 路径|rcl -rcf --buffer-size:8M|--drive-starred-only|key|key:value
这将覆盖所有其他标志，除了 --exclude
在这里查看所有 <a href='https://rclone.org/flags/'>Rclone 标志</a>。"""

bulk = """<b>批量下载</b>: -b

批量只能通过回复文本消息或包含按行分隔链接的文本文件使用。
例如:
链接1 -n 新名称 -up remote1:path1 -rcf |key:value|key:value
链接2 -z -n 新名称 -up remote2:path2
链接3 -e -n 新名称 -up remote2:path2
通过此命令回复此示例 -> /cmd -b(批量)

注意: 与命令一起的任何参数将设置给所有链接
/cmd -b -up remote: -z -m 文件夹名称 (所有链接内容在一个压缩文件夹中上传到一个目的地)
因此，如果您添加了 -m 和命令，则无法为链接设置不同的上传目的地
您可以像种子一样，从批量中设置链接的开始和结束，使用 -b start:end 或仅结束 -b :end 或仅开始 -b start。
默认起点是从零(第一个链接)到无限。"""

rlone_dl = """<b>Rclone 下载</b>:

像链接一样处理 rclone 路径
/cmd main:dump/ubuntu.iso 或 rcl(选择配置、远程和路径)
用户可以从用户设置添加自己的 rclone
如果您想从配置中手动添加路径，请在路径前添加 mrcc: 不带空格
/cmd mrcc:main:dump/ubuntu.iso
您可以简单地从所有者/用户配置中编辑，无需在路径前添加 mrcc:"""

extract_zip = """<b>解压/压缩</b>: -e -z

/cmd 链接 -e 密码 (解压受密码保护的文件)
/cmd 链接 -z 密码 (压缩并设置密码保护)
/cmd 链接 -z 密码 -e (解压并压缩，设置密码保护)
注意: 当同时使用解压和压缩选项时，会先解压然后再压缩，所以始终先解压"""

join = """<b>合并分割文件</b>: -j

此选项仅在解压和压缩之前有效，所以它主要与 -m 参数(同一目录)一起使用
通过回复:
/cmd -i 3 -j -m 文件夹名称
/cmd -b -j -m 文件夹名称
如果您有链接(文件夹)包含分割文件:
/cmd 链接 -j"""

tg_links = """<b>TG 链接</b>:

像任何直接链接一样处理链接
有些链接需要用户访问权限，因此您必须为其添加 USER_SESSION_STRING。
三种类型的链接:
公开: https://t.me/channel_name/message_id
私人: tg://openmessage?user_id=xxxxxx&message_id=xxxxx
超级: https://t.me/c/channel_id/message_id
范围: https://t.me/channel_name/first_message_id-last_message_id
范围示例: tg://openmessage?user_id=xxxxxx&message_id=555-560 或 https://t.me/channel_name/100-150
注意: 范围链接仅在通过命令回复时有效"""

sample_video = """<b>样本视频</b>: -sv

为一个视频或视频文件夹创建样本视频。
/cmd -sv (它将采用默认值，即 60 秒样本持续时间和 4 秒部分持续时间)。
您可以控制这些值。例如: /cmd -sv 70:5(样本持续时间:部分持续时间) 或 /cmd -sv :5 或 /cmd -sv 70。"""

screenshot = """<b>截图</b>: -ss

为一个视频或视频文件夹创建截图。
/cmd -ss (它将采用默认值，即 10 张照片)。
您可以控制这个值。例如: /cmd -ss 6。"""

seed = """<b>BT 做种</b>: -d

/cmd 链接 -d 比率:做种时间 或通过回复文件/链接
要指定比率和做种时间，添加 -d 比率:时间。
例如: -d 0.7:10 (比率和时间) 或 -d 0.7 (仅比率) 或 -d :10 (仅时间)，其中时间以分钟为单位"""

zip_arg = """<b>压缩</b>: -z 密码

/cmd 链接 -z (压缩)
/cmd 链接 -z 密码 (压缩并设置密码保护)"""

qual = """<b>质量按钮</b>: -s

如果从 yt-dlp 选项中使用格式选项添加了默认质量，并且您需要为特定链接或使用多链接功能的链接选择质量。
/cmd 链接 -s"""

yt_opt = """<b>选项</b>: -opt

/cmd 链接 -opt {"format": "bv*+mergeall[vcodec=none]", "nocheckcertificate": True, "playliststart": 10, "fragment_retries": float("inf"), "matchtitle": "S13", "writesubtitles": True, "live_from_start": True, "postprocessor_args": {"ffmpeg": ["-threads", "4"]}, "wait_for_video": (5, 100), "download_ranges": [{"start_time": 0, "end_time": 10}]}

从这个<a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184'>文件</a>中查看所有 yt-dlp API 选项，或使用这个<a href='https://t.me/mltb_official_channel/177'>脚本</a>将命令行参数转换为 API 选项。"""

convert_media = """<b>转换媒体</b>: -ca -cv
/cmd 链接 -ca mp3 -cv mp4 (将所有音频转换为 mp3，所有视频转换为 mp4)
/cmd 链接 -ca mp3 (将所有音频转换为 mp3)
/cmd 链接 -cv mp4 (将所有视频转换为 mp4)
/cmd 链接 -ca mp3 + flac ogg (仅将 flac 和 ogg 音频转换为 mp3)
/cmd 链接 -cv mkv - webm flv (将所有视频转换为 mp4，除了 webm 和 flv)"""

force_start = """<b>强制开始</b>: -f -fd -fu
/cmd 链接 -f (强制下载和上传)
/cmd 链接 -fd (仅强制下载)
/cmd 链接 -fu (下载完成后直接强制上传)"""

gdrive = """<b>Gdrive</b>: 链接
如果 DEFAULT_UPLOAD 是 `rc`，则可以传递 up: `gd` 使用 gdrive 工具上传到 GDRIVE_ID。
/cmd gdriveLink 或 gdl 或 gdriveId -up gdl 或 gdriveId 或 gd
/cmd tp:gdriveLink 或 tp:gdriveId -up tp:gdriveId 或 gdl 或 gd (如果启用了服务账户，则使用 token.pickle)
/cmd sa:gdriveLink 或 sa:gdriveId -p sa:gdriveId 或 gdl 或 gd (如果禁用了服务账户，则使用服务账户)
/cmd mtp:gdriveLink 或 mtp:gdriveId -up mtp:gdriveId 或 gdl 或 gd(如果您已从用户设置添加了上传 gdriveId) (使用用户设置上传的用户 token.pickle)
您可以简单地使用所有者/用户令牌从用户设置编辑，无需在 ID 前添加 mtp:"""

rclone_cl = """<b>Rclone</b>: 路径
如果 DEFAULT_UPLOAD 是 `gd`，则可以传递 up: `rc` 上传到 RCLONE_PATH。
/cmd rcl/rclone_path -up rcl/rclone_path/rc -rcf flagkey:flagvalue|flagkey|flagkey:flagvalue
/cmd rcl 或 rclone_path -up rclone_path 或 rc 或 rcl
/cmd mrcc:rclone_path -up rcl 或 rc(如果您已从用户设置添加了 rclone 路径) (使用用户配置)
您可以简单地使用所有者/用户配置从用户设置编辑，无需在路径前添加 mrcc:"""

name_sub = r"""<b>名称替换</b>: -ns
/cmd 链接 -ns script/code/s | mirror/leech | tea/ /s | clone | cpu/ | \[mltb\]/mltb | \\text\\/text/s
这将影响所有文件。格式: 要替换的词/替换为的词/区分大小写
词替换。您可以添加模式而不是普通文本。超时: 60 秒
注意: 您必须在任何字符前添加 \，这些字符是: \^$.|?*+()[]{}-
1. script 将被替换为 code，区分大小写
2. mirror 将被替换为 leech
4. tea 将被替换为空格，区分大小写
5. clone 将被删除
6. cpu 将被替换为空格
7. [mltb] 将被替换为 mltb
8. \text\ 将被替换为 text，区分大小写
"""

transmission = """<b>Tg 传输</b>: -hl -ut -bt
/cmd 链接 -hl (根据大小通过用户和机器人会话下载) (混合下载)
/cmd 链接 -bt (通过机器人会话下载)
/cmd 链接 -ut (通过用户下载)"""

thumbnail_layout = """缩略图布局: -tl
/cmd 链接 -tl 3x3 (宽x高) 每行3张照片，每列3张照片"""

leech_as = """<b>下载为</b>: -doc -med
/cmd 链接 -doc (作为文档下载)
/cmd 链接 -med (作为媒体下载)"""

ffmpeg_cmds = """<b>FFmpeg 命令</b>: -ff
FFmpeg 命令列表的列表。您可以在上传前为所有文件设置多个 FFmpeg 命令。不要在开头写 ffmpeg，直接从参数开始。
注意:
1. 在您希望机器人在命令运行完成后删除原始文件的列表中添加 <code>-del</code>！
3. 要执行机器人中预添加的列表之一，如: ({"subtitle": ["-i mltb.mkv -c copy -c:s srt mltb.mkv"]})，您必须使用 -ff subtitle (列表键)
示例: ["-i mltb.mkv -c copy -c:s srt mltb.mkv", "-i mltb.video -c copy -c:s srt mltb", "-i mltb.m4a -c:a libmp3lame -q:a 2 mltb.mp3", "-i mltb.audio -c:a libmp3lame -q:a 2 mltb.mp3", "-i mltb -map 0:a -c copy mltb.mka -map 0:s -c copy mltb.srt"]
这里我将解释如何使用 mltb.*，它是指您想要处理的文件的引用。
1. 第一个命令: 输入是 mltb.mkv，所以这个命令将只对 mkv 视频起作用，输出也是 mltb.mkv，所以所有输出都是 mkv。-del 将在命令运行完成后删除原始媒体。
2. 第二个命令: 输入是 mltb.video，所以这个命令将对所有视频起作用，输出只是 mltb，所以扩展名与输入文件相同。
3. 第三个命令: 输入是 mltb.m4a，所以这个命令将只对 m4a 音频起作用，输出是 mltb.mp3，所以输出扩展名是 mp3。
4. 第四个命令: 输入是 mltb.audio，所以这个命令将对所有音频起作用，输出是 mltb.mp3，所以输出扩展名是 mp3。"""

YT_HELP_DICT = {
    "main": yt,
    "重命名": f"{new_name}\n注意: 不要添加文件扩展名",
    "压缩": zip_arg,
    "质量选择": qual,
    "下载选项": yt_opt,
    "多链接": multi_link,
    "同一目录": same_dir,
    "缩略图": thumb,
    "分割大小": split_size,
    "上传位置": upload,
    "Rclone参数": rcf,
    "批量下载": bulk,
    "视频采样": sample_video,
    "截图": screenshot,
    "格式转换": convert_media,
    "强制开始": force_start,
    "名称替换": name_sub,
    "TG传输": transmission,
    "缩略图布局": thumbnail_layout,
    "下载类型": leech_as,
    "FFmpeg命令": ffmpeg_cmds,
}

MIRROR_HELP_DICT = {
    "main": mirror,
    "重命名": new_name,
    "下载认证": "<b>直接链接授权</b>: -au -ap\n\n/cmd 链接 -au 用户名 -ap 密码",
    "请求头": "<b>直接链接自定义标头</b>: -h\n\n/cmd 链接 -h key: value key1: value1",
    "解压/压缩": extract_zip,
    "选择文件": "<b>BT/JDownloader/Sabnzbd 文件选择</b>: -s\n\n/cmd 链接 -s 或通过回复文件/链接",
    "做种设置": seed,
    "多链接": multi_link,
    "同一目录": same_dir,
    "缩略图": thumb,
    "分割大小": split_size,
    "上传位置": upload,
    "Rclone参数": rcf,
    "批量下载": bulk,
    "合并分割": join,
    "Rclone下载": rlone_dl,
    "TG链接": tg_links,
    "视频采样": sample_video,
    "截图": screenshot,
    "格式转换": convert_media,
    "强制开始": force_start,
    "用户下载": user_download,
    "名称替换": name_sub,
    "TG传输": transmission,
    "缩略图布局": thumbnail_layout,
    "下载类型": leech_as,
    "FFmpeg命令": ffmpeg_cmds,
}

CLONE_HELP_DICT = {
    "main": clone,
    "多链接": multi_link,
    "批量下载": bulk,
    "谷歌云盘": gdrive,
    "Rclone": rclone_cl,
}

RSS_HELP_MESSAGE = """
使用此格式添加 feed 网址:
标题1 链接 (必需)
标题2 链接 -c 命令 -inf xx -exf xx
标题3 链接 -c 命令 -d 比率:时间 -z 密码

-c 命令 -up mrcc:remote:path/subdir -rcf --buffer-size:8M|key|key:value
-inf 用于包含词过滤器。
-exf 用于排除词过滤器。
-stv true 或 false (敏感过滤器)

示例: 标题 https://www.rss-url.com -inf 1080 or 720 or 144p|mkv or mp4|hevc -exf flv or web|xxx
这个过滤器将解析标题中包含`(1080 或 720 或 144p) 和 (mkv 或 mp4) 和 hevc`但不包含 (flv 或 web) 和 xxx 词的链接。您可以添加任何您想要的内容。

另一个示例: -inf 1080 or 720p|.web. or .webrip.|hvec or x264. 这将解析标题中包含 (1080 或 720p) 和 (.web. 或 .webrip.) 和 (hvec 或 x264) 的内容。我在 1080 前后添加了空格以避免错误匹配。如果标题中的数字是 `10805695`，如果添加没有空格的 1080，它将匹配 1080。

过滤器注意事项:
1. | 表示和。
2. 在相似键之间添加 `or`，您可以在质量之间或扩展名之间添加它，所以不要像这样添加过滤器 f: 1080|mp4 or 720|web，因为这将解析 1080 和 (mp4 或 720) 和 web ... 而不是 (1080 和 mp4) 或 (720 和 web)。
3. 您可以根据需要添加任意数量的 `or` 和 `|`。
4. 查看标题，如果在质量或扩展名或其他内容之后或之前有静态特殊字符，请在过滤器中使用它们以避免错误匹配。
超时: 60 秒。
"""

PASSWORD_ERROR_MESSAGE = """
<b>此链接需要密码!</b>
- 在链接后插入 <b>::</b> 并在标志后写入密码。

<b>示例:</b> 链接::我的密码
"""

user_settings_text = {
    "LEECH_SPLIT_SIZE": f"发送下载分割大小（以字节为单位）或使用 gb 或 mb。例如：40000000 或 2.5gb 或 1000mb。IS_PREMIUM_USER: {TgClient.IS_PREMIUM_USER}。超时：60 秒",
    "LEECH_DUMP_CHAT": """"发送下载目标 ID/用户名/PM。
* b:id/@username/pm (b: 表示通过机器人下载) (聊天的 id 或用户名，或写 pm 表示私人消息，机器人将私下发送文件给您) 何时应该使用 b:(通过机器人下载)? 当您的默认设置是通过用户下载，但您想为特定任务通过机器人下载时。
* u:id/@username(u: 表示通过用户下载) 这种情况下 OWNER 添加了 USER_STRING_SESSION。
* h:id/@username(混合下载) h: 根据文件大小通过机器人和用户上传文件。
* id/@username|topic_id(在特定聊天和主题中下载) 添加 | 不带空格，并在聊天 id 或用户名后写入主题 id。超时：60 秒""",
    "LEECH_FILENAME_PREFIX": r"发送下载文件名前缀。您可以添加 HTML 标签。例如：<code>@mychannel</code>。超时：60 秒",
    "THUMBNAIL_LAYOUT": "发送缩略图布局（宽x高，2x2，3x3，2x4，4x4，...）。例如：3x3。超时：60 秒",
    "RCLONE_PATH": "发送 Rclone 路径。如果您想使用您的 rclone 配置，请通过所有者/用户配置从 usetting 编辑或在 rclone 路径前添加 mrcc:。例如 mrcc:remote:folder。超时：60 秒",
    "RCLONE_FLAGS": "key:value|key|key|key:value 。在这里查看所有 <a href='https://rclone.org/flags/'>Rclone标志</a>\n例如：--buffer-size:8M|--drive-starred-only",
    "GDRIVE_ID": "发送 Gdrive ID。如果您想使用您的 token.pickle，请通过所有者/用户令牌从 usetting 编辑或在 id 前添加 mtp:。例如：mtp:F435RGGRDXXXXXX 。超时：60 秒",
    "INDEX_URL": "发送索引 URL。超时：60 秒",
    "UPLOAD_PATHS": "发送具有路径值的键的字典。例如：{'path 1': 'remote:rclonefolder', 'path 2': 'gdrive1 id', 'path 3': 'tg chat id', 'path 4': 'mrcc:remote:', 'path 5': b:@username} 。超时：60 秒",
    "EXCLUDED_EXTENSIONS": "发送排除的扩展名，用空格分隔，开头不带点。超时：60 秒",
    "NAME_SUBSTITUTE": r"""字词替换。您可以添加模式而不是普通文本。超时：60 秒
注意：您必须在这些字符前添加 \：\^$.|?*+()[]{}-
例如：script/code/s | mirror/leech | tea/ /s | clone | cpu/ | \[mltb\]/mltb | \\text\\/text/s
1. script 将被替换为 code，区分大小写
2. mirror 将被替换为 leech
4. tea 将被替换为空格，区分大小写
5. clone 将被删除
6. cpu 将被替换为空格
7. [mltb] 将被替换为 mltb
8. \text\ 将被替换为 text，区分大小写
""",
    "YT_DLP_OPTIONS": """发送 YT-DLP 选项字典。超时：60 秒
格式：{key: value, key: value, key: value}。
例如：{"format": "bv*+mergeall[vcodec=none]", "nocheckcertificate": True, "playliststart": 10, "fragment_retries": float("inf"), "matchtitle": "S13", "writesubtitles": True, "live_from_start": True, "postprocessor_args": {"ffmpeg": ["-threads", "4"]}, "wait_for_video": (5, 100), "download_ranges": [{"start_time": 0, "end_time": 10}]}
从这个<a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184'>文件</a>中查看所有 yt-dlp API 选项，或使用这个<a href='https://t.me/mltb_official_channel/177'>脚本</a>将命令行参数转换为 API 选项。""",
    "FFMPEG_CMDS": """FFmpeg 命令列表的字典。您可以在上传前为所有文件设置多个 FFmpeg 命令。不要在开头写 ffmpeg，直接从参数开始。
例如：{"subtitle": ["-i mltb.mkv -c copy -c:s srt mltb.mkv", "-i mltb.video -c copy -c:s srt mltb"], "convert": ["-i mltb.m4a -c:a libmp3lame -q:a 2 mltb.mp3", "-i mltb.audio -c:a libmp3lame -q:a 2 mltb.mp3"], extract: ["-i mltb -map 0:a -c copy mltb.mka -map 0:s -c copy mltb.srt"]}
注意：
- 在您希望机器人在命令运行完成后删除原始文件的列表中添加`-del`！
- 要在机器人中执行这些列表之一，例如，您必须使用 -ff subtitle（列表键）或 -ff convert（列表键）
这里我将解释如何使用 mltb.*，它是指您想要处理的文件的引用。
1. 第一个命令：输入是 mltb.mkv，所以这个命令将只对 mkv 视频起作用，输出也是 mltb.mkv，所以所有输出都是 mkv。-del 将在命令运行完成后删除原始媒体。
2. 第二个命令：输入是 mltb.video，所以这个命令将对所有视频起作用，输出只是 mltb，所以扩展名与输入文件相同。
3. 第三个命令：输入是 mltb.m4a，所以这个命令将只对 m4a 音频起作用，输出是 mltb.mp3，所以输出扩展名是 mp3。
4. 第四个命令：输入是 mltb.audio，所以这个命令将对所有音频起作用，输出是 mltb.mp3，所以输出扩展名是 mp3。""",
}


help_string = f"""
注意：尝试不带任何参数使用每个命令以查看更多详细信息。
/{BotCommands.MirrorCommand[0]} 或 /{BotCommands.MirrorCommand[1]}：开始镜像到云端。
/{BotCommands.QbMirrorCommand[0]} 或 /{BotCommands.QbMirrorCommand[1]}：使用 qBittorrent 开始镜像到云端。
/{BotCommands.JdMirrorCommand[0]} 或 /{BotCommands.JdMirrorCommand[1]}：使用 JDownloader 开始镜像到云端。
/{BotCommands.NzbMirrorCommand[0]} 或 /{BotCommands.NzbMirrorCommand[1]}：使用 Sabnzbd 开始镜像到云端。
/{BotCommands.YtdlCommand[0]} 或 /{BotCommands.YtdlCommand[1]}：镜像 yt-dlp 支持的链接。
/{BotCommands.LeechCommand[0]} 或 /{BotCommands.LeechCommand[1]}：开始下载到 Telegram。
/{BotCommands.QbLeechCommand[0]} 或 /{BotCommands.QbLeechCommand[1]}：使用 qBittorrent 开始下载。
/{BotCommands.JdLeechCommand[0]} 或 /{BotCommands.JdLeechCommand[1]}：使用 JDownloader 开始下载。
/{BotCommands.NzbLeechCommand[0]} 或 /{BotCommands.NzbLeechCommand[1]}：使用 Sabnzbd 开始下载。
/{BotCommands.YtdlLeechCommand[0]} 或 /{BotCommands.YtdlLeechCommand[1]}：下载 yt-dlp 支持的链接。
/{BotCommands.CloneCommand} [drive_url]：复制文件/文件夹到 Google Drive。
/{BotCommands.CountCommand} [drive_url]：计算 Google Drive 的文件/文件夹数量。
/{BotCommands.DeleteCommand} [drive_url]：从 Google Drive 删除文件/文件夹（仅限所有者和 Sudo）。
/{BotCommands.UserSetCommand[0]} 或 /{BotCommands.UserSetCommand[1]} [query]：用户设置。
/{BotCommands.BotSetCommand[0]} 或 /{BotCommands.BotSetCommand[1]} [query]：机器人设置。
/{BotCommands.SelectCommand}：通过 gid 或回复选择种子或 nzb 中的文件。
/{BotCommands.CancelTaskCommand[0]} 或 /{BotCommands.CancelTaskCommand[1]} [gid]：通过 gid 或回复取消任务。
/{BotCommands.ForceStartCommand[0]} 或 /{BotCommands.ForceStartCommand[1]} [gid]：通过 gid 或回复强制开始任务。
/{BotCommands.CancelAllCommand} [query]：取消所有 [status] 任务。
/{BotCommands.ListCommand} [query]：在 Google Drive 中搜索。
/{BotCommands.SearchCommand} [query]：使用 API 搜索种子。
/{BotCommands.StatusCommand}：显示所有下载的状态。
/{BotCommands.StatsCommand}：显示机器人所在机器的统计信息。
/{BotCommands.PingCommand}：检查 Ping 机器人所需的时间（仅限所有者和 Sudo）。
/{BotCommands.AuthorizeCommand}：授权聊天或用户使用机器人（仅限所有者和 Sudo）。
/{BotCommands.UnAuthorizeCommand}：取消授权聊天或用户使用机器人（仅限所有者和 Sudo）。
/{BotCommands.UsersCommand}：显示用户设置（仅限所有者和 Sudo）。
/{BotCommands.AddSudoCommand}：添加 sudo 用户（仅限所有者）。
/{BotCommands.RmSudoCommand}：删除 sudo 用户（仅限所有者）。
/{BotCommands.RestartCommand}：重启并更新机器人（仅限所有者和 Sudo）。
/{BotCommands.LogCommand}：获取机器人的日志文件。方便获取崩溃报告（仅限所有者和 Sudo）。
/{BotCommands.ShellCommand}：运行 shell 命令（仅限所有者）。
/{BotCommands.AExecCommand}：执行异步函数（仅限所有者）。
/{BotCommands.ExecCommand}：执行同步函数（仅限所有者）。
/{BotCommands.ClearLocalsCommand}：清除 {BotCommands.AExecCommand} 或 {BotCommands.ExecCommand} 本地变量（仅限所有者）。
/{BotCommands.RssCommand}：RSS 菜单。
"""
