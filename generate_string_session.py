import argparse
import sys

try :
    from pyrogram import Client
except Exception as e :
    print(e)
    print("\nInstall pyrogram: pip3 install pyrogram")
    exit(1)

parser = argparse.ArgumentParser(description="生成Pyrogram会话字符串")
parser.add_argument("--api_id", type=int, help="Telegram API ID")
parser.add_argument("--api_hash", type=str, help="Telegram API Hash")
parser.add_argument("--phone", type=str, help="电话号码（带国家代码）")

args = parser.parse_args()

# 使用命令行参数或默认值
API_KEY = args.api_id if args.api_id else 12345678  # 替换为您的默认API KEY
API_HASH = args.api_hash if args.api_hash else "abcdef1234567890abcdef1234567890"  # 替换为您的默认API HASH
PHONE = args.phone

print("生成Pyrogram会话字符串...")
print(f"使用API ID: {API_KEY}")
print(f"使用API HASH: {API_HASH}")

try :
    if PHONE :
        with Client(name="USS", api_id=API_KEY, api_hash=API_HASH, phone_number=PHONE, in_memory=True) as app :
            session_string = app.export_session_string()
    else :
        with Client(name="USS", api_id=API_KEY, api_hash=API_HASH, in_memory=True) as app :
            session_string = app.export_session_string()

    print("\n您的SESSION_STRING已生成:")
    print("-" * 50)
    print(session_string)
    print("-" * 50)
    print("\n请将此字符串复制到您的配置文件中的USER_SESSION_STRING变量。")
except Exception as e :
    print(f"生成会话字符串时出错: {e}")