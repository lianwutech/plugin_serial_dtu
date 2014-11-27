#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Apatce公司RCD系列设备协议类
"""

import logging

from libs.base_protocol import BaseProtocol


logger = logging.getLogger('plugin')


class ApatcercdProtocol(BaseProtocol):
    def __init__(self, protocol_params):
        BaseProtocol.__init__(self, protocol_params)
        # 修改协议名称
        self.protocol = "apatcercd"
        self.device_type = "apatcercd"
        # 缓存命令来方便解析数据
        self.device_cmd_msg = None

    def process_data(self, network_name, data):
        """
        返回device_data
        :param data_msg:
        :return:
        """
        device_data_msg_list = []
        if self.device_cmd_msg is not None:
            device_id = self.device_cmd_msg["device_id"]
            device_addr = self.device_cmd_msg["device_addr"]
            device_port = self.device_cmd_msg["device_port"]
            device_type = self.device_cmd_msg["device_type"]
        else:
            device_id = "%s/%s/%d" % (network_name, self.device_addr, self.device_port)
            device_addr = self.device_addr
            device_port = self.device_port
            device_type = self.device_type

        device_data_msg = {
            "device_id": device_id,
            "device_addr": device_addr,
            "device_port": device_port,
            "device_type": device_type,
            "protocol": self.protocol,
            "data": data
        }
        device_data_msg_list.append(device_data_msg)

        return device_data_msg_list

    def process_cmd(self, device_cmd_msg):
        """
        返回cmd_msg
        :param device_cmd:
        :return:
        """
        self.device_cmd_msg = device_cmd_msg
        return device_cmd_msg.get("resource_route", "")

