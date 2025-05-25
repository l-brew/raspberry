#!/usr/bin/env python3
import sys
import time
import threading
import configparser
from datetime import datetime, timedelta
import logging

from pid import pid
from http_comm import http_comm
import comm_layer
import socket_comm
import two_point_control
from web.comm_layer_web import create_app

# Import simulated sensors and actuators
from simulation.sim_sensors import SimPT100, SimNtc, SimTilt2, SimSysinfo, SimStirrer, SimRelayCtrl

# Import the terminal server
from terminal.comm_layer_terminal import CommLayerTerminalServer

class start_simulation:

    def __init__(self):
        self.comm = comm_layer.Comm_layer(self)
        self.cfgName = "temp_reg.config"
        self.dataName = "data.csv"
        self.config = configparser.ConfigParser()
        self.config['Controller'] = {}
        self.config['Server'] = {}
        self.config.read(self.cfgName)
        self.ctlConfig = self.config['Controller']
        self.serverConfig = self.config['Server']

        self.sysinfo = SimSysinfo()

        self.logfile = self.dataName
        self.fh = open(self.logfile, "a+")

        self.stirrer1 = SimStirrer(13, 26)

        self.t1 = SimPT100()
        self.t1.update()
        threading.Thread(target=self.t1.run, daemon=True).start()

        self.ntc1 = SimNtc('P9_39', beta=3889)
        self.ntc2 = SimNtc('P9_37')
        controller_type = self.ctlConfig.get("type", "pid")
        if controller_type == "pid":
            self.pid1 = pid()
            self.pid1.setSetPoint(float(self.ctlConfig.get("SetPoint", "20")))
            self.pid1.setK_p(float(self.ctlConfig.get("K_p", "6")))
            self.pid1.setK_i(float(self.ctlConfig.get("K_i", "0.01")))
            self.pid1.setI_sat_p(float(self.ctlConfig.get("I_sat_p", "60")))
            self.pid1.setI_sat_n(float(self.ctlConfig.get("I_sat_n", "-60")))
        elif controller_type == "twopoint":
            self.pid1 = two_point_control.Two_point(
                setPoint=float(self.ctlConfig.get("SetPoint", "20")),
                dead_time=float(self.ctlConfig.get("dead_time", "600")),
                hysteresis=float(self.ctlConfig.get("hysteresis", "1"))
            )
        else:
            raise Exception("Wrong controller Type: " + str(self.ctlConfig.get("type")))

        self.ramp = float(self.ctlConfig.get("Ramp", "0"))
        self.setPoint = self.pid1.getSetPoint()

        self.ctl1 = SimRelayCtrl(self.comm, self.pid1, self.t1, self.ctlConfig.get("HeaterPort", 16),
                                 self.ctlConfig.get("CoolerPort", 17), float(self.ctlConfig.get("CtlPeriod", "3600")))

        self.tilt = SimTilt2()
        self.tilt.connect()

        self.http1 = http_comm(self.serverConfig, self.comm)
        self.http1.run()

        self.socket_comm = socket_comm.Socket_comm(self.comm)
        threading.Thread(target=self.socket_comm.run, daemon=True).start()

        # Start the terminal server in a background thread
        self.terminal_server = CommLayerTerminalServer(self.comm)
        threading.Thread(target=self.terminal_server.start, daemon=True).start()
        print("Terminal server started. Connect via socket to interact with the simulation.")
        
        # Start the Flask web interface in a background thread
        self.flask_app = create_app(self.comm)
        def run_web_interface():
            self.flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        threading.Thread(target=run_web_interface, daemon=True).start()
        print("Web interface started. Connect to http://localhost:8080 to interact with the simulation.")

    def writeConfig(self):
        with open(self.cfgName, "w") as cfgFile:
            self.config.write(cfgFile)
            cfgFile.close()

    def getServer(self):
        return self.http1

    def getRamp(self):
        return self.ramp

    def setRamp(self, ramp):
        self.ramp = ramp

    def getSetPoint(self):
        return self.setPoint

    def setSetPoint(self, setPoint):
        self.setPoint = setPoint

    def getCtlConfig(self):
        return self.ctlConfig

    def getServerConfig(self):
        return self.serverConfig

    def getLogfile(self):
        return self.logfile

    def getTarget(self):
        return self.setPoint

    def mainLoop(self):
        last_time = datetime.today()
        threading.Thread(target=self.ctl1.run, daemon=True).start()
        while True:
            delta_t = (datetime.today() - last_time) / timedelta(milliseconds=1) / 1000.
            last_time = datetime.today()
            if self.ramp != 0:
                if self.pid1.getSetPoint() == self.setPoint:
                    pass
                else:
                    if abs(self.pid1.getSetPoint() - self.setPoint) <= (self.ramp / 60.):
                        self.pid1.setSetPoint(self.setPoint)
                    elif self.pid1.getSetPoint() < self.setPoint:
                        self.pid1.setSetPoint(self.pid1.getSetPoint() + (self.ramp / 60. * delta_t))
                    elif self.pid1.getSetPoint() > self.setPoint:
                        self.pid1.setSetPoint(self.pid1.getSetPoint() - self.ramp / 60. * delta_t)
            else:
                self.pid1.setSetPoint(self.setPoint)

            self.ntc1.update()
            self.ntc2.update()
            if self.ctl1.isRunning():
                self.pid1.calculate(self.t1.getVal())
            self.comm.update()
            time.sleep(1)

def main():
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='brew_sim.log',
                        level=logging.DEBUG, datefmt='%d.%m.%Y %H:%M:%S')
    logging.debug('Start Simulation')
    s = start_simulation()
    s.mainLoop()

if __name__ == "__main__":
    import dbg
    from os import path
    if path.exists("/tmp/brewdbg"):
        dbg.debug()
    main()
