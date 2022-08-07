import time
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap


import relay_ctrl

class Sim_Temp:
    __TIMESTEP = 0.1
    __TIME_SCALE = 1

    __WEIGHT = 1
    __INITIAL_TEMPERATURE_CELCIUS = 10
    __POWER_KW = 4
    __HEAT_LOSS_KW = 1

    __SPECIFIC_THERMAL_CAPACITY_KJ = 4.2

    __INITIAL_TEMPERATURE_KELVIN = __INITIAL_TEMPERATURE_CELCIUS + 273.15
    __THERMAL_CAPACITY_J = __SPECIFIC_THERMAL_CAPACITY_KJ*1000 * __WEIGHT
    __POWER_W = __POWER_KW *  1000
    __HEAT_LOSS_W = __HEAT_LOSS_KW * 1000

    def __init__(self) -> None:
        self.val=self.__INITIAL_TEMPERATURE_CELCIUS
        self.heat_amount = self.__INITIAL_TEMPERATURE_KELVIN * self.__THERMAL_CAPACITY_J 
        self.val = self.heat_amount / self.__THERMAL_CAPACITY_J
    
    def update(self):
        
        self.heat_amount += self.__POWER_W * self.__TIMESTEP *relay_ctrl.relay- self.__HEAT_LOSS_W * self.__TIMESTEP

        self.val = self.heat_amount / self.__THERMAL_CAPACITY_J - 273.15

    def run(self):
        while True:
            self.update()
            time.sleep(self.__TIMESTEP / self.__TIME_SCALE)

    def getVal(self):
        return self.val