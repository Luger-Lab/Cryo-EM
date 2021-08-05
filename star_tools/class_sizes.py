#!/usr/bin/env python

import argparse
import glob, math
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("-f",help='Single file for extracting class sizes',type=str,dest='f',default='')
parser.add_argument("--all",help='Plot class sizes vs iteration for all current "model.star" files. Overrides the "-f" option.',action='store_true',dest='all')
parser.add_argument("-o",help='Prefix for output files',type=str,dest='o',default='class_size_check')
parser.add_argument("--2d",help='Process 2D classes, instead of the default of 3D classes',action='store_true',dest='is2D')
parser.add_argument("--num",help='Print total particle number instead of class %% of total particles',action='store_true',dest='particle_count')
parser.add_argument("-ct_iter",help='If you continued this classification from a previous one, enter the initial continuation iteration (example: for files that look like "run_ct25_it0##_model.star", you would enter "25" for this value).',dest='ct_iter',default=0,type=str)
args = parser.parse_args()

if args.is2D:
    offset = 2
else:
    offset = 0

#In case someone throws in multiple spaces, "loop them out"
while "  " in str(args.ct_iter):
    args.ct_iter = args.ct_iter.replace("  "," ")

if " " in str(args.ct_iter):
    ct_split = np.array(args.ct_iter.split(" "),dtype=int)
else:
    ct_split = np.array(args.ct_iter,dtype=int)


if args.all:
    odata = args.o+"_class_sizes_per_iter.csv"
    ofile = open(odata,'w')
    header= False #Only write the header once
    filelist = glob.glob("*model.star")
    it_list = np.zeros(len(filelist),dtype=int)
    #Remove the multiple copies of the same it # as a result of ct option
    for FILEID in range(len(filelist)):
        FILE = filelist[FILEID]
        it_idx = FILE.split("_it")[1].split("_model")[0]
        it_list[FILEID] = it_idx

    sorted_idx = np.argsort(it_list)
    sorted_it  = it_list[sorted_idx]

    for idx in range(len(sorted_idx)):
        FILE = filelist[sorted_idx[idx]]
        
        if args.particle_count:
            DFILE= FILE.replace('model','data')
            if idx==0:
                particle_data = np.genfromtxt(DFILE,skip_header=27,delimiter='\t',dtype=str)
            else:
                particle_data = np.genfromtxt(DFILE,skip_header=30,delimiter='\t',dtype=str)
            total_num = len(particle_data)
        this_file = open(FILE,'r')
        these_lines = this_file.readlines()
        if header:
            ofile.write(str(sorted_it[idx])+",")
        for line_idx in range(len(these_lines)):
            LINE = these_lines[line_idx]
            if not header:
                if "_rlnNrClasses" in LINE:
                    while "  " in LINE:
                        LINE = LINE.replace("  "," ")
                    num_classes = int(LINE.split(" ")[1])
                    if not header:
                        ofile.write("Iteration,")
                        for idx in range(num_classes):
                            ofile.write("Class "+str(idx+1)+",")
                        ofile.write("\n")
                        header = True
                    ofile.write(str(sorted_it[idx])+",")
        
            if "_rlnOverallFourierCompleteness" in LINE:
                for class_idx in range(1,num_classes+1):
                    class_line = these_lines[line_idx+class_idx+offset]
                    while "  " in class_line:
                        class_line = class_line.replace("  "," ")
                    class_dist = float(class_line.split(" ")[1])
                    if args.particle_count:
                        class_dist = class_dist * total_num
                    ofile.write(str(class_dist)+",")
                ofile.write('\n')
                break
                
    ofile.close()

    plot_data = np.genfromtxt(odata,dtype=float,delimiter=',',skip_header=1)
    plt.figure(figsize=(7.,4.))
    for idx in range(num_classes):
        plt.plot(plot_data[:,0],plot_data[:,idx+1],label='Class '+str(idx+1))
    plt.xlabel('Iteration')
    plt.xlim(0,len(plot_data[:,0]))
    if args.particle_count:
        plt.ylabel('Class Size (# of particles)')
    else:
        plt.ylabel('Class Size (%)')
    if not args.is2D:
        plt.legend(loc=0,ncol=math.ceil(num_classes/4.))
    plt.tight_layout()
    plt.savefig(args.o+"_class_sizes_per_iter.pdf",format='pdf')
    plt.show()
elif args.f != '':
    class_sizes = np.array([],dtype=float)
    ofile = open(args.o+"_class_sizes.csv",'w')
    this_file = open(args.f,'r')
    these_lines = this_file.readlines()
    for line_idx in range(len(these_lines)):
        LINE = these_lines[line_idx]
        if '_rlnNrClasses' in LINE:
            while "  " in LINE:
                LINE = LINE.replace("  "," ")
            num_classes = int(LINE.split(" ")[1])
        if "_rlnOverallFourierCompleteness" in LINE:
            for class_idx in range(1,num_classes+1):
                class_line = these_lines[line_idx + class_idx + offset]
                while "  " in class_line:
                    class_line = class_line.replace("  "," ")
                class_dist = float(class_line.split(" ")[1])
                class_sizes= np.append(class_sizes,class_dist)
                ofile.write("Class "+str(class_idx)+", "+str(class_dist)+"\n")
            break
    ofile.close()
    plt.figure(figsize=(4.,4.))
    for idx in range(1,num_classes+1):
        plt.bar(idx,class_sizes[idx-1],width=0.8,align='center')
    plt.xlabel('Class')
    if args.particle_count:
        plt.ylabel('Class Size (# of particles)')
    else:
        plt.ylabel('Class Size (%)')
    plt.tight_layout()
    plt.savefig(args.o+"_class_sizes.pdf",format='pdf')
    plt.show()
else:
    print("ERROR: Please supply a single file with \"-f [filename]\" or call the \"--all\" option.")
