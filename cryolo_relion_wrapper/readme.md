# Introduction

The files contained here are used for wrapping crYOLO functionality directly in to the RELION gui, without need for switching between programs. In order for these scripts to work, they should be placed in the RELION installation's `bin` directory (or anywhere in the `PATH` when `relion` is also callable, technically). The `janni_cryolo_relion_wrapper.py` excecutable is called by RELION's `External` program-type, with the inputs as described below.

## Installation

Placing the wrapper scripts and linking to the crYOLO installation are managed by the `installer.py` script. That script takes two inputs (`-rpath`, the path to the RELION installation, and `-cpath`, the path to the crYOLO installation). It will then place the scripts in the `bin` folder of the RELION installation while replace the `CRYOLO_INSTALL_PATH` string of the wrapper call with the proper location of the crYOLO installation.

## Using the wrapper

Need to do this still.
