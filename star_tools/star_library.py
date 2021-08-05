#!/usr/bin/env python

'''
    This library was designed to help parse STAR files in to custom scripts.

    Written by Samuel Bowerman (University of Colorado).

    Date: August 2021
'''

import os,argparse
import numpy as np

#The full list of particle data will be within one single class
class PARTICLE_DATA(object):
    def __init__(self):
        self.string_metadata = ['_rlnImageName','_rlnMicrographName']
        self.int_metadata    = ['_rlnClassNumber','_rlnRandomSubset','_rlnOpticsGroup','_rlnNrOfSignificantSamples','_rlnGroupNumber']
        self.float_metadata  = ['_rlnCoordinateX','_rlnCoordinateY','_rlnAngleRot','_rlnAngleTilt','_rlnAnglePsi','_rlnOriginXAngst','_rlnOriginYAngst','_rlnDefocusU','_rlnDefocusV','_rlnDefocusAngle','_rlnPhaseShift','_rlnCtfBfactor','_rlnCtfScalefactor','_rlnNormCorrection','_rlnLogLikeliContribution','_rlnMaxValueProbDistribution','_rlnAutopickFigureOfMerit','_rlnCtfMaxResolution','_rlnCtfFigureOfMerit','_rlnOriginX','_rlnOriginY','_rlnDetectorPixelSize','_rlnMagnification']


    #Set each particle information as a list that we can append to as we find new particles
    #def set_particle_metadata(self,metaname,metavalue):
    #    return_metavalue = []
    #    if metaname in self.int_metadata:
    #        metavalue = int(metavalue)
    #    elif metaname in self.float_metadata:
    #        metavalue = float(metavalue)
    #    elif metaname in self.string_metadata:
    #        metavalue = str(metavalue[0])
    #    setattr(self,metaname,return_metavalue.append(metavalue))

    #Append metavalue to the end of pre-existing PARTICLE_DATA.metaname list
    def add_particle_metadata(self,metaname,metavalue):
        if metaname in self.int_metadata:
            metavalue = int(metavalue)
        elif metaname in self.float_metadata:
            metavalue = float(metavalue)
        elif metaname in self.string_metadata:
            metavalue = str(metavalue)

        if self.get_metadata(metaname) is None:
            updated_metavalues = []
            updated_metavalues.append(metavalue)
        else:
            updated_metavalues = self.get_metadata(metaname)
            updated_metavalues.append(metavalue)

        setattr(self,metaname,updated_metavalues)

    def get_metadata(self,metaname):
        try:
            metavalue = getattr(self,metaname)
            return metavalue 
        except:
            print("Metavariable \""+metaname+"\" has not yet been set.")
            return None

#Each different "data_optics" line (i.e., each Optics Group) will have separate objects whose attributes will be associated with the proper metadata
class OPTICS_GROUP(object):
    def __init__(self):
        self.string_metadata = ['_rlnOpticsGroupName']
        self.int_metadata    = ['_rlnOpticsGroup','_rlnImageSize','_rlnImageDimensionality']
        self.float_metadata  = ['_rlnMicrographOriginalPixelSize','_rlnSphericalAberration','_rlnAmplitudeContrast','_rlnImagePixelSize','_rlnVoltage']

    #def __init__(self,OpticsGroupName="opticsGroup1",OpticsGroup=1,MicrographOriginalPixelSize=0.8211,
    #             Voltage=300,SphericalAberration=2.7,AmplitudeContrast=0.1,ImagePixelSize=0.8211,
    #             ImageSize=128,ImageDimensionality=2):
    #    self.OpticsGroupName = OpticsGroupName
    #    self.OpticsGroup = OpticsGroup
    #    self.MicrographOriginalPixelSize = MicrographOriginalPixelSize
    #    self.Voltage = Voltage
    #    self.SphericalAberration = SphericalAberration
    #    self.AmplitudeContrast = AmplitudeContrast
    #    self.ImagePixelSize = ImagePixelSize
    #    self.ImageSize = ImageSize
    #    self.ImageDimensionality = ImageDimensionality
    
    #Kind of redundant, but easier to remember than "setattr()" - and having this here helps me remember to use setattr() more
    def set_metadata(self,metaname,metavalue):
        #Set numericals away from strings
        if metaname in self.int_metadata:
            metavalue = int(metavalue)
        elif metaname in self.float_metadata:
            metavalue = float(metavalue)
        setattr(self,metaname,metavalue)

    #Kind of redundant, like above, but helps us look if a value has been set yet or not.
    def get_metadata(self,metaname):
        try:
            return getattr(self,metaname)
        except:
            print("MetaVariable \""+metaname+"\" is not yet defined.")
            return None



