from asyncio import sleep
import aiohttp
import time
from urllib.parse import quote
from ...core.config_manager import Config
from ... import LOGGER

async def get_download_url(tid):
    """获取种子下载链接"""
    if not Config.FSM_PASSKEY:
        raise Exception("FSM_PASSKEY未设置，无法获取下载链接")
        
    # 构建下载链接，添加source参数以符合API要求
    params = {
        'tid': tid,
        'passkey': Config.FSM_PASSKEY,
        'source': 'direct'
    }
    
    # 构建查询字符串
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    download_url = f"{Config.FSM_DOWNLOAD_URL_BASE}?{query_string}"
    return download_url

async def make_fsm_request(endpoint, params=None, stream=False):
    """发送FSM API请求"""
    headers = {'APITOKEN': Config.FSM_API_TOKEN}
    url = f"{Config.FSM_API_BASE_URL.rstrip('/')}/{endpoint}"
    
    LOGGER.info(f"FSM请求: 端点={endpoint}, URL={url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if not response.ok:
                    error_text = await response.text()
                    LOGGER.error(f"FSM请求失败: 状态码={response.status}, 错误={error_text}")
                    raise Exception(f"FSM请求失败: {response.status}, message='{error_text}', url='{url}'")
                if stream:
                    return response
                return await response.json()
    except aiohttp.ClientError as e:
        LOGGER.error(f"FSM请求失败: {e}")
        raise Exception(f"FSM请求失败: {e}")

async def get_torrent_types():
    """获取种子分类信息"""
    response = await make_fsm_request('Torrents/listType')
    return response.get('data', [])

async def get_systematics():
    """获取种子优惠列表"""
    response = await make_fsm_request('Torrents/listSystematics')
    return response.get('data', [])

async def search_torrents(keyword, type_id='0', systematics='0', tags='[]', page='1'):
    """搜索种子"""
    params = {
        'type': type_id,
        'systematics': systematics,
        'tags': tags,
        'keyword': keyword,
        'page': page
    }
    
    response = await make_fsm_request('Torrents/listTorrents', params)
    
    # 替换图片URL
    if 'data' in response and 'list' in response['data']:
        for item in response['data']['list']:
            if 'cover' in item:
                item['cover'] = item['cover'].replace(
                    'https://img.fsm.name',
                    'https://qinzhi-pt-fsm-images.qinzhiai.com'
                )
    
    return response

async def get_torrent_details(tid):
    """获取种子详情"""
    params = {'tid': tid}
    response = await make_fsm_request('Torrents/details', params)
    
    # 替换图片URL
    if response.get('success') and 'data' in response:
        torrent_data = response['data'].get('torrent', {})
        
        # 替换cover URL
        if 'cover' in torrent_data:
            torrent_data['cover'] = torrent_data['cover'].replace(
                'https://img.fsm.name',
                'https://qinzhi-pt-fsm-images.qinzhiai.com'
            )
        
        # 替换content中的图片URL
        if 'content' in torrent_data:
            torrent_data['content'] = torrent_data['content'].replace(
                'https://img.fsm.name',
                'https://qinzhi-pt-fsm-images.qinzhiai.com'
            )
        
        # 替换actress头像URL
        if 'actress' in torrent_data:
            for actress in torrent_data['actress']:
                if 'avatar' in actress:
                    actress['avatar'] = actress['avatar'].replace(
                        'https://img.fsm.name',
                        'https://qinzhi-pt-fsm-images.qinzhiai.com'
                    )
        
        # 替换screenshots中的URL
        if 'screenshots' in torrent_data:
            torrent_data['screenshots'] = [
                url.replace('https://img.fsm.name', 'https://qinzhi-pt-fsm-images.qinzhiai.com')
                for url in torrent_data['screenshots']
            ]
    
    return response

def create_magnet_link(file_hash, title):
    """创建磁力链接"""
    encoded_title = quote(title)
    magnet_link = f"magnet:?xt=urn:btih:{file_hash}&dn={encoded_title}"
    return magnet_link