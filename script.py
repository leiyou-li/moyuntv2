import requests

def fetch_and_filter(urls):
    filtered_lines = []
    
    for url in urls:
        # 获取文件内容
        print(f"Fetching content from {url}")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch content from {url}. Status code: {response.status_code}")
            continue
        else:
            print(f"Content fetched successfully from {url}")
        
        content = response.content.decode('utf-8-sig')  # 使用utf-8-sig解码以去除BOM
        
        # 过滤掉包含 "ipv6" 的行以及特定的频道内容
        filtered_lines.extend([line for line in content.splitlines() if 'ipv6' not in line.lower() and not any(keyword in line for keyword in ["㊙VIP测试", "关注公众号", "天微科技", "获取测试密码"])])
    
    # 保存到新文件
    with open('live_ipv4.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(filtered_lines))
    print("Filtered content saved to live_ipv4.txt")

if __name__ == "__main__":
    urls = [
        'https://raw.githubusercontent.com/leiyou-li/IPTV4/refs/heads/main/live.txt',
        'https://pt.qintutu.top/lives/zxl1.txt',
        'https://pt.qintutu.top/lives/zxl.txt',
       
    ]
    fetch_and_filter(urls)