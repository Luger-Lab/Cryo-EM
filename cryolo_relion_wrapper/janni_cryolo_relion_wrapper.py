#!CRYOLO_INSTALL_PATH/bin/python

'''
    This script is designed to wrap cryolo and janni into a Relion Scheduler processing list.

    Original Version written by Samuel Bowerman (6/17/2021).
'''

import os,sys,argparse,itertools,datetime
import subprocess
import numpy as np
from cryolo_wrapper_library import *

#Some libraries for crYOLO and relion disagree, so have the cryolo ones prepended only when running from the wrapper.
cryolo_path = "CRYOLO_INSTALL_PATH"
old_PATH = os.environ["PATH"]
os.environ["PATH"] = os.path.join(cryolo_path,"bin") + os.pathsep + old_PATH
old_LD_LIB = os.environ["LD_LIBRARY_PATH"]
os.environ["LD_LIBRARY_PATH"] = os.path.join(cryolo_path,"lib") + os.pathsep + old_LD_LIB

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--train",action='store_true',help="Do cryolo_train (prepare the picking model), not cryolo_predict (full set particle picking).")
parser.add_argument("--manual",action='store_true',help="Manually pick particles (typically for training model)")
parser.add_argument("--predict",action='store_true',help="Pick particles from micrographs using model from \"--model\"")
parser.add_argument("--p_model",default="/pl/active/BioKEM/cryolo_gen_models/gmodel_phosnet_202005_nn_N63_c17.h5",help="Model to use for particle picking")
parser.add_argument("--denoise",action='store_true',help="Denoise micrographs from \"--in_mics\", rather than pick or train on them")
parser.add_argument("--nmic",default=15,type=int,help="Number of micrographs to denoise (and use for manual picking pre-training)")
parser.add_argument("--extension",default=".mrc",help="Extension by which to recognize micrographs for denoising and picking")
parser.add_argument("--n_model",default="/pl/active/BioKEM/cryolo_gen_models/gmodel_janni_20190703.h5",help="Model for micrograph denoising.")
parser.add_argument("--config_setup",action='store_true',help="Set up the config_cryolo.json file instead of running any denoising/picking.")
parser.add_argument("--threshold",default=0.1,type=float,help="Threshold for picking algorithm (higher = more selective/fewer particles).")
parser.add_argument("--train_path",help="Path to micrographs for neural net training (i.e., path to manually picked micrographs")
parser.add_argument("--distance",help="crYOLO-enforced distance constraint to omit boxes. (i.e., particles must be spaces \"--distance\" apart to be considered).")

#Define default paths for picking and noise models since an input of "" doesn't trip the "default", but just a blank string
#These calls won't be run by relion (i.e., the default paths won't change unless you hard-code them here)
parser.add_argument("--n_model_default",default="/pl/active/BioKEM/cryolo_gen_models/gmodel_janni_20190703.h5",help="Path to default model to use if none is explicitly defined")
parser.add_argument("--p_model_default",default="/pl/active/BioKEM/cryolo_gen_models/gmodel_phosnet_202005_nn_N63_c17.h5",help="Path to default model to use if none is explicitly defined")

#The following arguments are specific to different "relion external program" calls
parser.add_argument("--in_mics",help="Input paths for micrographs star, fed to program by relion")
parser.add_argument("--in_parts",help="Input paths for particles star, fed to program by relion")
parser.add_argument("--o",help="Output folder (relion pipeline formatted)")
parser.add_argument("--j",help="Number of CPU threads given to task")
parser.add_argument("--pipeline_control",help="Haven't defined this yet...")


#Load inputs
args = parser.parse_args()

#Check and see if different .h5 models were defined
if args.n_model == "":
    args.n_model = args.n_model_default
if args.p_model == "":
    args.p_model = args.p_model_default

#set up log file
logfile = open(os.path.join(args.o,"cryolo_wrapper_logfile.log"),'w')

modelist = np.array([args.denoise,args.config_setup,args.train,args.predict,args.manual],dtype=bool)
flag_combos = itertools.combinations(modelist,2)
for combo in list(flag_combos):
    if combo[0] == True and combo[1] == True:
        logfile.write("Cannot choose to simultaneously run multiple cryolo modes (denoise, config_setup, train, predict, manual)")
        quit()

if args.denoise:
    try:
        do_denoise(args,logfile)
        #generate the successful output file
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_SUCCESS"))
    except:
        #generate the failed operation flag
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_FAILURE"))
elif args.manual:
    try:
        do_manual_pick(args,logfile)
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_SUCCESS"))
    except:
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_FAILURE"))

elif args.config_setup:
    try:
        do_config_setup(args,logfile)
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_SUCCESS"))
    except:
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_FAILURE"))
elif args.train:
    try:
        do_train(args,logfile)
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_SUCCESS"))
    except:
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_FAILURE"))
elif args.predict:
    if 1:
        do_predict(args,logfile)
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_SUCCESS"))
    else:
        os.system("touch "+os.path.join(args.o,"RELION_JOB_EXIT_FAILURE"))
#Gotta clean up your files
logfile.close()
#Picked boxes should go to "External/job###/micrographs/[micrograph_name]_cryolo.star"

#Program needs to respect RELION_JOB_EXIT_SUCCESS and RELION_JOB_EXIT_FAILURE convention

#Program needs to write "RELION_OUTPUT_NODES.star" file, which explains the node/edge connections

#Program needs to interface with RELION_JOB_ABORT_NOW -> RELION_JOB_EXIT_ABORTED (and remove RELION_JOB_ABORT_NOW file)
