#!/usr/bin/env python

import numpy as np
import os,argparse
import glob

def read_star_by_line(STARFILE,MRCFILE,OFILE):
    this_file = open(STARFILE,'r')
    these_lines=this_file.readlines()
    for line in these_lines:
        #For lines that don't begin with the "new line" character
        if len(line) > 1:
            this_line = line.split()
            if not this_line[0][0].isnumeric():
                continue
            else:
                this_x = this_line[0]
                this_y = this_line[1]
                ofile.write(this_x+'\t'+this_y+'\t')
                ofile.write(MRCFILE+'\n')
        #If line begins with "newline" character                
        else:
            continue


#Command Line Options
parser = argparse.ArgumentParser()
parser.add_argument("-sf",help='Full path to the folder containing the .star files that will be imported to cryosparc',required=True)
parser.add_argument("-mf",help='Full path to folder containing micrographs to which the .star files should be linked',required=True)
parser.add_argument("-o",help='Path & name for the output (combined) .star file for importing to cryosparc')
args = parser.parse_args()

#Get list of star files before we generate the new star file
star_list = glob.glob(os.path.join(args.sf,"*.star"))

#Write header information for concatenated .star file
ofile = open(args.o,'w')
ofile.write("\ndata_\n\nloop_\n_rlnCoordinateX #1\n_rlnCoordinateY #2\n_rlnMicrographName #3\n")

#Add an MRC file to each star's particle line
for STARFILE in star_list:
    STARBASE = os.path.split(STARFILE)[1]
    MRCBASE  = STARBASE[:-5] +".mrc"
    MRCFULL  = os.path.join(args.mf,MRCBASE)
    read_star_by_line(STARFILE,MRCFULL,ofile)

#Close and write the new .star file
ofile.close()
