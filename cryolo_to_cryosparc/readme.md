# Preparing crYOLO-Identified Particles for CryoSPARC Analysis

## 

The command-line tool that I wrote for this is "convert_stars_to_csparc.py", and it should already be installed to the current cryolo "bin/" directory (i.e., you should have access to the command by calling "module load cryolo").

1. Convert the many .star files created by crYOLO in to a single .star file.
   - convert_stars_to_csparc.py -sf [path to folder containing cryolo star files] -mf [absolute path to the micrographs folder] -o [output name for the new .star file]
     - The "-mf" micrographs folder path MUST be the *absolute* path (starting from /data/, so "/data/folder1/folder2/eventually/the/micrographs_folder"), and it should point to the micrographs that were fed in to crYOLO for picking (I used the "doseweighted" mrc's found in the cryoSPARC motion correction output folder).
     - The "-o" and "-sf" folders can be either relative (i.e., directions from your current folder) or absolute (starting from "/data").
   - Example: `convert_stars_to_csparc.py -sf /data/cryosparc_projects_folder/v2.12.4/sam/P10/J91/cryolo_picking/all_boxes/STAR/ -mf /data/cryosparc_projects_folder/v2.12.4/sam/P10/J91/motioncorrected/ -o csparc_import.star`
2. Import the cumulative .star file in to cryoSPARC:
   - Choose the "Import Particles" job from the "Job Builder"
     - Make sure that the "Advanced Mode" switch is turned "On"
       - This toggle switch can be found beneath the "Building" text while you are constructing the job.
   - Drag and Drop the micrographs from the "Patch CTF Estimation" job assosciated with your motion-corrected micrographs.
   - Put the path to your combined. star file (i.e., "csparc_import.star" in the previous example) in the "Particle Meta Path" input.
   - Leave the "Particle Data Path" input blank.
   - Turn on "Ignore raw data".
     - This way, cryoSPARC will only look for particle coordinates, and not the micrographs of the extracted particles.
   - Set "Length of mic. path suffix to cut" to 4
   - Set "Length of the part. path suffix to cut" to 4
   - Submit the job.
3. Once the particle import is complete, start a "Patch CTF Extraction" job.
   - Drag and drop the associated "Patch CTF estimation" exposures in to the "exposures" input field.
   - Drag and drop the imported particles in to the particles input.
   - Submit the job.
4. Now that you've linked the CTF values for each particle, you need to actually extract them using the "Extract from Micrographs" jobs.
   - Drag and drop the "Patch CTF estimation" exposures in to the micrographs input field.
   - Drag and drop the particles from the "Patch CTF Extraction" job in to the particles input.
   - Choose your GPU count, extraction box size and Fourier cropping, and any other input options that you want to customize.
   - Submit the job.
5. You can now use the particles output from the previous job to run your typical analysis pipeline (2/3D classing, etc.). Enjoy!
