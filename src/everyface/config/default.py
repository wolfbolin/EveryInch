# -*- coding: utf-8 -*-

# 配置多线程的相关信息
MAX_WORKERS = 10

# MongoDB相关的数据库配置
MONGO = {
    'host': 'example.com',
    'port': 27017,
    'username': 'username',
    'password': 'password',
    'authSource': 'database_name',
    'authMechanism': 'SCRAM-SHA-1'
}
MONGO_DB = 'example_db'
MONGO_SET = 'example_set'

# AIPFace密钥池配置
AIPFace = [{
    'appId': 'example_id',
    'apiKey': 'example_key',
    'secretKey': 'example_key'
}]

# 人脸相册缓存路径
ALBUM = 'Album_path'
