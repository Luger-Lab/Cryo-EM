# Introduction

The files contained here are used for wrapping crYOLO functionality directly in to the RELION gui, without need for switching between programs. In order for these scripts to work, they should be placed in the RELION installation's `bin` directory (or anywhere in the `PATH` when `relion` is also callable, technically). The `janni_cryolo_relion_wrapper.py` excecutable is called by RELION's `External` program-type, with the inputs as described below.

## Installation

Placing the wrapper scripts and linking to the crYOLO installation are managed by the `installer.py` script. That script takes two inputs (`-rpath`, the path to the RELION installation, and `-cpath`, the path to the crYOLO installation). It will then place the scripts in the `bin` folder of the RELION installation while replace the `CRYOLO_INSTALL_PATH` string of the wrapper call with the proper location of the crYOLO installation.

## Using the wrapper

### Denoising Micrographs for Manual Picking (pre-Training)

These instructions assume that you've already motion-corrected and CTF-corrected your raw images in RELION (or imported a micrograph stack and CTF-corrected in RELION).

   1. Select the `External` job-type from RELION GUI.
   2. Enter `janni_cryolo_relion_wrapper.py` for the `External executable:` line.
   3. For `Input micrographs:`, click `Browse` and navigate to the CtfFind job containing the micrographs that you want, then select its `micrographs_ctf.star` file.
   4. Click the `Params` tab.
       * This tab allows you to provide flags and values to the `janni_cryolo_relion_wrapper.py` function. The first box next to a custom parameter is the "label" of the parameter, and the value of that box will be passed to the `janni_cryolo_relion_wrapper.py` function as "`--[parameter label]`" (without the "\[ \]" characters). The second box is the value to assign to this parameter. For some parameters, such as defining the "mode of operation" (i.e., `denoise`, `train`, `predict`, etc.), the second box should be left empty.
   5. For `Param1`, put `denoise` in the first box and leave the second box empty.
   6. For `Param2`, put `nmic` in the second box and put the number of micrographs that you would like to use for your next manual picking job.
   7. Click the `Running` tab.
   8. Set `Number of threads:` to 1.
   9. If using luger-imaging-4 or the Blanca GPU cluster, set `Submit to queue?` to `Yes`. Otherwise, set it to `No`.
       * If you are not using a queuing system, then the `External` job will not currently set which GPU will be assigned to this task, which means that GPU 0 will likely be assigned to run this job. Please assign specific GPU ID's for simultaneously-running jobs accordingly (i.e., specifically request a different GPU(s) for those task(s)).
   11. Set your "queue settings" accordingly, if relevant.
   12. Click `Run!`.
   13. Once the task is complete, it will generate a `micrographs_denoised.star` file in the job's output folder. This file will be fed to the `manual` task in the next step.

### Using the Wrapper to Open `cryolo_boxmanager.py` and Manually Pick on Denoised Micrographs

   1. 
