# Introduction

The files contained here are used for wrapping crYOLO functionality directly in to the RELION gui, without need for switching between programs. This has exclusively been tested on version 3.1 of RELION, but it should hopefully work with any version that has the `External` job type. In order for these scripts to work, they should be placed in the RELION installation's `bin` directory (or anywhere in the `PATH` when `relion` is also callable, technically). The `janni_cryolo_relion_wrapper.py` excecutable is called by RELION's `External` program-type, with the inputs as described below.

If you use this wrapper in your research, please note our assistance in the "Acknowledgements" section of your manuscript and direct others to this GitHub page - if you feel so inclined :) 

## Installation

You should download/store the scripts from the wrapper's github repository in a separate folder from both your RELION and crYOLO installations. Then, placing the wrapper scripts in the RELION folder and linking to the crYOLO installation are dynamically managed by the `installer.py` script (which should be run from within the same folder as the `janni_cryolo_relion_wrapper.py` and `cryolo_wrapper_library.py` files). That script takes two inputs (`-rpath`, the path to the RELION installation, and `-cpath`, the path to the crYOLO installation). It will then place the scripts in the `bin` folder of the RELION installation while replacing the `CRYOLO_INSTALL_PATH` string of the wrapper call with the proper location of the crYOLO installation. An example for how the installation call should look is as follows:

`python install.py -rpath /home/luger-software/programs/relion/build/ -cpath /home/luger-software/programs/cryolo/anaconda3/envs/cryolo`

## Using the wrapper

### Denoising Micrographs for Manual Picking (pre-Training)

These instructions assume that you've already motion-corrected and CTF-corrected your raw images in RELION (or imported a micrograph stack and CTF-corrected in RELION).

   1. Select the `External` job-type from the RELION GUI.
   2. Enter `janni_cryolo_relion_wrapper.py` for the `External executable:` line.
   3. For `Input micrographs:`, click `Browse` and navigate to the CtfFind job containing the micrographs that you want, then select its `micrographs_ctf.star` file.
   4. Click the `Params` tab.
       * This tab allows you to provide flags and values to the `janni_cryolo_relion_wrapper.py` function. The first box next to a custom parameter is the "label" of the parameter, and the value of that box will be passed to the `janni_cryolo_relion_wrapper.py` function as "`--[parameter label]`" (without the "\[ \]" characters). The second box is the value to assign to this parameter. For some parameters, such as defining the "mode of operation" (i.e., `denoise`, `train`, `predict`, etc.), the second box should be left empty.
   5. For `Param1`, put `denoise` in the first box and leave the second box empty.
   6. For `Param2`, put `nmic` in the second box and put the number of micrographs that you would like to use for your next manual picking job.
   7. For `Param3`, put `n_model` (for "noise model") in the first box and put the path to your janni `*.h5` model file in the second box (for example, `/data/LugerLab/sam/gmodel_janni_20190703.h5`)
   8. Click the `Running` tab.
   9. Set `Number of threads:` to 1.
   10. If using luger-imaging-4 or the Blanca GPU cluster, set `Submit to queue?` to `Yes`. Otherwise, set it to `No`.
       * If you are not using a queuing system, then the `External` job will not currently set which GPU will be assigned to this task, which means that GPU 0 will likely be assigned to run this job. Please assign specific GPU ID's for simultaneously-running jobs accordingly (i.e., specifically request a different GPU(s) for those task(s)).
   11. Set your "queue settings" accordingly, if relevant.
   12. Click `Run!`.
   13. Once the task is complete, it will generate a `micrographs_denoised.star` file in the job's output folder. This file will be fed to the `manual` task in the next step.

### Using the Wrapper to Open `cryolo_boxmanager.py` and Manually Pick on Denoised Micrographs

   1. Select the `External` job-type from the RELION GUI.
   2. Once again, use `janni_cryolo_relion_wrapper.py` as the `External executable:`.
   3. For the `Input Micrographs`, you should now direct to the `micrographs_denoised.star` in the output folder of your previous `External` job (the one you just ran to denoise your micrographs).
   4. In the `Params` tab, put `manual` in the first box of `Param1` and leave the second box empty. No other parameters need to be defined.
   5. On the `Running` tab, keep the `Number of threads:` to `1` and do not submit to a queue, regardless of whether you are running on a queuing system or not (this is a very low-profile task, and can be run on the "head node" of whatever server you are on, if applicable).
   6. Click `Run!`, and the `cryolo_boxmanager.py` should shortly pop up.
   7. Do your particle picking across the micrographs.
   8. When you go to save your manual picks (`File -> Write -> BOX`), choose the `boxes` folder within the output of the current job (`External -> [job number or job alias] -> boxes`).
   9. Close the box manager and return to the main RELION GUI, this job should now register as "finished" by RELION.

