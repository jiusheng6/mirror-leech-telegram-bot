import time
import traceback
from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from .. import LOGGER
from ..core.mltb_client import TgClient
from ..core.config_manager import Config as ConfigImport

# 创建对Config的本地引用
Config = ConfigImport
from ..helper.telegram_helper.message_utils import send_message, edit_message, delete_message
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.telegram_helper.button_build import ButtonMaker
from ..helper.ext_utils.telegraph_helper import telegraph
from ..helper.ext_utils.bot_utils import new_task
from ..helper.ext_utils.fsm_utils import get_torrent_types, get_systematics, search_torrents, get_torrent_details, \
    get_download_url

# 在模块加载时一次性载入配置
Config.load()

# 常量
RESULTS_PER_PAGE = 10  # 每页显示的结果数
MAX_TELEGRAPH_RESULTS = 50  # Telegraph页面最大显示结果数

# 回调数据前缀
TYPE_PREFIX = "fsmt:"  # 缩短前缀
SYSTEM_PREFIX = "fsms:"  # 缩短前缀
DOWNLOAD_PREFIX = "fsmd:"  # 缩短前缀
PAGE_PREFIX = "fsmp:"  # 缩短前缀

# 存储当前搜索上下文的字典，使用用户ID作为键
search_contexts = {}


@new_task
async def fsm_search(client, message) :
    """处理/fsm命令搜索种子"""
    # 检查命令是否包含搜索关键词
    args = message.text.split(" ", 1)
    if len(args) == 1 :
        help_msg = "请提供搜索关键词。\n示例: /fsm 关键词"
        return await send_message(message, help_msg)

    keyword = args[1]
    user_id = message.from_user.id

    try :
        # 记录开始尝试获取类型
        LOGGER.info(f"FSM搜索: 正在获取种子分类信息，关键词: {keyword}")
        indicator_msg = await send_message(message, "<b>正在获取种子分类信息...</b>")

        # 获取种子分类
        torrent_types = await get_torrent_types()

        # 记录获取到的分类
        LOGGER.info(f"FSM搜索: 成功获取种子分类数量: {len(torrent_types)}")

        # 创建分类按钮
        buttons = ButtonMaker()
        for i, type_item in enumerate(torrent_types) :
            # 使用简短的索引作为回调数据
            buttons.data_button(
                type_item['name'],
                f"{TYPE_PREFIX}{i}"
            )

            # 将索引与类型ID的映射保存在用户上下文中
            if user_id not in search_contexts :
                search_contexts[user_id] = {}

            if 'type_mapping' not in search_contexts[user_id] :
                search_contexts[user_id]['type_mapping'] = {}

            search_contexts[user_id]['type_mapping'][str(i)] = type_item['id']
            search_contexts[user_id]['keyword'] = keyword

            LOGGER.debug(f"FSM搜索: 添加分类按钮: {type_item['name']} (ID: {type_item['id']})")

        # 添加"全部"按钮
        buttons.data_button("全部分类", f"{TYPE_PREFIX}all")
        buttons.data_button("取消", f"{TYPE_PREFIX}cancel")

        button = buttons.build_menu(2)
        return await edit_message(indicator_msg, "请选择种子分类:", button)

    except Exception as e :
        LOGGER.error(f"FSM搜索错误: {e}")

        # 尝试打印更详细的错误信息
        error_trace = traceback.format_exc()
        LOGGER.error(f"FSM搜索异常详情:\n{error_trace}")

        # 检查FSM API配置
        # 重新导入以确保获取最新设置
        from ..core.config_manager import Config
        api_token = Config.FSM_API_TOKEN
        passkey = Config.FSM_PASSKEY
        base_url = Config.FSM_API_BASE_URL

        # 配置检查
        LOGGER.info(f"FSM API配置检查:\n"
                    f"- API基础URL: {base_url}\n"
                    f"- API令牌存在: {'是' if api_token else '否'} (长度: {len(api_token) if api_token else 0})\n"
                    f"- Passkey存在: {'是' if passkey else '否'} (长度: {len(passkey) if passkey else 0})\n")

        # 尝试从环境变量中读取
        import os
        env_token = os.environ.get('FSM_API_TOKEN', '')
        env_passkey = os.environ.get('FSM_PASSKEY', '')
        LOGGER.info(f"环境变量检查:\n"
                    f"- 环境变量FSM_API_TOKEN存在: {'是' if env_token else '否'}\n"
                    f"- 环境变量FSM_PASSKEY存在: {'是' if env_passkey else '否'}")

        # 在错误信息中包含更多详细信息
        error_msg = f"错误: {str(e)}\n\n"
        error_msg += "详细请查看日志。可能与 FSM API 认证相关或 API 地址变更。"

        return await send_message(message, error_msg)


