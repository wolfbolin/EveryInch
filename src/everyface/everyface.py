# -*- coding: utf-8 -*-
# Common package
import os
import base64
from math import ceil
from aip import AipFace
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
        image = fp.read()
        image = str(base64.b64encode(image), 'utf8')  # 图像需要经过base64编码

        # 开始反复尝试识别该图像
        result = {'error_code': 18}
        while result['error_code'] != 0:
            try:
                result = mission_data['aip'].detect(image=image,
                                                    image_type=mission_data['image_type'],
                                                    options=mission_data['options'])
            except Exception:
                continue
        face_info = {
            'code': mission_data['code'],
            'age': result['result']['face_list'][0]['age'],  # 年龄
            'beauty': result['result']['face_list'][0]['beauty'],  # 颜值
            'gender': result['result']['face_list'][0]['gender']['type'],  # 性别
            'gender_probability': result['result']['face_list'][0]['gender']['probability']  # 性别置信度
        }

        # 将获取到的数据写入数据库中
        mongo_db = mongo_conn[config.MONGO_SET]
        result = mongo_db.update_one(
            {
                'code': face_info['code']
            },
            {
                '$set': face_info
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

    # 批量创建AIP连接对象
    util.print_a('正在批量创建AIP连接对象')
    aip_list = []
    for aip_key in config.AIPFace:
        aip_list.append(AipFace(**aip_key))
    if len(aip_list) == 0:
        util.print_w('没有AIP帐号怎么识别鸭')
        exit()

    util.print_a('正在进行识别前的初始化')
    # 建立线程池，当连接对象过多时需要改写为线程池！！
    all_work = []  # 线程管理数组
    executor = ThreadPoolExecutor(max_workers=len(aip_list))

    # 建立MongoDB数据库连接
    mongo_conn = dao.mongo_conn()
    mongo_set = mongo_conn[config.MONGO_SET]
    exclude_list = []  # 检索需要排除的任务编号
    for face in mongo_set.find({}, {'code': True}):
        exclude_list.append(face['code'])

    # 遍历相册，向AIP对象分配任务
    util.print_a('正在向AIP对象分配任务')
    it = 0  # AIP对象任务分配指针，指向下一个可用的AIP对象
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
                'options': {
                    'max_face_num': 1,
                    'face_field': "age,beauty,gender",
                },
                'aip': aip_list[it],
                'mongo': mongo_conn
            }
            it += 1
            it %= len(aip_list)
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
        util.process_bar(completed_work, len(file_list), '完成%d项，修改%d行' % (completed_work, rowcount))
