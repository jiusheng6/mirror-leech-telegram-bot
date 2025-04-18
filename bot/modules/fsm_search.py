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
BROWSE_PREFIX = "fsmb:"  # 浏览分类前缀
DETAILS_PREFIX = "fsmi:"  # 种子详情前缀

# 存储当前搜索上下文的字典，使用用户ID作为键
search_contexts = {}


@new_task
async def fsm_search(client, message) :
    """处理/fsm命令搜索种子"""
    args = message.text.split(" ", 1)
    if len(args) == 1 :
        help_msg = "请提供搜索关键词。\n示例: /fsm 关键词"
        return await send_message(message, help_msg)

    keyword = args[1]
    user_id = message.from_user.id

    try :
        LOGGER.info(f"FSM搜索: 正在获取种子分类信息，关键词: {keyword}")
        indicator_msg = await send_message(message, "<b>🔍 正在获取种子分类信息...</b>")

        torrent_types = await get_torrent_types()
        LOGGER.info(f"FSM搜索: 成功获取种子分类数量: {len(torrent_types)}")

        buttons = ButtonMaker()
        for i, type_item in enumerate(torrent_types) :
            buttons.data_button(type_item['name'], f"{TYPE_PREFIX}{i}")
            if user_id not in search_contexts :
                search_contexts[user_id] = {}
            if 'type_mapping' not in search_contexts[user_id] :
                search_contexts[user_id]['type_mapping'] = {}
            search_contexts[user_id]['type_mapping'][str(i)] = type_item['id']
            search_contexts[user_id]['keyword'] = keyword
            LOGGER.debug(f"FSM搜索: 添加分类按钮: {type_item['name']} (ID: {type_item['id']})")

        buttons.data_button("全部分类", f"{TYPE_PREFIX}all")
        buttons.data_button("取消", f"{TYPE_PREFIX}cancel")

        button = buttons.build_menu(2)
        return await edit_message(indicator_msg, "<b>🔍 请选择种子分类:</b>", button)

    except Exception as e :
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
async def fsm_browse(client, message) :
    """按分类浏览种子"""
    user_id = message.from_user.id

    try :
        LOGGER.info("FSM分类浏览: 正在获取种子分类信息")
        indicator_msg = await send_message(message, "<b>🔍 正在获取种子分类信息...</b>")

        torrent_types = await get_torrent_types()
        LOGGER.info(f"FSM分类浏览: 成功获取种子分类数量: {len(torrent_types)}")

        buttons = ButtonMaker()
        for i, type_item in enumerate(torrent_types) :
            buttons.data_button(type_item['name'], f"{BROWSE_PREFIX}{i}")
            if user_id not in search_contexts :
                search_contexts[user_id] = {}
            if 'type_mapping' not in search_contexts[user_id] :
                search_contexts[user_id]['type_mapping'] = {}
            search_contexts[user_id]['type_mapping'][str(i)] = type_item['id']
            search_contexts[user_id]['keyword'] = "分类浏览"  # 标记为分类浏览
            LOGGER.debug(f"FSM分类浏览: 添加分类按钮: {type_item['name']} (ID: {type_item['id']})")

        buttons.data_button("全部分类", f"{BROWSE_PREFIX}all")
        buttons.data_button("取消", f"{BROWSE_PREFIX}cancel")

        button = buttons.build_menu(2)
        return await edit_message(indicator_msg, "<b>📂 请选择要浏览的种子分类:</b>", button)

    except Exception as e :
        LOGGER.error(f"FSM分类浏览错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"FSM分类浏览异常详情:\n{error_trace}")
        error_msg = f"错误: {str(e)}\n\n详细请查看日志。"
        return await send_message(message, error_msg)


@new_task
async def show_torrent_details(client, message, tid) :
    """显示种子详细信息"""
    try :
        await send_message(message, f"<b>🔍 正在获取种子 <code>{tid}</code> 的详细信息...</b>")
        torrent_details = await get_torrent_details(tid)

        if not torrent_details.get('success', False) :
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

        # 创建详情消息
        detail_msg = (
            f"<b>🎬 {title}</b>\n\n"
            f"<b>📊 种子信息:</b>\n"
            f"• <b>大小:</b> {file_size}\n"
            f"• <b>做种/下载:</b> {upload}/{download}\n"
            f"• <b>完成数:</b> {finish}\n"
            f"• <b>分类:</b> {torrent_type}\n"
            f"• <b>发布时间:</b> {created}\n"
            f"• <b>标签:</b> {tags_text}\n\n"
        )

        # 处理演员信息（如果有）
        actresses = torrent.get('actress', [])
        if actresses :
            actress_names = [actress.get('name', '未知') for actress in actresses]
            detail_msg += f"<b>👩 演员:</b> {', '.join(actress_names)}\n\n"

        # 添加下载命令
        detail_msg += f"<b>📥 下载命令:</b>\n<code>/fsm -do {tid}</code>\n"

        # 创建按钮
        buttons = ButtonMaker()
        if torrent.get('cover') or torrent.get('content') :
            # 使用Telegraph创建详情页面
            telegraph_content = []
            telegraph_content.append(f"<h3>{title}</h3>")
            telegraph_content.append(f"<p>📁 大小: {file_size} | 👥 做种/下载: {upload}/{download}</p>")
            telegraph_content.append(f"<p>📂 分类: {torrent_type} | 📅 上传日期: {created}</p>")

            # 添加封面图片
            if torrent.get('cover') :
                telegraph_content.append(f"<img src='{torrent.get('cover')}' />")

            # 添加内容描述
            if torrent.get('content') :
                telegraph_content.append(torrent.get('content'))

            # 添加截图
            screenshots = torrent.get('screenshots', [])
            if screenshots :
                telegraph_content.append("<h4>📸 截图:</h4>")
                for screenshot in screenshots :
                    telegraph_content.append(f"<img src='{screenshot}' />")

            telegraph_page = await telegraph.create_page(
                title=f"FSM种子详情: {title}",
                content=''.join(telegraph_content)
            )
            telegraph_url = telegraph_page['url']
            buttons.url_button("📋 查看完整详情", telegraph_url)

        buttons.data_button("📥 获取下载链接", f"{DOWNLOAD_PREFIX}{tid}")
        buttons.data_button("❌ 关闭", f"{DETAILS_PREFIX}close")
        button = buttons.build_menu(2)

        return await send_message(message, detail_msg, button)

    except Exception as e :
        LOGGER.error(f"显示种子详情错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"显示种子详情异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 显示种子详情失败:</b> {str(e)}")


@new_task
async def fsm_hot(client, message) :
    """显示热门种子列表"""
    user_id = message.from_user.id

    try :
        indicator_msg = await send_message(message, "<b>🔥 正在获取热门种子列表...</b>")

        # 设置搜索上下文
        if user_id not in search_contexts :
            search_contexts[user_id] = {}
        search_contexts[user_id]['keyword'] = "热门种子排行"
        search_contexts[user_id]['selected_type'] = "0"
        search_contexts[user_id]['selected_system'] = "0"

        # 获取所有种子
        search_results = await search_torrents("", "0", "0", page="1")

        if not search_results.get('success', False) :
            return await edit_message(indicator_msg,
                                      f"<b>❌ 获取热门种子失败:</b> {search_results.get('msg', '未知错误')}")

        torrents = search_results['data'].get('list', [])

        if not torrents :
            return await edit_message(indicator_msg, "<b>❌ 未找到热门种子</b>")

        # 按做种人数排序
        for torrent in torrents :
            if isinstance(torrent.get('peers'), dict) :
                torrent['_seeders'] = torrent['peers'].get('upload', 0)
            else :
                torrent['_seeders'] = 0

        sorted_torrents = sorted(torrents, key=lambda x : x.get('_seeders', 0), reverse=True)

        # 创建热门种子结果集
        hot_results = {
            'success' : True,
            'data' : {
                'list' : sorted_torrents[:30],  # 仅展示前30个
                'page' : 1,
                'maxPage' : 1
            },
            'msg' : '热门种子'
        }

        # 修改消息标题
        await edit_message(indicator_msg, "<b>🔥 FSM热门种子排行榜</b>")

        # 使用原有的结果处理函数展示热门种子
        await handle_search_results(client, indicator_msg, hot_results, user_id)

    except Exception as e :
        LOGGER.error(f"获取热门种子错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"获取热门种子异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 获取热门种子失败:</b> {str(e)}")


@new_task
async def fsm_latest(client, message) :
    """显示最新上传的种子"""
    user_id = message.from_user.id

    try :
        indicator_msg = await send_message(message, "<b>🆕 正在获取最新上传种子...</b>")

        # 设置搜索上下文
        if user_id not in search_contexts :
            search_contexts[user_id] = {}
        search_contexts[user_id]['keyword'] = "最新上传种子"
        search_contexts[user_id]['selected_type'] = "0"
        search_contexts[user_id]['selected_system'] = "0"

        # 获取所有种子
        search_results = await search_torrents("", "0", "0", page="1")

        if not search_results.get('success', False) :
            return await edit_message(indicator_msg,
                                      f"<b>❌ 获取最新种子失败:</b> {search_results.get('msg', '未知错误')}")

        torrents = search_results['data'].get('list', [])

        if not torrents :
            return await edit_message(indicator_msg, "<b>❌ 未找到种子</b>")

        # 按创建时间排序
        for torrent in torrents :
            created_ts = torrent.get('createdTs', 0)
            torrent['_time_ts'] = created_ts

        sorted_torrents = sorted(torrents, key=lambda x : x.get('_time_ts', 0), reverse=True)

        # 创建最新种子结果集
        latest_results = {
            'success' : True,
            'data' : {
                'list' : sorted_torrents[:30],  # 仅展示前30个
                'page' : 1,
                'maxPage' : 1
            },
            'msg' : '最新种子'
        }

        # 修改消息标题
        await edit_message(indicator_msg, "<b>🆕 FSM最新上传种子</b>")

        # 使用原有的结果处理函数展示最新种子
        await handle_search_results(client, indicator_msg, latest_results, user_id)

    except Exception as e :
        LOGGER.error(f"获取最新种子错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"获取最新种子异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 获取最新种子失败:</b> {str(e)}")


@new_task
async def fsm_search_by_tag(client, message, tag) :
    """按标签搜索种子"""
    user_id = message.from_user.id

    try :
        indicator_msg = await send_message(message, f"<b>🏷️ 正在搜索标签:</b> <i>{tag}</i>...")

        # 设置搜索上下文
        if user_id not in search_contexts :
            search_contexts[user_id] = {}
        search_contexts[user_id]['keyword'] = f"标签:{tag}"
        search_contexts[user_id]['selected_type'] = "0"
        search_contexts[user_id]['selected_system'] = "0"

        # 使用标签作为关键词搜索
        search_results = await search_torrents(tag, "0", "0", page="1")

        # 使用原有的结果处理函数展示搜索结果
        await handle_search_results(client, indicator_msg, search_results, user_id)

    except Exception as e :
        LOGGER.error(f"标签搜索错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"标签搜索异常详情:\n{error_trace}")
        return await send_message(message, f"<b>❌ 标签搜索失败:</b> {str(e)}")


@new_task
async def fsm_callback(client, callback_query) :
    """处理FSM搜索按钮的回调查询"""
    message = callback_query.message
    data = callback_query.data
    user_id = callback_query.from_user.id

    if user_id not in search_contexts :
        search_contexts[user_id] = {}

    try :
        if data.startswith(TYPE_PREFIX) :
            type_data = data[len(TYPE_PREFIX) :]
            if type_data == "cancel" :
                await callback_query.answer("已取消搜索")
                if user_id in search_contexts :
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 搜索已取消！</b>")

            keyword = search_contexts[user_id].get('keyword', '')
            if type_data == "all" :
                type_id = "0"
            else :
                type_id = search_contexts[user_id]['type_mapping'].get(type_data, "0")
            search_contexts[user_id]['selected_type'] = type_id

            try :
                systematics = await get_systematics()
            except Exception as e :
                LOGGER.error(f"获取优惠类型失败: {e}")
                await callback_query.answer("获取优惠类型失败，请重试", show_alert=True)
                return await edit_message(message, f"<b>❌ 获取优惠类型失败:</b> {str(e)}")

            buttons = ButtonMaker()
            for i, sys_item in enumerate(systematics) :
                buttons.data_button(sys_item['name'], f"{SYSTEM_PREFIX}{i}")
                if 'system_mapping' not in search_contexts[user_id] :
                    search_contexts[user_id]['system_mapping'] = {}
                search_contexts[user_id]['system_mapping'][str(i)] = sys_item['id']

            buttons.data_button("全部优惠", f"{SYSTEM_PREFIX}all")
            buttons.data_button("取消", f"{SYSTEM_PREFIX}cancel")

            button = buttons.build_menu(2)
            await callback_query.answer("请选择优惠类型")
            await edit_message(message, "<b>🔍 请选择优惠类型:</b>", button)

        elif data.startswith(SYSTEM_PREFIX) :
            sys_data = data[len(SYSTEM_PREFIX) :]
            if sys_data == "cancel" :
                await callback_query.answer("已取消搜索")
                if user_id in search_contexts :
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 搜索已取消！</b>")

            keyword = search_contexts[user_id].get('keyword', '')
            type_id = search_contexts[user_id].get('selected_type', "0")
            if sys_data == "all" :
                systematics_id = "0"
            else :
                systematics_id = search_contexts[user_id]['system_mapping'].get(sys_data, "0")
            search_contexts[user_id]['selected_system'] = systematics_id

            await callback_query.answer("正在搜索中...")
            await edit_message(message, f"<b>🔍 正在搜索:</b> <i>{keyword}</i>...")

            try :
                search_results = await search_torrents(keyword, type_id, systematics_id)
                await handle_search_results(client, message, search_results, user_id)
            except Exception as e :
                LOGGER.error(f"搜索种子错误: {e}")
                error_trace = traceback.format_exc()
                LOGGER.error(f"搜索种子异常详情:\n{error_trace}")
                await edit_message(message, f"<b>❌ 搜索失败:</b> {str(e)}")

        elif data.startswith(DOWNLOAD_PREFIX) :
            tid = data[len(DOWNLOAD_PREFIX) :]
            await callback_query.answer("正在获取下载链接...", show_alert=True)

            try :
                torrent_details = await get_torrent_details(tid)
                if not torrent_details.get('success', False) :
                    return await edit_message(message,
                                              f"<b>❌ 获取种子详情失败:</b> {torrent_details.get('msg', '未知错误')}")
                torrent = torrent_details.get('data', {}).get('torrent', {})
                title = torrent.get('title', f'FSM_Torrent_{tid}')
            except Exception as e :
                LOGGER.error(f"获取种子详情错误: {e}")
                title = f'FSM_Torrent_{tid}'

            try :
                download_url = await get_download_url(tid)
                if not download_url :
                    return await edit_message(message, "<b>❌ 无法获取下载链接</b>")
            except Exception as e :
                LOGGER.error(f"获取下载链接错误: {e}")
                return await edit_message(message, f"<b>❌ 获取下载链接失败:</b> {str(e)}")

            msg = (
                f"<code>{download_url}</code>\n\n"
            )
            await edit_message(message, msg)

        elif data.startswith(PAGE_PREFIX) :
            page = data[len(PAGE_PREFIX) :]
            if page == "noop" :
                await callback_query.answer("当前页码信息")
                return
            keyword = search_contexts[user_id].get('keyword', '')
            type_id = search_contexts[user_id].get('selected_type', "0")
            systematics_id = search_contexts[user_id].get('selected_system', "0")

            # 确保页码是整数并保存到用户上下文中
            page_num = int(page)
            search_contexts[user_id]['current_page'] = page_num

            await callback_query.answer(f"正在加载第 {page} 页...")
            await edit_message(message, f"<b>📃 正在获取第 {page} 页的搜索结果...</b>")

            try :
                search_results = await search_torrents(keyword, type_id, systematics_id, page=page)
                # 确保使用我们自己跟踪的页码，而不是仅依赖API响应
                search_results['data']['page'] = page_num
                await handle_search_results(client, message, search_results, user_id)
            except Exception as e :
                LOGGER.error(f"翻页搜索错误: {e}")
                await edit_message(message, f"<b>❌ 获取第 {page} 页失败:</b> {str(e)}")

        # 处理浏览分类回调
        elif data.startswith(BROWSE_PREFIX) :
            browse_data = data[len(BROWSE_PREFIX) :]
            if browse_data == "cancel" :
                await callback_query.answer("已取消浏览")
                if user_id in search_contexts :
                    del search_contexts[user_id]
                return await edit_message(message, "<b>❌ 浏览已取消！</b>")

            if browse_data == "all" :
                type_id = "0"
            else :
                type_id = search_contexts[user_id]['type_mapping'].get(browse_data, "0")
            search_contexts[user_id]['selected_type'] = type_id
            search_contexts[user_id]['selected_system'] = "0"  # 默认选择全部优惠

            await callback_query.answer("正在浏览分类...")
            await edit_message(message, f"<b>📂 正在获取分类内容...</b>")

            try :
                search_results = await search_torrents("", type_id, "0")
                await handle_search_results(client, message, search_results, user_id)
            except Exception as e :
                LOGGER.error(f"浏览分类错误: {e}")
                error_trace = traceback.format_exc()
                LOGGER.error(f"浏览分类异常详情:\n{error_trace}")
                await edit_message(message, f"<b>❌ 浏览分类失败:</b> {str(e)}")

        # 处理详情回调
        elif data.startswith(DETAILS_PREFIX) :
            details_data = data[len(DETAILS_PREFIX) :]
            if details_data == "close" :
                await callback_query.answer("已关闭详情")
                return await delete_message(message)

    except Exception as e :
        LOGGER.error(f"FSM回调错误: {e}")
        error_trace = traceback.format_exc()
        LOGGER.error(f"FSM回调异常详情:\n{error_trace}")

        error_str = str(e).lower()
        if "message_not_modified" in error_str or "message was not modified" in error_str :
            await callback_query.answer("内容未变更")
            return

        await callback_query.answer(f"出错了: {str(e)[:50]}", show_alert=True)
        await edit_message(message, f"<b>❌ 错误:</b> {str(e)}")


async def handle_search_results(client, message, search_results, user_id) :
    """
    处理并显示搜索结果，使用优化的Telegraph页面
    """
    if not search_results.get('success', False) :
        return await edit_message(message, f"<b>❌ 搜索失败:</b> {search_results.get('msg', '未知错误')}")

    torrents = search_results['data'].get('list', [])
    max_page = int(search_results['data'].get('maxPage', 1))
    current_page = int(search_results['data'].get('page', 1))
    keyword = search_contexts[user_id].get('keyword', '')

    if not torrents :
        return await edit_message(
            message,
            f"<b>🔍 未找到与</b> <i>'{keyword}'</i> <b>相关的结果</b>"
        )

    # 保存当前页
    search_contexts[user_id]['current_page'] = current_page

    try :
        # 构建 Telegraph 页面内容
        telegraph_content = []
        telegraph_content.append(f"<h3>🔍 FSM 搜索: {keyword}</h3>")
        telegraph_content.append(f"<p>找到 <b>{len(torrents)}</b> 个结果 | 第 {current_page}/{max_page} 页</p>")
        telegraph_content.append("<hr/><ol>")
        for torrent in torrents[:MAX_TELEGRAPH_RESULTS] :
            title = torrent.get('title', '未知')
            size = torrent.get('fileSize', '未知')
            seeds = torrent.get('peers', {}).get('upload', 0) if isinstance(torrent.get('peers'),
                                                                            dict) else torrent.get('_seeders', 0)
            leech = torrent.get('peers', {}).get('download', 0) if isinstance(torrent.get('peers'), dict) else 0
            category = torrent.get('type', {}).get('name', '未知')
            tid = torrent.get('tid')
            created_ts = torrent.get('createdTs', 0)
            created = time.strftime('%Y-%m-%d', time.localtime(created_ts)) if created_ts else '未知'
            free_type = torrent.get('systematic', {}).get('name', '')
            free_badge = f"【{free_type}】" if free_type else ""

            telegraph_content.append(
                f"<li>"
                f"<h4>{free_badge}{title}</h4>"
                f"<p>📁 大小: <b>{size}</b></p>"
                f"<p>👥 做种/下载: <b>{seeds}/{leech}</b></p>"
                f"<p>📂 分类: {category}</p>"
                f"<p>📅 上传日期: {created}</p>"
                f"<p>🆔 种子ID: <code>{tid}</code></p>"
                f"<p>📥 下载命令:</p>"
                f"<p><code>/fsm -do {tid}</code></p>"
                f"<p>📋 详情命令:</p>"
                f"<p><code>/fsm -de {tid}</code></p>"
                f"</li><hr/>"
            )
        telegraph_content.append("</ol>")

        # 创建并获取 Telegraph 页面 URL
        telegraph_page = await telegraph.create_page(
            title=f"FSM搜索: {keyword}",
            content=''.join(telegraph_content)
        )
        telegraph_url = telegraph_page['url']

        # 在消息正文中嵌入 Telegraph 链接
        result_msg = (
            f"<b>🔍 FSM搜索结果</b>\n\n"
            f"<b>关键词:</b> <code>{keyword}</code>\n"
            f"<b>找到结果:</b> {len(torrents)} 个\n\n"
            f"📋 完整列表：<a href=\"{telegraph_url}\">在Telegraph查看</a>\n\n"
            f"👇 <i>点击下方按钮翻页或刷新</i>\n"
        )
        if torrents :
            result_msg += "\n<b>📊 热门结果预览:</b>\n"
            for i, torrent in enumerate(torrents[:3], 1) :
                t_title = torrent.get('title', '未知')
                t_seeds = torrent.get('peers', {}).get('upload', 0) if isinstance(torrent.get('peers'),
                                                                                  dict) else torrent.get('_seeders', 0)
                t_size = torrent.get('fileSize', '未知')
                t_tid = torrent.get('tid')
                result_msg += (
                    f"{i}. <b>{t_title}</b>\n"
                    f"   📁 {t_size} | 👥 {t_seeds} | 🆔 <code>{t_tid}</code>\n\n"
                )

        # 构造分页、刷新、取消按钮
        buttons = ButtonMaker()
        if max_page > 1 :
            if current_page > 1 :
                buttons.data_button("⬅️ 上一页", f"{PAGE_PREFIX}{current_page - 1}")
            if current_page < max_page :
                buttons.data_button("下一页 ➡️", f"{PAGE_PREFIX}{current_page + 1}")
        buttons.data_button("🔄 刷新", f"{PAGE_PREFIX}{current_page}")
        buttons.data_button("❌ 取消", f"{TYPE_PREFIX}cancel")
        button_layout = buttons.build_menu(2)

        # 最后更新消息
        await edit_message(message, result_msg, button_layout)

    except Exception as e :
        LOGGER.error(f"处理搜索结果错误: {e}\n{traceback.format_exc()}")
        err = str(e).lower()
        if "message_not_modified" in err or "tag is not allowed" in err :
            # 如果内容没变或 Telegraph 标签错误，提醒用户
            return await edit_message(message, f"<b>❌ 处理搜索结果失败:</b> {str(e)}")
        await edit_message(message, f"<b>❌ 处理搜索结果异常:</b> {str(e)}")


@new_task
async def fsm_command_handler(client, message) :
    """处理 /fsm 命令，支持选项和搜索功能"""
    args = message.text.split()

    # 显示帮助信息
    if len(args) == 1 :
        help_msg = (
            "<b>FSM 种子搜索帮助</b>\n\n"
            "<b>📌 基本命令:</b>\n"
            "• <code>/fsm 关键词</code> - 搜索种子\n"
            "• <code>/fsm -do 种子ID</code> - 下载种子\n"
            "• <code>/fsm -de 种子ID</code> - 查看种子详情\n"
            "• <code>/fsm -b</code> - 按分类浏览种子\n"
            "• <code>/fsm -h</code> - 查看热门种子\n"
            "• <code>/fsm -l</code> - 查看最新种子\n"
            "• <code>/fsm -t 标签名</code> - 按标签搜索\n\n"
            "<b>🔍 高级用法:</b>\n"
            "• <code>/fsm 关键词 page:2</code> - 搜索并跳到指定页码\n"
            "• <code>/fsm download 种子ID</code> - 兼容旧版下载命令"
        )
        return await send_message(message, help_msg)

    # 检查第二个参数是否为选项（以-开头）
    if len(args) >= 2 and args[1].startswith('-') :
        option = args[1].lower()

        # 下载选项：-d, -do, -download
        if option in ['-d', '-do', '-download'] and len(args) >= 3 :
            tid = args[2]
            try :
                await send_message(message, f"正在获取种子 <code>{tid}</code> 的下载链接...")
                download_url = await get_download_url(tid)
                if not download_url :
                    return await send_message(message, "无法获取下载链接")

                msg = f"<code>{download_url}</code>\n\n"
                return await send_message(message, msg)
            except Exception as e :
                LOGGER.error(f"FSM下载命令错误: {e}")
                return await send_message(message, f"错误: {str(e)}")

        # 详情选项：-de, -i, -info, -details
        elif option in ['-de', '-i', '-info', '-details'] and len(args) >= 3 :
            tid = args[2]
            return await show_torrent_details(client, message, tid)

        # 浏览选项：-b, -browse
        elif option in ['-b', '-browse'] :
            return await fsm_browse(client, message)

        # 热门选项：-h, -hot
        elif option in ['-h', '-hot'] :
            return await fsm_hot(client, message)

        # 最新选项：-l, -latest, -new
        elif option in ['-l', '-latest', '-new'] :
            return await fsm_latest(client, message)

        # 标签选项：-t, -tag
        elif option in ['-t', '-tag'] and len(args) >= 3 :
            tag = args[2]
            return await fsm_search_by_tag(client, message, tag)

        # 未知选项
        else :
            return await send_message(message,
                                      f"<b>❌ 未知选项:</b> <code>{option}</code>\n使用 <code>/fsm</code> 查看帮助。")

    # 处理旧版下载命令兼容性
    if len(args) >= 2 and args[1] == 'download' :
        if len(args) < 3 :
            return await send_message(message, "缺少种子ID，请使用正确的格式: /fsm download <tid>")

        tid = args[2]
        try :
            await send_message(message, f"正在获取种子 <code>{tid}</code> 的下载链接...")
            download_url = await get_download_url(tid)
            if not download_url :
                return await send_message(message, "无法获取下载链接")

            msg = (
                f"<code>{download_url}</code>\n\n"
            )
            return await send_message(message, msg)
        except Exception as e :
            LOGGER.error(f"FSM下载命令错误: {e}")
            return await send_message(message, f"错误: {str(e)}")

    # 处理搜索命令（默认行为）
    page = 1
    keyword = ""
    if len(args) > 1 :
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
            user_id = message.from_user.id
            if user_id not in search_contexts :
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