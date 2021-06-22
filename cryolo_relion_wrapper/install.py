#!/usr/bin/env python

import os,shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-rpath",help='Path to relion installation base folder (up to, but not including, the bin/ folder with the "relion" executable)',required=True)
parser.add_argument("-cpath",help='Path to the crYOLO conda environment (ex: /home/luger-software/programs/cryolo/anaconda3/envs/cryolo/)',required=True)
args = parser.parse_args()

base_wrapper    = open("janni_cryolo_relion_wrapper.py",'r')
install_wrapper = open(os.path.join(args.rpath,"bin/janni_cryolo_relion_wrapper.py"),'w')
base_wrapper_lines = base_wrapper.lines()

for LINE in base_wrapper_lines:
  if "CRYOLO_INSTALL_PATH" in LINE:
    LINE = LINE.replace("CRYOLO_INSTALL_PATH",args.cpath)
  install_wrapper.write(LINE)
base_wrapper.close()
install_wrapper.close()

shutil.copyfile("cryolo_wrapper_library.py",os.path.join(args.rpath,"bin/cryolo_wrapper_library.py"))

print("Installation is complete!")
