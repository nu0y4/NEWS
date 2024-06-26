from flask import Flask, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def index():
    # 渲染模板文件
    return render_template('index.html')
@app.route('/get_zgc_news')
def get_zgc_news():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['MBGNEWs']  # 选择数据库

    # 从 zgc 集合中随机提取 10 条记录
    zgc_collection = db.zgc
    zgc_news_items = list(zgc_collection.aggregate([{"$sample": {"size": 10}}]))

    # 从 cctv 集合中随机提取 10 条记录
    cctv_collection = db.cctv
    cctv_news_items = list(cctv_collection.aggregate([{"$sample": {"size": 10}}]))

    # 构造响应数据
    news_groups = {
        "中关村": [{"title": item['title'], "link": item['link']} for item in zgc_news_items],
        "央视新闻": [{"title": item['title'], "link": item['link']} for item in cctv_news_items]
    }

    response = news_groups

    # 关闭数据库连接
    client.close()

    # 返回 JSON 数据
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
