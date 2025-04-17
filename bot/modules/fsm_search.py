import time
from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from .. import LOGGER
from ..core.mltb_client import TgClient
from ..core.config_manager import Config
from ..helper.telegram_helper.message_utils import sendMessage, editMessage, deleteMessage
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.telegram_helper.button_build import ButtonMaker
from ..helper.ext_utils.telegraph_helper import telegraph
from ..helper.ext_utils.bot_utils import new_task, get_readable_time
from ..helper.ext_utils.fsm_utils import (
    get_torrent_types, get_systematics, search_torrents, 
    get_torrent_details, create_magnet_link
)

# 常量
RESULTS_PER_PAGE = 10  # 每页显示的结果数
MAX_TELEGRAPH_RESULTS = 25  # Telegraph页面最大显示结果数

# 回调数据前缀
TYPE_PREFIX = "fsmtype:"
SYSTEM_PREFIX = "fsmsys:"
DOWNLOAD_PREFIX = "fsmdl:"
PAGE_PREFIX = "fsmpage:"

@new_task
async def fsm_search(client, message):
    """处理/fsm命令搜索种子"""
    # 检查命令是否包含搜索关键词
    args = message.text.split(" ", 1)
    if len(args) == 1:
        help_msg = "请提供搜索关键词。\n示例: /fsm 关键词"
        return await sendMessage(help_msg, client, message)
    
    keyword = args[1]
    
    try:
        # 获取种子分类
        torrent_types = await get_torrent_types()
        
        # 创建分类按钮
        buttons = ButtonMaker()
        for type_item in torrent_types:
            buttons.data_button(
                type_item['name'], 
                f"{TYPE_PREFIX}{type_item['id']}:{keyword}"
            )
            
        # 添加"全部"按钮
        buttons.data_button("全部分类", f"{TYPE_PREFIX}0:{keyword}")
        buttons.data_button("取消", f"{TYPE_PREFIX}cancel")
        
        button = buttons.build_menu(2)
        return await sendMessage("请选择种子分类:", client, message, button)
    
    except Exception as e:
        LOGGER.error(f"FSM搜索错误: {e}")
        return await sendMessage(f"错误: {str(e)}", client, message)

@new_task
async def fsm_callback(client, callback_query):
    """处理FSM搜索按钮的回调查询"""
    message = callback_query.message
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    try:
        # 处理分类选择
        if data.startswith(TYPE_PREFIX):
            type_data = data[len(TYPE_PREFIX):].split(":", 1)
            if type_data[0] == "cancel":
                await callback_query.answer()
                return await editMessage(message, "搜索已取消！")
                
            type_id = type_data[0]
            keyword = type_data[1]
            
            # 获取优惠类型
            systematics = await get_systematics()
            
            # 创建优惠类型按钮
            buttons = ButtonMaker()
            for sys_item in systematics:
                buttons.data_button(
                    sys_item['name'], 
                    f"{SYSTEM_PREFIX}{sys_item['id']}:{type_id}:{keyword}"
                )
                
            # 添加"全部"按钮
            buttons.data_button("全部优惠", f"{SYSTEM_PREFIX}0:{type_id}:{keyword}")
            buttons.data_button("取消", f"{SYSTEM_PREFIX}cancel")
            
            button = buttons.build_menu(2)
            await callback_query.answer()
            await editMessage(message, "请选择优惠类型:", button)
            
        # 处理优惠类型选择
        elif data.startswith(SYSTEM_PREFIX):
            sys_data = data[len(SYSTEM_PREFIX):].split(":", 2)
            if sys_data[0] == "cancel":
                await callback_query.answer()
                return await editMessage(message, "搜索已取消！")
                
            systematics_id = sys_data[0]
            type_id = sys_data[1]
            keyword = sys_data[2]
            
            await callback_query.answer()
            await editMessage(message, f"<b>正在搜索:</b> <i>{keyword}</i>...")
            
            # 搜索种子
            search_results = await search_torrents(keyword, type_id, systematics_id)
            await handle_search_results(client, message, search_results, type_id, systematics_id, keyword)
            
        # 处理下载按钮
        elif data.startswith(DOWNLOAD_PREFIX):
            dl_data = data[len(DOWNLOAD_PREFIX):].split(":", 2)
            tid = dl_data[0]
            file_hash = dl_data[1]
            title = dl_data[2] if len(dl_data) > 2 else f"FSM_Torrent_{tid}"
            
            # 创建磁力链接
            magnet_link = create_magnet_link(file_hash, title)
            
            await callback_query.answer("已生成磁力链接")
            await editMessage(
                message,
                f"为以下种子生成了磁力链接: {title}\n\n"
                f"`{magnet_link}`\n\n"
                f"回复此消息并使用 /{BotCommands.QbMirrorCommand} 命令开始下载。",
                parse_mode='Markdown'
            )
            
        # 处理翻页
        elif data.startswith(PAGE_PREFIX):
            page_data = data[len(PAGE_PREFIX):].split(":", 3)
            page = page_data[0]
            type_id = page_data[1]
            systematics_id = page_data[2]
            keyword = page_data[3]
            
            await callback_query.answer()
            await editMessage(message, f"<b>正在获取第 {page} 页...</b>")
            
            # 搜索种子的新页面
            search_results = await search_torrents(keyword, type_id, systematics_id, page=page)
            await handle_search_results(client, message, search_results, type_id, systematics_id, keyword)
            
    except Exception as e:
        LOGGER.error(f"FSM回调错误: {e}")
        await callback_query.answer(f"出错了: {str(e)[:50]}", show_alert=True)
        await editMessage(message, f"错误: {str(e)}")

