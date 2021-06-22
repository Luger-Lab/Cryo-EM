#!/usr/bin/env python
'''
Original version written by Samuel Bowerman (6/22/2021)
'''

import os,sys,glob,datetime,itertools,subprocess,shutil
import numpy as np

def do_denoise(args,logfile):
    starttime = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    logfile.write("Beginning 'Denoise' task at "+starttime+"\n\n")

    mics_star_path = args.in_mics
    #Extract list of .mrc files from input .star file
    mics_star_file = open(mics_star_path,'r')
    star_lines = mics_star_file.readlines()
    mics_star_file.close()

    #We will also use the mic_file_list later to build the output .star file
    mic_file_list = []
    star_line_list= []
    denoised_out_star = open(os.path.join(args.o,"micrographs_denoised.star"),'w')
    denoised_star_header_complete = False

    for line in star_lines:
        first_column = line.split(" ")[0] #the mrc image should consistently be the first thing in the list, if the line describes a micrograph (either from MotCorr or from CtfFind job
        if "MotionCorr" in first_column: #Will always be the first column, if in a correct row
            mic_file_list.append(first_column)
            if not denoised_star_header_complete:
                denoised_out_star.write("_rlnDenoisedMicrograph #"+str(rln_idx+1)+"\n")
                denoised_star_header_complete = True
            #We don't want to include the "new line" character (the "-1"th index) because we are adding to the line
            #denoised_out_star.write(line[:-1]+"\t")
            star_line_list.append(line[:-1]+" ")
        else:
            denoised_out_star.write(line)
            if "_rln" in line: #Need to keep track of how many _rlnColumns we have
                rln_idx = int(line.split(" ")[-2].replace("#","")) #The "-1" idx is the new line character, so the "-2" idx will be "#[rln_idx]" string


    #Randomly pick args.nmic number of files to denoise etc.
    mic_idx = np.arange(len(mic_file_list))
    denoise_idxs = np.random.choice(mic_idx,size=args.nmic,replace=False)
    denoise_list = np.array(mic_file_list)[denoise_idxs]
    denoise_star_lines = np.array(star_line_list)[denoise_idxs]
    for idx in range(args.nmic):
        mic_basename = os.path.basename(denoise_list[idx])
        denoised_mic = os.path.join(args.o,"denoised/for_picking/"+mic_basename)
        denoised_out_star.write(denoise_star_lines[idx]+denoised_mic+"\n")
    denoised_out_star.close()

    #Create a folder to house the mic list for denoising/manual picking
    for_pick_folder = os.path.join(args.o,"for_picking")
    if not os.path.isdir(for_pick_folder):
        logfile.write(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+": creating folder = "+for_pick_folder+"\n")
        os.mkdir(for_pick_folder)
    #If the folder does exist, get rid of old symlinks
    else:
        for FILE in glob.glob(os.path.join(for_pick_folder,"*.*")):
            os.unlink(FILE)

    #This folder will hold the post-denoising mics
    after_denoise_folder = os.path.join(args.o,"denoised")
    if not os.path.isdir(after_denoise_folder):
        logfile.write(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+": creating folder = "+after_denoise_folder+"\n")
        os.mkdir(after_denoise_folder)

    #put symbolic links to the randomly-selected micrographs in to the "for_picking" folder
    for FILE in denoise_list:
        #Call os.path.basename to remove the prefix path (maintained by glob.glob call)
        link_path = os.path.join(for_pick_folder,os.path.basename(FILE))
        logfile.write(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+": creating symbolic link for micrograph: "+FILE+" -> "+link_path)
        os.symlink(os.path.join(os.getcwd(),FILE),link_path)

    #Now that the preparation work has been done, start denoising micrographs
    function_call = "janni_denoise.py denoise -ol 24 -bs 4 -g 0 "+for_pick_folder+" " +after_denoise_folder+" "+args.n_model
    logfile.write(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+": Sending function call = "+function_call+"\n")
    #Need to split the program and inputs in subprocess call (needs to be list, not string)
    function_call_split = function_call.split(" ")
    subprocess.call(function_call_split)

    #Need to make pipeline .star file information
    out_nodes_star = open(os.path.join(args.o,"RELION_OUTPUT_NODES.star"),'w')
    out_nodes_star.write("data_output_nodes\n")
    out_nodes_star.write("loop_\n")
    out_nodes_star.write("_rlnPipeLineNodeName #1\n")
    out_nodes_star.write("_rlnPipeLineNodeType #2\n")
    out_nodes_star.write(os.path.join(args.o,"micrographs_denoised.star")+"\t1\n")
    out_nodes_star.close()