### Using the Wrapper to Generate your crYOLO Config File

   1. Start a new `External` job in the RELION GUI, using the same `janni_cryolo_relion_wrapper.py` external executable.
   2. For your `Input micrographs:`, choose the `micrographs_train_metadata.star` file from your previous "manual pick" external job.
   3. Go to the `Params` tab.
   4. For `Param1`, enter `config_setup` in the first box and leave the second box blank.
   5. For `Param2`, enter `p_model` (for "picking model") in the first box and in the second box put the name of the `.h5` model that want cryolo to write with your trained model (i.e., "pick_model_2021_06_22.h5").
   6. For `Param3`, enter `n_model` (for "noise model") in the first box and put the path to the same janni `.h5` file that you used in the denoising step.
   7. In the `Running` tab, keep the `Number of threads:` at `1` and don't use the queuing system, even if you are on a GPU server (this job is low-profile and will be over very quickly).
   8. Click `Run!`. Your `config_cryolo.json` file should now be generated.

### Using the Wrapper to Train a crYOLO Picking Model

   1. Start a new `External` job in the RELION GUI, with the same external executable call as before.
   2. For `Input Micrographs:`, choose the `micrographs_config.star` file generated by your previous job.
   3. Click on the `Params` tab.
   4. For `Param1`, put `train` in the first box and leave the second box empty.
   5. Click on the `Running` tab.
   6. Set the number of threads to the same value as what you would typically feed `cryolo_train.py` with the `-nc` option.
      * Something reasonable might be to set `Number of threads:` to 10, for instance.
   7. If using workstation 4 or the Blanca GPU server, set `Submit to queue?` to `Yes` and set your queue values accordingly.
      * If you are not using a queuing system, keep in mind that the task will automatically be assigned to GPU 0, and you should assign parallel GPU tasks accordingly (tell them to use a different GPU than 0).
   9. Click `Run!`, and RELION should then call (or queue) the `cryolo_gui.py train` routine.
   10. Once the job is completed, the output folder (`External/[job # or alias]/`) will have a `particles_model.star` file.
      * This `particles_model.star` file does not actually contain the same contents as the `.h5` model that you generated, but it will be used to tell the future `predict` tasks where exactly it can find the `config_cryolo.json` file (the crYOLO configuration file) that properly matches with the listed picking `.h5` model.

### Using the Wrapper to have crYOLO Pick Your Particle Coordinates

   1. Start a new `External` job in the RELION GUI, using the same external executable call as the previous steps.
   2. For `Input micrographs:`, choose the `micrographs` `.star` file from a previous RELION job that contained the micrographs that you would like to pick across.
      * This can be the micrographs from a `CtfFind` task, or maybe even a `Select` (subset selection) task where you filtered out unwanted micrographs.
   3. For `Input particles:`, put the `particles_model.star` file that you generated previously with a `train` call to the `External` process.
   4. Click on the `Params` tab.
   5. For `Param1`, put `predict` in the first box and leave the second box blank.
   6. For `Param2`, put `threshold` in the first box and put the "picking threshold" value that you would like in the second box.
      * Lower values are less restrictive, and I typically set this to 0.1 (but I also do not "swear" by that value - it's purely just my convention).
   7. For `Param3`, put `distance` in the first box and put an integer value in the second to define the distance constraint for particle identification.
      * This is the parameter that tells crYOLO how far apart particles should be spaced to be considered. Particles spaced at a distance below the `distance` value will be discarded from the collection.
   8. Click on the `Running` tab.
   9. Set the `Number of threads:` to something reasonable for your computational system (I typically use `10` on the workstations).
   10. If running on computer 4 or the Blanca GPU server, set `Submit to queue?` to `Yes` and set your queue parameters appropriately.
      * As before, the task will automatically be assigned to GPU 0 if you are not using a queuing system, so any other GPU tasks being run in parallel should be assigned to a different GPU than 0.
   11. Once this task is complete, you can use the output particles `.star` files in the standard RELION `Particle extraction` task (put the `Input coordinates:` path to this `External` job's `coords_suffix_cryolo.star` file).
      * Your `micrograph STAR file:` in the `Particle extraction` job should point to the same job that you had previously used in this `predict` mode of the `External` program.
   12. From here, you'll be using RELION just like you would any other workflow. Enjoy!
