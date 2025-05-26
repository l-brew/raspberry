
#!/usr/bin/env python3
import os

def is_raspberry_pi():
    try:
        with open('/proc/device-tree/model', 'r') as model_file:
            model = model_file.read()
            return 'Raspberry Pi' in model
    except Exception:
        return False

if not is_raspberry_pi():
    # Import simulated sensors and actuators
    from simulation.sim_sensors import PT100, Ntc, Tilt2, Sysinfo, Stirrer, Relay_ctrl
else:
    from sensors_actuators.pt100 import PT100
    from sensors_actuators.relay_ctrl import Relay_ctrl
    from sensors_actuators.stirrer import Stirrer
    from sensors_actuators.tilt2_bleak import Tilt2
    from sensors_actuators.ntc import Ntc
    from utils.sysinfo import Sysinfo


from controllers.pid import Pid
import time
import configparser
from utils.dataLogger import dataLogger
import threading
from datetime import datetime,timedelta
import logging
from comm_layer.comm_layer import Comm_layer
from comm_layer.http_comm import http_comm
from comm_layer.socket_comm import Socket_comm
from comm_layer.web.comm_layer_web import create_app
from comm_layer.terminal.comm_layer_terminal import CommLayerTerminalServer
from controllers import two_point_control

class start:

    def __init__(self):
        pass
        self.comm=Comm_layer(self)
        self.cfgName = "config/temp_reg.config"
        self.dataName = "data/data.csv"
        self.config = configparser.ConfigParser()
        self.config['Controller']={}
        self.config['Server']={}
        self.config.read(self.cfgName)
        self.ctlConfig=self.config['Controller']
        self.serverConfig=self.config['Server']

        self.sysinfo = Sysinfo()

        self.logfile =self.dataName
        self.fh=open(self.logfile, "a+")

        #self.logger=dataLogger(self.dataName)

        self.stirrer1 = Stirrer(13,26)

        self.t1 = PT100()
        self.t1.update()

        threading.Thread(target=self.t1.run, daemon=True).start()



        self.ntc1 = Ntc('P9_39',beta=3889)
        self.ntc2 = Ntc('P9_37')
        controller_type = self.ctlConfig.get("type","pid")
        if controller_type  == "pid":
            self.pid1=Pid()
            self.pid1.setSetPoint(float(self.ctlConfig.get("SetPoint","20")))
            self.pid1.setK_p(float(self.ctlConfig.get("K_p","6")))
            self.pid1.setK_i(float(self.ctlConfig.get("K_i","0.01")))
            self.pid1.setI_sat_p(float(self.ctlConfig.get("I_sat_p","60")))
            self.pid1.setI_sat_n(float(self.ctlConfig.get("I_sat_n","-60")))
        elif controller_type == "twopoint":
            self.pid1=two_point_control.Two_point(
                  setPoint   = float(self.ctlConfig.get("SetPoint","20"))
                , dead_time  = float(self.ctlConfig.get("dead_time","600"))
                , hysteresis = float(self.ctlConfig.get("hysteresis","1"))
            )
        else:
            raise Exception("Wrong controller Type: "+str(self.ctlConfig.get("type")) )

        self.ramp=float(self.ctlConfig.get("Ramp","0"))
        self.setPoint=self.pid1.getSetPoint()


        self.ctl1 = Relay_ctrl(self.comm,self.pid1,self.t1,self.ctlConfig.get("HeaterPort",16),
             self.ctlConfig.get("CoolerPort",17),float(self.ctlConfig.get("CtlPeriod","3600")))
        

        self.tilt = Tilt2()
        self.tilt.connect()
        
        self.http1= http_comm(self.serverConfig,self.comm)
        self.http1.run()
        
        self.socket_comm = Socket_comm(self.comm)
        threading.Thread(target=self.socket_comm.run,daemon=True).start()
        
        # Start the terminal server in a background thread
        self.terminal_server = CommLayerTerminalServer(self.comm)
        threading.Thread(target=self.terminal_server.start, daemon=True).start()
        print("Terminal server started. Connect via socket to interact with the system.")

        # Start the Flask web interface in a background thread
        self.flask_app = create_app(self.comm)
        def run_web_interface():
            self.flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        threading.Thread(target=run_web_interface, daemon=True).start()
        print("Web interface started. Connect to http://localhost:8080 to interact with the system.")

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
        threading.Thread(target=self.ctl1.run, daemon=True).start()
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
    logging.debug('Start System')
    s=start()
    s.mainLoop()

if __name__=="__main__":
    import utils.dbg
    from os import path
    if path.exists("/tmp/brewdbg"): 
        utils.dbg.debug()
    main()
