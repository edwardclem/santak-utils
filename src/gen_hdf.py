'''
Generates an HDF5 file with the following top-level groups:

All dataset names are the decimal unicode code points of the corresponding characters.
All datasets contain the character name and description in metadata.

imgs:
contours:
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

        imgs_group = h5f.create_group("imgs")

        #copying to hdf5
        for i, char_id in enumerate(char_ids):
            ds = imgs_group.create_dataset(str(char_id), data=imgs[i])
            ds.attrs['name'] = np.string_(unicodedata.name(chr(int(char_id))))
            ds.attrs['desc'] = np.string_("")


        contours_group = h5f.create_group("contours")

        for i, char_id in enumerate(char_ids):
            ds = contours_group.create_dataset(str(char_id), data=contours[i])
            ds.attrs['name'] = np.string_(unicodedata.name(chr(int(char_id))))
            ds.attrs['desc'] = np.string_("")




if __name__=="__main__":
    run(parse(argv[1:]))
