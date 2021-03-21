class Comm_layer:
    def __init__(self):
        pass

    def command(self,cmd):
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
                    self.start.pid1.setI_err(float(cmd["i_err"])/getK_i())
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
                    print("ramp Up")
                    self.start.pid1.setSetPoint(self.start.t1.getVal())
                    self.start.ctl1.run()

                if "reset" in cmd.keys():
                    if cmd["reset"] == "true" :
                       self.start.pid1.setI_err(0)
                if "setI" in cmd.keys():
                   self.start.pid1.setI_err(float(cmd["setI"])/self.start.pid1.getK_i())
                if "plotMinutes" in cmd.keys():
                        regler.plotSeconds
                if "rampup2" in cmd.keys():
                    # ramp up to value in specified time
                    minutes=float(cmd["rampup2"]["minutes"])
                    temp=float(cmd["rampup2"]["temp"])
                    cur_val=self.start.pid1.getSetPoint()
                    print(minutes,temp)
                    if cur_val != temp:
                        if minutes== 0 :
                            self.start.setRamp(0)
                            self.start.setSetPoint(temp)
                            self.start.pid1.setSetPoint(temp)
                        else:
                            ramp=abs(temp-cur_val)/minutes
                            self.start.setRamp(ramp)
                            self.start.setSetPoint(temp)
