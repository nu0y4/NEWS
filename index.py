import os

from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for, flash
from pymongo import MongoClient
import hashlib

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'f1se56f1g5r'
# MongoDB连接设置
client = MongoClient('mongodb://localhost:27017/')
db = client['MBGNEWs']
user_collection = db['user']


def md5_hash(password):
    return hashlib.md5(password.encode()).hexdigest()

# 配置上传路径
UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 上传头像的路由
@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    username = request.cookies.get('username')

    if not username:
        flash('请先登录')
        return redirect(url_for('login'))

    if 'avatar' not in request.files:
        flash('没有选择文件')
        return redirect(request.url)

    file = request.files['avatar']

    if file.filename == '':
        flash('未选择文件')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # 获取文件的实际扩展名
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        # 使用用户账号的MD5值作为文件名，保留扩展名
        hashed_filename = f"{md5_hash(username)}.{file_extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], hashed_filename)
        file.save(filepath)
        flash('头像上传成功！')
        return redirect(url_for('profile'))
    else:
        flash('上传失败，不支持的文件类型')
        return redirect(url_for('profile'))


@app.route('/')
def index():
    # 渲染模板文件
    username = request.cookies.get('username')
    if username:
        # print(username)
        return render_template('index.html', username=username[0].upper())
    else:
        return render_template('index.html', username='')


@app.route('/setting')
def setting():
    username = request.cookies.get('username')

    if username:
        # 生成MD5哈希的文件名，但不限定扩展名
        hashed_filename_base = md5_hash(username)
        avatar_path = None

        # 查找文件是否存在，并自动匹配文件的扩展名
        for ext in ALLOWED_EXTENSIONS:
            potential_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{hashed_filename_base}.{ext}")
            if os.path.exists(potential_avatar_path):
                avatar_path = potential_avatar_path
                break

        # 如果头像文件存在，使用用户头像；否则，使用null.png
        if avatar_path:
            avatar_url = url_for('static', filename=f'uploads/avatars/{os.path.basename(avatar_path)}')
        else:
            avatar_url = url_for('static', filename='uploads/avatars/null.png')

        # 查询 user_collection 中的 email
        user_data = user_collection.find_one({"username": username})
        if user_data and 'email' in user_data:
            email = user_data['email']
        else:
            email = ""

        return render_template('setting/index.html', username=username, avatar_url=avatar_url, email=email)
    else:
        # 未登录用户，显示默认头像
        avatar_url = url_for('static', filename='uploads/avatars/null.png')
        return render_template('setting/index.html', username='', avatar_url=avatar_url, email="空")


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
        user = user_collection.find_one({'username': username})

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
            user_collection.insert_one({'username': username, 'password': hashed_password})
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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = request.cookies.get('username')

    if not username:
        flash('请先登录')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 获取表单数据
        # new_username = request.form['username']
        new_password = request.form['password']

        # 对密码进行MD5加密
        password_hash = md5_hash(new_password)

        # 更新用户信息到数据库
        user_collection.update_one(
            {"username": username},
            {
                "$set": {
                    # "username": new_username,
                    "password": password_hash
                }
            }
        )

        # 更新cookie中的用户名
        # resp = make_response(redirect(url_for('profile')))
        # resp.set_cookie('username', new_username)
        # flash("个人信息已更新")
        # return resp

    # 获取用户信息
    user_data = user_collection.find_one({"username": username})

    if user_data:
        password = user_data.get('password', '')
    else:
        flash("用户信息未找到")
        return redirect(url_for('profile'))
    setting = url_for('setting')

    # 渲染模板并传递用户数据
    return redirect(setting)


@app.route('/email', methods=['GET', 'POST'])
def email():
    username = request.cookies.get('username')

    if not username:
        flash('请先登录')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 获取表单数据
        # new_username = request.form['username']
        new_email = request.form['email']

        # 对密码进行MD5加密
        # password_hash = md5_hash(new_password)

        # 更新用户信息到数据库
        user_collection.update_one(
            {"username": username},
            {
                "$set": {
                    # "username": new_username,
                    "email": new_email
                }
            }
        )

        # 更新cookie中的用户名
        # resp = make_response(redirect(url_for('profile')))
        # resp.set_cookie('username', new_username)
        # flash("个人信息已更新")
        # return resp

    # 获取用户信息
    user_data = user_collection.find_one({"username": username})

    if user_data:
        email = user_data.get('email', '')
    else:
        flash("用户信息未找到")
        return redirect(url_for('setting'))
    setting = url_for('setting')

    # 渲染模板并传递用户数据
    return redirect(setting)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
