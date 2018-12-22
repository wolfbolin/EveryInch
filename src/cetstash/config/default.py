# -*- coding: utf-8 -*-

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
MONGO_STU_SET = 'example_set'
MONGO_CET_SET = 'example_set'

# 图片缓存文件地址
CACHE_PATH = './cache/'

# 数据下载链接
CET_DATA_URL = 'example_url'
CET_JPEG_URL = 'example_url'
CET_DATA_HEADERS = {
    'Host': 'example_host',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Origin': 'example_origin',
    'Upgrade-Insecure-Requests': '1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'EveryInch spider',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'example_referer',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}
CET_JPEG_HEADERS = {
    'Host': 'example_host',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'User-Agent': 'EveryInch spider',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Referer': 'example_referer',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}