class STARFILE(object):

    #If starfile already exists, read in values. Otherwise, we will generate data in the future.
    # data_optics and data_particles are stored in separate "dictionaries of objects"
    def __init__(self,fname="",relion3_0=False):
        self.fname = fname
        self.relion3_0 = relion3_0
        self.optics_metanames    = []
        self.particles_metanames = []
        self.optics_groups       = {}
        if not self.fname == "":
            self.n_particles = 0
            if not relion3_0:
                self.GetOpticsGroups()
            self.GetParticleData()

    def GetParticleData(self):
        print("Identifying per-particle MetaData")
        star_file = open(self.fname,'r')
        star_lines= star_file.readlines()
        star_file.close()

        particle_metanames= []
        particle_metacol  = []

        found_particles = False
        in_loop = False
        for LINE in star_lines:
            num_metadatas = len(particle_metanames)
            if not found_particles:
                if ((not self.relion3_0) and ("data_particles" in LINE)) or ((self.relion3_0) and ("data_images" in LINE)):
                    found_particles = True
                    self.particle_data = PARTICLE_DATA()
            else:
                if "loop_" in LINE:
                    in_loop = True
                elif "_rln" in LINE:
                    METAVARIABLE,METACOLUMN = LINE.replace("\n"," ").split("#")
                    METAVARIABLE = METAVARIABLE.replace(" ","")
                    particle_metanames.append(METAVARIABLE)
                    particle_metacol.append(METACOLUMN)
                    print("Identified "+METAVARIABLE+" metavariable ("+str(num_metadatas+1)+" total)")
                elif num_metadatas > 0:
                    LINE = LINE.replace(" \n","")
                    while "  " in LINE:
                        LINE = LINE.replace("  "," ")
                    SPLIT_LINE = LINE.split(" ")
                    if SPLIT_LINE[0]=="": #Can happen if rows start with a space
                        SPLIT_LINE = SPLIT_LINE[1:]
                    if len(SPLIT_LINE) == num_metadatas:
                        for idx in range(num_metadatas):
                            metavariable = particle_metanames[idx]
                            metavalue = SPLIT_LINE[idx]
                            self.particle_data.add_particle_metadata(metavariable,metavalue)
                        self.n_particles += 1
        for metavariable in particle_metanames:
            if metavariable not in self.particles_metanames:
                self.particles_metanames.append(metavariable)



    def GetOpticsGroups(self,additional_star=""):
        if additional_star=="":
            star_file = open(self.fname,'r')
        else:
            star_file = open(additional_star,'r') #Allow us to add data from multiple STAR files together
        star_lines= star_file.readlines()
        star_file.close()

        optics_metaname = []
        optics_metacol  = []

        found_optics = False
        found_particles = False
        in_loop = False
        for LINE in star_lines:
            num_metadatas = len(optics_metaname)
            if not found_optics:
                if "data_optics" in LINE:
                    found_optics = True
            else:
                if "loop_" in LINE:
                    in_loop = True
                elif "data_particles" in LINE:
                    print("Encountered \"data_particles\", completing data_optics metadata import.")
                    break
                elif "_rln" in LINE:
                    METAVARIABLE,METACOLUMN = LINE.replace("\n","").split("#")
                    METAVARIABLE = METAVARIABLE.replace(" ","")
                    optics_metaname.append(METAVARIABLE)
                    optics_metacol.append(METACOLUMN)
                    print("Identified "+METAVARIABLE+" metavariable ("+str(num_metadatas+1)+" total)")
                elif (num_metadatas > 0):
                    while "  " in LINE:
                        LINE = LINE.replace(" \n","").replace("  "," ")
                    SPLIT_LINE = LINE.split(" ")
                    if SPLIT_LINE[0]=="":
                        SPLIT_LINE=SPLIT_LINE[1:]
                    if len(SPLIT_LINE) == num_metadatas: #We only want to pull lines that have the right number of entries to fill out every metadata
                        group_loc = np.where(np.array(optics_metaname)=="_rlnOpticsGroup")[0][0]
                        group = SPLIT_LINE[group_loc]
                        self.optics_groups[group] = OPTICS_GROUP()
                        for idx in range(num_metadatas):
                            self.optics_groups[group].set_metadata(optics_metaname[idx],SPLIT_LINE[idx])

        #When merging multiple STAR files, we may need to add extra METAVARIABLES than what was in the original list
        for METAVARIABLE in optics_metaname: 
            if METAVARIABLE not in self.optics_metanames:
                self.optics_metanames.append(METAVARIABLE)

    def ConvertOriginAtoPix(self,optics_group_ids,angpix_per_group):
        #Load as numpy arrays to make the math faster (vectorize the conversion)
        x_origins     = np.array(self.particle_data.get_metadata('_rlnOriginXAngst'))
        y_origins     = np.array(self.particle_data.get_metadata('_rlnOriginYAngst'))
        o_groups      = np.array(self.particle_data.get_metadata('_rlnOpticsGroup'))
        scale_factors = np.ones(len(x_origins),dtype=float) #Use this for a vectorized multiplication action
        
        for idx in range(len(optics_group_ids)):
            ogroup = optics_group_ids[idx]
            members = np.where(o_groups==int(ogroup))
            scale_factors[members] = 1.0 / angpix_per_group[idx]

        x_origins_conv= np.multiply(x_origins,scale_factors)
        y_origins_conv= np.multiply(y_origins,scale_factors)

        self.particle_data._rlnOriginX = np.around(x_origins_conv,decimals=6)
        self.particle_data._rlnOriginY = np.around(y_origins_conv,decimals=6)

        self.particles_metanames.append('_rlnOriginX')
        self.particles_metanames.append('_rlnOriginY')

    def ImagePixelSize_to_DetectorPixelSize(self,optics_groups,angpix_per_group):
        o_groups = np.array(self.particle_data.get_metadata('_rlnOpticsGroup'))
        pix_arr  = np.ones(len(o_groups),dtype=float)
        
        for idx in range(len(optics_groups)):
            ogroup = optics_groups[idx]
            members= np.where(o_groups==int(ogroup))
            pix_arr[members] = angpix_per_group[idx]

        self.particle_data._rlnDetectorPixelSize = pix_arr
        self.particles_metanames.append('_rlnDetectorPixelSize')

    def ValueToParticles(self,METANAME,optics_groups,value_per_group):
        o_groups = np.array(self.particle_data.get_metadata('_rlnOpticsGroup'))
        v_array  = np.ones(len(o_groups),dtype=float)

        for idx in range(len(optics_groups)):
            ogroup = optics_groups[idx]
            members= np.where(o_groups==int(ogroup))
            v_array[members] = value_per_group[idx]

        setattr(self.particle_data,METANAME, v_array)
        self.particles_metanames.append(METANAME)


    def ConvertToRelion3_0(self):
        '''
        To convert to relion 3.0 from relion 3.1, need to modify some variables:
            1. _rlnOrigin[X/Y] needs to be converted from Angstroms (r3.1) to Pixels (r3.0)
            2. _rlnImagePixelSize needs to be converted to _rlnDetectorPixelSize and attached to each particle
            3. _rlnVoltage needs to be attached to each particle
            4. _rlnSphericalAberration needs to be attached to each particle
            5. _rlnAmplitudeContrast needs to be attached to each particle
        '''
        
        #Use Optics Group to Convert A to Pix
        optics_groups = [key for key in self.optics_groups]
        optics_ids = []
        angpix_per_group = []
        voltage_per_group= []
        saberr_per_group = []
        amp_con_per_group= []

        for idx in range(len(optics_groups)):
            optics_ids.append(self.optics_groups[optics_groups[idx]].get_metadata('_rlnOpticsGroup'))
            angpix_per_group.append(self.optics_groups[optics_groups[idx]].get_metadata('_rlnImagePixelSize'))
            voltage_per_group.append(self.optics_groups[optics_groups[idx]].get_metadata('_rlnVoltage'))
            saberr_per_group.append(self.optics_groups[optics_groups[idx]].get_metadata('_rlnSphericalAberration'))
            amp_con_per_group.append(self.optics_groups[optics_groups[idx]].get_metadata('_rlnAmplitudeContrast'))

        self.ConvertOriginAtoPix(optics_groups,angpix_per_group)
        
        #Convert PixelSize MetaVariable Name
        self.ImagePixelSize_to_DetectorPixelSize(optics_groups,angpix_per_group)
        
        #Attach scope params per particle
        self.ValueToParticles('_rlnVoltage',optics_groups,voltage_per_group)
        self.ValueToParticles('_rlnSphericalAberration',optics_groups,saberr_per_group)
        self.ValueToParticles('_rlnAmplitudeContrast',optics_groups,amp_con_per_group)        
 
    def WriteStarFile_Relion3_0(self,starfilename):
        starfile = open(starfilename,'w')
        starfile.write("#Generated for relion3.0-compliance with custom scripts by Samuel Bowerman (University of Colorado)\n\n")
        starfile.write("data_images\n\nloop_\n")
        star_col = 1
        exclude_list = ['_rlnOriginXAngst','_rlnOriginYAngst','_rlnOpticsGroup']
        for idx in range(len(self.particles_metanames)):
            METAVARIABLE = self.particles_metanames[idx]
            if METAVARIABLE not in exclude_list:
                starfile.write(METAVARIABLE+" #"+str(star_col)+"\n")
                star_col += 1
        for idx in range(self.n_particles):
            for idx2 in range(len(self.particles_metanames)):
                METAVARIABLE = self.particles_metanames[idx2]
                if METAVARIABLE not in exclude_list:
                    METAVALUE    = self.particle_data.get_metadata(METAVARIABLE)[idx]
                    starfile.write(str(METAVALUE)+" ")
            starfile.write("\n")
        starfile.close()

    def WriteStarFile(self,starfilename,relion3_0_format=False):
        if self.relion3_0 or relion3_0_format:
            self.WriteStarFile_Relion3_0(starfilename)
        else:
            starfile = open(starfilename,'w')
            starfile.write("#Generated for relion 3.1-compliance with custom scripts by Samuel Bowerman (University of Colorado)\n\n")
            starfile.write("data_optics\n\nloop_\n")
            for idx in range(len(self.optics_metanames)):
                starfile.write(self.optics_metanames[idx]+" #"+str(idx+1)+"\n")
            for key in self.optics_groups:
                for meta_idx in range(len(self.optics_metanames)):
                    try:
                        metavalue = self.optics_groups[key].get_metadata(self.optics_metanames[meta_idx])
                    except:
                        print("MetaVariable \""+self.optics_metanames[meta_idx]+"\" does not exist for optics group \""+key+"\". Consider hand-setting parameter, printing as \"0.0000\" in "+starfilename)
                        metavalue = "0.0000"
                    starfile.write(str(metavalue)+" ")
                starfile.write("\n")

            starfile.write("\ndata_particles\n\nloop_\n")
            for idx in range(len(self.particles_metanames)):
                METAVARIABLE = self.particles_metanames[idx]
                starfile.write(METAVARIABLE+" #"+str(idx+1)+"\n")
            for idx in range(self.n_particles):
                for idx2 in range(len(self.particles_metanames)):
                    METAVARIABLE = self.particles_metanames[idx2]
                    METAVALUE    = self.particle_data.get_metadata(METAVARIABLE)[idx]
                    starfile.write(str(METAVALUE))
                    starfile.write(" ")
                starfile.write("\n")         
            starfile.close()
        