@new_task
async def fsm_callback(client, callback_query) :
    """处理FSM搜索按钮的回调查询"""
    message = callback_query.message
    data = callback_query.data
    user_id = callback_query.from_user.id

    # 确保用户上下文存在
    if user_id not in search_contexts :
        search_contexts[user_id] = {}

    try :
        # 处理分类选择
        if data.startswith(TYPE_PREFIX) :
            type_data = data[len(TYPE_PREFIX) :]
            if type_data == "cancel" :
                await callback_query.answer()
                # 清理上下文
                if user_id in search_contexts :
                    del search_contexts[user_id]
                return await edit_message(message, "搜索已取消！")

            # 从上下文中获取关键词
            keyword = search_contexts[user_id].get('keyword', '')

            # 获取实际的类型ID
            if type_data == "all" :
                type_id = "0"  # 全部分类
            else :
                type_id = search_contexts[user_id]['type_mapping'].get(type_data, "0")

            # 保存到上下文
            search_contexts[user_id]['selected_type'] = type_id

            # 获取优惠类型
            systematics = await get_systematics()

            # 创建优惠类型按钮
            buttons = ButtonMaker()
            for i, sys_item in enumerate(systematics) :
                buttons.data_button(
                    sys_item['name'],
                    f"{SYSTEM_PREFIX}{i}"
                )

                # 存储索引与系统ID的映射
                if 'system_mapping' not in search_contexts[user_id] :
                    search_contexts[user_id]['system_mapping'] = {}

                search_contexts[user_id]['system_mapping'][str(i)] = sys_item['id']

            # 添加"全部"按钮
            buttons.data_button("全部优惠", f"{SYSTEM_PREFIX}all")
            buttons.data_button("取消", f"{SYSTEM_PREFIX}cancel")

            button = buttons.build_menu(2)
            await callback_query.answer()
            await edit_message(message, "请选择优惠类型:", button)

        # 处理优惠类型选择
        elif data.startswith(SYSTEM_PREFIX) :
            sys_data = data[len(SYSTEM_PREFIX) :]
            if sys_data == "cancel" :
                await callback_query.answer()
                # 清理上下文
                if user_id in search_contexts :
                    del search_contexts[user_id]
                return await edit_message(message, "搜索已取消！")

            # 从上下文中获取数据
            keyword = search_contexts[user_id].get('keyword', '')
            type_id = search_contexts[user_id].get('selected_type', "0")

            # 获取实际的系统ID
            if sys_data == "all" :
                systematics_id = "0"  # 全部优惠
            else :
                systematics_id = search_contexts[user_id]['system_mapping'].get(sys_data, "0")

            # 保存到上下文
            search_contexts[user_id]['selected_system'] = systematics_id

            await callback_query.answer()
            await edit_message(message, f"<b>正在搜索:</b> <i>{keyword}</i>...")

            # 搜索种子并发送到Telegraph
            search_results = await search_torrents(keyword, type_id, systematics_id)
            await handle_search_results(client, message, search_results, user_id)

        # 处理下载按钮
        elif data.startswith(DOWNLOAD_PREFIX) :
            tid = data[len(DOWNLOAD_PREFIX) :]  # 只传递种子ID

            await callback_query.answer("正在获取下载链接...")

            # 获取种子详情以获取标题
            try :
                torrent_details = await get_torrent_details(tid)
                if not torrent_details.get('success', False) :
                    await edit_message(message, f"获取种子详情失败: {torrent_details.get('msg', '未知错误')}")
                    return

                torrent = torrent_details.get('data', {}).get('torrent', {})
                title = torrent.get('title', f'FSM_Torrent_{tid}')
            except :
                title = f'FSM_Torrent_{tid}'

            # 获取下载链接
            download_url = await get_download_url(tid)
            if not download_url :
                await edit_message(message, "无法获取下载链接")
                return

            # 提供下载链接给用户
            msg = f"为以下种子生成了下载链接: {title}\n\n"
            msg += f"📁 <b>直接下载链接</b> (带Passkey):\n"
            msg += f"<code>{download_url}</code>\n\n"
            msg += f"回复此消息并使用 /{BotCommands.QbMirrorCommand} 命令开始下载。"

            await edit_message(message, msg)

        # 处理翻页
        elif data.startswith(PAGE_PREFIX) :
            page = data[len(PAGE_PREFIX) :]  # 只获取页码

            # 从上下文中获取搜索数据
            keyword = search_contexts[user_id].get('keyword', '')
            type_id = search_contexts[user_id].get('selected_type', "0")
            systematics_id = search_contexts[user_id].get('selected_system', "0")

            await callback_query.answer()
            await edit_message(message, f"<b>正在获取第 {page} 页...</b>")

            # 搜索种子的新页面
            search_results = await search_torrents(keyword, type_id, systematics_id, page=page)
            await handle_search_results(client, message, search_results, user_id)

    except Exception as e :
        LOGGER.error(f"FSM回调错误: {e}")
        await callback_query.answer(f"出错了: {str(e)[:50]}", show_alert=True)
        await edit_message(message, f"错误: {str(e)}")


