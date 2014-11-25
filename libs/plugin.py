#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
插件通用库
"""
import os
import json
import logging
import logging.config

from libs.utils import *

# 全局变量
devices_file_name = "devices.txt"
config_file_name = "plugin.cfg"

# 创建日志目录
mkdir("/logs")

# 加载logging.conf
logging.config.fileConfig('logging.conf')

# 日志处理
logger = logging.getLogger('plugin')

# 获取配置项
def load_config():
    if os.path.exists(config_file_name):
        config_file = open(config_file_name, "r+")
        content = config_file.read()
        config_file.close()
        try:
            config_info = convert(json.loads(content.encode("utf-8")))
            logger.debug("load config info success，%s" % content)
            return config_info
        except Exception, e:
            logger.error("load config info fail，%r" % e)
            return None
    else:
        logger.error("config file is not exist. Please check!")
        return None

# 加载设备信息
def load_devices_info_dict():
    devices_info_dict = dict()
    if os.path.exists(devices_file_name):
        devices_file = open(devices_file_name, "r+")
        content = devices_file.read()
        devices_file.close()
        try:
            devices_info_dict.update(json.loads(content))
        except Exception, e:
            logger.error("devices.txt内容格式不正确")
    else:
        devices_file = open(devices_file_name, "w+")
        devices_file.write("{}")
        devices_file.close()
    logger.debug("devices_info_dict加载结果%r" % devices_info_dict)
    return devices_info_dict


# 新增设备
def check_device(devices_info_dict, device_id, device_type, device_addr, device_port):
    # 如果设备不存在则设备字典新增设备并写文件
    if device_id not in devices_info_dict:
        # 新增设备到字典中
        devices_info_dict[device_id] = {
            "device_id": device_id,
            "device_type": device_type,
            "device_addr": device_addr,
            "device_port": device_port
        }
        logger.info("发现新设备%r" % devices_info_dict[device_id])
        #写文件
        devices_file = open(devices_file_name, "w+")
        devices_file.write(json.dumps(devices_info_dict))
        devices_file.close()