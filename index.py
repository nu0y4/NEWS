from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/')
def index():
    # 渲染模板文件
    username = request.cookies.get('username')
    print(username)
    return render_template('index.html', username=username)


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if 'username' not in request.form or 'password' not in request.form:
            return render_template('login/index.html')
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')

        # 这里你可以添加用户名和密码验证逻辑
        if username == 'admin' and password == 'admin':  # 简单示例
            resp = make_response(redirect(url_for('index')))
            if remember:
                resp.set_cookie('username', username, max_age=30 * 24 * 60 * 60)
                resp.set_cookie('password', password, max_age=30 * 24 * 60 * 60)
            else:
                resp.set_cookie('username', username)
                resp.set_cookie('password', password)
            return resp
        else:
            resp = make_response(redirect(url_for('login')))
            # return '<script>alert(`密码错误`)</script>', 401
    return render_template('login/index.html')


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
    app.run(debug=True, host='0.0.0.0')
