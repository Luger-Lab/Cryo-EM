# Star Handling Tools

This folder contains programs that I (Sam) have found useful for diagnosing RELION performance or for swapping between versions of relion. So far, there are two programs to consider:

 1. [class_sizes.py](#class_sizes-py)
 2. [relion31_to_relion30.py](#relion31_to_relion30-py)


## class_sizes.py

This function allows you to diagnose the convergence of your 2-D and 3-D classifications in RELION.

## relion31_to_relion30.py

This function allows you to take a STAR file generated by RELION (v3.1) and make it back-compatible for v3.0, just in case you liked some functionalities of the previous version better (such as particle subtraction).

    usage: relion31_to_relion30.py [-h] -istar ISTAR [-ostar OSTAR]

    optional arguments:
    -h, --help    show this help message and exit
    -istar ISTAR  Input STAR file (from relion3.1) that you want converted to
                  relion3.0-compliance
    -ostar OSTAR  Output STAR file in relion3.0-compliant format (Default =
                  "relion30_format.star")

**Note:** When you run your task in RELION-3.0, it might be necessary for you to tell RELION what the pixel resolution of your reference maps are. To do this, use the `additional arguments:` portion of the `Running` tab. For example, if your reference map has a resolution of 1.065 A, you would put ``--angpix 1.065`` in to that box.