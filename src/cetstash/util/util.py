# -*- coding: utf-8 -*-
# Common package
import os
import sys
import time

"""
被其他运行包所引用的工具包
提供了大部分常用功能
"""


# 自定义异常
class ErrorSignal(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def print_e(message):
    print('\033[0;31;0m[ERROR] {}\033[0m'.format(str(message)))


def print_d(message):
    print('\033[0;32;0m[DONE] {}\033[0m'.format(str(message)))


def print_w(message):
    print('\033[0;33;0m[WARNING] {}\033[0m'.format(str(message)))


def print_a(message):
    print('\033[0;34;0m[ACTION] {}\033[0m'.format(str(message)))


def print_t(message):
    print('\033[0;36;0m[TIPS] {}\033[0m'.format(str(message)))


def print_i(message):
    print('\033[0;37;0m[INFO] {}\033[0m'.format(str(message)))


def process_bar(now, total, attach=''):
    # 在窗口底部动态显示进度条
    rate = now / total
    rate_num = int(rate * 100)
    bar_length = int(rate_num / 2)
    blank = '                                                    '
    if rate_num == 100:
        bar = 'Pid:%5d:%s%s' % (os.getpid(), attach, blank)
        bar = '\r' + bar[0:30]
        bar += '%s>%d%%\n' % ('=' * bar_length, rate_num)
    else:
        bar = 'Pid:%5d:%s%s' % (os.getpid(), attach, blank)
        bar = '\r' + bar[0:30]
        bar += '%s>%d%%' % ('=' * bar_length, rate_num)
    sys.stdout.write(bar)
    sys.stdout.flush()


def print_data_size(data, remarks=''):
    # 展示变量当前内存消耗状态
    print_i('{}消耗内存{}kb'.format(remarks, sys.getsizeof(data) / 1024))


def print_http_status(result, remarks=''):
    # 展示网络请求地址与状态，另有附加信息可选
    if result.status_code == 200 or result.status_code == 302:
        print_i('%s HTTP状态%d url=%s' % (remarks, result.status_code, result.url))
    else:
        print_e('%s HTTP状态%d url=%s' % (remarks, result.status_code, result.url))
        raise ErrorSignal("网络连接异常或失败，请重试")
