#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
modbus协议类
本协议仅作为框架使用，仅支持rtu通达
"""

import logging

from libs.base_protocol import BaseProtocol


logger = logging.getLogger('plugin')


class ModbusProtocol(BaseProtocol):
    def __init__(self, protocol_params):
        BaseProtocol.__init__(self, protocol_params)
        # 修改协议名称
        self.protocol = "modbus"
        self.device_type = "modbus"

    def process_data(self, network_name, data):
        """
        返回device_data
        :param data_msg:
        :return:
        """
        return []

    def process_cmd(self, device_cmd_msg):
        """
        返回cmd_msg
        :param device_cmd:
        :return:
        """
        return ""

