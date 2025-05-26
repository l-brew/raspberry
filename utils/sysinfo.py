import subprocess
import re

class Sysinfo:
    def __init__(self):
        self.cpu_temp_regex = re.compile(r'temp1:.*')


    def get_cpu_temp(self):
        proc=subprocess.run(['/usr/bin/sensors'], capture_output=True)
        line = self.cpu_temp_regex.search(proc.stdout.decode('utf_8'))[0]
        temp= float(re.sub(r'temp1:.*\+(.*)°C',r'\1',line))
        return temp

if __name__ == '__main__':
    sysinfo=Sysinfo()

    sysinfo.get_cpu_temp()