async def handle_search_results(client, message, search_results, user_id) :
    """处理并显示搜索结果，始终使用Telegraph"""
    if not search_results.get('success', False) :
        return await edit_message(message, f"搜索失败: {search_results.get('msg', '未知错误')}")

    torrents = search_results.get('data', {}).get('list', [])
    max_page = search_results.get('data', {}).get('maxPage', 1)
    current_page = int(search_results.get('data', {}).get('page', 1))

    # 从上下文中获取搜索关键词
    keyword = search_contexts[user_id].get('keyword', '')

    if not torrents :
        return await edit_message(message, f"未找到与 <i>'{keyword}'</i> 相关的结果")

    # 为所有结果创建Telegraph页面
    telegraph_content = []

    # 添加搜索信息
    telegraph_content.append(f"<h4>FSM 搜索结果: {keyword}</h4>")
    telegraph_content.append(f"<p>当前第 {current_page} 页，共 {max_page} 页</p>")

    # 创建结果表格
    telegraph_content.append("<table>")
    telegraph_content.append(
        "<thead><tr><th>标题</th><th>大小</th><th>做种</th><th>分类</th><th>上传日期</th><th>操作</th></tr></thead>")
    telegraph_content.append("<tbody>")

    # 添加每个种子作为一行
    count = 0
    for torrent in torrents[:MAX_TELEGRAPH_RESULTS] :  # 限制结果以防Telegraph出问题
        title = torrent.get('title', '未知')
        size = torrent.get('fileSize', '未知')
        seeds = torrent.get('peers', {}).get('upload', 0)
        category = torrent.get('type', {}).get('name', '未知')
        tid = torrent.get('tid')

        # 格式化时间戳
        created_ts = torrent.get('createdTs', 0)
        if created_ts :
            created_time = time.strftime('%Y-%m-%d', time.localtime(created_ts))
        else :
            created_time = '未知'

        # 格式化行
        row = f"<tr><td>{title}</td><td>{size}</td><td>{seeds}</td><td>{category}</td><td>{created_time}</td>"

        # 添加下载按钮/链接 - 为Telegraph提供命令
        row += f"<td>使用命令: <code>/fsm download {tid}</code></td></tr>"

        telegraph_content.append(row)
        count += 1

    telegraph_content.append("</tbody></table>")

    if max_page > 1 :
        telegraph_content.append("<br><center><h4>页面导航</h4></center>")
        nav_text = ""
        if current_page > 1 :
            nav_text += f"<a href='https://t.me/share/url?url=/fsm%20{keyword}%20page:{current_page - 1}'>« 上一页</a> | "
        nav_text += f"当前第 {current_page} 页"
        if current_page < max_page :
            nav_text += f" | <a href='https://t.me/share/url?url=/fsm%20{keyword}%20page:{current_page + 1}'>下一页 »</a>"
        telegraph_content.append(f"<center>{nav_text}</center>")

    # 创建Telegraph页面
    telegraph_page = await telegraph.create_page(
        title=f"FSM搜索: {keyword}",
        content=''.join(telegraph_content)
    )
    telegraph_url = telegraph_page['url']

    # 为Telegram消息创建按钮
    buttons = ButtonMaker()
    buttons.url_button("在Telegraph查看结果", telegraph_url)

    # 如果需要，添加分页按钮（使用简短的回调数据）
    if max_page > 1 :
        if current_page > 1 :
            buttons.data_button(
                "⬅️ 上一页",
                f"{PAGE_PREFIX}{current_page - 1}"
            )
        if current_page < max_page :
            buttons.data_button(
                "下一页 ➡️",
                f"{PAGE_PREFIX}{current_page + 1}"
            )

    button = buttons.build_menu(1)
    await edit_message(
        message,
        f"找到 {count} 个与 <i>'{keyword}'</i> 相关的结果。在Telegraph查看详细信息:",
        button
    )


