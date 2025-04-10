import argparse
import sys
import os
import time

try :
    from pyrogram import Client
    from pyrogram.errors import PhoneCodeInvalid, PhoneCodeExpired
except Exception as e :
    print(e)
    print("\nInstall pyrogram: pip3 install pyrogram")
    exit(1)

parser = argparse.ArgumentParser(description="生成Pyrogram会话字符串")
parser.add_argument("--api_id", type=int, required=True, help="Telegram API ID")
parser.add_argument("--api_hash", type=str, required=True, help="Telegram API Hash")
parser.add_argument("--phone", type=str, required=True, help="电话号码（带国家代码）")
parser.add_argument("--password", type=str, help="两步验证密码（如果有）")
parser.add_argument("--code_file", type=str, help="存放验证码的文件路径")

args = parser.parse_args()

API_ID = args.api_id
API_HASH = args.api_hash
PHONE = args.phone
PASSWORD = args.password
CODE_FILE = args.code_file or "verification_code.txt"

print("生成Pyrogram会话字符串...")
print(f"使用API ID: {API_ID}")
print(f"使用API HASH: {API_HASH}")
print(f"电话号码: {PHONE}")
print(f"验证码将从文件读取: {CODE_FILE}")

# 清空或创建验证码文件
with open(CODE_FILE, "w") as f :
    f.write("")

# 创建客户端但不连接
app = Client(
    "temp_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE,
    in_memory=True
)


# 自定义电话验证码处理器
async def phone_code_handler() :
    print(f"Telegram已发送验证码到 {PHONE}")
    print(f"请将验证码写入文件: {CODE_FILE}")

    # 等待验证码文件被填写
    code = ""
    max_wait = 300  # 最多等待300秒
    wait_time = 0

    while not code and wait_time < max_wait :
        try :
            with open(CODE_FILE, "r") as f :
                code = f.read().strip()
            if code :
                return code
        except :
            pass

        time.sleep(5)
        wait_time += 5
        print(f"等待验证码... 已等待{wait_time}秒")

    if not code :
        raise Exception("等待验证码超时")

    return code


# 自定义密码处理器
async def password_handler() :
    if PASSWORD :
        return PASSWORD
    raise Exception("需要两步验证密码，但未提供")


try :
    # 设置验证码和密码处理器
    app.phone_code_handler = phone_code_handler
    app.password_handler = password_handler

    # 启动客户端
    app.start()

    # 导出会话字符串
    session_string = app.export_session_string()

    print("\n您的SESSION_STRING已生成:")
    print("-" * 50)
    print(session_string)
    print("-" * 50)
    print("\n请将此字符串复制到您的配置文件中的USER_SESSION_STRING变量。")

    # 停止客户端
    app.stop()

    # 清理临时文件
    try :
        os.remove(CODE_FILE)
        os.remove("temp_session.session")
    except :
        pass

except Exception as e :
    print(f"生成会话字符串时出错: {e}")