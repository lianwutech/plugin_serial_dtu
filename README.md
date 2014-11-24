plugin_serial_modbus
==================
串口访问modbus网络
设备配置样例：
{
    "mnet1/1/0":{
        "device_id":"mnet1/1/0",
        "device_type":"modbus",
        "device_addr": "1",
        "device_port": "0"
        }
}
device_id、device_addr、device_port均为字符串
device_id的组成格式：device_network/slave_id／0
device_addr:slave_id
device_port:0

mqtt测试报文样例：
{"command": {"count": 2, "addr": 0, "func_code": 3}}
