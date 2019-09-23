import os
os.system("sudo pip3 install -e /home/jdw/projects/sugarrush/code")

from sugarrush.examples.langford import run_langford

run_langford(24)