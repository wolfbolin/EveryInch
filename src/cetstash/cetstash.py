# -*- coding: utf-8 -*-
# Common package
import os
# Personal package
import dao
import util
import config
import spider

if __name__ == '__main__':
    """
    main()
    """
    # 先连接MongoDB获取学生列表
    util.print_a('正在读取数据库中的学生列表')
    mongo_conn = dao.mongo_conn()
    student_set = mongo_conn[config.MONGO_STU_SET]
    student_list = []
    for student in student_set.find(projection={'code': True, 'name': True}):
        student_list.append(student)
    util.print_d('已完成学生列表的读取')

    # 检索已经下载过的照片信息
    util.print_a('开始检索已经下载过的照片信息')
    for index, student in enumerate(student_list):
        file_path = config.CACHE_PATH + '{}.jpg'.format(student['code'])
        if os.path.exists(file_path):
            student['cache'] = True
        else:
            student['cache'] = False
        util.process_bar(index + 1, len(student_list), '已检索{}条数据'.format(index + 1))
    util.print_d('已完成学生照片的检索')

    # 利用多线程完成数据的检索与下载
    util.print_a('开始学生数据的检索与下载')
    rowcount = util.multiprocess(task=spider.download, main_data=student_list,
                                 max_thread=1, multithread=util.mongo_multithread)
    util.print_d('完成{}条数据的更新'.format(rowcount))
