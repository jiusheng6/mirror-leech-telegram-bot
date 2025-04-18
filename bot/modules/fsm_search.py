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
async def fsm_search(client, message):
    """处理/fsm命令搜索种子"""
    args = message.text.split(" ", 1)
    if len(args) == 1:
        help_msg = "请提供搜索关键词。\n示例: /fsm 关键词"
        return await send_message(message, help_msg)

    keyword = args[1]
    user_id = message.from_user.id

    try:
        LOGGER.info(f"FSM搜索: 正在获取种子分类信息，关键词: {keyword}")
        indicator_msg = await send_message(message, "<b>🔍 正在获取种子分类信息...</b>")

        torrent_types = await get_torrent_types()
        LOGGER.info(f"FSM搜索: 成功获取种子分类数量: {len(torrent_types)}")

        buttons = ButtonMaker()
        for i, type_item in enumerate(torrent_types):
            buttons.data_button(type_item['name'], f"{TYPE_PREFIX}{i}")
            if user_id not in search_contexts:
                search_contexts[user_id] = {}
            if 'type_mapping' not in search_contexts[user_id]:
                search_contexts[user_id]['type_mapping'] = {}
            search_contexts[user_id]['type_mapping'][str(i)] = type_item['id']
            search_contexts[user_id]['keyword'] = keyword
            LOGGER.debug(f"FSM搜索: 添加分类按钮: {type_item['name']} (ID: {type_item['id']})")

        buttons.data_button("全部分类", f"{TYPE_PREFIX}all")
        buttons.data_button("取消", f"{TYPE_PREFIX}cancel")

        button = buttons.build_menu(2)
        return await edit_message(indicator_msg, "<b>🔍 请选择种子分类:</b>", button)

    except Exception as e:
        LOGGER.error(f"FSM搜索错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"FSM搜索异常详情:\n{error_trace}")

        from ..core.config_manager import Config
        api_token = Config.FSM_API_TOKEN
        passkey = Config.FSM_PASSKEY
        base_url = Config.FSM_API_BASE_URL

        LOGGER.info(f"FSM API配置检查:\n"
                    f"- API基础URL: {base_url}\n"
                    f"- API令牌存在: {'是' if api_token else '否'} (长度: {len(api_token) if api_token else 0})\n"
                    f"- Passkey存在: {'是' if passkey else '否'} (长度: {len(passkey) if passkey else 0})\n")

        import os
        env_token = os.environ.get('FSM_API_TOKEN', '')
        env_passkey = os.environ.get('FSM_PASSKEY', '')
        LOGGER.info(f"环境变量检查:\n"
                    f"- 环境变量FSM_API_TOKEN存在: {'是' if env_token else '否'}\n"
                    f"- 环境变量FSM_PASSKEY存在: {'是' if env_passkey else '否'}")

        error_msg = f"错误: {str(e)}\n\n详细请查看日志。可能与 FSM API 认证相关或 API 地址变更。"
        return await send_message(message, error_msg)


@new_task
async def fsm_callback(client, callback_query):
    """处理FSM搜索按钮的回调查询"""
    message = callback_query.message
    data = callback_query.data
    user_id = callback_query.from_user.id

    if user_id not in search_contexts:
        search_contexts[user_id] = {}

    try:
        if data.startswith(TYPE_PREFIX):
            type_data = data[len(TYPE_PREFIX):]
            if type_data == "cancel":
                await callback_query.answer("已取消搜索")
                if user_id in search_contexts:
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 搜索已取消！</b>")

            keyword = search_contexts[user_id].get('keyword', '')
            if type_data == "all":
                type_id = "0"
            else:
                type_id = search_contexts[user_id]['type_mapping'].get(type_data, "0")
            search_contexts[user_id]['selected_type'] = type_id

            try:
                systematics = await get_systematics()
            except Exception as e:
                LOGGER.error(f"获取优惠类型失败: {e}")
                await callback_query.answer("获取优惠类型失败，请重试", show_alert=True)
                return await edit_message(message, f"<b>❌ 获取优惠类型失败:</b> {str(e)}")

            buttons = ButtonMaker()
            for i, sys_item in enumerate(systematics):
                buttons.data_button(sys_item['name'], f"{SYSTEM_PREFIX}{i}")
                if 'system_mapping' not in search_contexts[user_id]:
                    search_contexts[user_id]['system_mapping'] = {}
                search_contexts[user_id]['system_mapping'][str(i)] = sys_item['id']

            buttons.data_button("全部优惠", f"{SYSTEM_PREFIX}all")
            buttons.data_button("取消", f"{SYSTEM_PREFIX}cancel")

            button = buttons.build_menu(2)
            await callback_query.answer("请选择优惠类型")
            await edit_message(message, "<b>🔍 请选择优惠类型:</b>", button)

        elif data.startswith(SYSTEM_PREFIX):
            sys_data = data[len(SYSTEM_PREFIX):]
            if sys_data == "cancel":
                await callback_query.answer("已取消搜索")
                if user_id in search_contexts:
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 搜索已取消！</b>")

            keyword = search_contexts[user_id].get('keyword', '')
            type_id = search_contexts[user_id].get('selected_type', "0")
            if sys_data == "all":
                systematics_id = "0"
            else:
                systematics_id = search_contexts[user_id]['system_mapping'].get(sys_data, "0")
            search_contexts[user_id]['selected_system'] = systematics_id

            await callback_query.answer("正在搜索中...")
            await edit_message(message, f"<b>🔍 正在搜索:</b> <i>{keyword}</i>...")

            try:
                search_results = await search_torrents(keyword, type_id, systematics_id)
                await handle_search_results(client, message, search_results, user_id)
            except Exception as e:
                LOGGER.error(f"搜索种子错误: {e}")
                error_trace = traceback.format_exc()
                LOGGER.error(f"搜索种子异常详情:\n{error_trace}")
                await edit_message(message, f"<b>❌ 搜索失败:</b> {str(e)}")

        elif data.startswith(DOWNLOAD_PREFIX):
            tid = data[len(DOWNLOAD_PREFIX):]
            await callback_query.answer("正在获取下载链接...", show_alert=True)

            try:
                torrent_details = await get_torrent_details(tid)
                if not torrent_details.get('success', False):
                    return await edit_message(message, f"<b>❌ 获取种子详情失败:</b> {torrent_details.get('msg', '未知错误')}")
                torrent = torrent_details.get('data', {}).get('torrent', {})
                title = torrent.get('title', f'FSM_Torrent_{tid}')
            except Exception as e:
                LOGGER.error(f"获取种子详情错误: {e}")
                title = f'FSM_Torrent_{tid}'

            try:
                download_url = await get_download_url(tid)
                if not download_url:
                    return await edit_message(message, "<b>❌ 无法获取下载链接</b>")
            except Exception as e:
                LOGGER.error(f"获取下载链接错误: {e}")
                return await edit_message(message, f"<b>❌ 获取下载链接失败:</b> {str(e)}")

            msg = (
                f"<b>✅ 为以下种子生成了下载链接:</b>\n{title}\n\n"
                f"📁 <b>直接下载链接</b> (带Passkey):\n"
                f"<code>{download_url}</code>\n\n"
                f"📝 回复此消息并使用 /{BotCommands.QbMirrorCommand} 命令开始下载。"
            )
            await edit_message(message, msg)

        elif data.startswith(PAGE_PREFIX):
            page = data[len(PAGE_PREFIX):]
            if page == "noop":
                await callback_query.answer("当前页码信息")
                return
            keyword = search_contexts[user_id].get('keyword', '')
            type_id = search_contexts[user_id].get('selected_type', "0")
            systematics_id = search_contexts[user_id].get('selected_system', "0")

            await callback_query.answer(f"正在加载第 {page} 页...")
            await edit_message(message, f"<b>📃 正在获取第 {page} 页的搜索结果...</b>")

            try:
                search_results = await search_torrents(keyword, type_id, systematics_id, page=page)
                await handle_search_results(client, message, search_results, user_id)
            except Exception as e:
                LOGGER.error(f"翻页搜索错误: {e}")
                await edit_message(message, f"<b>❌ 获取第 {page} 页失败:</b> {str(e)}")

    except Exception as e:
        LOGGER.error(f"FSM回调错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"FSM回调异常详情:\n{error_trace}")

        error_str = str(e).lower()
        if "message_not_modified" in error_str or "message was not modified" in error_str:
            await callback_query.answer("内容未变更")
            return

        await callback_query.answer(f"出错了: {str(e)[:50]}", show_alert=True)
        await edit_message(message, f"<b>❌ 错误:</b> {str(e)}")


async def handle_search_results(client, message, search_results, user_id):
    """处理并显示搜索结果，使用优化的Telegraph页面"""
    if not search_results.get('success', False):
        return await edit_message(message, f"<b>❌ 搜索失败:</b> {search_results.get('msg', '未知错误')}")

    torrents = search_results.get('data', {}).get('list', [])
    max_page = search_results.get('data', {}).get('maxPage', 1)
    current_page = int(search_results.get('data', {}).get('page', 1))
    keyword = search_contexts[user_id].get('keyword', '')

    if not torrents:
        return await edit_message(message, f"<b>🔍 未找到与</b> <i>'{keyword}'</i> <b>相关的结果</b>")

    search_contexts[user_id]['current_page'] = current_page

    try:
        telegraph_content = []
        telegraph_content.append(f"<h3>🔍 FSM 搜索: {keyword}</h3>")
        telegraph_content.append(f"<p>找到 <b>{len(torrents)}</b> 个结果 | 第 {current_page}/{max_page} 页</p>")
        telegraph_content.append("<hr/>")
        telegraph_content.append("<ol>")

        for torrent in torrents[:MAX_TELEGRAPH_RESULTS]:
            title = torrent.get('title', '未知')
            size = torrent.get('fileSize', '未知')
            seeds = torrent.get('peers', {}).get('upload', 0)
            leech = torrent.get('peers', {}).get('download', 0)
            category = torrent.get('type', {}).get('name', '未知')
            tid = torrent.get('tid')
            created_ts = torrent.get('createdTs', 0)
            created_time = time.strftime('%Y-%m-%d', time.localtime(created_ts)) if created_ts else '未知'
            free_type = torrent.get('systematic', {}).get('name', '')
            free_badge = f"【{free_type}】" if free_type else ""

            item = "<li>"
            item += f"<h4>{free_badge}{title}</h4>"
            item += "<p>📁 大小: <b>" + size + "</b></p>"
            item += "<p>👥 做种/下载: <b>" + str(seeds) + "/" + str(leech) + "</b></p>"
            item += "<p>📂 分类: " + category + "</p>"
            item += "<p>📅 上传日期: " + created_time + "</p>"
            item += "<p>🆔 种子ID: <code>" + str(tid) + "</code></p>"
            item += "<p>📥 下载命令:</p>"
            item += "<p><code>/fsm download " + str(tid) + "</code></p>"
            item += "</li>"
            item += "<hr/>"
            telegraph_content.append(item)

        telegraph_content.append("</ol>")

        # if max_page > 1:
        #     telegraph_content.append("<hr/>")
        #     telegraph_content.append("<h4>页面导航</h4>")
        #     nav_parts = []
        #     if current_page > 1:
        #         nav_parts.append(
        #             f"<a href='https://t.me/share/url?url=/fsm%20{keyword}%20page:{current_page - 1}'>⬅️ 上一页</a>")
        #     nav_parts.append(f"<b>{current_page}/{max_page}</b>")
        #     if current_page < max_page:
        #         nav_parts.append(
        #             f"<a href='https://t.me/share/url?url=/fsm%20{keyword}%20page:{current_page + 1}'>下一页 ➡️</a>")
        #     telegraph_content.append("<p>" + " | ".join(nav_parts) + "</p>")

        telegraph_page = await telegraph.create_page(
            title=f"FSM搜索: {keyword}",
            content=''.join(telegraph_content)
        )
        telegraph_url = telegraph_page['url']

        buttons = ButtonMaker()
        buttons.url_button("📋 在Telegraph查看详细列表", telegraph_url)

        # 第二行：添加简洁的分页按钮
        if max_page > 1 :
            if current_page > 1 :
                buttons.data_button("⬅️ 上一页", f"{PAGE_PREFIX}{current_page - 1}")
            if current_page < max_page :
                buttons.data_button("下一页 ➡️", f"{PAGE_PREFIX}{current_page + 1}")

        buttons.data_button("🔄 刷新", f"{PAGE_PREFIX}{current_page}")
        buttons.data_button("❌ 取消", f"{TYPE_PREFIX}cancel")
        button = buttons.build_menu(2)

        result_msg = (
            f"<b>🔍 FSM搜索结果</b>\n\n"
            f"<b>关键词:</b> <code>{keyword}</code>\n"
            f"<b>找到结果:</b> {len(torrents)} 个\n\n"
            f"👇 <i>点击下方按钮查看完整列表或使用命令下载</i>\n"
        )

        if torrents:
            result_msg += "\n<b>📊 热门结果预览:</b>\n"
            for i, torrent in enumerate(torrents[:3], 1):
                title = torrent.get('title', '未知')
                seeds = torrent.get('peers', {}).get('upload', 0)
                size = torrent.get('fileSize', '未知')
                tid = torrent.get('tid')
                result_msg += (
                    f"{i}. <b>{title}</b>\n"
                    f"   📁 {size} | 👥 {seeds} | 🆔 <code>{tid}</code>\n\n"
                )

        await edit_message(message, result_msg, button)

    except Exception as e:
        LOGGER.error(f"处理搜索结果错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"处理搜索结果异常详情:\n{error_trace}")

        error_str = str(e).lower()
        if "tag is not allowed" in error_str:
            await edit_message(message, f"<b>❌ Telegraph标签错误:</b> {str(e)}\n\n请联系开发者修复。")
        else:
            await edit_message(message, f"<b>❌ 处理搜索结果失败:</b> {str(e)}")


@new_task
async def fsm_command_handler(client, message):
    """处理 /fsm 命令，包括直接下载和搜索功能"""
    args = message.text.split()
    if len(args) >= 2 and args[1] == 'download':
        if len(args) < 3:
            return await send_message(message, "缺少种子ID，请使用正确的格式: /fsm download <tid>")

        tid = args[2]
        try:
            await send_message(message, f"正在获取种子 <code>{tid}</code> 的详情...")
            torrent_details = await get_torrent_details(tid)
            if not torrent_details.get('success', False):
                return await send_message(message, f"获取种子详情失败: {torrent_details.get('msg', '未知错误')}")
            torrent = torrent_details.get('data', {}).get('torrent', {})
            title = torrent.get('title', f'FSM_Torrent_{tid}')
            download_url = await get_download_url(tid)
            if not download_url:
                return await send_message(message, "无法获取下载链接")

            msg = (
                f"为以下种子生成了下载链接: {title}\n\n"
                f"📁 <b>直接下载链接</b> (带Passkey):\n"
                f"<code>{download_url}</code>\n\n"
                f"回复此消息并使用 /{BotCommands.QbMirrorCommand} 命令开始下载。"
            )
            return await send_message(message, msg)
        except Exception as e:
            LOGGER.error(f"FSM下载命令错误: {e}")
            return await send_message(message, f"错误: {str(e)}")

    page = 1
    keyword = ""
    if len(args) > 1:
        for arg in args[1:]:
            if arg.startswith("page:"):
                try:
                    page = int(arg.split(":", 1)[1])
                except:
                    pass
            else:
                keyword += f"{arg} "
        keyword = keyword.strip()

        if keyword and page > 1:
            user_id = message.from_user.id
            if user_id not in search_contexts:
                search_contexts[user_id] = {}
            search_contexts[user_id]['keyword'] = keyword
            search_contexts[user_id]['selected_type'] = '0'
            search_contexts[user_id]['selected_system'] = '0'

            await send_message(message, f"<b>正在搜索:</b> <i>{keyword}</i> (第 {page} 页)...")
            search_results = await search_torrents(keyword, '0', '0', page=str(page))
            return await handle_search_results(client, message, search_results, user_id)

    await fsm_search(client, message)


# 模块初始化日志
LOGGER.info("FSM 搜索模块已加载")
