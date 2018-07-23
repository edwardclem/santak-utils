'''
Generates an HDF5 file with the following top-level groups:

gen_hdf.py performs edge detection on all images in a user-supplied folder, and reduces the corresponding contours via subsampling. Subsampling is performed by skipping edge points. Use of HDF5 features is limited due to OpenCV's limited HDF5 API. The unicode code points of each character are stored in a dataset in the root group named "unicode".

The source images and output contours are saved in datasets with groups "/imgs", "/contours" - dataset names are integer unicode code points. Text descriptions are found in dataset "/descs" with indices corresponding to the characters in "unicode".

'''
import numpy as np
import cv2
import unicodedata
from argparse import ArgumentParser
from sys import argv
import glob
import os
from tqdm import tqdm
#using HDF5 for better interoperability with c++ code
import h5py


def parse(args):
    parser = ArgumentParser()
    parser.add_argument("--imgs", help="folder with location of rendered images")
    parser.add_argument("--skip", help="skipping interval", type=int)
    parser.add_argument("--min", help="minimum number of points in contour", type=int)
    parser.add_argument("--out", help="location of output hdf5 file")
    return parser.parse_args(args)


def reduce_contours(contours, step=6, min_pts=35):
    '''
    keeps every step points, removes the rest. Alternative to probabilistic subsampling.
    '''
    merged = np.concatenate(contours)

    total_points = merged.shape[0]
    #TODO: better selection of new step if doesn't work
    if total_points/step > min_pts:
        kept_idx = np.arange(0, total_points, step)
        return merged[kept_idx, :, :]
    else:
        return merged

def load_imgs(folder):
    print("loading prototypes from {}".format(folder))
    filenames = glob.glob("{}/*.png".format(folder))

    char_ids = [os.path.basename(filename).split(".")[0] for filename in filenames]
    imgs = [cv2.imread(filename) for filename in filenames]
    return char_ids, imgs


def gen_contour(img):
    '''
    Runs canny edge detector on image, then outputs contours.
    '''
    edges = cv2.Canny(img, img.shape[0], img.shape[1])
    _, cnt, _  = cv2.findContours(edges, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # contour = np.concatenate(cnt)

    return cnt

def run(args):

    char_ids, imgs = load_imgs(args.imgs)

    contours = [gen_contour(img) for img in tqdm(imgs)]

    #reduce all_contours_target
    contours = [reduce_contours(contour, step=args.skip, min_pts=args.min) for contour in tqdm(contours)]

    #list of arrays

    with h5py.File(args.out, 'w') as h5f:
        #creating imgs group
        #converting to integer
        char_ids = [int(id) for id in char_ids]

        h5f.create_dataset('unicode', data=np.array(char_ids))

        descs = [np.string_(unicodedata.name(chr(char_id))) for char_id in char_ids]

        h5f.create_dataset("descs", (len(descs), ), dtype="S10", data=descs)

        #creating images and contours groups
        imgs_group = h5f.create_group("imgs")
        #copying to hdf5
        for i, char_id in enumerate(char_ids):
            ds = imgs_group.create_dataset(str(char_id), data=imgs[i])

        contours_group = h5f.create_group("contours")

        for i, char_id in enumerate(char_ids):
            ds = contours_group.create_dataset(str(char_id), data=contours[i])




if __name__=="__main__":
    run(parse(argv[1:]))
