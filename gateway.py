#!/usr/bin/env python3
"""
绒光公社 - 物联网数据采集网关主程序
Rongguang IoT Gateway Main Program
"""

import json
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import threading
import queue

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        self.devices = {}
        self.running = False
    
    def register_device(self, device_id: str, device_type: str, 
                       connection_params: Dict) -> bool:
        """注册设备"""
        self.devices[device_id] = {
            "id": device_id,
            "type": device_type,
            "params": connection_params,
            "status": "registered",
            "last_data": None,
            "last_seen": None
        }
        logger.info(f"设备 {device_id} 注册成功")
        return True
    
    def start_device(self, device_id: str) -> bool:
        """启动设备"""
        if device_id not in self.devices:
            logger.error(f"设备 {device_id} 未注册")
            return False
        
        self.devices[device_id]["status"] = "running"
        logger.info(f"设备 {device_id} 启动成功")
        return True
    
    def stop_device(self, device_id: str) -> bool:
        """停止设备"""
        if device_id not in self.devices:
            return False
        
        self.devices[device_id]["status"] = "stopped"
        logger.info(f"设备 {device_id} 已停止")
        return True
    
    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """获取设备状态"""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> List[Dict]:
        """获取所有设备"""
        return list(self.devices.values())


class DataCollector:
    """数据采集器"""
    
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.data_queue = queue.Queue()
    
    def collect(self, device_id: str, data_type: str) -> Optional[Dict]:
        """采集数据"""
        device = self.device_manager.get_device_status(device_id)
        if not device or device["status"] != "running":
            logger.warning(f"设备 {device_id} 未运行")
            return None
        
        # 模拟数据采集
        data = self._simulate_data_collection(device_id, data_type)
        
        # 添加到队列
        self.data_queue.put(data)
        
        # 更新设备状态
        device["last_data"] = data
        device["last_seen"] = datetime.now().isoformat()
        
        logger.info(f"从设备 {device_id} 采集到数据")
        return data
    
    def _simulate_data_collection(self, device_id: str, 
                                   data_type: str) -> Dict:
        """模拟数据采集（实际项目中替换为真实硬件接口）"""
        timestamp = datetime.now().isoformat() + "Z"
        
        if data_type == "temperature":
            return {
                "device_id": device_id,
                "timestamp": timestamp,
                "sensor_type": "temperature_humidity",
                "data": {
                    "temperature": 25.5,
                    "humidity": 45,
                    "battery_level": 85
                }
            }
        elif data_type == "gps":
            return {
                "device_id": device_id,
                "sheep_id": "RG-SH-2026-001",
                "timestamp": timestamp,
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
        elif data_type == "rfid":
            return {
                "device_id": device_id,
                "timestamp": timestamp,
                "sensor_type": "rfid_reader",
                "data": {
                    "tag_id": "EPC-96-GEN2-001",
                    "sheep_id": "RG-SH-2026-001",
                    "read_count": 1,
                    "rssi": -65
                }
            }
        else:
            return {
                "device_id": device_id,
                "timestamp": timestamp,
                "data_type": data_type,
                "data": {}
            }
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.data_queue.qsize()


class CloudSync:
    """云端同步器"""
    
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.sync_interval = 300  # 5分钟
        self.running = False
    
    def upload(self, data: Dict) -> bool:
        """上传数据到云端"""
        # 模拟上传（实际项目中替换为真实HTTP请求）
        logger.info(f"上传数据到云端: {data['device_id']}")
        return True
    
    def sync_batch(self, data_list: List[Dict]) -> bool:
        """批量同步数据"""
        logger.info(f"批量同步 {len(data_list)} 条数据")
        return True
    
    def start_sync_loop(self, data_queue: queue.Queue):
        """启动同步循环"""
        self.running = True
        
        def sync_worker():
            while self.running:
                batch = []
                while not data_queue.empty() and len(batch) < 100:
                    try:
                        data = data_queue.get(timeout=1)
                        batch.append(data)
                    except queue.Empty:
                        break
                
                if batch:
                    self.sync_batch(batch)
                
                time.sleep(self.sync_interval)
        
        thread = threading.Thread(target=sync_worker)
        thread.daemon = True
        thread.start()
        logger.info("云端同步循环已启动")


class IoTGateway:
    """物联网网关主类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device_manager = DeviceManager()
        self.data_collector = DataCollector(self.device_manager)
        self.cloud_sync = CloudSync(
            api_endpoint=config.get("api_endpoint", ""),
            api_key=config.get("api_key", "")
        )
        self.running = False
    
    def initialize(self):
        """初始化网关"""
        logger.info("正在初始化物联网网关...")
        
        # 注册配置中的设备
        for device_config in self.config.get("devices", []):
            self.device_manager.register_device(
                device_id=device_config["id"],
                device_type=device_config["type"],
                connection_params=device_config.get("params", {})
            )
        
        logger.info("网关初始化完成")
    
    def start(self):
        """启动网关"""
        self.running = True
        logger.info("物联网网关已启动")
        
        # 启动所有设备
        for device_id in self.device_manager.devices:
            self.device_manager.start_device(device_id)
        
        # 启动云端同步
        self.cloud_sync.start_sync_loop(self.data_collector.data_queue)
        
        # 主循环
        try:
            while self.running:
                self._main_loop()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到停止信号")
            self.stop()
    
    def _main_loop(self):
        """主循环"""
        # 定期采集数据
        for device_id, device in self.device_manager.devices.items():
            if device["status"] == "running":
                # 根据设备类型采集不同数据
                if device["type"] == "temperature_sensor":
                    self.data_collector.collect(device_id, "temperature")
                elif device["type"] == "gps_tracker":
                    self.data_collector.collect(device_id, "gps")
                elif device["type"] == "rfid_reader":
                    self.data_collector.collect(device_id, "rfid")
    
    def stop(self):
        """停止网关"""
        self.running = False
        self.cloud_sync.running = False
        
        # 停止所有设备
        for device_id in self.device_manager.devices:
            self.device_manager.stop_device(device_id)
        
        logger.info("物联网网关已停止")
    
    def get_status(self) -> Dict:
        """获取网关状态"""
        return {
            "running": self.running,
            "devices": len(self.device_manager.devices),
            "queue_size": self.data_collector.get_queue_size(),
            "uptime": "running"  # 实际项目中计算运行时间
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="绒光公社物联网网关")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    args = parser.parse_args()
    
    # 加载配置（简化版本，实际使用YAML解析）
    config = {
        "api_endpoint": "https://api.rongguang.community",
        "api_key": "demo-key",
        "devices": [
            {
                "id": "TEMP-001",
                "type": "temperature_sensor",
                "params": {"pin": 4}
            },
            {
                "id": "GPS-001",
                "type": "gps_tracker",
                "params": {"interval": 300}
            },
            {
                "id": "RFID-001",
                "type": "rfid_reader",
                "params": {"port": "/dev/ttyUSB0"}
            }
        ]
    }
    
    # 创建并启动网关
    gateway = IoTGateway(config)
    gateway.initialize()
    gateway.start()


if __name__ == "__main__":
    main()