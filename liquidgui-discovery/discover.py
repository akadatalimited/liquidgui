#!/usr/bin/env python3 
  
from tkinter import *


def read_line(s):  
    p = Path('/dev/input/event18', '/sys/class/hwmon/hwmon9')
