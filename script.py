import requests
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
import re
import time
import aiohttp
import asyncio

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_url_validity(url):
    try:
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"URL {url} is invalid or unreachable: {e}")
        return False

async def fetch_content_async(session, url):
    try:
        logging.info(f"Fetching content from {url}")
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logging.error(f"Failed to fetch content from {url}: {e}")
        return None

def filter_content(content):
    if content is None:
        return []
    keywords = ["㊙VIP测试", "关注公众号", "天微科技", "获取测试密码", "更新时间"]
    return [line for line in content.splitlines() if 'ipv6' not in line.lower() and not any(keyword in line for keyword in keywords)]

def check_stream_validity(url):
    try:
        command = ['ffmpeg', '-i', url, '-t', '10', '-f', 'null', '-']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if result.returncode == 0:
            stderr = result.stderr.decode('utf-8')
            fps_match = re.search(r"(\d+\.?\d*) fps", stderr)
            if fps_match:
                fps = float(fps_match.group(1))
                return fps
            else:
                return 0.0
        else:
            logging.error(f"Stream {url} is not playable: {result.stderr.decode('utf-8')}")
            return 0.0
    except subprocess.TimeoutExpired:
        logging.error(f"Stream {url} check timed out")
        return 0.0
    except Exception as e:
        logging.error(f"Error checking stream {url}: {e}")
        return 0.0

async def fetch_and_filter_async(urls):
    filtered_lines = []
    
    async with aiohttp.ClientSession() as session:
        # 首先检查URL的有效性
        valid_urls = [url for url in urls if check_url_validity(url)]
        # 然后异步获取内容
        tasks = [fetch_content_async(session, url) for url in valid_urls]
        results = await asyncio.gather(*tasks)
    
    for content in results:
        filtered_lines.extend(filter_content(content))
    
    # 检查即将生成的live_ipv4.txt文件中的每个URL直播源是否能正常流畅直播
    valid_lines = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for line in filtered_lines:
            if line.startswith('http'):
                url = line.split()[0]
                futures.append(executor.submit(check_stream_validity, url))
            else:
                valid_lines.append((0.0, line))
        
        for line, future in zip(filtered_lines, futures):
            if line.startswith('http'):
                url = line.split()[0]
                fps = future.result()
                if fps > 0:
                    valid_lines.append((fps, line))
                else:
                    logging.warning(f"Skipping unplayable stream: {url}")
            else:
                valid_lines.append((0.0, line))
    
    # 按流畅度排序
    valid_lines.sort(key=lambda x: x[0], reverse=True)
    
    # 提取排序后的行
    sorted_lines = [line for fps, line in valid_lines]
    
    # 将排序后的直播源插入到原始的#genre#标签中
    genre_lines = []
    current_genre = None
    for line in sorted_lines:
        if line.startswith('#genre#'):
            current_genre = line
            genre_lines.append(line)
        elif current_genre and line.startswith('http'):
            genre_lines.append(line)
    
    with open('live_ipv4.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(genre_lines))
    logging.info("Filtered content saved to live_ipv4.txt")

if __name__ == "__main__":
    start_time = time.time()
    urls = [
        'https://raw.githubusercontent.com/leiyou-li/IPTV4/refs/heads/main/live.txt',
        'https://raw.githubusercontent.com/kimwang1978/collect-tv-txt/main/merged_output.txt',
        'http://xhztv.top/zbc.txt',
        'http://ww.weidonglong.com/dsj.txt',
        'https://tv.youdu.fan:666/live/',
        'https://live.zhoujie218.top/tv/iptv6.txt',
        'http://tipu.xjqxz.top/live1213.txt',
        'https://tv.iill.top/m3u/Live',
        'http://www.lyyytv.cn/yt/zhibo/1.txt',
        'http://live.nctv.top/x.txt',
        'http://www.lyyytv.cn/yt/zhibo/1.txt',
        'https://github.moeyy.xyz/https://raw.githubusercontent.com/Ftindy/IPTV-URL/main/huyayqk.m3u',
        'https://ghp.ci/raw.githubusercontent.com/MemoryCollection/IPTV/refs/heads/main/itvlist.m3u',
        'https://live.fanmingming.com/tv/m3u/ipv6.m3u'
    ]
    asyncio.run(fetch_and_filter_async(urls))
    end_time = time.time()
    logging.info(f"Total time taken: {end_time - start_time} seconds")