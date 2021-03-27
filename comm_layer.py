import traceback
import time

class Comm_layer:
    def __init__(self,start):
        self.start=start
        pass

    def command(self,cmd):
        writeConfig=False
        if "ramp" in cmd.keys():
            self.start.setRamp(float(cmd["ramp"]))
            writeConfig=True
        if "soll" in cmd.keys():
            self.start.setSetPoint(float(cmd["soll"]))
            writeConfig=True
        if "k_p" in cmd.keys():
            self.start.pid1.setK_p(float(cmd["k_p"]))
            writeConfig=True
        if "k_i" in cmd.keys():
            self.start.pid1.setK_i(float(cmd["k_i"]))
            writeConfig=True
        if "freeze" in cmd.keys():
            if cmd["freeze"] == "true":
                self.start.pid1.freeze()
            if cmd["freeze"] == "false":
                self.start.pid1.unfreeze()
        if "i_err" in cmd.keys():
            self.start.pid1.setI_err(float(cmd["i_err"]))
        if "period" in cmd.keys():
            self.start.ctl1.setPeriod(float(cmd["period"]))
        if "reg" in cmd.keys():
            if cmd["reg"] == "on" :
                self.start.ctl1.start()
            elif cmd["reg"] == "off" :
                self.start.ctl1.stop()
                self.start.ctl1.allOff()
        if "cooler" in cmd.keys():
            if cmd["cooler"] == "on" :
                self.start.ctl1.stop()
                self.start.ctl1.coolerOn()
            if cmd["cooler"] == "tgl" :
                self.start.ctl1.stop()
                if self.start.ctl1.coolerIsOn():
                    self.start.ctl1.coolerOff()
                else:
                    self.start.ctl1.coolerOn()
            elif cmd["cooler"] == "off" :
                self.start.ctl1.coolerOff()
        if "heater" in cmd.keys():
            if cmd["heater"] == "on" :
                self.start.ctl1.stop()
                self.start.ctl1.heaterOn()
            if cmd["heater"] == "tgl" :
                self.start.ctl1.stop()
                if self.start.ctl1.heaterIsOn():
                    self.start.ctl1.heaterOff()
                else:
                    self.start.ctl1.heaterOn()
            elif cmd["heater"] == "off" :
                self.start.ctl1.heaterOff()
        if "stirrer" in cmd.keys():
            
            if cmd["stirrer"] == "off" :
                self.start.stirrer1.stop()
            else:
                try:
                    self.start.stirrer1.start(float(cmd["stirrer"]))
                except :
                    print(traceback.cmdat_exc())
                    pass
        if "rampUp" in cmd.keys():
            self.start.pid1.setSetPoint(self.start.t1.getVal())
            self.start.ctl1.run()

        if "reset" in cmd.keys():
            if cmd["reset"] == "true" :
                self.start.pid1.setI_err(0)
        if "setI" in cmd.keys():
            self.start.pid1.setI_err(float(cmd["setI"])/self.start.pid1.getK_i())
        if "rampup2" in cmd.keys():
            # ramp up to value in specified time
            minutes=float(cmd["rampup2"]["minutes"])
            temp=float(cmd["rampup2"]["temp"])
            cur_val=self.start.pid1.getSetPoint()
            if cur_val != temp:
                if minutes== 0 :
                    self.start.setRamp(0)
                    self.start.setSetPoint(temp)
                    self.start.pid1.setSetPoint(temp)
                else:
                    ramp=abs(temp-cur_val)/minutes
                    self.start.setRamp(ramp)
                    self.start.setSetPoint(temp)

        if writeConfig :
            self.start.getCtlConfig()["SetPoint"]=str(self.start.getSetPoint())
            self.start.getCtlConfig()["K_p"]=str(self.start.pid1.getK_p())
            self.start.getCtlConfig()["K_i"]=str(self.start.pid1.getK_i())
            self.start.writeConfig()


    def get_status_dict(self):
        power = self.start.pid1.getCtlSig()
        if power > 100:
            power = 100
        elif power < -100:
            power = -100

        data = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),
            'temp': self.start.t1.getVal(),
            'set_point': self.start.pid1.getSetPoint(),
            'k_i': self.start.pid1.getK_i(),
            'k_p': self.start.pid1.getK_p(),
            'actuating_value' : self.start.pid1.getCtlSig(),
            'err' :self.start.pid1.getErr()*self.start.pid1.getK_p(),
            'i_err' : self.start.pid1.getI_err()*self.start.pid1.getK_i(),
            'heater' :self.start.ctl1.heaterIsOn(),
            'cooler' :self.start.ctl1.coolerIsOn(),
            'stirrer' :self.start.stirrer1.isRunning(),
            'power' :power,
            'reg' :self.start.ctl1.isRunning(),
            'ramp' :self.start.getRamp(),
            'target' :self.start.getTarget(),
            'period' :self.start.ctl1.getPeriod(),
            'frozen' :self.start.pid1.getFrozen(),
            'tilt_temp' : self.start.tilt.temp,
            'tilt_grav' : self.start.tilt.grav,
            'ntc1':self.start.sysinfo.get_cpu_temp(),
            'ntc2': self.start.ntc2.getVal()
                }

        return data


    def update(self):
        self.start.http1.update()
        self.start.socket_comm.update(self.get_status_dict())
