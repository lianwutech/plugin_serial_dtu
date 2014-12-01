#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
HTTP-Client通道类
通过调用管理类对象的process_data函数实现信息的发送。
"""

import time
import logging
from httplib2 import Http

from libs.base_channel import BaseChannel


logger = logging.getLogger('plugin')


def get_dict(url):
    http_obj = Http(timeout=5)
    try:
        resp, content = http_obj.request(
            uri=url,
            method='GET',
            headers={'Content-Type': 'application/json; charset=UTF-8'})
    except Exception,e:
        logger.error("get_dict exception:%r" % e)
        return ""

    if resp.status == 200:
        return content

    return ""


class HttpClientChannel(BaseChannel):
    def __init__(self, channel_params, devices_file_name, protocol, mqtt_client, network_name):
        BaseChannel.__init__(self, channel_params, devices_file_name, protocol, mqtt_client, network_name)
        self.host = self.channel_params.get("host", "127.0.0.1")
        self.port = self.channel_params.get("port", 0)
        self.protocol.set_device_info(self.host, self.port)

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

        while True:
            # 该线程保持空转
            time.sleep(5)

    def process_cmd(self, device_cmd_msg):
        device_info = None
        device_id = device_cmd_msg.get("device_id", "")
        device_cmd = device_cmd_msg["command"]
        if device_id in self.devices_info_dict:
            device_info = self.devices_info_dict[device_id]

        # 对指令进行处理
        if device_info is not None:
            # 根据设备指令组装消息
            device_url = self.protocol.process_cmd(device_cmd_msg)
            visit_url = "http://" + self.host + ":" + self.port + "/" + device_url
            result = get_dict(visit_url)
            if len(result) > 0:
                device_data_msg_dict = self.protocol.process_data(self.network_name, result)
                logger.debug("Process data result: %r" % device_data_msg_dict)
                for device_data_msg in device_data_msg_dict:
                    self.check_device(device_data_msg["device_id"],
                                      device_data_msg["device_type"],
                                      device_data_msg["device_addr"],
                                      device_data_msg["device_port"])
                    self.mqtt_client.publish_data(device_data_msg)
            else:
                logger.error("访问url(%s)返回失败." % visit_url)
