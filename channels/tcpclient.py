#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
TCP-Client通道类
通过调用管理类对象的process_data函数实现信息的发送。
仅支持单个设备
"""

import time
import socket
import logging

from libs.base_channel import BaseChannel


logger = logging.getLogger('plugin')


class TcpClientChannel(BaseChannel):
    def __init__(self, channel_params, devices_file_name, protocol, mqtt_client, network_name):
        BaseChannel.__init__(self, channel_params, devices_file_name, protocol, mqtt_client, network_name)
        self.host = self.channel_params.get("host", "127.0.0.1")
        self.port = self.channel_params.get("port", 0)
        self.protocol.set_device_info(self.host, self.port)
        self.socket = None

    @staticmethod
    def check_config(channel_params):
        if "host" not in channel_params or "port" not in channel_params:
            return False
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

        # 创建连接
        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        try:
            self.socket.connect((self.host, self.port))
            while True:
                # 监听消息
                data = self.socket.recv(1024)
                if len(data) > 0:
                    device_data_dict = self.protocol.process_data(self.network_name, data)
                    logger.debug("Process data result: %r" % device_data_dict)
                    for device_data in device_data_dict:
                        self.check_device(device_data["device_id"],
                                          device_data["device_type"],
                                          device_data["device_addr"],
                                          device_data["device_port"])
                        self.mqtt_client.publish_data(device_data)
                else:
                    time.sleep(1)
                    logger.debug("No data, sleep 1s.")
        except Exception, e:
            logger.error("Socket error, error info:%r" % e)
            self.socket.close()
            self.socket = None

    def process_cmd(self, device_cmd_msg):
        # 确保device_id在设备字典中
        device_id = device_cmd_msg["device_id"]
        if device_id not in self.devices_info_dict:
            logger.info("设备%s不在设备库中。" % device_id)
            return
        try:
            command = self.protocol.process_cmd(device_cmd_msg)
            if command is not None:
                self.socket.send(command)
            else:
                logger.info("消息%r处理返回空。" % device_cmd_msg)
        except Exception, e:
            logger.error("Send_cmd error, error info:%r" % e)
