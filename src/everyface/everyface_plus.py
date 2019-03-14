# -*- coding: utf-8 -*-
# Common package
import io
import os
import json
import base64
import requests
from PIL import Image, ImageFile
from concurrent.futures import ThreadPoolExecutor, as_completed
# Personal package
import dao
import util
import config


def detect_face(mission_data):
    """
    多线程函数
    完成主线程交付的单张照片识别任务
    :param mission_data: 任务数据
    :return: 修改数据库的行数
    """
    # 开始读取图像文件
    with open(mission_data['image'], 'rb') as fp:
        # 图像需要经过jpeg图像格式校正和base64编码
        image_obj = Image.open(fp)
        image = io.BytesIO()
        image_obj.save(image, 'jpeg')
        image = str(base64.b64encode(image.getvalue()), 'utf8')

        # 构建请求信息
        http_url = config.FACE_PLUS['url']
        http_data = {
            'api_key': config.FACE_PLUS['api_key'],
            'api_secret': config.FACE_PLUS['api_secret'],
            'image_base64': image,
            'return_attributes': mission_data['return_attributes']
        }

        # 开始反复尝试识别该图像
        result = result_json = None
        result_code = 100
        while result_code != 200:
            try:
                result = requests.post(url=http_url, data=http_data)
            except Exception:
                continue
            result_code = result.status_code
            result_text = result.text
            result_json = json.loads(result_text)
            # if result_code == 403 and result_json['error_message'] == 'CONCURRENCY_LIMIT_EXCEEDED':
            #     util.print_e('并发数超过限制， API Key 的 QPS 已经达到上限')
            # if result_code == 403 and result_json['error_message'] == 'IMAGE_ERROR_UNSUPPORTED_FORMAT: image_base64':
            #     util.print_e('{}:对应的图像无法正确解析，有可能是数据破损'.format(mission_data['code']))

        # 为适应高频的数据抓取，手动关闭http连接
        result.close()

        # 提取个人面貌信息数据
        face_info = {
            'age': result_json['faces'][0]['attributes']['age']['value'],  # 年龄
            'beauty': result_json['faces'][0]['attributes']['beauty'],  # 颜值（包含男性视角和女性视角）
            'gender': result_json['faces'][0]['attributes']['gender']['value'],  # 性别
            'skinstatus': result_json['faces'][0]['attributes']['skinstatus']
        }

        # 将获取到的数据写入数据库中
        mongo_db = mongo_conn[config.MONGO_SET]
        result = mongo_db.update_one(
            {
                'code': mission_data['code']
            },
            {
                '$set': {
                    'code': mission_data['code'],
                    'face_plus': face_info
                }
            },
            upsert=True
        )
        if result.upserted_id:
            return 1
        else:
            return result.modified_count


if __name__ == '__main__':
    """
    完成利用多个百度云帐号实现图片批量分析
    """
    # 扫描本地人脸相册
    util.print_a('正在扫描本地人脸相册')
    file_list = os.listdir(config.ALBUM)
    util.print_t('相册中包含{}张照片'.format(len(file_list)))

    util.print_a('正在进行识别前的初始化')

    # 建立线程池，当连接对象过多时需要改写为线程池！！
    all_work = []  # 线程管理数组
    executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)

    # 建立MongoDB数据库连接
    mongo_conn = dao.mongo_conn()
    mongo_set = mongo_conn[config.MONGO_SET]
    exclude_list = []  # 检索需要排除的任务编号
    for face in mongo_set.find({}, {'_id': False, 'aip_face': False}):
        if 'face_plus' in face and len(face['face_plus'].keys()) != 0:
            exclude_list.append(face['code'])

    # HTTP连接请求预设
    # requests.adapters.DEFAULT_RETRIES = config.MAX_WORKERS
    # 图像处理配置预设
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    # 遍历相册，向线程池分配任务
    util.print_a('正在向线程池分配任务，需要完成{}项任务'.format(len(file_list) - len(exclude_list)))
    for index, file in enumerate(file_list):
        if file.replace('.jpg', '') in exclude_list:
            # 跳过已经执行过的图像
            continue
        file_path = config.ALBUM + file
        if os.path.isfile(file_path):
            # 准备任务数据
            data = {
                'code': file.replace('.jpg', ''),
                'image': file_path,
                'image_type': 'BASE64',
                'return_attributes': "age,beauty,gender,skinstatus",
                'mongo': mongo_conn
            }
            # 向线程池提交任务
            work = executor.submit(detect_face, data)
            all_work.append(work)
        else:
            util.print_e('相册中包含了文件夹{}'.format(file))
        util.process_bar(index + 1, len(file_list), '已完成{}条任务的提交'.format(index + 1))

    # 等待线程池中所有任务结束
    util.print_a('正在等待所有任务结束')
    rowcount = completed_work = 0
    for work in as_completed(all_work):
        # 利用as_completed的阻塞效果完成信息的提取
        rowcount += work.result()
        completed_work += 1
        util.process_bar(completed_work, len(file_list), '完成%d项，修改%d项数据' % (completed_work, rowcount))
