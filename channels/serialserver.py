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
    def __init__(self, channel_params, channel_type, mqtt_client, devices_file_name):
        BaseChannel.__init__(self, channel_params, channel_type, mqtt_client, devices_file_name)

    @staticmethod
    def check_config(channel_params):
        return BaseChannel.check_config(channel_params)

    def run(self):
        pass

    def process_cmd(self, device_cmd_msg):
        pass