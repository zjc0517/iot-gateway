# 绒光公社 - 物联网数据采集网关

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

## 项目简介

物联网数据采集网关是连接牧场硬件设备与云平台的关键组件，实现羊只行为数据、环境数据的实时采集和上传。

**核心功能**：
- 🌡️ 环境数据监测（温度、湿度、GPS）
- 🐑 羊只行为追踪（运动步数、活动范围）
- 📡 多设备接入支持（RFID、摄像头、传感器）
- 🔐 数据加密传输（TLS 1.3）
- 📊 边缘计算（本地数据处理，减少云端压力）

## 技术架构

```
牧场硬件设备 → 边缘网关 → 云平台 → 区块链存证
                ↓
            本地缓存 → 离线同步
```

### 支持的硬件设备

| 设备类型 | 型号示例 | 数据类型 |
|---------|---------|---------|
| RFID耳标 | EPC Gen2 | 身份识别 |
| GPS项圈 | LoRaWAN | 位置追踪 |
| 温湿度传感器 | DHT22 | 环境监测 |
| 摄像头 | 海康威视 | 图像采集 |
| 称重设备 | 电子地磅 | 体重数据 |

## 快速开始

### 安装

```bash
git clone https://github.com/yourname/rongguang-iot-gateway.git
cd rongguang-iot-gateway
pip install -r requirements.txt
```

### 配置

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml 配置你的设备参数
```

### 运行

```bash
python gateway.py --config config.yaml
```

## 核心模块

### 1. 设备管理器 (DeviceManager)

```python
from gateway.device_manager import DeviceManager

manager = DeviceManager()

# 注册设备
manager.register_device(
    device_id="RFID-001",
    device_type="rfid_reader",
    connection_params={"port": "/dev/ttyUSB0", "baudrate": 9600}
)

# 启动设备
manager.start_device("RFID-001")
```

### 2. 数据采集器 (DataCollector)

```python
from gateway.data_collector import DataCollector

collector = DataCollector()

# 采集数据
data = collector.collect(
    device_id="RFID-001",
    data_type="sheep_id"
)
```

### 3. 云端同步 (CloudSync)

```python
from gateway.cloud_sync import CloudSync

sync = CloudSync(api_endpoint="https://api.rongguang.community")

# 上传数据
sync.upload(data)
```

## 数据格式

### 传感器数据

```json
{
  "device_id": "TEMP-001",
  "timestamp": "2026-03-27T12:00:00Z",
  "sensor_type": "temperature_humidity",
  "data": {
    "temperature": 25.5,
    "humidity": 45,
    "battery_level": 85
  },
  "location": {
    "pasture_id": "PASTURE-A",
    "coordinates": [116.0, 44.0]
  }
}
```

### GPS追踪数据

```json
{
  "device_id": "GPS-001",
  "sheep_id": "RG-SH-2026-001",
  "timestamp": "2026-03-27T12:00:00Z",
  "location": {
    "latitude": 44.0,
    "longitude": 116.0,
    "altitude": 1200
  },
  "movement": {
    "speed": 0.5,
    "heading": 90,
    "step_count": 1200
  }
}
```

## 配置示例

```yaml
# config.yaml
gateway:
  name: "牧场A-边缘网关"
  location: "内蒙古锡林郭勒"
  
cloud:
  api_endpoint: "https://api.rongguang.community"
  api_key: "your-api-key"
  sync_interval: 300  # 5分钟同步一次
  
devices:
  - id: "RFID-001"
    type: "rfid_reader"
    enabled: true
    params:
      port: "/dev/ttyUSB0"
      baudrate: 9600
      
  - id: "TEMP-001"
    type: "temperature_sensor"
    enabled: true
    params:
      pin: 4
      interval: 60  # 每分钟采集一次
      
  - id: "GPS-001"
    type: "gps_tracker"
    enabled: true
    params:
      update_interval: 300  # 每5分钟更新一次

security:
  encryption: true
  tls_version: "1.3"
  certificate_path: "/path/to/cert.pem"
```

## API接口

### 本地API

```python
# 启动API服务
python api_server.py

# 查询设备状态
curl http://localhost:8080/api/devices

# 获取实时数据
curl http://localhost:8080/api/data/latest
```

## 部署指南

### 硬件要求

- Raspberry Pi 4B (4GB RAM) 或更高
- 稳定的网络连接（4G/WiFi）
- UPS不间断电源（推荐）

### 系统安装

```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt

# 配置系统服务
sudo cp systemd/iot-gateway.service /etc/systemd/system/
sudo systemctl enable iot-gateway
sudo systemctl start iot-gateway
```

## 监控与运维

### 日志查看

```bash
# 查看实时日志
tail -f logs/gateway.log

# 查看系统状态
systemctl status iot-gateway
```

### 性能监控

```bash
# 查看资源占用
curl http://localhost:8080/api/metrics
```

## 贡献指南

欢迎提交Issue和PR，共同完善牧场物联网生态。

## 许可证

MIT License

## 联系我们

- 项目官网：https://rongguang.community
- 技术支持：tech@rongguang.community