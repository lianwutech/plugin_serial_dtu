#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    modbus网络的串口数据采集插件
    1、device_id的组成方式为ip_port_slaveid
    2、设备类型为0，协议类型为modbus
    3、devices_info_dict需要持久化设备信息，启动时加载，变化时写入
    4、device_cmd内容：json字符串
"""

import time

from setting import *
from libs.daemon import Daemon
from libs.plugin import *
from libs.mqttclient import MQTTClient

# 全局变量
devices_file_name = "devices.txt"
config_file_name = "plugin.cfg"

# 日志对象
logger = logging.getLogger('plugin')

# 配置信息
config_info = load_config(config_file_name)


# 主函数
class PluginDaemon(Daemon):
    def _run(self):
        # 切换工作目录
        os.chdir(cur_file_dir())

        if "channel_type" not in config_info \
                or "protocol_type" not in config_info \
                or "mqtt" not in config_info \
                or "channel" not in config_info \
                or "protocol" not in config_info:
            logger.fatal("配置文件配置项不全，启动失败。")
            return

        channel_type = config_info["channel_type"]
        protocol_type = config_info["protocol_type"]
        network_name = config_info["network_name"]

        # 获取channel类对象
        channel_class = load_channel(channel_type)

        # 获取protocol类对象
        protocol_class = load_protocol(protocol_type)

        # 参数检查
        if channel_class.check_config(config_info["channel"]) \
                and protocol_class.check_config(config_info["protocol"]) \
                and MQTTClient.check_config(config_info["mqtt"]):
            logger.debug("参数检查通过。")
        else:
            logger.fatal("channel、protocol、mqtt参数配置项错误，请检查.")
            return

        # 此处需注意启动顺序，先创建mqtt对象，然后创建channel对象，mqtt对象设置channel属性，mqtt才能够链接服务器
        # 1、初始化mqttclient对象
        mqtt_client = MQTTClient(config_info["mqtt"], network_name)

        # 2、初始化protocol对象
        protocol = protocol_class(config_info["protocol"])

        # 3、初始化channel对象
        channel = channel_class(config_info["channel"], devices_file_name, protocol, mqtt_client, network_name)

        # 4、设置通道对象
        mqtt_client.set_channel(channel)

        while True:
            if not channel.isAlive():
                logger.info("channel进程停止，重新启动。")
                channel.start()

            if not mqtt_client.isAlive():
                logger.info("mqtt进程停止，重新启动。")
                mqtt_client.start()
            logger.debug("周期处理结束")
            time.sleep(2)

# 主函数
def main(argv):
    pid_file_path = "/tmp/%s.pid" % plugin_name
    stdout_file_path = "/tmp/%s.stdout" % plugin_name
    stderr_file_path = "/tmp/%s.stderr" % plugin_name
    daemon = PluginDaemon(pid_file_path, stdout=stdout_file_path, stderr=stderr_file_path)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            logger.info("Unknown command")
            sys.exit(2)
        sys.exit(0)
    elif len(sys.argv) == 1:
        daemon.run()
    else:
        logger.info("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()