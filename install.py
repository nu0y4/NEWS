from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def printc(txt):
    print(f'[+]{txt}')
def check_and_create_mongodb():
    try:
        # 尝试连接到 MongoDB 服务
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # 尝试获取服务器信息来检查连接
        client.server_info()
    except ServerSelectionTimeoutError:
        printc("MongoDB 服务不存在，请先安装MongoDB！")
        return

    # 检查是否存在 MBGNEWs 数据库
    db_name = 'MBGNEWs'
    db_list = client.list_database_names()
    if db_name in db_list:
        printc("存在MBGNEWs数据库")
    else:
        db = client[db_name]
        printc(f"已创建数据库: {db_name}")

    # 获取数据库对象
    db = client[db_name]

    # 检查是否存在 zgc 集合
    if 'zgc' in db.list_collection_names():
        printc("集合 'zgc' 已存在")
    else:
        db.create_collection('zgc')
        printc("已创建集合 'zgc'")

    # 检查是否存在 cctv 集合
    if 'cctv' in db.list_collection_names():
        printc("集合 'cctv' 已存在")
    else:
        db.create_collection('cctv')
        printc("已创建集合 'cctv'")

    if 'user' in db.list_collection_names():
        printc("集合 'user' 已存在")
    else:
        db.create_collection('user')
        printc("已创建集合 'user'")

    # 关闭数据库连接
    client.close()

# 执行函数
check_and_create_mongodb()
