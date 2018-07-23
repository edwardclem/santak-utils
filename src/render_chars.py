#Given a font file in ttf format, renders all characters in code_range as image files.

import matplotlib
from PIL import ImageFont, ImageDraw, Image
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from argparse import ArgumentParser
import os
import pathlib
from sys import argv
import numpy as np
from tqdm import trange


my_dpi=96
start_int = 73728
end_int = 74649

#changing this will change threshold for "bad" corners
top_lim = 1.2
bot_lim = -0.2

def parse(args):
	parser = ArgumentParser()
	parser.add_argument("--code_range", help="decimal unicode code point range to be rendered.", nargs=2, type=int)
	parser.add_argument("--font", help="font path.")
	parser.add_argument("--fsize", help="font size to render", default=150, type=int)
	parser.add_argument("--outf", help="output folder for rendered images.")
	return parser.parse_args(args)


#renders a character at the given position with the given character size
#increasing size to avoid clipping issues
#NOTE: DEPRECIATED
def render_char(unicodechar, outfile=None, fig_dim=500, dpi=my_dpi, rotation=0,
							char_size=150, pos=(0.5, 0.5), check_clipping=True):
	fig, ax = plt.subplots(1, 1, figsize=(fig_dim/dpi, fig_dim/dpi), dpi=dpi)
	#unpack tuple
	x, y = pos
	t = ax.text(x, y, unicodechar, size=char_size, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, rotation=rotation)
	plt.axis('off')
	if outfile:
		plt.savefig(outfile)
		print("saved to {}".format(outfile))
		if check_clipping:
			#check if text is inside canvas
			#this is so gross, but there's no way to do this until after it's been rendered
			#half width, and half-height
			width, height = t.get_window_extent().width/fig_dim, t.get_window_extent().height/fig_dim
			#create corner points (with rotation), check if they're all in bounds
			#create corner points with box center as origin, perform rotation, translate back
			corners = [np.array([-width/2, -height/2]), np.array([width/2, -height/2]),
						np.array([-width/2, height/2]), np.array([width/2, height/2])]
			#create rotation matrix
			theta = np.radians(rotation)
			c, s = np.cos(theta), np.sin(theta)
			R = np.array([[c, -s], [s, c]])
			for cnr in corners:
				#rotate corner, translate,
				cnr_prime = R.dot(cnr) + np.array(pos)
				if cnr_prime[0] > top_lim or cnr_prime[0] < bot_lim or cnr_prime[1] > top_lim or cnr_prime[1] < bot_lim:
					print("bad corner, removing")
					os.remove(outfile)
					break
			plt.close()
	else:
		plt.show()


def render_char2(unicodechar, font, outfile, fig_dim=300):
	'''
	Renders an image of the unicode char from the provided font.
	Way less gross than the other one.
	'''


	img = Image.new('RGB', (fig_dim, fig_dim), (255, 255, 255))

	draw = ImageDraw.Draw(img)

	draw.text((0, 0), unicodechar, font=font, fill=(0,0,0))

	img.save(outfile, "PNG")

def run(args):

	#load font from args

	font = ImageFont.truetype(args.font, args.fsize)

	#create outfolder if not present
	pathlib.Path(args.outf).mkdir(exist_ok=True)

	for i in trange(args.code_range[0], args.code_range[1] + 1):
		uchar = chr(i)
		render_char2(uchar, font, '{}/{}.png'.format(args.outf, i))


if __name__=="__main__":
    run(parse(argv[1:]))