async def handle_search_results(client, message, search_results, type_id, systematics_id, keyword):
    """处理并显示搜索结果"""
    if not search_results.get('success', False):
        return await editMessage(message, f"搜索失败: {search_results.get('msg', '未知错误')}")
    
    torrents = search_results.get('data', {}).get('list', [])
    max_page = search_results.get('data', {}).get('maxPage', 1)
    current_page = int(search_results.get('data', {}).get('page', 1))
    
    if not torrents:
        return await editMessage(message, f"未找到与 <i>'{keyword}'</i> 相关的结果")
    
    # 如果结果较多，使用Telegraph
    if len(torrents) > RESULTS_PER_PAGE:
        telegraph_content = []
        
        # 添加搜索信息
        telegraph_content.append(f"<h4>FSM 搜索结果: {keyword}</h4>")
        telegraph_content.append(f"<p>当前第 {current_page} 页，共 {max_page} 页</p>")
        
        # 创建结果表格
        telegraph_content.append("<table>")
        telegraph_content.append("<thead><tr><th>标题</th><th>大小</th><th>做种</th><th>分类</th><th>上传日期</th><th>操作</th></tr></thead>")
        telegraph_content.append("<tbody>")
        
        # 添加每个种子作为一行
        for torrent in torrents[:MAX_TELEGRAPH_RESULTS]:  # 限制结果以防Telegraph出问题
            title = torrent.get('title', '未知')
            size = torrent.get('fileSize', '未知')
            seeds = torrent.get('peers', {}).get('upload', 0)
            category = torrent.get('type', {}).get('name', '未知')
            tid = torrent.get('tid')
            file_hash = torrent.get('fileHash', '')
            
            # 格式化时间戳
            created_ts = torrent.get('createdTs', 0)
            if created_ts:
                created_time = time.strftime('%Y-%m-%d', time.localtime(created_ts))
            else:
                created_time = '未知'
            
            # 格式化行
            row = f"<tr><td>{title}</td><td>{size}</td><td>{seeds}</td><td>{category}</td><td>{created_time}</td>"
            
            # 添加下载按钮/链接 - 为Telegraph提供命令
            row += f"<td>使用命令: <code>/fsm download {tid}</code></td></tr>"
            
            telegraph_content.append(row)
            
        telegraph_content.append("</tbody></table>")
        
        if max_page > 1:
            telegraph_content.append("<br><center><h4>页面导航</h4></center>")
            nav_text = ""
            if current_page > 1:
                nav_text += f"<a href='https://t.me/share/url?url=/fsm%20{keyword}%20page:{current_page-1}'>« 上一页</a> | "
            nav_text += f"当前第 {current_page} 页"
            if current_page < max_page:
                nav_text += f" | <a href='https://t.me/share/url?url=/fsm%20{keyword}%20page:{current_page+1}'>下一页 »</a>"
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
        
        # 如果需要，添加分页按钮
        if max_page > 1:
            if current_page > 1:
                buttons.data_button(
                    "⬅️ 上一页", 
                    f"{PAGE_PREFIX}{current_page-1}:{type_id}:{systematics_id}:{keyword}"
                )
            if current_page < max_page:
                buttons.data_button(
                    "下一页 ➡️", 
                    f"{PAGE_PREFIX}{current_page+1}:{type_id}:{systematics_id}:{keyword}"
                )
                
        button = buttons.build_menu(1)
        await editMessage(
            message,
            f"找到 {len(torrents)} 个与 <i>'{keyword}'</i> 相关的结果。在Telegraph查看详细信息:",
            button
        )
    else:
        # 结果较少，直接在Telegram中显示
        result_message = f"<b>'{keyword}'的搜索结果:</b>\n\n"
        
        buttons = ButtonMaker()
        for torrent in torrents:
            title = torrent.get('title', '未知')
            size = torrent.get('fileSize', '未知')
            seeds = torrent.get('peers', {}).get('upload', 0)
            category = torrent.get('type', {}).get('name', '未知')
            tid = torrent.get('tid')
            file_hash = torrent.get('fileHash', '')
            
            # 格式化时间戳
            created_ts = torrent.get('createdTs', 0)
            if created_ts:
                created_time = time.strftime('%Y-%m-%d', time.localtime(created_ts))
            else:
                created_time = '未知'
            
            # 添加种子详情到消息
            result_message += f"🍿 <b>{title}</b>\n"
            result_message += f"   大小: {size} | 做种: {seeds} | 分类: {category} | 日期: {created_time}\n"
            
            # 为每个种子添加下载按钮
            short_title = title[:20] + ('...' if len(title) > 20 else '')
            buttons.data_button(
                f"下载: {short_title}", 
                f"{DOWNLOAD_PREFIX}{tid}:{file_hash}:{title[:50].replace(':', ' ')}"
            )
            result_message += "\n"
        
        # 如果需要，添加分页按钮
        if max_page > 1:
            if current_page > 1:
                buttons.data_button(
                    "⬅️ 上一页", 
                    f"{PAGE_PREFIX}{current_page-1}:{type_id}:{systematics_id}:{keyword}"
                )
            if current_page < max_page:
                buttons.data_button(
                    "下一页 ➡️", 
                    f"{PAGE_PREFIX}{current_page+1}:{type_id}:{systematics_id}:{keyword}"
                )
        
        button = buttons.build_menu(1)
        await editMessage(message, result_message, button)

