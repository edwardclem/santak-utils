#!/bin/bash

char_script=src/render_chars.py
hdf_script=src/gen_hdf.py
fontpath=resources/CuneiformComposite.ttf

outfolder="rendered/all_composite/"
hdf_out="hdf/all_composite.h5"

#renders all characters in the cuneiform unicode block.
python $char_script --outf $outfolder --code_range 73728 74606 --font $fontpath

python $hdf_script --imgs $outfolder --skip 10 --min 35 --out $hdf_out
