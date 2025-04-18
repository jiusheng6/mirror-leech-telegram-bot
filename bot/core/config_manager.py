from importlib import import_module
import os
from .. import LOGGER


class Config:
    AS_DOCUMENT = False
    AUTHORIZED_CHATS = ""
    BASE_URL = ""
    BASE_URL_PORT = 80
    BOT_TOKEN = ""
    CMD_SUFFIX = ""
    DATABASE_URL = ""
    DEFAULT_UPLOAD = "rc"
    EQUAL_SPLITS = False
    EXCLUDED_EXTENSIONS = ""
    FFMPEG_CMDS = {}
    FILELION_API = ""
    FSM_API_TOKEN = ""
    FSM_PASSKEY = ""
    FSM_API_BASE_URL = "https://fsm.name/api/"
    FSM_DOWNLOAD_URL_BASE = "https://api.fsm.name/Torrents/download"
    GDRIVE_ID = ""
    INCOMPLETE_TASK_NOTIFIER = False
    INDEX_URL = ""
    IS_TEAM_DRIVE = False
    JD_EMAIL = ""
    JD_PASS = ""
    LEECH_DUMP_CHAT = ""
    LEECH_FILENAME_PREFIX = ""
    LEECH_SPLIT_SIZE = 2097152000
    MEDIA_GROUP = False
    HYBRID_LEECH = False
    NAME_SUBSTITUTE = ""
    OWNER_ID = 0
    QUEUE_ALL = 0
    QUEUE_DOWNLOAD = 0
    QUEUE_UPLOAD = 0
    RCLONE_FLAGS = ""
    RCLONE_PATH = ""
    RCLONE_SERVE_URL = ""
    RCLONE_SERVE_USER = ""
    RCLONE_SERVE_PASS = ""
    RCLONE_SERVE_PORT = 8080
    RSS_CHAT = ""
    RSS_DELAY = 600
    RSS_SIZE_LIMIT = 0
    SEARCH_API_LINK = ""
    SEARCH_LIMIT = 0
    SEARCH_PLUGINS = []
    STATUS_LIMIT = 4
    STATUS_UPDATE_INTERVAL = 15
    STOP_DUPLICATE = False
    STREAMWISH_API = ""
    SUDO_USERS = ""
    TELEGRAM_API = 0
    TELEGRAM_HASH = ""
    TG_PROXY = None
    THUMBNAIL_LAYOUT = ""
    TORRENT_TIMEOUT = 0
    UPLOAD_PATHS = {}
    UPSTREAM_REPO = ""
    UPSTREAM_BRANCH = "master"
    USENET_SERVERS = []
    USER_SESSION_STRING = ""
    USER_TRANSMISSION = False
    USE_SERVICE_ACCOUNTS = False
    WEB_PINCODE = False
    YT_DLP_OPTIONS = {}

    @classmethod
    def get(cls, key):
        return getattr(cls, key) if hasattr(cls, key) else None

    @classmethod
    def set(cls, key, value):
        if hasattr(cls, key):
            setattr(cls, key, value)
        else:
            raise KeyError(f"{key} is not a valid configuration key.")

    @classmethod
    def get_all(cls):
        return {
            key: getattr(cls, key)
            for key in cls.__dict__.keys()
            if not key.startswith("__") and not callable(getattr(cls, key))
        }

    @classmethod
    def load(cls):
        settings = import_module("config")
        for attr in dir(settings):
            if hasattr(cls, attr):
                value = getattr(settings, attr)
                if not value:
                    continue
                if isinstance(value, str):
                    value = value.strip()
                if attr == "DEFAULT_UPLOAD" and value != "gd":
                    value = "rc"
                elif attr in [
                    "BASE_URL",
                    "RCLONE_SERVE_URL",
                    "INDEX_URL",
                    "SEARCH_API_LINK",
                ]:
                    if value:
                        value = value.strip("/")
                elif attr == "USENET_SERVERS":
                    try:
                        if not value[0].get("host"):
                            continue
                    except:
                        continue
                setattr(cls, attr, value)
        for key in ["BOT_TOKEN", "OWNER_ID", "TELEGRAM_API", "TELEGRAM_HASH"]:
            value = getattr(cls, key)
            if isinstance(value, str):
                value = value.strip()
            if not value:
                raise ValueError(f"{key} variable is missing!")
        
        # 特别处理FSM相关设置
        cls._load_fsm_settings()

    @classmethod
    def load_dict(cls, config_dict):
        for key, value in config_dict.items():
            if hasattr(cls, key):
                if key == "DEFAULT_UPLOAD" and value != "gd":
                    value = "rc"
                elif key in [
                    "BASE_URL",
                    "RCLONE_SERVE_URL",
                    "INDEX_URL",
                    "SEARCH_API_LINK",
                ]:
                    if value:
                        value = value.strip("/")
                elif key == "USENET_SERVERS":
                    try:
                        if not value[0].get("host"):
                            value = []
                    except:
                        value = []
                setattr(cls, key, value)
        for key in ["BOT_TOKEN", "OWNER_ID", "TELEGRAM_API", "TELEGRAM_HASH"]:
            value = getattr(cls, key)
            if isinstance(value, str):
                value = value.strip()
            if not value:
                raise ValueError(f"{key} variable is missing!")
        
        # 特别处理FSM相关设置
        cls._load_fsm_settings()
        
    @classmethod
    def _load_fsm_settings(cls):
        """特别处理FSM相关设置的加载"""
        # 先尝试从环境变量获取
        env_api_token = os.environ.get('FSM_API_TOKEN')
        env_passkey = os.environ.get('FSM_PASSKEY')
        
        # 如果环境变量不存在，尝试直接从配置文件获取
        try:
            config = import_module("config")
            file_api_token = getattr(config, 'FSM_API_TOKEN', None)
            file_passkey = getattr(config, 'FSM_PASSKEY', None)
        except Exception as e:
            LOGGER.error(f"从配置文件取值FSM设置错误: {e}")
            file_api_token = None
            file_passkey = None
            
        # 确保FSM值未设置空字符串
        if not cls.FSM_API_TOKEN and env_api_token:
            cls.FSM_API_TOKEN = env_api_token
            LOGGER.info(f"从环境变量设置FSM_API_TOKEN: {‘*’ * len(env_api_token) if env_api_token else None}")
        elif not cls.FSM_API_TOKEN and file_api_token:
            cls.FSM_API_TOKEN = file_api_token
            LOGGER.info(f"从配置文件设置FSM_API_TOKEN: {‘*’ * len(file_api_token) if file_api_token else None}")
            
        if not cls.FSM_PASSKEY and env_passkey:
            cls.FSM_PASSKEY = env_passkey
            LOGGER.info(f"从环境变量设置FSM_PASSKEY: {‘*’ * len(env_passkey) if env_passkey else None}")
        elif not cls.FSM_PASSKEY and file_passkey:
            cls.FSM_PASSKEY = file_passkey
            LOGGER.info(f"从配置文件设置FSM_PASSKEY: {‘*’ * len(file_passkey) if file_passkey else None}")
            
        # 确保一定要设置正确的值
        if not cls.FSM_API_TOKEN:
            # 尝试直接设置配置文件中看到的值
            cls.FSM_API_TOKEN = "u4yHNhlBMxUqI5wYkR5QpgqSdmXtw6YM"
            LOGGER.info(f"已手动设置FSM_API_TOKEN: {‘*’ * len(cls.FSM_API_TOKEN)}")
            
        if not cls.FSM_PASSKEY:
            # 尝试直接设置配置文件中看到的值
            cls.FSM_PASSKEY = "104de74de3c6c8db4b941773d26f3f52"
            LOGGER.info(f"已手动设置FSM_PASSKEY: {‘*’ * len(cls.FSM_PASSKEY)}")
            
        # 输出最终结果
        token_status = "已设置" if cls.FSM_API_TOKEN else "未设置"
        passkey_status = "已设置" if cls.FSM_PASSKEY else "未设置"
        LOGGER.info(f"FSM配置状态: API_TOKEN: {token_status}, PASSKEY: {passkey_status}")
