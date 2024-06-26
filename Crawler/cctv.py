import requests
import json
from pymongo import MongoClient


def fetch_and_store_cctv_news():
    # 发送 GET 请求获取数据
    url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp?cb=china'
    response = requests.get(url)

    # 设置响应内容的编码为 UTF-8
    response.encoding = 'utf-8'

    # 解析 JSONP 响应
    jsonp_data = response.text
    json_data = jsonp_data[len('china('):-1]  # 移除 JSONP 包装
    data = json.loads(json_data)

    # 提取需要的数据
    news_list = data['data']['list']
    extracted_news = [{'title': item['title'], 'link': item['url']} for item in news_list]

    # 连接到 MongoDB 并插入数据
    client = MongoClient('mongodb://localhost:27017/')
    db = client['MBGNEWs']  # 选择数据库
    collection = db.cctv  # 选择 cctv 集合

    # 清空集合中的旧数据（可选）
    collection.delete_many({})

    # 插入新数据
    collection.insert_many(extracted_news)

    # 关闭数据库连接
    client.close()

    print("Data fetched and stored successfully.")


# 执行函数
fetch_and_store_cctv_news()
