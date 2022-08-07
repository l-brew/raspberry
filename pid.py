from dataset import *


class pid:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self.err = 0
        self.update_local_variables(create=True)
        self.ctlSig = 0.
        self.frozen = False

    def update_local_variables(self, create=False):
        self.k_p = self.dataset.get_value('k_p', create, float, 0)
        self.k_i = self.dataset.get_value('k_i', create, float, 0)
        self.i_sat_p = self.dataset.get_value('i_sat_p', create, float, 0)
        self.i_sat_n = self.dataset.get_value('i_sat_n', create, float, 0)
        self.setPoint = self.dataset.get_value('setPoint', create, float, 0)
        self.i_err = self.dataset.get_value('i_err', create, float, 0)

    def update_dataset(self, create=False):
        self.dataset.update_if_unchanged('i_err', self.i_err)

    def calculate(self, actVal):
        self.update_local_variables()
        if actVal is None:
            return
        if self.frozen:
            self.ctlSig = self.setPoint
            return self.ctlSig
        # calculate error
        self.err = self.setPoint-actVal
        # integrate
        self.i_err = self.i_err + self.err
        # saturate integrator
        if self.i_err * self.k_i > self.i_sat_p:
            self.i_err = self.i_sat_p/self.k_i
        elif self.i_err * self.k_i < self.i_sat_n:
            self.i_err = -self.i_sat_n / self.k_i

        self.ctlSig = self.err*self.k_p + self.i_err * self.k_i
        self.update_dataset()
        return self.ctlSig

    def setSetPoint(self, setPoint):
        self.setPoint = setPoint

    def getSetPoint(self):
        return self.setPoint

    def getErr(self):
        return self.err

    def setErr(self, err):
        self.err = err

    def getI_err(self):
        return self.i_err

    def setI_err(self, i_err):
        self.i_err = i_err

    def getK_p(self):
        return self.k_p

    def setK_p(self, k_p):
        self.k_p = k_p

    def getK_i(self):
        return self.k_i

    def setK_i(self, k_i):
        self.k_i = k_i

    def getI_sat_p(self):
        return self.i_sat_p

    def setI_sat_p(self, i_sat_p):
        self.i_sat_p = i_sat_p

    def getI_sat_n(self):
        return self.i_sat_n

    def setI_sat_n(self, i_sat_n):
        self.i_sat_n = i_sat_n

    def getCtlSig(self):
        return self.ctlSig

    def setCtlSig(self, ctlSig):
        self.ctlSig = ctlSig

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def getFrozen(self):
        return self.frozen
