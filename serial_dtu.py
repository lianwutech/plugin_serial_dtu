#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    感知无限公司
    1、device_id的组成方式为ip_port
    2、设备类型为0，未知
    3、通过全局变量来管理每个介入设备，信息包括device_id，thread对象，handler对象
    4、设备数据传输格式：
        对于内置传感器：字符串不变；整形转成字符串；二进制转成16进制字符串
        对于透传数据：data为数据的16进制字符串
    5、设备指令传输格式：
        对于继电器控制，device_cmd内容为json字符串，ctrl_cmd："0x1a"／"0x2a"／"0x3b",ctrl_param:整形字符串如"10"
        对于透传指令，device_cmd为透传的指令
    6、devices_info_dict需要持久化设备信息，启动时加载，变化时写入
"""
import sys
import os
import time
import serial
import paho.mqtt.client as mqtt
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import threading
import logging
import ConfigParser
try:
    import paho.mqtt.publish as publish
except ImportError:
    # This part is only required to run the example from within the examples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import paho.mqtt.publish"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.publish as publish
from json import loads, dumps

from libs.utils import *
from libs.znetmsgdefine import *
from libs.znetmessage import *
from libs.serialcommunicate import *
from libs.platformdevicedefine import *

# 全局变量
# 设备信息字典
devices_info_dict = dict()

# 切换工作目录
# 程序运行路径
procedure_path = cur_file_dir()
# 工作目录修改为python脚本所在地址，后续成为守护进程后会被修改为'/'
os.chdir(procedure_path)

# 日志对象
logger = logging.getLogger('serial_dtu')
hdlr = logging.FileHandler('./serial_dtu.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

# 加载配置项
config = ConfigParser.ConfigParser()
config.read("./serial_dtu.cfg")
serial_port = config.get('serial', 'port')
serial_baund = int(config.get('serial', 'baund'))
mqtt_server_ip = config.get('mqtt', 'server')
mqtt_server_port = int(config.get('mqtt', 'port'))
gateway_topic = config.get('gateway', 'topic')

# 获取本机ip
ip_addr = get_ip_addr()

# 加载设备信息字典
devices_info_file = "./devices.txt"


def load_devices_info_dict():
    devices_file = open(devices_info_file, "r+")
    if os.path.exists(devices_info_file):
        content = devices_file.read()
        devices_file.close()
        try:
            devices_info_dict = loads(content)
        except Exception, e:
            logger.error("devices.txt内容格式不正确")


# 新增设备
def check_device(device_id, device_type, device_addr, device_port):
    # 如果设备不存在则设备字典新增设备并写文件
    if device_id not in devices_info_dict:
        # 新增设备到字典中
        devices_info_dict[device_id] = {
            "device_id": device_id,
            "device_type": device_type,
            "device_addr": device_addr,
            "device_port": device_port
        }
        #写文件
        devices_file = open(devices_info_file, "w+")
        devices_file.write(dumps(devices_info_dict))
        devices_file.close()


def publish_device_data(device_id, device_type, device_addr, device_port, device_data):
    # device_data: 16进制字符串
    # 组包
    device_msg = "%s,%d,%s,%d,%s" % (device_id, device_type, device_addr, device_port, device_data)

    # MQTT发布
    publish.single(topic=gateway_topic,
                   payload=device_msg,
                   hostname=mqtt_server_ip,
                   port=mqtt_server_port)
    logger.info("向Topic(%s)发布消息：%s" % (gateway_topic, device_msg))


def process_dtu_data(serial_data):
    """
    串口数据处理
    :param data_sender:
    :param serial_data:
    :return:
    """
    # modbus解码

    # 组消息包
    device_id = "%s_%s_%s" % (ip_addr, serial_port, "0")
    device_addr = serial_port
    device_port = serial_baund
    device_type = 0
    device_data = serial_data
    check_device(device_id, device_type, device_addr, device_port)
    publish_device_data(device_id, device_type, device_addr, device_port, device_data)


# 串口数据读取线程
def process_mqtt(device_id):
    """
    :param device_id 设备地址
    :return:
    """
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, rc):
        logger.info("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for device_id in devices_info_dict:
            device_info = devices_info_dict[device_id]
            logger.debug("device_info:%r" % device_info)
            if device_info["device_type"] == const.DEVICE_TYPE_DELAY_CTRL or \
                            device_info["device_type"] == const.ZNET_DEVICE_TYPE_SENSOR_NONE:
                mqtt_client.subscribe(device_id)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        logger.info("收到数据消息" + msg.topic + " " + str(msg.payload))
        # 消息只包含device_cmd，为json字符串
        device_cmd = loads(msg.payload)

        # 根据topic确定设备由当前进程负责
        # 透传指令



        zigbee_ctrl_msg = GZXXZigbeeNetMessage()

        device_info = devices_info_dict["device_id"]
        node_port = device_info["device_port"]
        # 指令消息处理对象
        if len(device_info["device_addr"]) == 0:
            zigbee_ctrl_msg.msg['tag_data']['tag_addr'] = "FFFFFF"
        else:
            # 根据协议，读卡器地址前两个字节为网络地址，第三个字节统一为0xef
            zigbee_ctrl_msg.msg['tag_data']['tag_addr'] = device_info["device_addr"]

        zigbee_ctrl_msg.msg['frame_type'] = zigbee_ctrl_msg.msg_engine.msg_def.const.FH_READER
        zigbee_ctrl_msg.msg['tag_data_type'] = zigbee_ctrl_msg.msg_engine.msg_def.const.MESSAGE_TYPE_RELAY_CTRL
        # 0x2切换到手动状态
        zigbee_ctrl_msg.msg['tag_data']['control_mode_switch'] = 2

        _delay_ctrl_reg = []
        for i in range(0, 8):
            ctrl_reg = dict()
            if i == node_port - 1:
                ctrl_reg["ctrl_cmd"] = int(device_cmd["ctrl_cmd"], 16)
                ctrl_reg["ctrl_delay_time"] = int(device_cmd["ctrl_delay_time"])
            else:
                ctrl_reg["ctrl_cmd"] = 0xff
                ctrl_reg["ctrl_delay_time"] = 0xffff
            logger.debug("%d delay_ctrl_reg: %s" % (i, ctrl_reg))
            _delay_ctrl_reg.append(ctrl_reg)
        zigbee_ctrl_msg.msg['tag_data']['delay_ctrl_reg'] = _delay_ctrl_reg

        # 消息打包
        try:
            # logger.debug("zigbee_msg: %s" % dumps(zigbee_ctrl_msg.msg['tag_data']))
            zigbee_ctrl_msg.pack()
            logger.debug("打包后结果:%r" % zigbee_ctrl_msg.msg['frame_data_buff'])
            # 指令下发
            cooperator_serial.send(zigbee_ctrl_msg.msg['frame_data_buff'])
        except Exception, e:
            logger.error("消息打包错误，错误内容：%s" % e)

    mqtt_client = mqtt.Client(client_id=gateway_topic)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(mqtt_server_ip, mqtt_server_port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    mqtt_client.loop_forever()


if __name__ == "__main__":

    # 加载设备数据
    load_devices_info_dict()

    # 初始化modbus客户端
    modbus_client = ModbusClient(method='rtu', port=serial_port, baudrate=serial_baund, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1)
    modbus_client.connect()

    # 初始化mqtt监听
    mqtt_thread = threading.Thread(target=process_mqtt)
    mqtt_thread.start()


    data_buff = ""
    while True:

        # 如果线程停止则创建
        if not mqtt_thread.is_alive():
            mqtt_thread = threading.Thread(target=process_mqtt)
            mqtt_thread.start()

        # 读取串口数据并解析
        # 串口数据读取
        logger.debug("串口数据读取")
        try:
            serial_data = cooperator_serial.recv()
        except Exception, e:
            serial_data = ""
            logger.error(e)
            logger.info("重新打开串口")
            result, error_info = cooperator_serial.open(serial_settings)
            if result:
                logger.error("重新打开串口成功")
            else:
                logger.error("重新打开串口失败")

        # 解析串口数据
        if len(serial_data) > 0:
            logger.debug("串口数据: %r" % serial_data)
            logger.debug("16进制串口数据: %s" % serial_data.encode("hex"))
            logger.debug("串口数据长度: %d" % (len(serial_data)))

            # 组消息包
            process_dtu_data(serial_data)


        logger.debug("处理完成，休眠0.1秒")
        time.sleep(0.1)

