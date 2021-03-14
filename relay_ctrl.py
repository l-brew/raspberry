import threading
import pid
from gpiozero import LED
import sensor

class relay_ctrl():

    def __init__(self,pid,sensor,gpioH,gpioC,period=10):
        self.setPoint=50
        self.gpioH=gpioH
        self.gpioC=gpioC
        self.tmp=0
        self.period=period
        self.gpio_h=LED(self.gpioH)
        self.gpio_c=LED(self.gpioC)
        self.sensor=sensor
        self.pid=pid
        self.ctlOn=False

    def setServer(self,server):
        self.server=server

    def on(self):
        if self.ctlOn==False:
            return
        # perf=timer.perf_counter()

        if(self.pid.getCtlSig()!=0):
            if self.pid.getCtlSig() > 0 :
                self.gpio_h.on()
                self.gpio_c.off()
            else:
                self.gpio_h.off()
                self.gpio_c.on()
            self.onDelay=abs(self.pid.getCtlSig())/100.*self.period
            self.offDelay=self.period-self.onDelay
            if (self.onDelay< self.period):
                self.timer = threading.Timer(self.onDelay, self.off) 
                self.timer.start()
            else :
                self.onDelay=self.period
                self.timer = threading.Timer(self.period, self.on)
                self.timer.start()
        else:
            self.gpio_h.off()
            self.gpio_c.off()
            self.timer = threading.Timer(self.period, self.on)
            self.timer.start()
        self.server.update()

    def off(self):
        if self.ctlOn==False:
            return
        self.gpio_h.off()
        self.gpio_c.off()
        self.timer = threading.Timer(self.offDelay, self.on)
        self.timer.start()
        self.server.update()

        # self.ctlSig


    def run(self):
        if self.ctlOn==False:
            self.ctlOn=True
            self.on()

    def getPeriod(self):
        return self.period

    def setPeriod(self, period):
        self.period=period 


    def stop(self):
        self.timer.cancel()
        self.ctlOn=False

    def isRunning(self):
        return self.ctlOn

    def coolerOn(self):
        self.gpio_c.on()

    def coolerOff(self):
        self.gpio_c.off()

    def heaterOn(self):
        self.gpio_h.on()

    def heaterOff(self):
        self.gpio_h.off()

    def allOff(self):
        self.gpio_h.off()
        self.gpio_c.off()

    def coolerIsOn(self):
        return self.gpio_c.is_lit

    def heaterIsOn(self):
        return self.gpio_h.is_lit
