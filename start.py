#!/usr/bin/env python3
import pt100 
from relay_ctrl import relay_ctrl
from pid import pid
import time
from http_comm import http_comm 
import configparser
from dataLogger import dataLogger
from stirrer import stirrer
import tilt2_client
import ntc
import sysinfo
import threading
from datetime import datetime,timedelta
import logging
import comm_layer
import socket_comm

class start:

    def __init__(self):
        pass
        self.comm=comm_layer.Comm_layer(self)
        self.cfgName = "temp_reg.config"
        self.dataName = "data.csv"
        self.config = configparser.ConfigParser()
        self.config['Controller']={}
        self.config['Server']={}
        self.config.read(self.cfgName)
        self.ctlConfig=self.config['Controller']
        self.serverConfig=self.config['Server']

        self.sysinfo = sysinfo.Sysinfo()

        self.logfile =self.dataName
        self.fh=open(self.logfile, "a+")

        #self.logger=dataLogger(self.dataName)

        self.stirrer1 = stirrer(13,26)

        self.t1 = pt100.PT100()
        self.t1.update()

        threading.Thread(target=self.t1.run).start()



        self.ntc1 = ntc.Ntc('P9_39',beta=3889)
        self.ntc2 = ntc.Ntc('P9_37')

        self.pid1=pid()
        self.pid1.setSetPoint(float(self.ctlConfig.get("SetPoint","20")))
        self.pid1.setK_p(float(self.ctlConfig.get("K_p","6")))
        self.pid1.setK_i(float(self.ctlConfig.get("K_i","0.01")))
        self.pid1.setI_sat_p(float(self.ctlConfig.get("I_sat_p","60")))
        self.pid1.setI_sat_n(float(self.ctlConfig.get("I_sat_n","-60")))

        self.ramp=float(self.ctlConfig.get("Ramp","0"))
        self.setPoint=self.pid1.getSetPoint()


        self.ctl1 = relay_ctrl(self.comm,self.pid1,self.t1,self.ctlConfig.get("HeaterPort",16),
             self.ctlConfig.get("CoolerPort",17),float(self.ctlConfig.get("CtlPeriod","10")))
        

        self.tilt = tilt2_client.Tilt2()
        self.tilt.connect()
        
        self.http1= http_comm(self.serverConfig,self.comm)

  
        self.http1.run()
        
        self.socket_comm = socket_comm.Socket_comm(self.comm)
        threading.Thread(target=self.socket_comm.run,daemon=True).start()
        

    def writeConfig(self):
        with open(self.cfgName,"w") as cfgFile:
            self.config.write(cfgFile)
            cfgFile.close()

    def getServer(self):
        return self.http1

    def getRamp(self):
        return self.ramp

    def setRamp(self,ramp):
        self.ramp=ramp

    def getSetPoint(self):
        return self.setPoint

    def setSetPoint(self,setPoint):
        self.setPoint=setPoint

    def getCtlConfig(self):
        return self.ctlConfig

    def getServerConfig(self):
        return self.serverConfig

    def getLogfile(self):
        return self.logfile

    def getTarget(self):
        return self.setPoint

    def mainLoop(self):
        last_time=datetime.today()
        threading.Thread(target=self.ctl1.run).start()
        ramping=False
        while True:
            delta_t = (datetime.today()-last_time)/timedelta(milliseconds=1)/1000.
            last_time=datetime.today()
            if(self.ramp != 0):
                if(self.pid1.getSetPoint()==self.setPoint):
                    pass
                else:
                    if(abs(self.pid1.getSetPoint() - self.setPoint)) <= (self.ramp/60.):
                        self.pid1.setSetPoint(self.setPoint)
                        #self.stirrer1.play([[2000,1],[0,1],[2000,1],[0,1],[2000,1],[0,0]])
                    elif(self.pid1.getSetPoint() < self.setPoint ) :
                        self.pid1.setSetPoint(self.pid1.getSetPoint()+(self.ramp/60.*delta_t))
                    elif(self.pid1.getSetPoint() > self.setPoint ) :
                        self.pid1.setSetPoint(self.pid1.getSetPoint()-self.ramp/60.*delta_t)
            else:
                self.pid1.setSetPoint(self.setPoint)


            self.ntc1.update()
            self.ntc2.update()
            if self.ctl1.isRunning():
                self.pid1.calculate(self.t1.getVal())
            self.comm.update()
            time.sleep(1)
            # self.fh.write("%s;%2.2f;%2.2f;%2.2f;%3.2f\n"%
           # self.logger.add([round(time.time(),2),
            #round(self.pid1.getCtlSig(),2),round(self.pid1.getCtlSig(),2),round(self.t1.getVal(),2),round(self.t1.getVal(),2)])


def main():
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='brew.log',
                        level=logging.DEBUG,datefmt='%d.%m.%Y %H:%M:%S')
    logging.debug('Start')
    s=start()
    s.mainLoop()

if __name__=="__main__":
    import dbg
    from os import path
    if path.exists("/tmp/brewdbg"):
        dbg.debug()
    main()