import random
import threading
import time

class PT100:
    def __init__(self):
        self.val = 20.0  # Start at room temp
        self.tempList = [self.val]
        self._running = False

    def update(self):
        # Simulate temperature drift
        new_val = self.val + random.uniform(-0.2, 0.2)
        self.tempList.append(new_val)
        if len(self.tempList) > 5:
            self.tempList.pop(0)
        self.val = sum(self.tempList) / len(self.tempList)

    def run(self):
        self._running = True
        while self._running:
            self.update()
            time.sleep(0.1)

    def getVal(self):
        return self.val

    def stop(self):
        self._running = False

class Ntc:
    def __init__(self, pin, beta=3889, r0=10000, t0=298.15):
        self.val = 25.0  # Start at room temp
        self.tempList = [self.val]
        self.pin = pin
        self.beta = beta
        self.r0 = r0
        self.t0 = t0

    def update(self):
        # Simulate temperature drift
        new_val = self.val + random.uniform(-0.5, 0.5)
        self.tempList.append(new_val)
        if len(self.tempList) > 5:
            self.tempList.pop(0)
        self.val = sum(self.tempList) / len(self.tempList)

    def getVal(self):
        return self.val

class Tilt2:
    def __init__(self):
        self.temp = 20.0
        self.grav = 1.050
        self._running = False

    def connect(self):
        # Start background threads to simulate updates
        threading.Thread(target=self._simulate, daemon=True).start()

    def _simulate(self):
        self._running = True
        while self._running:
            # Simulate plausible temperature and gravity changes
            self.temp += random.uniform(-0.1, 0.1)
            self.grav += random.uniform(-0.0005, 0.0005)
            time.sleep(5)

    def stop(self):
        self._running = False

class Sysinfo:
    def __init__(self):
        pass

    def get_cpu_temp(self):
        # Simulate CPU temp between 40 and 60 C
        return random.uniform(40, 60)

class Stirrer:
    def __init__(self, pwm_pin, sd_pin):
        self.pwm_pin = pwm_pin
        self.sd_pin = sd_pin
        self.duty = 0
        self.freq = 15000
        self.rampLock = False
        self.running = False

    def ramp(self, duty):
        if duty > 100:
            duty = 100
        if self.rampLock:
            return
        self.rampLock = True
        direct = 1 if (duty > self.duty) else -1
        while (duty - self.duty) * direct >= 0:
            self.duty = self.duty + direct * 2
            if self.duty > 0:
                self.running = True
            else:
                self.running = False
            time.sleep(0.1)
            if self.duty == duty:
                break
        self.rampLock = False

    def start(self, duty):
        if duty > 100:
            duty = 100
        if duty < 0:
            duty = 0
        threading.Thread(target=self.ramp, args=(duty,), daemon=True).start()

    def stop(self):
        threading.Thread(target=self.ramp, args=(0,), daemon=True).start()

    def play(self, tune):
        # Simulate playing a tune (do nothing)
        pass

    def isRunning(self):
        return self.duty > 0

class Relay_ctrl:
    def __init__(self, comm, pid, sensor, gpioH, gpioC, period=3600):
        self.setPoint = 50
        self.gpioH = gpioH
        self.gpioC = gpioC
        self.tmp = 0
        self.period = period
        self.sensor = sensor
        self.pid = pid
        self.ctlOn = False
        self.event = threading.Event()
        self.comm = comm
        self.heater_state = False
        self.cooler_state = False

    def run(self):
        self.ctlOn = True
        while True:
            self.event.clear()
            while self.ctlOn == False:
                self.event.wait()
            if self.pid.getCtlSig() != 0:
                if self.pid.getCtlSig() > 0:
                    self.heater_state = True
                    self.cooler_state = False
                else:
                    self.heater_state = False
                    self.cooler_state = True
                self.comm.update()
                self.onDelay = abs(self.pid.getCtlSig()) / 100. * self.period
                self.offDelay = self.period - self.onDelay
                if self.onDelay < self.period:
                    self.event.wait(self.onDelay)
                else:
                    self.onDelay = self.period
                    self.event.wait(self.period)
                    continue
            else:
                self.heater_state = False
                self.cooler_state = False
                self.comm.update()
                self.event.wait(self.period)
                continue
            self.heater_state = False
            self.cooler_state = False
            self.comm.update()
            self.event.wait(self.offDelay)

    def getPeriod(self):
        return self.period

    def setPeriod(self, period):
        self.period = period
        self.event.set()

    def stop(self):
        self.ctlOn = False
        self.event.set()

    def start(self):
        self.ctlOn = True
        self.event.set()

    def isRunning(self):
        return self.ctlOn

    def coolerOn(self):
        self.cooler_state = True

    def coolerOff(self):
        self.cooler_state = False

    def heaterOn(self):
        self.heater_state = True

    def heaterOff(self):
        self.heater_state = False

    def allOff(self):
        self.heater_state = False
        self.cooler_state = False

    def coolerIsOn(self):
        return self.cooler_state

    def heaterIsOn(self):
        return self.heater_state
