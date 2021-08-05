#!/usr/bin/env python

from star_library import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-istar",help="Input STAR file (from relion3.1) that you want converted to relion3.0-compliance",required=True)
parser.add_argument("-ostar",help="Output STAR file in relion3.0-compliant format (Default = \"relion30_format.star\")")
args = parser.parse_args()

r31 = STARFILE(fname=args.istar)

r31.ConvertToRelion3_0()
r31.WriteStarFile(args.ostar,relion3_0_format=True)
