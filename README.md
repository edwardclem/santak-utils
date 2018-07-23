# santak-utils
Data (pre)processing for cuneiform character recognition.

# Dependencies

The scripts in this respository require:

* numpy
* tqdm
* OpenCV 3
* h5py
* Pillow

# Generating Character Images

render_chars.py renders all characters in a unicode code point range from the provided ttf font file. The rendered characters are saved in PDF format to an output folder.

To use, run:

`render_chars.py [-h] [--code_range CODE_RANGE CODE_RANGE] [--font FONT]
                       [--fsize FSIZE] [--outf OUTF]`

# Generating HDF Data Archives

gen_hdf.py performs edge detection on all images in a user-supplied folder, and reduces the corresponding contours via subsampling. Subsampling is performed by skipping edge points. The source images and output contours are saved in an hdf5 dataset with groups "/imgs" and "/contours". Each group contains an attribute 'count', the total element count. Each dataset contains attributes "uchr", the decimal unicode code point, and "desc", a text description of the character. 

To use, run:
`gen_hdf.py [-h] [--imgs IMGS] [--skip SKIP] [--min MIN] [--out OUT]`

#Example

`pipeline.sh` contains example usage.
