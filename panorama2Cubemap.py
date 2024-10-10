import numpy as np
import imageio
import sys, math, os
import argparse
from PIL import Image
import re
'''
将文件夹下的全景图转为六个面的图片，分别为 front back left right up down
'''
parser = argparse.ArgumentParser(description='Turn a panorama image into a cube map (6 images)')
parser.add_argument("--size", default=512, type=int, help="Size of output image sides")
parser.add_argument("--type", default="jpg", help="File Type to save as, jpg, png etc.")
parser.add_argument('-i',"--input_dir", required=True, help="Directory containing input panorama files")
parser.add_argument("--onefile",
                    help="Save output as one concatenated file, still uses intermediate files as temp storage.")
parser.add_argument("--quality", type=int, help="Quality of jpeg output. (Only valid for jpeg format)")
parser.add_argument('-o',"--output_dir", required=True, help="Directory to save output files")

args = parser.parse_args()

def process_image(input_file, output_dir):
    SIZE = args.size
    HSIZE = SIZE / 2.0
    im = imageio.v2.imread(input_file)
    side_im = np.zeros((SIZE, SIZE), np.uint8)
    color_side = np.zeros((SIZE, SIZE, 3), np.uint8)
    side_names = ["front", "back", "left", "right", "up", "down"]
    for i, side_name in enumerate(side_names):
        it = np.nditer(side_im, flags=['multi_index'], op_flags=['readwrite'])
        while not it.finished:
            axA = it.multi_index[0]
            axB = it.multi_index[1]
            z = -axA + HSIZE
            if i == 0:  # front
                x = HSIZE
                y = -axB + HSIZE
            elif i == 1:  # back
                x = -HSIZE
                y = axB - HSIZE
            elif i == 2:  # left
                x = axB - HSIZE
                y = HSIZE
            elif i == 3:  # right
                x = -axB + HSIZE
                y = -HSIZE
            elif i == 4:  # up
                z = HSIZE
                x = axB - HSIZE
                y = axA - HSIZE
            elif i == 5:  # down
                z = -HSIZE
                x = axB - HSIZE
                y = -axA + HSIZE

            r = math.sqrt(float(x * x + y * y + z * z))
            theta = math.acos(float(z) / r)
            phi = -math.atan2(float(y), x)

            ix = int((im.shape[1] - 1) * phi / (2 * math.pi))
            iy = int((im.shape[0] - 1) * (theta) / math.pi)
            r = im[iy, ix, 0]
            g = im[iy, ix, 1]
            b = im[iy, ix, 2]
            color_side[axA, axB, 0] = r
            color_side[axA, axB, 1] = g
            color_side[axA, axB, 2] = b

            it.iternext()

        file_name = os.path.basename(input_file);
        file_name = re.sub(r'\.jpg$', '', file_name)

        output_file = os.path.join(output_dir, f"{file_name}_{side_name}.{args.type}")
        if args.quality and args.type == "jpg":
            pimg = Image.fromarray(color_side)
            pimg.save(output_file, quality=args.quality)
        else:
            imageio.imsave(output_file, color_side)

    if args.onefile:
        ifiles = []
        for i, side_name in enumerate(side_names):
            ifiles.append(imageio.v2.imread(os.path.join(output_dir, f"{file_name}_{side_name}.{args.type}")))
        onefile = np.concatenate(ifiles, axis=1)
        onefile_output = os.path.join(output_dir, f"{file_name}_onefile.{args.type}")
        imageio.imsave(onefile_output, onefile)
        for i, side_name in enumerate(side_names):
            os.unlink(os.path.join(output_dir, f"{file_name}_{side_name}.{args.type}"))

def main():
    # Check if output directory exists, if not create it
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for filename in os.listdir(args.input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_file = os.path.join(args.input_dir, filename)
            process_image(input_file, args.output_dir)

if __name__ == "__main__":
    main()