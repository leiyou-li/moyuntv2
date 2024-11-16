import requests
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor

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

def fetch_content(url):
    try:
        logging.info(f"Fetching content from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content.decode('utf-8-sig')
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch content from {url}: {e}")
        return None

def filter_content(content):
    if content is None:
        return []
    keywords = ["㊙VIP测试", "关注公众号", "天微科技", "获取测试密码"]
    return [line for line in content.splitlines() if 'ipv6' not in line.lower() and not any(keyword in line for keyword in keywords)]

def check_stream_validity(url):
    try:
        # 使用ffmpeg检查流媒体是否能正常播放
        command = ['ffmpeg', '-i', url, '-t', '5', '-f', 'null', '-']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if result.returncode == 0:
            return True
        else:
            logging.error(f"Stream {url} is not playable: {result.stderr.decode('utf-8')}")
            return False
    except subprocess.TimeoutExpired:
        logging.error(f"Stream {url} check timed out")
        return False
    except Exception as e:
        logging.error(f"Error checking stream {url}: {e}")
        return False

def fetch_and_filter(urls):
    filtered_lines = []
    
    with ThreadPoolExecutor() as executor:
        # 首先检查URL的有效性
        valid_urls = [url for url in urls if check_url_validity(url)]
        # 然后获取内容
        results = list(executor.map(fetch_content, valid_urls))
    
    for content in results:
        filtered_lines.extend(filter_content(content))
    
    # 检查即将生成的live_ipv4.txt文件中的每个URL直播源是否能正常流畅直播
    valid_lines = []
    with ThreadPoolExecutor() as executor:
        futures = []
        for line in filtered_lines:
            if line.startswith('http'):
                url = line.split()[0]  # 提取URL部分
                futures.append(executor.submit(check_stream_validity, url))
            else:
                valid_lines.append(line)
        
        for line, future in zip(filtered_lines, futures):
            if line.startswith('http'):
                url = line.split()[0]
                if future.result():
                    valid_lines.append(line)
                else:
                    logging.warning(f"Skipping unplayable stream: {url}")
            else:
                valid_lines.append(line)
    
    with open('live_ipv4.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(valid_lines))
    logging.info("Filtered content saved to live_ipv4.txt")

if __name__ == "__main__":
    urls = [
        'https://raw.githubusercontent.com/leiyou-li/IPTV4/refs/heads/main/live.txt',
        'https://pt.qintutu.top/lives/zxl1.txt',
        'https://pt.qintutu.top/lives/zxl.txt',
    ]
    fetch_and_filter(urls)