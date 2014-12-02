#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
基础协议类
内存拼接和消息处理由协议类来处理
"""


class BaseProtocol(object):
    def __init__(self, protocol_params):
        self.protocol_params = protocol_params
        self.protocol_type = "basic"
        self.device_addr = "addr1"
        self.device_port = "port1"
        self.device_type = "basic"
        # 缓存命令来方便解析数据
        self.device_cmd_msg = None

    @staticmethod
    def check_config(protocol_params):
        return True

    def set_device_info(self, device_addr, device_port):
        # 设置默认的设备地址和端口
        # 设备地址和端口都是字符串类型
        self.device_addr = str(device_addr).replace(".", "_").replace(" ", "")
        self.device_port = str(device_port).replace(".", "_").replace(" ", "")

    def process_data(self, network_name, data):
        """
        返回device_data数组
        :param network_name:网络名称，data:收到的数据
        :return:设备数据字典
        设备数据格式:device_id, device_addr, device_port, device_type, data
        """
        return []

    def process_cmd(self, device_cmd_msg):
        """
        处理设备指令
        :param device_cmd_msg:设备指令，格式为device_id, device_addr, device_port, device_type, cmd
        :return:
        """
        self.device_cmd_msg = device_cmd_msg
        return ""

