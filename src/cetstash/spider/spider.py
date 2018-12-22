# -*- coding: utf-8 -*-
# Common package
import re
import requests
from bs4 import BeautifulSoup
# Personal package
import util
import config


def download(student_data):
    """
    多线程处理函数
    控制每个学生信息的下载过程
    :return: 修改的数据行数
    """
    # 获取MongoDB数据库连接
    mongo_conn = student_data['mongo_conn']

    # 尝试获取CET4信息
    cet4, cet4_data = download_cet(student_data['code'], student_data['name'], '四级')
    if cet4 and student_data['cache'] is False:
        cache_status = download_img(cet4_data['image_url'], student_data['code'])

    # 尝试获取CET6信息
    cet6, cet6_data = download_cet(student_data['code'], student_data['name'], '六级')
    if cet6 and student_data['cache'] is False:
        cache_status = download_img(cet6_data['image_url'], student_data['code'])

    # 更新学生CET信息
    mongo_db = mongo_conn[config.MONGO_CET_SET]
    cet_data = mongo_db.find_one({'code': student_data['code']})
    if cet_data is None:
        cet_data = {
            'code': student_data['code'],
            'name': student_data['name'],
            'cet4': cet4_data,
            'cet6': cet6_data,
        }
    elif cet4:
        cet_data['cet4'] = cet4_data
    elif cet6:
        cet_data['cet6'] = cet6_data
    # 根据修改后的数据更新数据库
    result = mongo_db.update_one(
        {
            'code': cet_data['code']
        },
        {
            '$set': cet_data
        },
        upsert=True
    )
    return result.modified_count


def download_cet(code, name, level):
    """
    单线程处理函数
    完成学生CET信息的读取，供download调用
    :param code: 学生学号
    :param name: 学生姓名
    :param level: 考试级别
    :return: 学生的CET数据
    """
    try:
        http_data = {
            'username': code.encode('gbk'),
            'password': name.encode('gbk'),
            'bmlb': level.encode('gbk'),
            'Submit': '确 认'.encode('gbk')
        }
    except UnicodeEncodeError:
        util.print_e('部分信息无法被编码：{};{};{}'.format(code, name, level))
        return False, {}

    # 多次发起下载尝试
    http_result = None
    for i in range(5):
        http_result = requests.post(config.CET_DATA_URL, headers=config.CET_DATA_HEADERS, data=http_data)
        if http_result.status_code == 200:
            break
    if http_result.status_code != 200:
        util.print_e('部分信息无法被下载：{};{};{}'.format(code, name, level))
        return False, {}
    elif http_result.headers['Content-Length'] == '61':
        # 获取不到数据，正常情况
        return False, {}
    else:
        # 下载数据成功，开始解析网页数据
        http_result.encoding = 'gb2312'  # 设置解码方式
        soup = BeautifulSoup(http_result.text, "lxml")
        result = {
            'level': level,
            'ticket': soup.find(id='zkz')['value'],  # 获取准考证号
            'image_url': soup.find('img')['src'],  # 获取照片地址
            'time': soup.find(id='yx1')['value']  # 获取考试时间
        }
        # 解析时间数据
        time_group = re.match('^([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日.*$', result['time'])
        result['time'] = '{}-{}-{}'.format(time_group.group(1), time_group.group(2), time_group.group(3))
        return True, result


def download_img(url, code):
    """
    单线程处理函数
    获取学生的照片信息并储存在本地缓存，供download调用
    :param url: 下载链接后缀
    :param code: 学生学号
    :return: 下载结果
    """
    http_result = requests.get(config.CET_JPEG_URL + url, headers=config.CET_JPEG_HEADERS)
    if http_result.status_code != 200:
        util.print_e('学生照片无法被下载：{}'.format(code))
        return False
    file_path = config.CACHE_PATH + '{}.jpg'.format(code)
    with open(file_path, 'wb') as img_file:
        img_file.write(http_result.content)
    return True
