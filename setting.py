#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    应用参数配置文件
"""

import os
import sys
import logging
import logging.config

from libs.utils import *


# 设置系统为utf-8  勿删除
reload(sys)
sys.setdefaultencoding('utf-8')

# 程序运行路径
# 工作目录切换为python脚本所在地址，后续成为守护进程后会被修改为'/'
procedure_path = cur_file_dir()
os.chdir(procedure_path)
# 通过工作目录获取当前插件名称
plugin_name = procedure_path.split("/")[-1]

# 创建日志目录
mkdir("logs")

# 加载logging.conf
logging.config.fileConfig('logging.conf')
