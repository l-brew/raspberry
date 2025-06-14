import threading
from gpiozero import LED


class Relay_ctrl():

    def __init__(self,comm,pid,sensor,gpioH,gpioC,period=3600):
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
        self.event=threading.Event()
        self.comm=comm

    
    def run(self):
        self.ctlOn=True
        while True:
            self.event.clear()
            while self.ctlOn==False:
                self.event.wait()

            if(self.pid.getCtlSig()!=0):
                if self.pid.getCtlSig() > 0 :
                    self.gpio_h.on()
                    self.gpio_c.off()
                    self.comm.update()
                else:
                    self.gpio_h.off()
                    self.gpio_c.on()
                    self.comm.update()
                self.onDelay=abs(self.pid.getCtlSig())/100.*self.period
                self.offDelay=self.period-self.onDelay
                if (self.onDelay< self.period):
                    self.event.wait(self.onDelay)
                else :
                    self.onDelay=self.period
                    self.event.wait(self.period)
                    continue
            else:
                self.gpio_h.off()
                self.gpio_c.off()
                self.comm.update()
                self.event.wait(self.period)
                continue

            self.gpio_h.off()
            self.gpio_c.off()
            self.comm.update()
            self.event.wait(self.offDelay)

        # self.ctlSig



    def getPeriod(self):
        return self.period

    def setPeriod(self, period):
        self.period=period 
        self.event.set()


    def stop(self):
        self.ctlOn=False
        self.event.set()

    def start(self):
        self.ctlOn=True
        self.event.set()

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
