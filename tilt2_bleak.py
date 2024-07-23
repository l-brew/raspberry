import asyncio
from uuid import UUID


from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import re
import threading

# ibeacon_format = Struct(
#     "type_length" / Const(b"\x02\x15"),
#     "uuid" / Array(16, Byte),
#     "major" / Int16ub,
#     "minor" / Int16ub,
#     "power" / Int8sl,
# )

UUID_REGEX='A495BB..C5B14B44B5121370F02D74DE'

class Tilt2:
    def __init__(self):
        self.temp=None
        self.grav = None
        self.dev_id = 0
        self.p=re.compile(UUID_REGEX.lower())
        pass

    def device_found(self,
        device: BLEDevice, advertisement_data: AdvertisementData
    ):
        """Decode iBeacon."""
        try:
            apple_data = advertisement_data.manufacturer_data[0x004C]
            beacon_type = int.from_bytes(apple_data[0:2], "big")
            if beacon_type != 0x0215:
                return
            uuid = apple_data[2:18].hex()
            major = int.from_bytes(apple_data[18:20], "big")
            minor = int.from_bytes(apple_data[20:22], "big")
            if self.p.match(uuid) is None:
                return
            
            sg = minor / 1000 * 0.99435892
            t_f = major
            self.grav = 135.997 * (sg ** 3) - 630.272 * (sg ** 2) + 1111.14 * sg - 616.868
            self.temp = (t_f - 32) * 5 / 9.

        except Exception as e:
            pass
    


    async def mainloop(self):
        """Scan for devices."""
        scanner = BleakScanner()
        scanner.register_detection_callback(self.device_found)

        while True:
            await scanner.start()
            await asyncio.sleep(1.0)
            await scanner.stop()

    def loop_thread_fnc(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tilt.mainloop())
    
    def connect(self):
        threading.Thread(target=self.loop_thread_fnc,daemon=True).start()


if __name__ == "__main__":
    tilt = Tilt2()
    tilt.connect()
    import time
    time.sleep(20)

