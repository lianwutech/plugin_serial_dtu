#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
串口RTU通道类
仅支持modbus协议。
"""

import time
import logging

from pymodbus.client.sync import ModbusTcpClient

from libs.modbusdefine import *
from libs.base_channel import BaseChannel

logger = logging.getLogger('plugin')


class TcpRtuChannel(BaseChannel):
    def __init__(self, channel_params, channel_type, mqtt_client, devices_file_name):
        BaseChannel.__init__(self, channel_params, channel_type, mqtt_client, devices_file_name)
        # 配置项
        self.server = channel_params.get("server", "")
        self.port = channel_params.get("port", 0)
        self.protocol.set_device_info(self.server, self.port)
        # 通信对象
        self.modbus_client = None

    @staticmethod
    def check_config(channel_params):
        if "server" not in channel_params or "port" not in channel_params:
            return False
        return BaseChannel.check_config(channel_params)

    def run(self):
        self.modbus_client = ModbusTcpClient(host=self.server, port=self.port)
        try:
            self.modbus_client.connect()
            logger.debug("连接服务器成功.")
        except Exception, e:
            logger.error("连接服务器失败，错误信息：%r." % e)
            self.modbus_client = None
            return

        while True:
            # 该线程保持空转
            time.sleep(5)

    def process_cmd(self, device_cmd_msg):
        device_id = device_cmd_msg.get("device_id", "")
        device_cmd = device_cmd_msg["command"]
        if device_id in self.devices_info_dict:
            device_info = self.devices_info_dict[device_id]

        if device_cmd["func_code"] == const.fc_read_coils or device_cmd["func_code"] == const.fc_read_discrete_inputs:
            req_result = self.modbus_client.read_coils(device_cmd["addr"],
                                                       device_cmd["count"],
                                                       unit=int(device_info["device_addr"]))
            if req_result is None:
                logger.error("device_cmd(%r) retun None." % device_cmd)
                device_data = None
            else:
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": device_cmd["count"],
                    "values": req_result.bits
                }

        elif device_cmd["func_code"] == const.fc_write_coil:
            req_result = self.modbus_client.write_coil(device_cmd["addr"],
                                                       device_cmd["value"],
                                                       unit=int(device_info["device_addr"]))
            res_result = self.modbus_client.read_coils(device_cmd["addr"],
                                                       1,
                                                       unit=int(device_info["device_addr"]))
            if res_result is None:
                logger.error("device_cmd(%r) retun None." % device_cmd)
                device_data = None
            else:
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": 1,
                    "values": res_result.bits[0:1]
                }
        elif device_cmd["func_code"] == const.fc_write_coils:
            req_result = self.modbus_client.write_coils(device_cmd["addr"],
                                                        device_cmd["values"],
                                                        unit=int(device_info["device_addr"]))
            counter = len(device_cmd["values"])
            res_result = self.modbus_client.read_coils(device_cmd["addr"],
                                                       counter,
                                                       unit=int(device_info["device_addr"]))
            if res_result is None:
                logger.error("device_cmd(%r) retun None." % device_cmd)
                device_data = None
            else:
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": counter,
                    "values": res_result.bits
                }
        elif device_cmd["func_code"] == const.fc_write_register:
            req_result = self.modbus_client.write_register(device_cmd["addr"],
                                                           device_cmd["value"],
                                                           unit=int(device_info["device_addr"]))
            res_result = self.modbus_client.read_holding_registers(device_cmd["addr"],
                                                                   1,
                                                                   unit=int(device_info["device_addr"]))
            if res_result is None:
                logger.error("device_cmd(%r) retun None." % device_cmd)
                device_data = None
            else:
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": 1,
                    "values": res_result.registers[0:1]
                }
        elif device_cmd["func_code"] == const.fc_write_registers:
            result = self.modbus_client.write_registers(device_cmd["addr"],
                                                        device_cmd["values"],
                                                        unit=int(device_info["device_addr"]))
            counter = len(device_cmd["values"])
            res_result = self.modbus_client.read_input_registers(device_cmd["addr"],
                                                                 counter,
                                                                 unit=int(device_info["device_addr"]))
            if res_result is None:
                logger.error("device_cmd(%r) retun None." % device_cmd)
                device_data = None
            else:
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": counter,
                    "values": res_result.registers
                }
        elif device_cmd["func_code"] == const.fc_read_holding_registers:
            res_result = self.modbus_client.read_holding_registers(device_cmd["addr"],
                                                                   device_cmd["count"],
                                                                   unit=int(device_info["device_addr"]))
            if res_result is None:
                logger.error("device_cmd(%r) retun None." % device_cmd)
                device_data = None
            else:
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": device_cmd["count"],
                    "values": res_result.registers
                }
        elif device_cmd["func_code"] == const.fc_read_input_registers:
            res_result = self.modbus_client.read_input_registers(device_cmd["addr"],
                                                                 device_cmd["count"],
                                                                 unit=int(device_info["device_addr"]))
            if res_result is None:
                logger.error("device_cmd(%r) retun None." % device_cmd)
                device_data = None
            else:
                device_data = {
                    "func_code": device_cmd["func_code"],
                    "addr": device_cmd["addr"],
                    "count": device_cmd["count"],
                    "values": res_result.registers
                }
        else:
            logger.error("不支持的modbus指令：%d" % device_cmd["func_code"])
            device_data = None

        logger.debug("device_data:%r" % device_data)
        if device_data is not None:
            device_data_msg = {
                "device_id": device_info["device_id"],
                "device_addr": device_info["device_addr"],
                "device_port": device_info["device_port"],
                "device_type": device_info["device_type"],
                "protocol": self.protocol.protocol,
                "data": device_data
            }
            self.mqtt_client.publish_data(device_data_msg)