import requests

def check_links(file_path):
    valid_links = []
    with open(file_path, 'r') as file:
        for line in file:
            url = line.strip()
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    valid_links.append(url)
            except requests.exceptions.RequestException:
                continue
    return valid_links

if __name__ == "__main__":
    valid_links = check_links('live_ipv4.txt')
    with open('live_ipv4.txt', 'w') as file:
        file.write('\n'.join(valid_links))