"""IoT网关主程序 — python main.py --devices 5 --duration 30"""

import argparse, time, signal, sys, json, logging
from simulator import EarTagSimulator, EnvSensorSimulator, GPSTrackerSimulator
from mqtt_client import MQTTClient, MQTTConfig
from storage import Storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_simulation(args):
    storage = Storage(args.db)
    mqtt = MQTTClient(MQTTConfig(broker=args.broker, port=args.port, client_id=args.client_id))
    mqtt.connect()

    # Register data handler
    def on_data(topic, payload):
        logger.debug(f"MQTT {topic}: {json.dumps(payload, ensure_ascii=False)[:80]}")

    mqtt.subscribe("devices/#", on_data)

    # Create simulators
    simulators = []
    for i in range(args.devices):
        sid = f"RG-SH-MOCK-{i+1:04d}"
        simulators.append(EarTagSimulator(f"eartag-{i+1:03d}", sid))
        simulators.append(EnvSensorSimulator(f"env-{i+1:03d}"))
        simulators.append(GPSTrackerSimulator(f"gps-{i+1:03d}", sid))

    logger.info(f"Starting simulation: {args.devices} sheep, {len(simulators)} devices, {args.duration}s")

    running = True
    def handle_signal(sig, frame):
        nonlocal running
        running = False
        logger.info("Shutting down...")
    signal.signal(signal.SIGINT, handle_signal)

    start = time.time()
    readings = 0
    while running and (time.time() - start) < args.duration:
        for sim in simulators:
            data = sim.read()
            device_type = type(sim).__name__.replace("Simulator", "").lower()
            storage.insert(device_type, data)
            mqtt.publish(f"devices/{device_type}/{data.device_id}", data.__dict__ if hasattr(data, '__dict__') else {})
            readings += 1
        time.sleep(args.interval)

    elapsed = time.time() - start
    stats = storage.stats()
    logger.info(f"Done. {readings} readings in {elapsed:.1f}s ({readings/elapsed:.0f} msg/s)")
    logger.info(f"Storage: {json.dumps(stats)}")

    # Sample output
    if args.sample:
        rows = storage.query(limit=5)
        for r in rows:
            print(json.dumps(r, indent=2, ensure_ascii=False))

    mqtt.disconnect()
    storage.close()
    return 0


def main():
    p = argparse.ArgumentParser(description="绒光公社 IoT网关")
    p.add_argument("--devices", type=int, default=5, help="模拟羊只数量")
    p.add_argument("--duration", type=int, default=30, help="运行时长(秒)")
    p.add_argument("--interval", type=float, default=1.0, help="采集间隔(秒)")
    p.add_argument("--broker", default="localhost")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--client-id", default="rongguang-gateway")
    p.add_argument("--db", default="gateway.db")
    p.add_argument("--sample", action="store_true", help="打印采样数据")
    args = p.parse_args()
    return run_simulation(args)


if __name__ == "__main__":
    sys.exit(main())
