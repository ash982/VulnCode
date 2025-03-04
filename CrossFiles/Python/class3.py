import subprocess
import shlex
import re

class Class3:
    def __init__(self, input_data):
        self.input = input_data

    def process_dangersous1(self):
        print(f"Class3 processing: {self.input}")
        # Potentially unsafe operation
        p = subprocess.Popen(self.input, shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
        
    def process_dangersous2(self):
        print(f"Class3 processing: {self.input}")
        # Potentially unsafe operation
        cmd = shlex.quote(self.input)
        p = subprocess.Popen(cmd, shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
        
    def process_dangersous3(self):
        print(f"Class3 processing: {self.input}")
        # Potentially unsafe operation
        arg = self.input
        cmd = f"ls {arg}"
        p = subprocess.Popen(cmd, shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    
    def process_safe1(self):
        print(f"Class3 processing: {self.input}")
        # Potentially unsafe operation
        cmd = shlex.quote(self.input)
        p = subprocess.Popen(cmd, shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
        
    def process_safe2(self):
        print(f"Class3 processing: {self.input}")
        # Potentially unsafe operation
        cmd = self.input
        pattern = r"^ls\s+=\w+$"
        if re.match(pattern, cmd):
            p = subprocess.Popen(cmd, shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)   
            print("safe ls command")
        else:
            print("dangerous!")         