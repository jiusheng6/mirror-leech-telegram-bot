"""
Mirror-Leech-Telegram-Bot 配置文件
此文件包含Bot运行所需的所有配置项
请在使用前填写必填配置
"""

# ==================== 必填配置 ====================
BOT_TOKEN = ""                # Telegram Bot令牌，从 @BotFather 获取
OWNER_ID = 0                  # Bot拥有者的Telegram用户ID（数字）
TELEGRAM_API = 0              # Telegram API ID，从 my.telegram.org 获取
TELEGRAM_HASH = ""            # Telegram API Hash，从 my.telegram.org 获取

# ==================== 可选配置 ====================
# Telegram代理配置（如果需要）
TG_PROXY = {}                 # 格式: {'addr': 'IP:PORT', 'username': 'username', 'password': 'password'}

# 用户会话字符串（用于用户账号功能）
USER_SESSION_STRING = ""      # 用户账号会话字符串，用于访问私人频道内容等

# 命令后缀，用于区分同一聊天中的多个机器人
CMD_SUFFIX = ""               # 例如设置为"_"，则命令变为 /mirror_

# 权限控制
AUTHORIZED_CHATS = ""         # 授权使用机器人的聊天ID，用逗号分隔，例如："-100123456789,-100987654321"
SUDO_USERS = ""               # 具有管理权限的用户ID，用逗号分隔，例如："123456789,987654321"

# 数据库配置
DATABASE_URL = ""             # MongoDB或PostgreSQL数据库URL

# 状态显示设置
STATUS_LIMIT = 4              # 状态消息中显示的任务数量
DEFAULT_UPLOAD = "rc"         # 默认上传位置：rc (rclone) 或 gd (Google Drive)
STATUS_UPDATE_INTERVAL = 15   # 状态更新间隔（秒）

# 文件托管API密钥
FILELION_API = ""             # FileLion API密钥
STREAMWISH_API = ""           # StreamWish API密钥

# 文件处理设置
EXCLUDED_EXTENSIONS = ""      # 排除的文件扩展名，用空格分隔，例如："exe txt jpg"
INCOMPLETE_TASK_NOTIFIER = False  # 是否通知未完成的任务
YT_DLP_OPTIONS = ""           # yt-dlp下载器的自定义选项（JSON格式）
USE_SERVICE_ACCOUNTS = False  # 是否使用服务账户进行Google Drive操作
NAME_SUBSTITUTE = ""          # 文件名替换规则，格式: "原始文本/替换文本|原始文本/替换文本"
FFMPEG_CMDS = {}              # FFmpeg命令预设，用于视频/音频处理

# 上传路径设置
UPLOAD_PATHS = {}             # 预定义的上传路径，格式: {"path1": "destination1", "path2": "destination2"}

# ==================== Google Drive工具 ====================
GDRIVE_ID = ""                # Google Drive文件夹ID
IS_TEAM_DRIVE = False         # 是否是团队云端硬盘
STOP_DUPLICATE = False        # 是否阻止上传重复文件
INDEX_URL = ""                # Google Drive索引URL，以访问文件

# ==================== Rclone配置 ====================
RCLONE_PATH = ""              # Rclone配置路径，格式: "remote:path"
RCLONE_FLAGS = ""             # Rclone额外标志
RCLONE_SERVE_URL = ""         # Rclone服务URL
RCLONE_SERVE_PORT = 0         # Rclone服务端口
RCLONE_SERVE_USER = ""        # Rclone服务用户名
RCLONE_SERVE_PASS = ""        # Rclone服务密码

# ==================== JDownloader配置 ====================
JD_EMAIL = ""                 # JDownloader账号邮箱
JD_PASS = ""                  # JDownloader账号密码