def do_manual_pick(args,logfile):
    starttime = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    logfile.write("Beginning 'Manual Pick' task at "+starttime+"\n\n")

    logfile.write("Opening input micrographs star file: "+args.in_mics+"\n")
    denoised_star = open(args.in_mics,'r')
    denoised_star_lines = denoised_star.readlines()
    denoised_star.close()

    #Generate a folder within the job to link the mics for picking
    denoise_mic_folder = os.path.join(args.o,"denoised_folder")
    raw_mic_folder= os.path.join(args.o,"raw_image_folder")
    manual_pick_folder = os.path.join(args.o,"boxes")

    #If folders don't exist, then make them
    logfile.write("Generating folders for symbolic links and particle picks: %s; %s; %s\n" % (denoise_mic_folder, raw_mic_folder, manual_pick_folder))
    if not os.path.isdir(denoise_mic_folder):
        os.mkdir(denoise_mic_folder)
    if not os.path.isdir(raw_mic_folder):
        os.mkdir(raw_mic_folder)
    if not os.path.isdir(manual_pick_folder):
        os.mkdir(manual_pick_folder)

    #look for lines containing micrograph information, denoised images will be final column
    logfile.write("Determining raw and denoised micrographs for manual picking from "+args.in_mics+"\n")
    for LINE in denoised_star_lines:
        LINE = LINE.replace("\n","").replace("\t","")  #Things got weird around the new-line character, so I just got rid of it
        if "MotionCorr" in LINE: #The micrograph lines will just bet the ones with "MotionCorr" in the first column

            split_line = LINE.split(" ")
            #The original motion-corrected file will be the first column, the denoised version the last column
            link_path_prefix = os.getcwd()

            raw_rel_path = split_line[0]
            raw_basename = os.path.basename(raw_rel_path)
            raw_link_src = os.path.join(link_path_prefix,raw_rel_path)
            raw_link_dest= os.path.join(raw_mic_folder,raw_basename)

            currtime= datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
            if not os.path.exists(raw_link_dest):
                if os.path.exists(raw_link_src):
                    logfile.write(currtime+" = creating symbolic link "+raw_link_src+" -> "+raw_link_dest+"\n")
                    os.symlink(raw_link_src,raw_link_dest)
                else:
                    logfile.write(currtime+" = could not find source for symbolic link ("+raw_link_src+" -> "+raw_link_dest+")\n")
            else:
                logfile.write(currtime+" = Symbolic link already present at destination ("+raw_link_dest+")\n")
            denoise_rel_path = split_line[-1] #For some reason, "-1" isn't the new line character for .star files written through this python wrapper?
            denoise_basename = os.path.basename(denoise_rel_path)
            denoise_link_src = os.path.join(link_path_prefix,denoise_rel_path)
            denoise_link_dest= os.path.join(denoise_mic_folder,denoise_basename)
        
            if not os.path.exists(denoise_link_dest):
                currtime = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                if os.path.exists(denoise_link_src):
                    logfile.write(currtime+" = creating symbolic link "+denoise_link_src+" -> "+denoise_link_dest+"\n")
                    os.symlink(denoise_link_src,denoise_link_dest)
                else:
                    logfile.write(currtime+" = could not find source for symbolic link ("+denoise_link_src+" -> "+denoise_link_dest+")\n")
            else:
                logfile.write(currtime+" = Symbolic link already present at destination ("+denoise_link_dest+")\n")
        
    function_call = "cryolo_boxmanager.py -i "+denoise_mic_folder
    function_call_split = function_call.split(" ")

    logfile.write(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")+": sending function call = "+function_call+"\n")
    subprocess.call(function_call_split)

    #Need to code-in some kind of pipeline.star file for information for training
    train_star = open(os.path.join(args.o,"micrographs_train_metadata.star"),'w')
    #The first row will define the path to "train_images"
    train_star.write(os.path.join(args.o,"raw_image_folder")+"\n")
    #The second row will define the path to the "train_boxes" folder
    train_star.write(os.path.join(args.o,"boxes")+"\n")
    train_star.close()

   #Star file for managing relion pipeline flow
    out_nodes_star = open(os.path.join(args.o,"RELION_OUTPUT_NODES.star"),'w')
    out_nodes_star.write("data_output_nodes\n")
    out_nodes_star.write("loop_\n")
    out_nodes_star.write("_rlnPipeLineNodeName #1\n")
    out_nodes_star.write("_rlnPipeLineNodeType #2\n")
    out_nodes_star.write(os.path.join(args.o,"micrographs_train_metadata.star")+" 1\n")
    out_nodes_star.close()


def do_train(args,logfile):
    starttime = get_time()
    logfile.write("Beginning 'Training' task at "+starttime+"\n\n")
    
    train_paths_star = open(args.in_mics,'r')
    train_folders    = train_paths_star.readlines()
    train_images     = train_folders[0].replace("\n","")
    train_boxes      = train_folders[1].replace("\n","")
    config_path      = train_folders[2].replace("\n","")
    model_name       = train_folders[3].replace("\n","")

    function_call = "cryolo_gui.py train -c "+config_path+" -nc "+args.j+" -w 5"
    this_time = get_time()
    logfile.write(this_time+" = sending function call: "+function_call+"\n")
    function_call_split = function_call.split(" ")
    subprocess.call(function_call_split)

    #Copy the output picking model to the folder, to prevent potential over-writing by future trainings
    shutil.copyfile(model_name,os.path.join(args.o,model_name))
    
    #Pipeline STAR
    out_nodes_star = open(os.path.join(args.o,"RELION_OUTPUT_NODES.star"),'w')
    out_nodes_star.write("data_output_nodes\n")
    out_nodes_star.write("loop_\n")
    out_nodes_star.write("_rlnPipeLineNodeName #1\n")
    out_nodes_star.write("_rlnPipeLineNodeType #2\n")
    out_nodes_star.write(os.path.join(args.o,"particles_model.star")+" 3\n")
    out_nodes_star.close()

    #STAR file containing meta-data for picking
    trained_star = open(os.path.join(args.o,"particles_model.star"),'w')
    trained_star.write(os.path.join(args.o,model_name)+"\n")
    trained_star.write(config_path+"\n")
    trained_star.close()


def do_predict(args,logfile):
    starttime = get_time()
    logfile.write("Beginning 'Predict' task at "+starttime+"\n\n")

    mic_ctf_star   = open(args.in_mics, 'r')
    cryolo_star    = open(args.in_parts,'r')
    cryolo_lines   = cryolo_star.readlines()
    model_path     = cryolo_lines[0].replace("\n","")
    config_path    = cryolo_lines[1].replace("\n","")

    this_time = get_time()
    logfile.write(this_time+" = Using model "+model_path+" to pick particles on micrographs in "+args.in_mics+"\n")

    out_box_folder = os.path.join(args.o,"particles")
    
    #Find the micrograph folder from CTF path
    mic_ctf_star_lines = mic_ctf_star.readlines()
    #In case there are multiple runs joined together, we are going to look for unique CtfFind/micrographs folders, instead of just using the first we find
    ctf_mic_path_list = []
    CTFcol = 2 #Assume .star file follows default order but still explicitly identify below, just in case
    for LINE in mic_ctf_star_lines:
        if "_rlnCtfImage" in LINE:
            #Have to fix weird spacing issue
            LINE = LINE.replace(" \n","")
            CTFcol = int(LINE.split(" ")[-1].replace("#","")) - 1 #Relion is 1-indexed, python is 0-indexed
        if "MotionCorr" in LINE:
            while "  " in LINE: #since we are splitting by " ", we need to make sure there aren't any multi-" " left
                LINE = LINE.replace("  "," ")
            split_line = LINE.split(" ")
            CTF_full_path = split_line[CTFcol].replace(":mrc","") #Remove the weird nomenclature from .star file
            CTF_mic_folder= os.path.split(CTF_full_path)[0]
            ctf_mic_path_list.append(CTF_mic_folder)

    #Pull only the unique CTF/micrographs folders
    unique_paths = np.unique(np.array(ctf_mic_path_list))
    this_time = get_time()
    logfile.write(this_time+" = Identified the following micrograph path(s): "+str(unique_paths)+"\n")
    
    #We need to make symbolic links to a unified folder
    mic_folder = os.path.join(args.o,"micrographs")
    if not os.path.exists(mic_folder):
        os.mkdir(mic_folder)
    for mic_path in unique_paths:
        full_path = os.path.join(os.getcwd(),mic_path)
        mic_list = glob.glob(os.path.join(full_path,"*.mrc"))
        for MIC in mic_list:
            link_path = os.path.join(mic_folder,os.path.basename(MIC))
            if os.path.exists(link_path):
                os.unlink(link_path)
            os.symlink(MIC,link_path)

    #Make a folder for storing particle picks
    out_box_folder = os.path.join(args.o,"boxes")
    if not os.path.exists(out_box_folder):
        os.mkdir(out_box_folder)

    function_call = "cryolo_gui.py predict -c "+config_path+" -w "+model_path+" -i "+mic_folder+" -o "+out_box_folder+" -t "+str(args.threshold)+" -d "+str(args.distance)+" -nc "+args.j
    this_time = get_time()
    logfile.write(this_time+" = sending function call: "+function_call+"\n")
    function_call_split = function_call.split(" ")
    subprocess.call(function_call_split)


    #Pipeline STAR
    out_nodes_star = open(os.path.join(args.o,"RELION_OUTPUT_NODES.star"),'w')
    out_nodes_star.write("data_output_nodes\n")
    out_nodes_star.write("loop_\n")
    out_nodes_star.write("_rlnPipeLineNodeName #1\n")
    out_nodes_star.write("_rlnPipeLineNodeType #2\n")
    out_nodes_star.write(os.path.join(args.o,"coords_suffix_cryolo.star")+" 2\n")
    out_nodes_star.close()
       
    #Relion requires you to define coordinate suffixes for filenames (in this case "cryolo")
    suffix_star = open(os.path.join(args.o,"coords_suffix_cryolo.star"),'w')
    suffix_star.write(args.in_mics+"\n")
    suffix_star.close()
 
    #Take the .star files from cryolo and put them in relion-type arrangement
    star_list = glob.glob(os.path.join(args.o,"boxes/STAR/*.star"))
    for STAR in star_list:
        full_star_path = os.path.join(os.getcwd(),STAR)
        link_path = os.path.join(args.o,"micrographs/"+os.path.basename(STAR)).replace(".star","_cryolo.star")
        link_path.replace(".star","_cryolo.star") # have to do the swap defined by suffix above
        if os.path.exists(link_path):
            os.unlink(link_path)
        os.symlink(full_star_path,link_path)

    
def do_config_setup(args,logfile):
    starttime = get_time()
    logfile.write("Beginning 'Config Setup' task at "+starttime+"\n\n")
    
    this_time = get_time()
    logfile.write(this_time+" = Getting training micrographs and boxes from "+args.in_mics+"\n")
    train_paths_star = open(args.in_mics,'r')
    train_folders    = train_paths_star.readlines()
    train_images     = train_folders[0].replace("\n","")
    train_boxes      = train_folders[1].replace("\n","")
    this_time = get_time()
    logfile.write(this_time+" = Train images ("+train_images+") and training boxes ("+train_boxes+") folders identified.\n")

    this_time = get_time()
    logfile.write(this_time+" = Getting box size from training boxes .box files\n")
    train_box_files = glob.glob(os.path.join(train_boxes,"*.box"))
    x_coord,y_coord,xbox,ybox = np.genfromtxt(train_box_files[0],dtype=int,unpack=True)
    boxsize = np.copy(np.unique(xbox)[0])
    config_path = os.path.join(args.o,"config_cryolo.json")
    
    function_call = "cryolo_gui.py config --train_image_folder "+train_images+" --train_annot_folder "+train_boxes+" --saved_weights_name "+args.p_model+" --filter JANNI --janni_model "+args.n_model+" --log_path "+os.path.join(args.o,"cryolo_log.log "+config_path+" "+str(boxsize))
    this_time = get_time()
    logfile.write(this_time+" = Sending function call: "+function_call+"\n")
    function_call_split = function_call.split(" ")
    subprocess.call(function_call_split)

    #Copy the manually-picked training details to this job, which will then feed to the actual train job
    box_src = os.path.join(os.getcwd(),train_boxes)
    box_dest= os.path.join(args.o,"train_boxes")
    if os.path.exists(box_dest):
        os.unlink(box_dest)
    os.symlink(box_src,box_dest)
    mic_src = os.path.join(os.getcwd(),train_images)
    mic_dest= os.path.join(args.o,"train_images")
    if os.path.exists(mic_dest):
        os.unlink(mic_dest)
    os.symlink(mic_src,mic_dest)

    #Put the metadata in a dummy star file, like before
    config_star_path = os.path.join(args.o,"micrographs_config.star")
    config_star = open(config_star_path,'w')
    config_star.write(os.path.join(args.o,"train_images")+"\n")
    config_star.write(os.path.join(args.o,"train_boxes")+"\n")
    config_star.write(config_path+"\n")
    config_star.write(args.p_model+"\n")
    config_star.close()

    #Set up the relion pipeline info
    out_nodes_star = open(os.path.join(args.o,"RELION_OUTPUT_NODES.star"),'w')
    out_nodes_star.write("data_output_nodes\n")
    out_nodes_star.write("loop_\n")
    out_nodes_star.write("_rlnPipeLineNodeName #1\n")
    out_nodes_star.write("_rlnPipeLineNodeType #2\n")
    out_nodes_star.write(os.path.join(args.o,"micrographs_config.star")+" 1\n")
    out_nodes_star.close()

    #Symlink the config_cryolo.json file to the main project directory, so that the auto-pipeline can see that it doesn't need to repeat this step again
    config_basename = os.path.basename(config_path)
    if os.path.exists(config_basename):
        os.unlink(config_basename)
    os.symlink(os.path.join(os.getcwd(),config_path),config_basename)

def get_time():
    this_time = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    return this_time

