# EveryInch

![https://github.com/wolfbolin/EveryInch](https://img.shields.io/badge/build-passing-brightgreen.svg)![https://github.com/wolfbolin/EveryInch](https://img.shields.io/badge/license-GPL-orange.svg)![https://github.com/wolfbolin/EveryInch](https://img.shields.io/badge/status-stable-green.svg)

## 模块说明

### cetstash

该程序可以完成最近一次CET考试的信息抓取，并将有价值的信息缓存在MongoDB中。

使用者仅需要将default配置文件修改为config.py并填入适当的配置信息即可运行程序。

## everyface

该程序可以完成将图片缓存相册内所有的照片进行人脸分析，获取人脸的年龄、颜值、性别。

该程序的数据在一定程度上与仓库中其他程序有联动，数据的格式和存储形式有待完善。

程序使用了百度人脸识别API，并支持多个APPID的批量处理，当APPID过多时，需要改写为多线程。

使用者仅需要将default配置文件修改为config.py并填入适当的配置信息即可运行程序。

## 免责声明

本程序不得用于**商业用途**，仅供**个人研究**之用，请下载后在4小时内删除。
请勿用于商业及非法用途，如由此引起的相关法律法规责任，由使用者自行承担。