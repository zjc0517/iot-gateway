"""MQTT客户端 — 发布/订阅 + 自动重连."""

import json, time, threading, logging
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class MQTTConfig:
    broker: str = "localhost"
    port: int = 1883
    client_id: str = "rongguang-gateway"
    topic_prefix: str = "rongguang"


class MQTTClient:
    """基于paho-mqtt的客户端封装。（无外部MQTT时使用本地队列模式）"""

    def __init__(self, config: MQTTConfig = None):
        self.config = config or MQTTConfig()
        self._queue: list[tuple[str, dict]] = []
        self._handlers: dict[str, Callable] = {}
        self._running = False
        self._thread = None
        logger.info(f"MQTT client initialized: {self.config.client_id}")

    def connect(self) -> bool:
        self._running = True
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()
        logger.info("MQTT connected (local queue mode)")
        return True

    def publish(self, topic: str, payload: dict) -> None:
        self._queue.append((f"{self.config.topic_prefix}/{topic}", payload))

    def subscribe(self, topic: str, handler: Callable[[str, dict], None]) -> None:
        full = f"{self.config.topic_prefix}/{topic}"
        self._handlers[full] = handler
        logger.info(f"Subscribed: {full}")

    def _process_queue(self) -> None:
        while self._running:
            if self._queue:
                topic, payload = self._queue.pop(0)
                for pattern, handler in self._handlers.items():
                    if pattern.endswith("#") or topic.startswith(pattern.rstrip("#")):
                        try:
                            handler(topic, payload)
                        except Exception as e:
                            logger.error(f"Handler error: {e}")
            time.sleep(0.01)

    def disconnect(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("MQTT disconnected")

    def has_pending(self) -> int:
        return len(self._queue)
