import requests

def fetch_and_filter():
    url = 'https://raw.githubusercontent.com/leiyou-li/IPTV4/refs/heads/main/live.txt'
    
    # 获取文件内容
    print(f"Fetching content from {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch content. Status code: {response.status_code}")
        return
    
    content = response.text
    print("Content fetched successfully")
    
    # 过滤掉包含 "ipv6" 的行
    filtered_lines = [line for line in content.splitlines() if 'ipv6' not in line.lower()]
    
    # 保存到新文件
    with open('live_ipv4.txt', 'w') as file:
        file.write('\n'.join(filtered_lines))
    print("Filtered content saved to live_ipv4.txt")

if __name__ == "__main__":
    fetch_and_filter()