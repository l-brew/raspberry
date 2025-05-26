from enum import Enum,auto
import time 

class Two_point_state(Enum):
    IDLE = auto()
    HEATING = auto()
    COOLING = auto()

class Two_point:
    def __init__(self,setPoint=20.,hysteresis = 1 , dead_time = 600):
        self.setPoint= setPoint
        self.ctlSig=0.
        self.frozen=False
        self.hysteresis = hysteresis
        self.state = Two_point_state.IDLE
        self.dead_time = dead_time
        self.dead_time_counter = 0
        self.err = 0 
        self.old_state = self.state

    def calculate(self,actVal):
        if actVal is None:
            return
        if self.frozen:
            self.ctlSig=self.setPoint
            return self.ctlSig
        

        if (time.perf_counter() - self.dead_time_counter) >= self.dead_time:
            # calculate error
            self.err=self.setPoint-actVal

            if -self.err >= self.hysteresis/2:
                self.state = Two_point_state.COOLING
            if self.err >= self.hysteresis/2:
                self.state = Two_point_state.HEATING


        if self.old_state != self.state :
            self.dead_time = time.perf_counter()
            self.old_state = self.state
        if self.state == Two_point_state.COOLING:
            self.ctlSig = -100
        elif self.state == Two_point_state.HEATING:
            self.ctlSig = 100
        else:
            self.ctlSig = 0
        return self.ctlSig

    def setSetPoint(self,setPoint):
        self.setPoint=setPoint

    def getSetPoint(self):
        return self.setPoint

    def getErr(self):
        return self.err

    def setErr(self,err):
        self.err=err

    def getI_err(self):
        return 0

    def setI_err(self,i_err):
        ...

    def getK_p (self):
        return 0

    def setK_p (self,k_p ):
        ...

    def getK_i (self):
        return 0

    def setK_i (self,k_i ):
        ...

    def getI_sat_p (self):
        return 0

    def setI_sat_p (self,i_sat_p ):
        ...

    def getI_sat_n (self):
        return 0

    def setI_sat_n (self,i_sat_n ):
        ...

    def getCtlSig(self):
        return self.ctlSig

    def setCtlSig(self,ctlSig):
        self.ctlSig=ctlSig

    def freeze(self):
        self.frozen=True

    def unfreeze(self):
        self.frozen=False

    def getFrozen(self):
        return self.frozen
