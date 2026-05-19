"""IoT设备模拟器 — EarTag / EnvSensor / GPSTracker."""

import random, time
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EarTagData:
    device_id: str
    sheep_id: str
    temperature: float
    heart_rate: int
    activity: str
    battery: float
    timestamp: str


@dataclass
class EnvSensorData:
    device_id: str
    air_temp: float
    humidity: float
    pm25: float
    wind_speed: float
    timestamp: str


@dataclass
class GPSTrackerData:
    device_id: str
    sheep_id: str
    latitude: float
    longitude: float
    altitude: float
    speed: float
    timestamp: str


class EarTagSimulator:
    """羊只智能耳标模拟器 — 体温、心率、活动量."""

    def __init__(self, device_id: str, sheep_id: str):
        self.device_id = device_id
        self.sheep_id = sheep_id
        self.base_temp = random.uniform(38.5, 39.5)
        self.base_hr = random.randint(60, 80)

    def read(self) -> EarTagData:
        return EarTagData(
            device_id=self.device_id,
            sheep_id=self.sheep_id,
            temperature=round(self.base_temp + random.uniform(-0.5, 0.5), 1),
            heart_rate=self.base_hr + random.randint(-5, 5),
            activity=random.choice(["grazing", "resting", "walking", "drinking"]),
            battery=round(random.uniform(85.0, 99.9), 1),
            timestamp=datetime.now().isoformat(),
        )


class EnvSensorSimulator:
    """牧场环境传感器模拟器 — 温度、湿度、PM2.5、风速."""

    def __init__(self, device_id: str, lat: float = 44.0, lng: float = 116.0):
        self.device_id = device_id
        self.lat, self.lng = lat, lng

    def read(self) -> EnvSensorData:
        return EnvSensorData(
            device_id=self.device_id,
            air_temp=round(random.uniform(15.0, 35.0), 1),
            humidity=round(random.uniform(30.0, 70.0), 1),
            pm25=round(random.uniform(5.0, 50.0), 1),
            wind_speed=round(random.uniform(0.0, 15.0), 1),
            timestamp=datetime.now().isoformat(),
        )


class GPSTrackerSimulator:
    """GPS定位器模拟器 — 经纬度、海拔、速度."""

    def __init__(self, device_id: str, sheep_id: str, lat: float = 44.0, lng: float = 116.0):
        self.device_id = device_id
        self.sheep_id = sheep_id
        self.lat, self.lng = lat, lng

    def read(self) -> GPSTrackerData:
        self.lat += random.uniform(-0.001, 0.001)
        self.lng += random.uniform(-0.001, 0.001)
        return GPSTrackerData(
            device_id=self.device_id,
            sheep_id=self.sheep_id,
            latitude=round(self.lat, 6),
            longitude=round(self.lng, 6),
            altitude=round(random.uniform(800.0, 1200.0), 1),
            speed=round(random.uniform(0.0, 3.0), 2),
            timestamp=datetime.now().isoformat(),
        )
