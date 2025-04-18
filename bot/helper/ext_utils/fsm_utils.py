from asyncio import sleep
import aiohttp
import time
import asyncio
from urllib.parse import quote
from ...core.config_manager import Config
from ... import LOGGER

async def make_fsm_request(endpoint, params=None, stream=False):
    """发送FSM API请求"""
    # 尝试不同的请求头格式
    headers_formats = [
        {'APITOKEN': Config.FSM_API_TOKEN},
        {'X-APITOKEN': Config.FSM_API_TOKEN},
        {'X-API-TOKEN': Config.FSM_API_TOKEN},
        {'Authorization': f'Bearer {Config.FSM_API_TOKEN}'},
        {'Token': Config.FSM_API_TOKEN},
        {'Api-Token': Config.FSM_API_TOKEN},
        {'Apitoken': Config.FSM_API_TOKEN},
        {'apitoken': Config.FSM_API_TOKEN}
    ]
    
    url = f"{Config.FSM_API_BASE_URL.rstrip('/')}/{endpoint}"
    
    # 详细记录请求信息
    LOGGER.info(f"FSM请求详情: \n端点: {endpoint} \nURL: {url} \n参数: {params}")
    
    errors = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # 尝试所有头部格式
            for headers in headers_formats:
                header_name = list(headers.keys())[0]
                header_value = headers[header_name]
                
                LOGGER.info(f"尝试请求头: {header_name}={header_value[:5] if header_value else 'None'}...")
                
                try:
                    async with session.get(url, params=params, headers=headers, timeout=10) as response:
                        status = response.status
                        LOGGER.info(f"FSM响应状态码: {status}")
                        
                        # 记录响应头
                        resp_headers = dict(response.headers)
                        LOGGER.info(f"FSM响应头: {resp_headers}")
                        
                        # 如果是401，尝试记录响应内容以获取更多信息
                        if status == 401:
                            try:
                                error_text = await response.text()
                                LOGGER.error(f"401错误详情: {error_text}")
                                errors.append(f"Headers {header_name}='{header_value[:10]}...': {error_text}")
                            except Exception as e:
                                LOGGER.error(f"读取401响应内容出错: {e}")
                            continue  # 尝试下一个头部格式
                        
                        # 成功
                        if response.ok:
                            if stream:
                                return response
                            try:
                                json_data = await response.json()
                                LOGGER.info(f"FSM请求成功，使用头部: {header_name}")
                                return json_data
                            except Exception as e:
                                LOGGER.error(f"解析JSON响应出错: {e}")
                                text = await response.text()
                                LOGGER.info(f"原始响应内容: {text[:200]}")
                                raise Exception(f"解析响应失败: {e}")
                except Exception as e:
                    LOGGER.error(f"尝试头部 {header_name} 时出错: {e}")
                    errors.append(f"头部 {header_name} 错误: {e}")
            
            # 如果当前基础URL不是api.fsm.name，尝试备用API地址
            if not Config.FSM_API_BASE_URL.startswith("https://api.fsm.name"):
                alternate_url = "https://api.fsm.name/"
                LOGGER.info(f"尝试备用API基地址: {alternate_url}")
                
                try:
                    alt_url = f"{alternate_url.rstrip('/')}/{endpoint}"
                    async with session.get(alt_url, params=params, headers=headers_formats[0], timeout=10) as response:
                        status = response.status
                        LOGGER.info(f"备用API地址响应状态码: {status}")
                        
                        if response.ok:
                            if stream:
                                return response
                            json_data = await response.json()
                            LOGGER.info(f"备用API地址请求成功")
                            return json_data
                        else:
                            error_text = await response.text()
                            LOGGER.error(f"备用API地址请求失败: {error_text}")
                except Exception as e:
                    LOGGER.error(f"尝试备用API地址时出错: {e}")
            
            # 所有尝试都失败，汇总错误信息
            error_summary = "\n".join(errors) if errors else "无错误详情"
            LOGGER.error(f"所有API头部格式均失败! \n错误汇总:\n{error_summary}")
            
            # 尝试使用passkey作为认证（如果可用）
            if Config.FSM_PASSKEY:
                try:
                    passkey_params = dict(params) if params else {}
                    passkey_params['passkey'] = Config.FSM_PASSKEY
                    LOGGER.info(f"尝试使用passkey参数: {passkey_params}")
                    
                    async with session.get(url, params=passkey_params, timeout=10) as response:
                        status = response.status
                        LOGGER.info(f"Passkey请求响应状态码: {status}")
                        
                        if response.ok:
                            if stream:
                                return response
                            json_data = await response.json()
                            LOGGER.info("Passkey请求成功")
                            return json_data
                        else:
                            error_text = await response.text()
                            LOGGER.error(f"Passkey请求失败: {error_text}")
                except Exception as e:
                    LOGGER.error(f"Passkey请求出错: {e}")
            
            raise Exception(f"FSM API通信失败，所有认证方式均失败。请检查API令牌和基础URL。")
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

# 打印FSM配置信息，仅在模块加载时执行一次
LOGGER.info(f"当前FSM配置信息，时间戳: {time.time()}\n"
            f"API基础URL: {Config.FSM_API_BASE_URL}\n"
            f"API令牌长度: {len(Config.FSM_API_TOKEN) if Config.FSM_API_TOKEN else 0}\n"
            f"API令牌前5个字符: {Config.FSM_API_TOKEN[:5] if Config.FSM_API_TOKEN and len(Config.FSM_API_TOKEN) > 5 else '无效令牌'}\n"
            f"Passkey长度: {len(Config.FSM_PASSKEY) if Config.FSM_PASSKEY else 0}")

# 尝试可能的备用API基础URL，如果原始地址无法访问
async def test_alternative_base_urls():
    """测试备用API基础URL"""
    alternate_urls = [
        "https://fsm.name/api/",
        "https://api.fsm.name/",
        "https://www.fsm.name/api/",
        "https://fsm-api.com/api/",
        "https://fsm-api.net/api/"
    ]
    
    LOGGER.info("开始测试备用FSM API地址")
    
    for base_url in alternate_urls:
        if base_url == Config.FSM_API_BASE_URL:
            continue  # 跳过当前配置的URL
            
        LOGGER.info(f"测试备用URL: {base_url}")
        
        try:
            # 构造一个简单的测试请求
            url = f"{base_url.rstrip('/')}/ping"
            headers = {'APITOKEN': Config.FSM_API_TOKEN} if Config.FSM_API_TOKEN else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=5) as response:
                    if response.status < 500:  # 任何非服务器错误均表示服务存在
                        LOGGER.info(f"备用URL {base_url} 可访问，状态码: {response.status}")
                        text = await response.text()
                        LOGGER.info(f"响应内容: {text[:100]}")
        except Exception as e:
            LOGGER.info(f"测试备用URL {base_url} 失败: {e}")

# 当前模块已加载
LOGGER.info("FSM工具模块已加载，开始测试可能的API地址")

# 开启异步测试任务
try:
    asyncio.create_task(test_alternative_base_urls())
except Exception as e:
    LOGGER.error(f"创建备用URL测试任务失败: {e}")