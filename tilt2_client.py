import threading
import ScanUtility
import bluetooth._bluetooth as bluez
import re
import time
import traceback

PERIOD=5
UUID_REGEX='A495BB..C5B14B44B5121370F02D74DE'

class Tilt2:
    def __init__(self):
        self.temp=None
        self.grav = None
        self.dev_id = 0
        pass

    def connect(self):
        threading.Thread(target=self.start).start()

        
    def start(self):

        p=re.compile(UUID_REGEX.lower())
        try:
            sock = bluez.hci_open_dev(self.dev_id)


            print(sock)
            print("\n *** Looking for BLE Beacons ***\n")
            print("\n *** CTRL-C to Cancel ***\n")
        except:
            print("Error accessing bluetooth")
            print(traceback.format_exc())

        ScanUtility.hci_enable_le_scan(sock)
        # Scans for iBeacons
        try:
            while True:
                returnedList = ScanUtility.parse_events(sock, 10)
                for item in returnedList:
                    if item['type'] is 'iBeacon' and \
                                p.match(item['uuid'].replace('-','').lower()) is not None:
                        sg = item['minor'] / 1000
                        t_f = item['major']
                        self.grav = 135.997 * (sg ** 3) - 630.272 * (sg ** 2) + 1111.14 * sg - 616.868
                        self.temp = (t_f - 32) * 5 / 9.
        except KeyboardInterrupt:
            pass
