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
PREVIEW_RESULTS = 4  # 预览结果数量，增加到4个

# 回调数据前缀
TYPE_PREFIX = "fsmt:"  # 缩短前缀
SYSTEM_PREFIX = "fsms:"  # 缩短前缀
DOWNLOAD_PREFIX = "fsmd:"  # 缩短前缀
PAGE_PREFIX = "fsmp:"  # 缩短前缀
BROWSE_PREFIX = "fsmb:"  # 浏览分类前缀
DETAILS_PREFIX = "fsmi:"  # 种子详情前缀
HOT_PREFIX = "fsmh:"  # 热门种子前缀
LATEST_PREFIX = "fsml:"  # 最新种子前缀
VIEW_PREFIX = "fsmv:"  # 查看详情前缀 - 新增
BACK_PREFIX = "fsmback:"  # 返回前缀 - 新增

# 存储当前搜索上下文的字典，使用用户ID作为键
search_contexts = {}


# 辅助函数：HTML转义字符
def escape_html(text):
    """转义HTML中的特殊字符，确保输入是字符串"""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)  # 将非字符串类型转换为字符串
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# HTML清理函数 - 用于Telegraph内容
def clean_html_for_telegraph(html_content):
    """清理HTML内容，移除Telegraph不支持的标签"""
    if not html_content:
        return ""

    # 替换不支持的标签
    content = html_content

    # 替换span标签 (最常见的问题)
    import re
    # 替换带属性的span开始标签
    content = re.sub(r'<span[^>]*>', '', content)
    # 替换span结束标签
    content = re.sub(r'</span>', '', content)

    # 通用标签清理 - 可以根据需要扩展
    unsafe_tags = ['div', 'font', 'script', 'style', 'table', 'td', 'tr', 'th', 'tbody', 'thead']
    for tag in unsafe_tags:
        # 替换开始标签
        content = re.sub(f'<{tag}[^>]*>', '', content)
        # 替换结束标签
        content = re.sub(f'</{tag}>', '', content)

    return content


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
            search_contexts[user_id]['search_step'] = 'select_type'  # 记录当前步骤
            search_contexts[user_id]['indicator_msg'] = indicator_msg  # 保存消息对象
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
async def fsm_browse(client, message):
    """按分类浏览种子"""
    user_id = message.from_user.id

    try:
        LOGGER.info("FSM分类浏览: 正在获取种子分类信息")
        indicator_msg = await send_message(message, "<b>🔍 正在获取种子分类信息...</b>")

        torrent_types = await get_torrent_types()
        LOGGER.info(f"FSM分类浏览: 成功获取种子分类数量: {len(torrent_types)}")

        buttons = ButtonMaker()
        for i, type_item in enumerate(torrent_types):
            buttons.data_button(type_item['name'], f"{BROWSE_PREFIX}{i}")
            if user_id not in search_contexts:
                search_contexts[user_id] = {}
            if 'type_mapping' not in search_contexts[user_id]:
                search_contexts[user_id]['type_mapping'] = {}
            search_contexts[user_id]['type_mapping'][str(i)] = type_item['id']
            search_contexts[user_id]['keyword'] = "分类浏览"  # 标记为分类浏览
            search_contexts[user_id]['search_step'] = 'select_browse_type'  # 记录当前步骤
            search_contexts[user_id]['indicator_msg'] = indicator_msg  # 保存消息对象
            LOGGER.debug(f"FSM分类浏览: 添加分类按钮: {type_item['name']} (ID: {type_item['id']})")

        buttons.data_button("全部分类", f"{BROWSE_PREFIX}all")
        buttons.data_button("取消", f"{BROWSE_PREFIX}cancel")

        button = buttons.build_menu(2)
        return await edit_message(indicator_msg, "<b>📂 请选择要浏览的种子分类:</b>", button)

    except Exception as e:
        LOGGER.error(f"FSM分类浏览错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"FSM分类浏览异常详情:\n{error_trace}")
        error_msg = f"错误: {str(e)}\n\n详细请查看日志。"
        return await send_message(message, error_msg)


@new_task
async def fsm_hot(client, message, page="1"):
    """显示热门种子列表，支持分页"""
    user_id = message.from_user.id

    try:
        indicator_msg = await send_message(message, f"<b>🔥 正在获取热门种子列表 (第 {page} 页)...</b>")

        # 设置搜索上下文
        if user_id not in search_contexts:
            search_contexts[user_id] = {}
        search_contexts[user_id]['keyword'] = "热门种子排行"
        search_contexts[user_id]['selected_type'] = "0"
        search_contexts[user_id]['selected_system'] = "0"
        search_contexts[user_id]['current_page'] = int(page)
        search_contexts[user_id]['sort_type'] = "hot"
        search_contexts[user_id]['search_step'] = 'view_hot'  # 记录当前步骤
        search_contexts[user_id]['indicator_msg'] = indicator_msg  # 保存消息对象

        # 获取所有种子（使用指定页码）
        search_results = await search_torrents("", "0", "0", page=page)

        if not search_results.get('success', False):
            return await edit_message(indicator_msg,
                                      f"<b>❌ 获取热门种子失败:</b> {search_results.get('msg', '未知错误')}")

        torrents = search_results['data'].get('list', [])
        max_page = int(search_results['data'].get('maxPage', 1))
        current_page = int(page)

        if not torrents:
            return await edit_message(indicator_msg, "<b>❌ 未找到热门种子</b>")

        # 按做种人数排序
        for torrent in torrents:
            if isinstance(torrent.get('peers'), dict):
                torrent['_seeders'] = torrent['peers'].get('upload', 0)
            else:
                torrent['_seeders'] = 0

        sorted_torrents = sorted(torrents, key=lambda x: int(x.get('_seeders', 0)) if isinstance(x.get('_seeders'),
                                                                                                 str) else x.get(
            '_seeders', 0), reverse=True)

        # 创建热门种子结果集（保留原始的maxPage）
        hot_results = {
            'success': True,
            'data': {
                'list': sorted_torrents,
                'page': current_page,
                'maxPage': max_page
            },
            'msg': '热门种子'
        }

        # 修改消息标题
        await edit_message(indicator_msg, f"<b>🔥 FSM热门种子排行榜</b> (第 {page}/{max_page} 页)")

        # 使用原有的结果处理函数展示热门种子，但替换页面前缀
        await handle_search_results(client, indicator_msg, hot_results, user_id, page_prefix=HOT_PREFIX)

    except Exception as e:
        LOGGER.error(f"获取热门种子错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"获取热门种子异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 获取热门种子失败:</b> {str(e)}")


@new_task
async def fsm_latest(client, message, page="1"):
    """显示最新上传的种子，支持分页"""
    user_id = message.from_user.id

    try:
        indicator_msg = await send_message(message, f"<b>🆕 正在获取最新上传种子 (第 {page} 页)...</b>")

        # 设置搜索上下文
        if user_id not in search_contexts:
            search_contexts[user_id] = {}
        search_contexts[user_id]['keyword'] = "最新上传种子"
        search_contexts[user_id]['selected_type'] = "0"
        search_contexts[user_id]['selected_system'] = "0"
        search_contexts[user_id]['current_page'] = int(page)
        search_contexts[user_id]['sort_type'] = "latest"
        search_contexts[user_id]['search_step'] = 'view_latest'  # 记录当前步骤
        search_contexts[user_id]['indicator_msg'] = indicator_msg  # 保存消息对象

        # 获取所有种子（使用指定页码）
        search_results = await search_torrents("", "0", "0", page=page)

        if not search_results.get('success', False):
            return await edit_message(indicator_msg,
                                      f"<b>❌ 获取最新种子失败:</b> {search_results.get('msg', '未知错误')}")

        torrents = search_results['data'].get('list', [])
        max_page = int(search_results['data'].get('maxPage', 1))
        current_page = int(page)

        if not torrents:
            return await edit_message(indicator_msg, "<b>❌ 未找到种子</b>")

        # 按创建时间排序
        for torrent in torrents:
            created_ts = torrent.get('createdTs', 0)
            torrent['_time_ts'] = created_ts

        sorted_torrents = sorted(torrents, key=lambda x: x.get('_time_ts', 0), reverse=True)

        # 创建最新种子结果集（保留原始的maxPage）
        latest_results = {
            'success': True,
            'data': {
                'list': sorted_torrents,
                'page': current_page,
                'maxPage': max_page
            },
            'msg': '最新种子'
        }

        # 修改消息标题
        await edit_message(indicator_msg, f"<b>🆕 FSM最新上传种子</b> (第 {page}/{max_page} 页)")

        # 使用原有的结果处理函数展示最新种子，但替换页面前缀
        await handle_search_results(client, indicator_msg, latest_results, user_id, page_prefix=LATEST_PREFIX)

    except Exception as e:
        LOGGER.error(f"获取最新种子错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"获取最新种子异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 获取最新种子失败:</b> {str(e)}")


@new_task
async def fsm_search_by_tag(client, message, tag, page="1"):
    """按标签搜索种子，支持分页"""
    user_id = message.from_user.id

    try:
        indicator_msg = await send_message(message, f"<b>🏷️ 正在搜索标签:</b> <i>{tag}</i> (第 {page} 页)...")

        # 设置搜索上下文
        if user_id not in search_contexts:
            search_contexts[user_id] = {}
        search_contexts[user_id]['keyword'] = f"标签:{tag}"
        search_contexts[user_id]['tag'] = tag
        search_contexts[user_id]['selected_type'] = "0"
        search_contexts[user_id]['selected_system'] = "0"
        search_contexts[user_id]['current_page'] = int(page)
        search_contexts[user_id]['search_step'] = 'search_by_tag'  # 记录当前步骤
        search_contexts[user_id]['indicator_msg'] = indicator_msg  # 保存消息对象

        # 使用标签作为关键词搜索
        search_results = await search_torrents(tag, "0", "0", page=page)

        # 使用原有的结果处理函数展示搜索结果
        await handle_search_results(client, indicator_msg, search_results, user_id)

    except Exception as e:
        LOGGER.error(f"标签搜索错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"标签搜索异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 标签搜索失败:</b> {str(e)}")


@new_task
async def fsm_callback(client, callback_query):
    """处理FSM搜索按钮的回调查询"""
    message = callback_query.message
    data = callback_query.data
    user_id = callback_query.from_user.id

    if user_id not in search_contexts:
        search_contexts[user_id] = {}

    try:
        # 处理返回上一步按钮
        if data.startswith(BACK_PREFIX):
            back_data = data[len(BACK_PREFIX):]
            step = back_data

            # 根据当前步骤执行返回操作
            if step == "type":
                # 返回到选择分类类型
                if 'keyword' not in search_contexts[user_id]:
                    return await callback_query.answer("无法返回，搜索上下文已丢失", show_alert=True)

                keyword = search_contexts[user_id].get('keyword', '')
                await callback_query.answer(f"返回到分类选择")

                # 重新获取分类并显示
                torrent_types = await get_torrent_types()
                buttons = ButtonMaker()
                for i, type_item in enumerate(torrent_types):
                    buttons.data_button(type_item['name'], f"{TYPE_PREFIX}{i}")

                buttons.data_button("全部分类", f"{TYPE_PREFIX}all")
                buttons.data_button("取消", f"{TYPE_PREFIX}cancel")

                button = buttons.build_menu(2)
                search_contexts[user_id]['search_step'] = 'select_type'
                return await edit_message(message, f"<b>🔍 请选择种子分类:</b>", button)

            elif step == "system":
                # 返回到选择优惠类型
                if 'keyword' not in search_contexts[user_id]:
                    return await callback_query.answer("无法返回，搜索上下文已丢失", show_alert=True)

                await callback_query.answer(f"返回到优惠类型选择")

                # 重新获取系统类型并显示
                systematics = await get_systematics()
                buttons = ButtonMaker()
                for i, sys_item in enumerate(systematics):
                    buttons.data_button(sys_item['name'], f"{SYSTEM_PREFIX}{i}")

                buttons.data_button("全部优惠", f"{SYSTEM_PREFIX}all")
                buttons.data_button("取消", f"{SYSTEM_PREFIX}cancel")

                button = buttons.build_menu(2)
                search_contexts[user_id]['search_step'] = 'select_system'
                return await edit_message(message, f"<b>🔍 请选择优惠类型:</b>", button)

            else:
                # 默认返回到搜索起点
                await callback_query.answer("返回到搜索起点")
                if user_id in search_contexts:
                    del search_contexts[user_id]
                return await edit_message(message, "<b>🔍 搜索已重置。请使用 /fsm 命令重新开始搜索。</b>")

        elif data.startswith(TYPE_PREFIX):
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
            buttons.data_button("返回上一步", f"{BACK_PREFIX}type")
            buttons.data_button("取消", f"{SYSTEM_PREFIX}cancel")

            button = buttons.build_menu(2)
            search_contexts[user_id]['search_step'] = 'select_system'
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
            search_contexts[user_id]['search_step'] = 'view_results'

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

        elif data.startswith(VIEW_PREFIX):
            # 处理查看详情按钮回调
            tid = data[len(VIEW_PREFIX):]
            await callback_query.answer(f"正在获取种子 {tid} 的详情...")
            try:
                # 先检查是否已有加载消息，有则删除
                if 'loading_msg' in search_contexts[user_id]:
                    try:
                        await delete_message(search_contexts[user_id]['loading_msg'])
                    except Exception as e:
                        LOGGER.error(f"删除之前的加载消息出错: {e}")
                        # 继续执行，不阻断流程

                # 发送新的加载消息并保存引用
                loading_msg = await send_message(message, f"<b>🔍 正在获取种子 <code>{tid}</code> 的详细信息...</b>")
                search_contexts[user_id]['loading_msg'] = loading_msg

                # 显示详情
                await show_torrent_details(client, message, tid)
            except Exception as e:
                LOGGER.error(f"VIEW_PREFIX处理异常: {e}")
                await send_message(message, f"<b>❌ 获取种子详情时出错:</b> {str(e)}")

        elif data.startswith(DOWNLOAD_PREFIX):
            tid = data[len(DOWNLOAD_PREFIX):]
            await callback_query.answer("正在获取下载链接...", show_alert=True)

            try:
                torrent_details = await get_torrent_details(tid)
                if not torrent_details.get('success', False):
                    return await edit_message(message,
                                              f"<b>❌ 获取种子详情失败:</b> {torrent_details.get('msg', '未知错误')}")
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
                f"<code>{download_url}</code>\n\n"
            )
            await edit_message(message, msg)

        elif data.startswith(PAGE_PREFIX):
            page = data[len(PAGE_PREFIX):]
            if page == "noop":
                await callback_query.answer("当前页码信息")
                return

            # 调试日志
            LOGGER.debug(f"页码回调数据: {page}")

            keyword = search_contexts[user_id].get('keyword', '')
            type_id = search_contexts[user_id].get('selected_type', "0")
            systematics_id = search_contexts[user_id].get('selected_system', "0")

            # 确保页码是整数并保存到用户上下文中
            try:
                page_num = int(page)
                search_contexts[user_id]['current_page'] = page_num
            except ValueError:
                LOGGER.error(f"无效的页码: {page}")
                return await callback_query.answer("无效的页码", show_alert=True)

            await callback_query.answer(f"正在加载第 {page} 页...")
            await edit_message(message, f"<b>📃 正在获取第 {page} 页的搜索结果...</b>")

            try:
                search_results = await search_torrents(keyword, type_id, systematics_id, page=page)
                # 确保使用我们自己跟踪的页码
                search_results['data']['page'] = page_num
                await handle_search_results(client, message, search_results, user_id)
            except Exception as e:
                LOGGER.error(f"翻页搜索错误: {e}")
                await edit_message(message, f"<b>❌ 获取第 {page} 页失败:</b> {str(e)}")

        # 处理浏览分类回调
        elif data.startswith(BROWSE_PREFIX):
            browse_data = data[len(BROWSE_PREFIX):]
            if browse_data == "cancel":
                await callback_query.answer("已取消浏览")
                if user_id in search_contexts:
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 浏览已取消！</b>")

            # 明确检查是否是页码请求（使用特殊前缀区分）
            if browse_data.startswith("page_"):
                # 这是页码请求
                page = browse_data.replace("page_", "")
                LOGGER.debug(f"浏览分类分页请求: 页码={page}")
                type_id = search_contexts[user_id].get('selected_type', "0")

                await callback_query.answer(f"正在加载第 {page} 页...")
                await edit_message(message, f"<b>📂 正在获取分类内容 (第 {page} 页)...</b>")

                try:
                    # 确保保存当前页码到上下文
                    search_contexts[user_id]['current_page'] = int(page)
                    search_results = await search_torrents("", type_id, "0", page=page)
                    # 确保页码正确
                    search_results['data']['page'] = int(page)
                    await handle_search_results(client, message, search_results, user_id, page_prefix=BROWSE_PREFIX)
                except Exception as e:
                    LOGGER.error(f"浏览分类分页错误: {e}")
                    await edit_message(message, f"<b>❌ 获取分类第 {page} 页失败:</b> {str(e)}")
                return

            # 不是页码请求，则是分类选择
            if browse_data == "all":
                type_id = "0"
            else:
                type_id = search_contexts[user_id]['type_mapping'].get(browse_data, "0")
            search_contexts[user_id]['selected_type'] = type_id
            search_contexts[user_id]['selected_system'] = "0"  # 默认选择全部优惠

            await callback_query.answer("正在浏览分类...")
            await edit_message(message, "<b>📂 正在获取分类内容...</b>")

            try:
                search_results = await search_torrents("", type_id, "0")
                await handle_search_results(client, message, search_results, user_id, page_prefix=BROWSE_PREFIX)
            except Exception as e:
                LOGGER.error(f"浏览分类错误: {e}")
                error_trace = traceback.format_exc()
                LOGGER.error(f"浏览分类异常详情:\n{error_trace}")
                await edit_message(message, f"<b>❌ 浏览分类失败:</b> {str(e)}")

        # 处理热门种子分页回调
        elif data.startswith(HOT_PREFIX):
            hot_data = data[len(HOT_PREFIX):]
            if hot_data == "cancel":
                await callback_query.answer("已取消查看")
                if user_id in search_contexts:
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 查看已取消！</b>")

            # 直接将数据作为页码处理
            page = hot_data
            await callback_query.answer(f"正在加载第 {page} 页...")
            await edit_message(message, f"<b>🔥 正在获取热门种子 (第 {page} 页)...</b>")

            try:
                # 调用热门种子函数获取新页码数据
                search_contexts[user_id]['current_page'] = int(page)
                await fsm_hot(client, message, page)
            except Exception as e:
                LOGGER.error(f"热门种子分页错误: {e}")
                await edit_message(message, f"<b>❌ 获取热门种子第 {page} 页失败:</b> {str(e)}")

        # 处理最新种子分页回调
        elif data.startswith(LATEST_PREFIX):
            latest_data = data[len(LATEST_PREFIX):]
            if latest_data == "cancel":
                await callback_query.answer("已取消查看")
                if user_id in search_contexts:
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 查看已取消！</b>")

            # 直接将数据作为页码处理
            page = latest_data

            await callback_query.answer(f"正在加载第 {page} 页...")
            await edit_message(message, f"<b>🆕 正在获取最新种子 (第 {page} 页)...</b>")

            try:
                # 调用最新种子函数获取新页码数据
                search_contexts[user_id]['current_page'] = int(page)
                await fsm_latest(client, message, page)
            except Exception as e:
                LOGGER.error(f"最新种子分页错误: {e}")
                await edit_message(message, f"<b>❌ 获取最新种子第 {page} 页失败:</b> {str(e)}")

        # 处理详情回调
        elif data.startswith(DETAILS_PREFIX):
            details_data = data[len(DETAILS_PREFIX):]
            if details_data == "close":
                await callback_query.answer("已关闭详情")
                # 如果有之前的loading消息，同时删除它
                if 'loading_msg' in search_contexts[user_id]:
                    try:
                        await delete_message(search_contexts[user_id]['loading_msg'])
                    except Exception as e:
                        LOGGER.error(f"删除加载消息错误: {e}")
                return await delete_message(message)

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


async def handle_search_results(client, message, search_results, user_id, page_prefix=PAGE_PREFIX):
    """
    处理并显示搜索结果，使用优化的Telegraph页面
    可以指定不同的页面前缀以支持不同的分页功能
    """
    if not search_results.get('success', False):
        return await edit_message(message, f"<b>❌ 搜索失败:</b> {search_results.get('msg', '未知错误')}")

    torrents = search_results['data'].get('list', [])
    max_page = int(search_results['data'].get('maxPage', 1))
    current_page = int(search_results['data'].get('page', 1))
    keyword = search_contexts[user_id].get('keyword', '')
    total_count = search_results['data'].get('torrentCount', len(torrents))

    if not torrents:
        # 无结果时添加返回按钮 - 根据当前上下文决定返回步骤
        buttons = ButtonMaker()
        search_step = search_contexts[user_id].get('search_step', '')

        if search_step in ['select_system', 'view_results']:
            buttons.data_button("🔙 返回上一步", f"{BACK_PREFIX}system")
        elif search_step in ['select_type', 'select_browse_type']:
            buttons.data_button("🔙 返回上一步", f"{BACK_PREFIX}type")
        else:
            buttons.data_button("🔙 返回上一步", f"{BACK_PREFIX}start")

        button = buttons.build_menu(1)

        return await edit_message(
            message,
            f"<b>🔍 未找到与</b> <i>{keyword}</i> <b>相关的结果</b>",
            button
        )

    # 保存当前页
    search_contexts[user_id]['current_page'] = current_page

    try:
        # 构建 Telegraph 页面内容
        telegraph_content = []
        telegraph_content.append(f"<h3>🔍 FSM 搜索: {keyword}</h3>")
        telegraph_content.append(f"<p>找到 <b>{total_count}</b> 个结果 | 第 {current_page}/{max_page} 页</p>")
        telegraph_content.append("<hr/><ol>")

        for torrent in torrents[:MAX_TELEGRAPH_RESULTS]:
            title = torrent.get('title', '未知')
            size = torrent.get('fileSize', '未知')
            seeds = torrent.get('peers', {}).get('upload', 0) if isinstance(torrent.get('peers'),
                                                                            dict) else torrent.get('_seeders', 0)
            leech = torrent.get('peers', {}).get('download', 0) if isinstance(torrent.get('peers'), dict) else 0
            category = torrent.get('type', {}).get('name', '未知')
            tid = torrent.get('tid')
            created_ts = torrent.get('createdTs', 0)
            created = time.strftime('%Y-%m-%d', time.localtime(created_ts)) if created_ts else '未知'
            finish = torrent.get('finish', 0)  # 完成数

            # 处理标签信息
            tags = torrent.get('tags', [])
            tags_text = ""
            if tags:
                tags_text = f"<p>🏷️ 标签: {', '.join(['#' + tag for tag in tags])}</p>"

            # 处理演员信息
            actresses = torrent.get('actress', [])
            actress_text = ""
            if actresses:
                actress_names = [actress.get('name', '') for actress in actresses if 'name' in actress]
                if actress_names:
                    actress_text = f"<p>👩 演员: {', '.join(actress_names)}</p>"

            # 处理免费状态 - 添加详细日志以辅助调试
            status = torrent.get('status', {})
            free_badge = ""
            free_detail = ""

            # 检查status字段结构
            if isinstance(status, dict):
                has_status = status.get('hasStatus', True)  # 默认假设有状态
                LOGGER.debug(f"种子 {tid} 状态: status={status}")

                if 'name' in status and status['name']:  # 有明确名称的情况
                    status_name = status.get('name', '')
                    down_coefficient = status.get('downCoefficient', 1)
                    up_coefficient = status.get('upCoefficient', 1)

                    end_at = status.get('endAt', 0)
                    end_time = ""
                    if end_at:
                        end_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(end_at))
                        free_detail = f"(到期: {end_time})"

                    if status_name:
                        free_badge = f"【{status_name}】"

                    # 补充系数信息
                    if down_coefficient == 0:
                        free_badge = "【FREE】"
                        free_detail = f"免费下载 {free_detail}"
                    elif down_coefficient < 1:
                        discount = int((1 - down_coefficient) * 100)
                        free_badge = f"【{discount}%OFF】"
                        free_detail = f"下载折扣{discount}% {free_detail}"

                    if up_coefficient > 1:
                        if free_badge:
                            free_badge += f" {up_coefficient}x上传"
                        else:
                            free_badge = f"【{up_coefficient}x上传】"
                        free_detail += f" {up_coefficient}倍上传"
                elif has_status is False:
                    # 没有特殊状态
                    free_badge = "【普通】"
                    free_detail = "无优惠"

            # 处理优惠标记
            systematic = torrent.get('systematic', {})
            if isinstance(systematic, dict) and systematic.get('name', ''):
                sys_name = systematic.get('name', '')
                if free_badge:
                    free_badge += f" {sys_name}"
                else:
                    free_badge = f"【{sys_name}】"
                free_detail += f" {sys_name}"

            # 整理显示状态信息
            status_display = ""
            if free_badge:
                status_display = f"<p>🏷️ <b>{free_badge}</b> {free_detail}</p>"

            telegraph_content.append(
                f"<li id='torrent-{tid}'>"
                f"<h4>{free_badge} {title}</h4>"
                f"<p>📁 大小: <b>{size}</b> | 👥 做种/下载: <b>{seeds}/{leech}</b> | 🔄 完成: <b>{finish}</b></p>"
                f"<p>📂 分类: {category} | 📅 上传日期: {created}</p>"
                f"{status_display}"
                f"{tags_text}"
                f"{actress_text}"
                f"<p>🆔 种子ID: <code>{tid}</code></p>"
                f"<p>📥 下载命令: <code>/fsm -do {tid}</code></p>"
                f"<p>📋 详情命令: <code>/fsm -de {tid}</code></p>"
                f"</li><hr/>"
            )
        telegraph_content.append("</ol>")

        # 创建并获取 Telegraph 页面 URL
        try:
            # 清理HTML内容，移除不支持的标签
            content_text = ''.join(telegraph_content)
            cleaned_content = clean_html_for_telegraph(content_text)

            telegraph_page = await telegraph.create_page(
                title=f"FSM搜索: {keyword}",
                content=cleaned_content
            )
            telegraph_url = telegraph_page['url']
        except Exception as e:
            LOGGER.error(f"创建Telegraph页面错误: {e}")
            telegraph_url = "#"  # 使用占位符

        # 在消息正文中嵌入 Telegraph 链接
        result_msg = (
            f"<b>🔍 FSM搜索结果</b>\n\n"
            f"<b>关键词:</b> <code>{escape_html(keyword)}</code>\n"
            f"<b>找到结果:</b> {total_count} 个\n"
            f"<b>当前页码:</b> {current_page}/{max_page}\n\n"
        )

        if telegraph_url != "#":
            result_msg += f"📋 <b>完整列表：</b><a href=\"{telegraph_url}\">在Telegraph查看</a>\n\n"
        else:
            result_msg += "<b>⚠️ 无法创建完整列表页面</b>\n\n"

        result_msg += f"👇 <i>点击下方按钮翻页或查看详情</i>\n"

        if torrents:
            result_msg += "\n<b>📊 热门结果预览:</b>\n"
            # 美化热门结果预览，增加到4个
            for i, torrent in enumerate(torrents[:PREVIEW_RESULTS], 1):
                t_title = torrent.get('title', '未知')
                t_seeds = torrent.get('peers', {}).get('upload', 0) if isinstance(torrent.get('peers'),
                                                                                  dict) else torrent.get('_seeders', 0)
                t_size = torrent.get('fileSize', '未知')
                t_tid = torrent.get('tid')
                t_finish = torrent.get('finish', 0)  # 完成数

                # 处理结果预览中的免费状态
                status = torrent.get('status', {})
                free_badge = ""
                if isinstance(status, dict):
                    if 'name' in status and status['name']:
                        status_name = status.get('name', '')
                        down_coefficient = status.get('downCoefficient', 1)
                        up_coefficient = status.get('upCoefficient', 1)

                        if status_name:
                            free_badge = f"【{status_name}】"
                        elif down_coefficient == 0:
                            free_badge = "【FREE】"
                        elif down_coefficient < 1:
                            free_badge = f"【{int((1 - down_coefficient) * 100)}%OFF】"

                        if up_coefficient > 1:
                            if free_badge:
                                free_badge += f"⬆️{up_coefficient}x"
                            else:
                                free_badge = f"【⬆️{up_coefficient}x】"
                    elif status.get('hasStatus', True) is False:
                        free_badge = "【普通】"

                # 添加系统标记
                systematic = torrent.get('systematic', {})
                if isinstance(systematic, dict) and systematic.get('name', ''):
                    sys_name = systematic.get('name', '')
                    if free_badge:
                        free_badge += f" {sys_name}"
                    else:
                        free_badge = f"【{sys_name}】"

                # 处理标签
                tags = torrent.get('tags', [])
                tags_preview = ""
                if tags and len(tags) > 0:
                    tags_str = ', '.join([f'#{tag}' for tag in tags[:2]])
                    tags_preview = f" | 🏷️ {tags_str}"
                    if len(tags) > 2:
                        tags_preview += "..."

                # 美化结果预览格式
                result_msg += (
                    f"<b>{i}. {free_badge} {escape_html(t_title)}</b>\n"
                    f"   <code>📁 {escape_html(t_size)} | 👥 {t_seeds} | 🔄 {t_finish}</code>\n"
                    f"   <code>🆔 {escape_html(t_tid)}</code>{tags_preview}\n\n"
                )

        # 调试日志
        LOGGER.debug(f"构造分页按钮: 前缀={page_prefix}, 当前页={current_page}, 最大页={max_page}")

        # 构造分页、刷新、取消按钮
        buttons = ButtonMaker()

        # 为每个热门结果添加查看详情按钮
        for i, torrent in enumerate(torrents[:PREVIEW_RESULTS], 1):
            tid = torrent.get('tid')
            buttons.data_button(f"👁 查看详情 #{i}", f"{VIEW_PREFIX}{tid}")

        if max_page > 1:
            if current_page > 1:
                # 为浏览分类添加特殊前缀，明确区分
                if page_prefix == BROWSE_PREFIX:
                    buttons.data_button("⬅️ 上一页", f"{page_prefix}page_{current_page - 1}")
                else:
                    buttons.data_button("⬅️ 上一页", f"{page_prefix}{current_page - 1}")
            if current_page < max_page:
                if page_prefix == BROWSE_PREFIX:
                    buttons.data_button("下一页 ➡️", f"{page_prefix}page_{current_page + 1}")
                else:
                    buttons.data_button("下一页 ➡️", f"{page_prefix}{current_page + 1}")

        # 添加返回上一步按钮
        search_step = search_contexts[user_id].get('search_step', '')
        if search_step in ['select_system', 'view_results']:
            buttons.data_button("🔙 返回上一步", f"{BACK_PREFIX}system")
        elif search_step in ['select_type', 'select_browse_type']:
            buttons.data_button("🔙 返回上一步", f"{BACK_PREFIX}type")

        # 刷新按钮也需要特殊处理
        if page_prefix == BROWSE_PREFIX:
            buttons.data_button("🔄 刷新", f"{page_prefix}page_{current_page}")
        else:
            buttons.data_button("🔄 刷新", f"{page_prefix}{current_page}")
        buttons.data_button("❌ 取消", f"{TYPE_PREFIX}cancel")
        button_layout = buttons.build_menu(2)

        # 最后更新消息
        await edit_message(message, result_msg, button_layout)

    except Exception as e:
        LOGGER.error(f"处理搜索结果错误: {e}\n{traceback.format_exc()}")
        err = str(e).lower()
        if "message_not_modified" in err or "tag is not allowed" in err:
            # 如果内容没变或 Telegraph 标签错误，提醒用户
            return await edit_message(message, f"<b>❌ 处理搜索结果失败:</b> {str(e)}")
        await edit_message(message, f"<b>❌ 处理搜索结果异常:</b> {str(e)}")


@new_task
async def show_torrent_details(client, message, tid):
    """显示种子详细信息"""
    try:
        # 获取用户ID
        user_id = 0
        if hasattr(message, 'from_user') and message.from_user:
            user_id = message.from_user.id
        elif hasattr(message, 'chat') and message.chat:
            user_id = message.chat.id

        # 删除之前的加载消息
        try:
            if user_id in search_contexts and 'loading_msg' in search_contexts[user_id]:
                await delete_message(search_contexts[user_id]['loading_msg'])
                LOGGER.info(f"成功删除加载消息")
                del search_contexts[user_id]['loading_msg']
        except Exception as e:
            LOGGER.error(f"删除加载消息时出错: {e}")

        torrent_details = await get_torrent_details(tid)

        if not torrent_details.get('success', False):
            return await send_message(message, f"<b>❌ 获取种子详情失败:</b> {torrent_details.get('msg', '未知错误')}")

        torrent = torrent_details.get('data', {}).get('torrent', {})

        # 提取基本信息
        title = torrent.get('title', f'未知标题')
        file_size = torrent.get('fileSize', '未知大小')
        upload = torrent.get('peers', {}).get('upload', 0)
        download = torrent.get('peers', {}).get('download', 0)
        finish = torrent.get('finish', 0)
        created_ts = torrent.get('createdTs', 0)
        created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created_ts)) if created_ts else '未知'

        # 获取类型、标签信息
        torrent_type = torrent.get('type', {}).get('name', '未知')
        tags = torrent.get('tags', [])
        tags_text = ", ".join([f"#{tag}" for tag in tags]) if tags else "无标签"

        # 处理免费状态
        status = torrent.get('status', {})
        free_text = ""
        status_end_time = ""

        # 详细记录状态信息
        LOGGER.debug(f"种子状态信息: {status}")

        if status:
            has_status = status.get('hasStatus', True)  # 默认假设有状态
            status_name = status.get('name', '')
            down_coefficient = status.get('downCoefficient', 1)
            up_coefficient = status.get('upCoefficient', 1)
            end_at = status.get('endAt', 0)

            if end_at:
                status_end_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(end_at))

            LOGGER.debug(
                f"免费状态详情: 名称={status_name}, 下载系数={down_coefficient}, 上传系数={up_coefficient}, 结束时间={status_end_time}")

            if status_name:
                free_text = f"<b>🏷️ 优惠:</b> {status_name}"
                if status_end_time:
                    free_text += f" (到期: {status_end_time})"
                free_text += "\n"
            elif down_coefficient == 0:
                free_text = f"<b>🏷️ 优惠:</b> 免费 (FREE)"
                if status_end_time:
                    free_text += f" (到期: {status_end_time})"
                free_text += "\n"
            elif down_coefficient < 1:
                free_text = f"<b>🏷️ 优惠:</b> {int((1 - down_coefficient) * 100)}%折扣"
                if status_end_time:
                    free_text += f" (到期: {status_end_time})"
                free_text += "\n"
            elif has_status is False:
                free_text = "<b>🏷️ 优惠:</b> 无优惠\n"

            if up_coefficient > 1:
                free_text += f"<b>📈 上传:</b> {up_coefficient}倍\n"

        # 创建详情消息
        detail_msg = (
            f"<b>🎬 {escape_html(title)}</b>\n\n"
            f"<b>📊 种子信息:</b>\n"
            f"• <b>大小:</b> {escape_html(file_size)}\n"
            f"• <b>做种/下载:</b> {upload}/{download}\n"
            f"• <b>完成数:</b> {finish}\n"
            f"• <b>分类:</b> {escape_html(torrent_type)}\n"
            f"• <b>发布时间:</b> {escape_html(created)}\n"
        )

        if free_text:
            detail_msg += free_text

        detail_msg += f"• <b>标签:</b> {escape_html(tags_text)}\n\n"

        # 处理演员信息（如果有）
        actresses = torrent.get('actress', [])
        if actresses:
            actress_names = [escape_html(actress.get('name', '未知')) for actress in actresses]
            detail_msg += f"<b>👩 演员:</b> {', '.join(actress_names)}\n\n"

        # 添加下载命令
        detail_msg += f"<b>📥 下载命令:</b>\n<code>/fsm -do {tid}</code>\n"

        # 创建按钮
        buttons = ButtonMaker()
        has_content = False

        # 检查是否有描述内容
        if torrent.get('content'):
            has_content = True

        try:
            if torrent.get('cover') or has_content or torrent.get('screenshots'):
                # 使用Telegraph创建详情页面
                telegraph_content = []
                telegraph_content.append(f"<h3>{escape_html(title)}</h3>")
                telegraph_content.append(f"<p>📁 大小: {escape_html(file_size)} | 👥 做种/下载: {upload}/{download}</p>")
                telegraph_content.append(
                    f"<p>📂 分类: {escape_html(torrent_type)} | 📅 上传日期: {escape_html(created)}</p>")

                if free_text:
                    # 清理HTML并替换标签
                    cleaned_free_text = clean_html_for_telegraph(free_text)
                    cleaned_free_text = cleaned_free_text.replace('<b>', '<strong>').replace('</b>', '</strong>')
                    telegraph_content.append(f"<p>{cleaned_free_text}</p>")

                # 添加标签
                if tags:
                    telegraph_content.append(f"<p>🏷️ 标签: {escape_html(tags_text)}</p>")

                # 添加演员
                if actresses:
                    actress_names = [escape_html(actress.get('name', '未知')) for actress in actresses]
                    telegraph_content.append(f"<p>👩 演员: {', '.join(actress_names)}</p>")

                # 添加封面图片
                if torrent.get('cover'):
                    telegraph_content.append(f"<img src='{torrent.get('cover')}' />")

                # 添加内容描述
                if has_content:
                    telegraph_content.append("<h4>📝 内容描述:</h4>")
                    # 清理内容描述中的HTML
                    cleaned_content = clean_html_for_telegraph(torrent.get('content', ''))
                    telegraph_content.append(cleaned_content)

                # 添加截图
                screenshots = torrent.get('screenshots', [])
                if screenshots:
                    telegraph_content.append("<h4>📸 截图:</h4>")
                    for screenshot in screenshots:
                        telegraph_content.append(f"<img src='{screenshot}' />")

                # 添加评论信息
                comments = torrent_details.get('data', {}).get('commentInfo', {}).get('list', [])
                if comments:
                    telegraph_content.append("<h4>💬 评论:</h4>")
                    for comment in comments:
                        commenter = escape_html(comment.get('userInfo', {}).get('username', '匿名'))
                        comment_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(comment.get('ts', 0)))
                        comment_content = escape_html(comment.get('comment', ''))
                        telegraph_content.append(
                            f"<p><strong>{commenter}</strong> ({comment_time}):<br>{comment_content}</p>")

                # 将内容合并为字符串并清理
                content_text = ''.join(telegraph_content)
                cleaned_content = clean_html_for_telegraph(content_text)

                try:
                    # 尝试创建Telegraph页面
                    telegraph_page = await telegraph.create_page(
                        title=f"FSM种子详情: {escape_html(title)}",
                        content=cleaned_content
                    )
                    telegraph_url = telegraph_page['url']
                    buttons.url_button("📋 查看完整详情", telegraph_url)
                except Exception as e:
                    LOGGER.error(f"创建Telegraph页面错误: {e}")
                    # 在失败时提供一个备用选项
                    detail_msg += f"\n<b>⚠️ 无法创建完整详情页面: {str(e)}</b>\n"
        except Exception as e:
            LOGGER.error(f"准备Telegraph内容时出错: {e}")
            detail_msg += f"\n<b>⚠️ 准备详情内容时出错: {str(e)}</b>\n"

        buttons.data_button("📥 获取下载链接", f"{DOWNLOAD_PREFIX}{tid}")
        buttons.data_button("❌ 关闭", f"{DETAILS_PREFIX}close")
        button = buttons.build_menu(2)

        return await send_message(message, detail_msg, button)

    except Exception as e:
        LOGGER.error(f"显示种子详情错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"显示种子详情异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 显示种子详情失败:</b> {str(e)}")


@new_task
async def fsm_command_handler(client, message):
    """处理 /fsm 命令，支持选项和搜索功能"""
    args = message.text.split()

    # 显示帮助信息
    if len(args) == 1:
        help_msg = (
            "<b>FSM 种子搜索帮助</b>\n\n"
            "<b>📌 基本命令:</b>\n"
            "• <code>/fsm 关键词</code> - 搜索种子\n"
            "• <code>/fsm -do 种子ID</code> - 下载种子\n"
            "• <code>/fsm -de 种子ID</code> - 查看种子详情\n"
            "• <code>/fsm -b</code> - 按分类浏览种子\n"
            "• <code>/fsm -h [页码]</code> - 查看热门种子\n"
            "• <code>/fsm -l [页码]</code> - 查看最新种子\n"
            "• <code>/fsm -t 标签名 [页码]</code> - 按标签搜索\n\n"
            "<b>🔍 高级用法:</b>\n"
            "• <code>/fsm 关键词 page:2</code> - 搜索并跳到指定页码\n"
            "• <code>/fsm -h 2</code> - 查看热门种子第2页\n"
            "• <code>/fsm -l 3</code> - 查看最新种子第3页\n"
            "• <code>/fsm download 种子ID</code> - 兼容旧版下载命令"
        )
        return await send_message(message, help_msg)

    # 检查第二个参数是否为选项（以-开头）
    if len(args) >= 2 and args[1].startswith('-'):
        option = args[1].lower()

        # 下载选项：-d, -do, -download
        if option in ['-d', '-do', '-download'] and len(args) >= 3:
            tid = args[2]
            try:
                loading_msg = await send_message(message, f"正在获取种子 <code>{tid}</code> 的下载链接...")
                download_url = await get_download_url(tid)
                if not download_url:
                    return await edit_message(loading_msg, "<b>❌ 无法获取下载链接</b>")

                msg = f"<code>{download_url}</code>\n\n"
                return await edit_message(loading_msg, msg)
            except Exception as e:
                LOGGER.error(f"FSM下载命令错误: {e}")
                return await send_message(message, f"<b>❌ 错误:</b> {str(e)}")

        # 详情选项：-de, -i, -info, -details
        elif option in ['-de', '-i', '-info', '-details'] and len(args) >= 3:
            tid = args[2]
            return await show_torrent_details(client, message, tid)

        # 浏览选项：-b, -browse
        elif option in ['-b', '-browse']:
            return await fsm_browse(client, message)

        # 热门选项：-h, -hot
        elif option in ['-h', '-hot']:
            page = "1"
            if len(args) >= 3:
                try:
                    page = str(int(args[2]))  # 确保是一个有效的整数
                except:
                    pass
            return await fsm_hot(client, message, page)

        # 最新选项：-l, -latest, -new
        elif option in ['-l', '-latest', '-new']:
            page = "1"
            if len(args) >= 3:
                try:
                    page = str(int(args[2]))  # 确保是一个有效的整数
                except:
                    pass
            return await fsm_latest(client, message, page)

        # 标签选项：-t, -tag
        elif option in ['-t', '-tag'] and len(args) >= 3:
            tag = args[2]
            page = "1"
            if len(args) >= 4:
                try:
                    page = str(int(args[3]))  # 确保是一个有效的整数
                except:
                    pass
            return await fsm_search_by_tag(client, message, tag, page)

        # 未知选项
        else:
            return await send_message(message,
                                      f"<b>❌ 未知选项:</b> <code>{option}</code>\n使用 <code>/fsm</code> 查看帮助。")

    # 处理旧版下载命令兼容性
    if len(args) >= 2 and args[1] == 'download':
        if len(args) < 3:
            return await send_message(message,
                                      "<b>❌ 缺少种子ID，请使用正确的格式:</b> <code>/fsm download &lt;tid&gt;</code>")

        tid = args[2]
        try:
            loading_msg = await send_message(message, f"正在获取种子 <code>{tid}</code> 的下载链接...")
            download_url = await get_download_url(tid)
            if not download_url:
                return await edit_message(loading_msg, "<b>❌ 无法获取下载链接</b>")

            msg = (
                f"<code>{download_url}</code>\n\n"
            )
            return await edit_message(loading_msg, msg)
        except Exception as e:
            LOGGER.error(f"FSM下载命令错误: {e}")
            return await send_message(message, f"<b>❌ 错误:</b> {str(e)}")

    # 处理搜索命令（默认行为）
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
            search_contexts[user_id]['current_page'] = page
            search_contexts[user_id]['search_step'] = 'direct_search'  # 记录当前步骤

            loading_msg = await send_message(message,
                                             f"<b>正在搜索:</b> <i>{escape_html(keyword)}</i> (第 {page} 页)...")
            search_contexts[user_id]['indicator_msg'] = loading_msg  # 保存消息对象
            search_results = await search_torrents(keyword, '0', '0', page=str(page))
            return await handle_search_results(client, loading_msg, search_results, user_id)

    await fsm_search(client, message)


# 模块初始化日志
LOGGER.info("FSM 搜索模块已加载")