@new_task
async def fsm_command_handler(client, message) :
    """处理 /fsm 命令，包括直接下载和搜索功能"""
    args = message.text.split()
    if len(args) >= 2 and args[1] == 'download' :
        if len(args) < 3 :
            return await send_message(message, "缺少种子ID，请使用正确的格式: /fsm download <tid>")

        tid = args[2]
        try :
            # 获取种子详情
            await send_message(message, f"正在获取种子 <code>{tid}</code> 的详情...")
            torrent_details = await get_torrent_details(tid)

            if not torrent_details.get('success', False) :
                return await send_message(message, f"获取种子详情失败: {torrent_details.get('msg', '未知错误')}")

            torrent = torrent_details.get('data', {}).get('torrent', {})
            title = torrent.get('title', f'FSM_Torrent_{tid}')

            # 获取下载链接
            download_url = await get_download_url(tid)
            if not download_url :
                return await send_message(message, "无法获取下载链接")

            # 提供下载链接给用户
            msg = f"为以下种子生成了下载链接: {title}\n\n"
            msg += f"📁 <b>直接下载链接</b> (带Passkey):\n"
            msg += f"<code>{download_url}</code>\n\n"
            msg += f"回复此消息并使用 /{BotCommands.QbMirrorCommand} 命令开始下载。"

            return await send_message(message, msg)
        except Exception as e :
            LOGGER.error(f"FSM下载命令错误: {e}")
            return await send_message(message, f"错误: {str(e)}")

    # 处理带页码参数的搜索
    page = 1
    keyword = ""

    if len(args) > 1 :
        # 检查是否有页码参数
        for arg in args[1 :] :
            if arg.startswith("page:") :
                try :
                    page = int(arg.split(":", 1)[1])
                except :
                    pass
            else :
                keyword += f"{arg} "

        keyword = keyword.strip()

        if keyword and page > 1 :
            # 直接搜索指定页面
            user_id = message.from_user.id
            if user_id not in search_contexts :
                search_contexts[user_id] = {}

            search_contexts[user_id]['keyword'] = keyword
            search_contexts[user_id]['selected_type'] = '0'  # 默认全部分类
            search_contexts[user_id]['selected_system'] = '0'  # 默认全部优惠

            await send_message(message, f"<b>正在搜索:</b> <i>{keyword}</i> (第 {page} 页)...")
            search_results = await search_torrents(keyword, '0', '0', page=str(page))
            return await handle_search_results(client, message, search_results, user_id)

    # 正常处理搜索
    await fsm_search(client, message)


# 模块初始化日志
LOGGER.info("FSM 搜索模块已加载")