# ==================== Sabnzbd配置 ====================
USENET_SERVERS = [
    {
        "name": "main",           # 服务器名称
        "host": "",               # 服务器主机地址
        "port": 563,              # 服务器端口
        "timeout": 60,            # 连接超时（秒）
        "username": "",           # 用户名
        "password": "",           # 密码
        "connections": 8,         # 最大连接数
        "ssl": 1,                 # 是否使用SSL (0=否, 1=是)
        "ssl_verify": 2,          # SSL验证 (0=禁用, 1=验证主机, 2=验证对等方)
        "ssl_ciphers": "",        # SSL加密套件
        "enable": 1,              # 是否启用此服务器 (0=否, 1=是)
        "required": 0,            # 是否为必需服务器 (0=否, 1=是)
        "optional": 0,            # 是否为可选服务器 (0=否, 1=是)
        "retention": 0,           # 文件保留期（天）
        "send_group": 0,          # 是否发送组信息 (0=否, 1=是)
        "priority": 0,            # 服务器优先级 (0=普通, >0=优先)
    }
]

# ==================== 更新设置 ====================
UPSTREAM_REPO = ""            # 上游仓库URL，用于自动更新
UPSTREAM_BRANCH = "master"    # 上游仓库分支

# ==================== 下载设置 ====================
LEECH_SPLIT_SIZE = 0          # 下载文件分割大小（字节），0表示不分割
AS_DOCUMENT = False           # 是否将所有文件作为文档发送，而不是作为媒体
EQUAL_SPLITS = False          # 是否创建大小相等的分割部分
MEDIA_GROUP = False           # 是否将媒体文件作为组发送
USER_TRANSMISSION = False     # 是否使用用户会话下载
HYBRID_LEECH = False          # 是否启用混合下载（同时使用机器人和用户会话）
LEECH_FILENAME_PREFIX = ""    # 下载文件名前缀
LEECH_DUMP_CHAT = ""          # 下载文件转储聊天ID
THUMBNAIL_LAYOUT = ""         # 缩略图布局，格式: "WxH"（如 "3x3"）

# ==================== BT/Aria2c设置 ====================
TORRENT_TIMEOUT = 0           # 种子超时时间（秒），0表示无超时
BASE_URL = ""                 # Web服务基础URL
BASE_URL_PORT = 0             # Web服务端口
WEB_PINCODE = False           # 是否为web界面启用密码保护

# ==================== 队列系统 ====================
QUEUE_ALL = 0                 # 最大并行任务数，0表示无限制
QUEUE_DOWNLOAD = 0            # 最大并行下载任务数，0表示无限制
QUEUE_UPLOAD = 0              # 最大并行上传任务数，0表示无限制

# ==================== RSS设置 ====================
RSS_DELAY = 600               # RSS检查间隔（秒）
RSS_CHAT = ""                 # RSS发送消息的聊天ID
RSS_SIZE_LIMIT = 0            # RSS下载大小限制（字节），0表示无限制

# ==================== 种子搜索 ====================
SEARCH_API_LINK = ""          # 种子搜索API链接
SEARCH_LIMIT = 0              # 搜索结果限制，0表示使用默认值

# FSM API 配置
FSM_API_TOKEN = ""            # FSM API令牌，从环境变量获取或直接设置
FSM_PASSKEY = ""              # FSM下载所需的Passkey
FSM_API_BASE_URL = "https://fsm.name/api/"  # FSM API主地址
FSM_DOWNLOAD_URL_BASE = "https://api.fsm.name/Torrents/download"  # FSM下载接口基址
# 搜索插件列表
SEARCH_PLUGINS = [
    # qBittorrent官方插件
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/piratebay.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/limetorrents.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torlock.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentscsv.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/eztv.py",
    "https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines/torrentproject.py",
    # 社区插件
    "https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engines/master/kickass_torrent.py",
    "https://raw.githubusercontent.com/MaurizioRicci/qBittorrent_search_engines/master/yts_am.py",
    "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/linuxtracker.py",
    "https://raw.githubusercontent.com/MadeOfMagicAndWires/qBit-plugins/master/engines/nyaasi.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/ettv.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/glotorrents.py",
    "https://raw.githubusercontent.com/LightDestory/qBittorrent-Search-Plugins/master/src/engines/thepiratebay.py",
    "https://raw.githubusercontent.com/v1k45/1337x-qBittorrent-search-plugin/master/leetx.py",
    "https://raw.githubusercontent.com/nindogo/qbtSearchScripts/master/magnetdl.py",
    "https://raw.githubusercontent.com/msagca/qbittorrent_plugins/main/uniondht.py",
    "https://raw.githubusercontent.com/khensolomon/leyts/master/yts.py",
]
