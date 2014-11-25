#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    应用参数配置文件
"""

import os
import sys
import logging
import logging.config


#获取脚本文件的当前路径
def cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

# 设置系统为utf-8  勿删除
reload(sys)
sys.setdefaultencoding('utf-8')

# 程序运行路径
# 工作目录切换为python脚本所在地址，后续成为守护进程后会被修改为'/'
PROCEDURE_PATH = cur_file_dir()
os.chdir(PROCEDURE_PATH)

from libs.utils import mkdir
# 创建日志目录
mkdir("/logs")

# 加载logging.conf
logging.config.fileConfig('logging.conf')