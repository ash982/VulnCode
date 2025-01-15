import os

class Class1:
    def __init__(self, input_data):
        self.input = input_data

    def process(self):
        print(f"Class1 processing: {self.input}")
        # Potentially unsafe operation
        os.system(f"echo {self.input}")
