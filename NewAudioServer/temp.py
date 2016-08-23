from dateutil import parser as time_parser
from datetime import datetime
import time
a=datetime.now()
time.sleep(1)
b=datetime.now()

d=b-a

d.seconds

dt = time_parser.parse('2016-06-19 13:44:57.978000')

d.seconds