@new_task
async def fsm_command_handler(client, message):
    """处理 /fsm 命令，包括直接下载和搜索功能"""
    args = message.text.split()
    if len(args) >= 2 and args[1] == 'download':
        if len(args) < 3:
            return await sendMessage("缺少种子ID，请使用正确的格式: /fsm download <tid>", client, message)
            
        tid = args[2]
        try:
            # 获取种子详情
            await sendMessage(f"正在获取种子 <code>{tid}</code> 的详情...", client, message)
            torrent_details = await get_torrent_details(tid)
            
            if not torrent_details.get('success', False):
                return await sendMessage(f"获取种子详情失败: {torrent_details.get('msg', '未知错误')}", client, message)
            
            torrent = torrent_details.get('data', {}).get('torrent', {})
            title = torrent.get('title', f'FSM_Torrent_{tid}')
            file_hash = torrent.get('fileHash', '')
            
            if not file_hash:
                return await sendMessage("错误: 无法获取生成磁力链接所需的文件哈希", client, message)
            
            # 创建磁力链接
            magnet_link = create_magnet_link(file_hash, title)
            
            # 提供磁力链接给用户，让用户手动使用命令下载
            return await sendMessage(
                f"为以下种子生成了磁力链接: {title}\n\n"
                f"`{magnet_link}`\n\n"
                f"回复此消息并使用 /{BotCommands.QbMirrorCommand} 命令开始下载。",
                client, message
            )
        except Exception as e:
            LOGGER.error(f"FSM下载命令错误: {e}")
            return await sendMessage(f"错误: {str(e)}", client, message)
    
    # 处理带页码参数的搜索
    page = 1
    keyword = ""
    
    if len(args) > 1:
        # 检查是否有页码参数
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
            # 直接搜索指定页面
            await sendMessage(f"<b>正在搜索:</b> <i>{keyword}</i> (第 {page} 页)...", client, message)
            search_results = await search_torrents(keyword, '0', '0', page=str(page))
            return await handle_search_results(client, message, search_results, '0', '0', keyword)
    
    # 正常处理搜索
    await fsm_search(client, message)

# 注册命令和回调处理器
TgClient.bot.add_handler(MessageHandler(
    fsm_command_handler, 
    filters=filters.command(BotCommands.FsmCommand) & (CustomFilters.authorized | CustomFilters.sudo)
))

TgClient.bot.add_handler(CallbackQueryHandler(
    fsm_callback,
    filters=filters.regex('^fsm')
))

LOGGER.info("FSM 搜索模块已加载")