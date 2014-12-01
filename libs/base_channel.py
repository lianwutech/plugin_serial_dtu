#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通道类
负责管道通信时，也负责设备信息管理
"""
import os
import time
import json
import logging
import threading


logger = logging.getLogger('plugin')


class BaseChannel(object):
    """
    基础设备通信类
    针对每种通信模式实现各自的内容
    """

    def __init__(self, channel_params, devices_file_name, protocol, mqtt_client, network_name):
        self.protocol = protocol
        self.channel_params = channel_params
        self.network_name = network_name
        self.mqtt_client = mqtt_client
        self.devices_file_name = devices_file_name
        self.devices_info_dict = {}
        self.load_devices_info_dict()
        self.thread = None

    @staticmethod
    def check_config(channel_params):
        return True

    def run(self):
        while True:
            time.sleep(2)

    def process_cmd(self, device_cmd_msg):
        return

    # 加载设备信息
    def load_devices_info_dict(self):
        devices_info_dict = dict()
        if os.path.exists(self.devices_file_name):
            devices_file = open(self.devices_file_name, "r+")
            content = devices_file.read()
            logger.debug("devices.txt内容:%s" % content)
            devices_file.close()
            try:
                devices_info_dict.update(json.loads(content))
            except Exception, e:
                logger.error("devices.txt内容格式不正确")

        # 重写设备信息
        try:
            devices_file = open(self.devices_file_name, "w+")
            devices_file.write(json.dumps(devices_info_dict))
            devices_file.close()
        except Exception, e:
            logger.error("load devices info fail，%r" % e)
        logger.debug("devices_info_dict加载结果%r" % devices_info_dict)

        self.devices_info_dict = devices_info_dict

    # 设备检查
    def check_device(self, device_id, device_type, device_addr, device_port):
        # 如果设备不存在则设备字典新增设备并写文件
        if device_id not in self.devices_info_dict:
            # 新增设备到字典中
            self.devices_info_dict[device_id] = {
                "device_id": device_id,
                "device_type": device_type,
                "device_addr": device_addr,
                "device_port": device_port
            }
            logger.info("发现新设备%r" % self.devices_info_dict[device_id])

            #写文件
            devices_file = open(self.devices_file_name, "w+")
            devices_file.write(json.dumps(self.devices_info_dict))
            devices_file.close()

            # 上报设备信息
            device_msg = {
                "device_id": device_id,
                "device_type": device_type,
                "device_addr": device_addr,
                "device_port": device_port,
                "protocol": self.protocol.protocol_type,
                "data": ""
            }
            self.mqtt_client.publish_data(device_msg)
        else:
            logger.debug("设备已存在于设备列表中。")

    def start(self):
        if self.thread is not None:
            # 如果进程非空，则等待退出
            self.thread.join(1)

        # 启动一个新的线程来运行
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def isAlive(self):
        if self.thread is not None:
            return self.thread.isAlive()
        else:
            return False