#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
插件通用库
"""
import os
import json
import logging

from libs.utils import *
from libs.base_channel import BaseChannel
from libs.base_protocol import BaseProtocol


# 日志处理
logger = logging.getLogger('plugin')


# 获取配置项
def load_config(config_file_name):
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


# 加载channel类
def load_channel(channel_type):
    channel_type = channel_type.lower()
    # 扫描通道库
    # 通过扫描目录来获取支持的协议库
    cur_dir = cur_file_dir()
    if cur_dir is not None:
        channel_lib_path = cur_dir + "/channels"
        file_list = os.listdir(channel_lib_path)
        for file_name in file_list:
            file_path = os.path.join(channel_lib_path, file_name)
            if os.path.isfile(file_path) and channel_type + ".py" == file_name:
                channel_name, ext = os.path.splitext(file_name)
                # 确保协议名称为小写
                channel_name = channel_name.lower()
                # 加载库
                module_name = "channels." + channel_name
                try:
                    module = __import__(module_name)
                    channel_module_attrs = getattr(module, channel_name)
                    class_object = get_subclass(channel_module_attrs, BaseChannel)
                    return class_object
                except Exception, e:
                    logger.error("Load channel(%s) fail, error info:%r" % (module_name, e))
    return None


# 加载protocol类
def load_protocol(protocol_type):
    protocol_type = protocol_type.lower()
    # 通过扫描目录来获取支持的协议库
    cur_dir = cur_file_dir()
    if cur_dir is not None:
        protocol_lib_path = cur_dir + "/protocols"
        file_list = os.listdir(protocol_lib_path)
        for file_name in file_list:
            file_path = os.path.join(protocol_lib_path, file_name)
            if os.path.isfile(file_path) and protocol_type + ".py" == file_name:
                protocol_name, ext = os.path.splitext(file_name)
                # 确保协议名称为小写
                protocol_name = protocol_name.lower()
                # 加载库
                module_name = "protocols." + protocol_name
                try:
                    module = __import__(module_name)
                    # class_name = words_capitalize(protocol_name, "_") + "Protocol"
                    # class_object = getattr(module, class_name)
                    protocol_module = getattr(module, protocol_name)
                    class_object = get_subclass(protocol_module, BaseProtocol)
                    return class_object
                except Exception, e:
                    logger.error("Load protocol(%s) fail, error info:%r" % (module_name, e))

    return None