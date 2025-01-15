import sys
from class1 import Class1
from class2 import Class2

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input>")
        return

    tainted_input = sys.argv[1]

    obj1 = Class1(tainted_input)
    obj2 = Class2(tainted_input)

    obj1.process()
    obj2.process()

if __name__ == "__main__":
    main()

