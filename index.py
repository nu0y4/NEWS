from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for
from pymongo import MongoClient
import hashlib
app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['MBGNEWs']
users_collection = db['user']

def md5_hash(password):
    return hashlib.md5(password.encode()).hexdigest()

@app.route('/')
def index():
    # 渲染模板文件
    username = request.cookies.get('username')
    # print(username)
    return render_template('index.html', username=username[0].upper())

@app.route('/setting')
def setting():
    return '<script>alert(`还没做好,等过几天吧,这是个人信息的页面`);window.location.href="/";</script>'

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

        hashed_password = md5_hash(password)

        # 查找用户
        user = users_collection.find_one({'username': username})

        if user:
            # 用户存在，检查密码是否匹配
            if user['password'] == hashed_password:
                resp = make_response(redirect(url_for('index')))
                if remember:
                    resp.set_cookie('username', username, max_age=30 * 24 * 60 * 60)
                    resp.set_cookie('password', hashed_password, max_age=30 * 24 * 60 * 60)
                else:
                    resp.set_cookie('username', username)
                    resp.set_cookie('password', hashed_password)
                return resp
            else:
                return '<script>alert("密码错误"); window.location.href="/login";</script>', 401
        else:
            # 用户不存在，创建新用户
            users_collection.insert_one({'username': username, 'password': hashed_password})
            resp = make_response(redirect(url_for('index')))
            if remember:
                resp.set_cookie('username', username, max_age=30 * 24 * 60 * 60)
                resp.set_cookie('password', hashed_password, max_age=30 * 24 * 60 * 60)
            else:
                resp.set_cookie('username', username)
                resp.set_cookie('password', hashed_password)
            return resp

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
