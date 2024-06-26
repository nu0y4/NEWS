import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['MBGNEWs']  # 使用数据库
collection = db.zgc2  # 使用集合

burp0_url = "https://news.zol.com.cn:443/"
burp0_headers = {
    "Sec-Ch-Ua": "\"Chromium\";v=\"121\", \"Not A(Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Priority": "u=0, i",
    "Connection": "close"
}




# 发送 HTTP 请求
response = requests.get(burp0_url, headers=burp0_headers)
response.raise_for_status()  # 检查请求是否成功

# 使用 BeautifulSoup 解析 HTML 内容
soup = BeautifulSoup(response.content, 'html.parser')

# 查找 ID 为 newsTabCon 的 div
news_tab_con = soup.find('div', id='newsTabCon')

# 提取所有 a 标签的链接
num = 0
if news_tab_con:
    a_tags = news_tab_con.find_all('a')
    for a_tag in a_tags:
        link = a_tag.get('href')
        title = a_tag.get('title')
        if link and title and (not 'div.zol.com.cn' in link) and (not 'game.zol.com.cn' in link):
            link = str(link).replace('//', 'https://')
            # 将新闻标题和链接存储到 MongoDB
            collection.insert_one({'title': title, 'link': link})
            print(title)
            print(link)
            num +=1
    print(f'收集新闻数{num}')
else:
    print("没有找到ID为newsTabCon的div")

