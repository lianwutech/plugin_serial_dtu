#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
串口通道类
"""

import logging

import serial

from libs.base_channel import BaseChannel


logger = logging.getLogger('plugin')


class SerialChannel(BaseChannel):
    def __init__(self, channel_params, devices_file_name, protocol, mqtt_client):
        BaseChannel.__init__(self, channel_params, devices_file_name, protocol, mqtt_client)

    @staticmethod
    def check_config(channel_params):
        return BaseChannel.check_config(channel_params)

    def run(self):

        # 首先上报设备数据
        for device_id in self.devices_info_dict:
            device_info = self.devices_info_dict[device_id]
            device_msg = {
                "device_id": device_info["device_id"],
                "device_type": device_info["device_type"],
                "device_addr": device_info["device_addr"],
                "device_port": device_info["device_port"],
                "protocol": self.protocol.protocol,
                "data": ""
            }
            self.mqtt_client.publish_data(device_msg)

        pass

    def process_cmd(self, device_cmd_msg):
        pass