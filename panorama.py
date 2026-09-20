#!/usr/bin/env python

'''
Stitching sample
================

Show how to use Stitcher API from python in a simple way to stitch panoramas
or scans.
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv

import argparse
import sys

modes = (cv.Stitcher_PANORAMA, cv.Stitcher_SCANS)

parser = argparse.ArgumentParser(prog='stitching.py', description='Stitching sample.')
parser.add_argument('--mode',
    type = int, choices = modes, default = cv.Stitcher_PANORAMA,
    help = 'Determines configuration of stitcher. The default is `PANORAMA` (%d), '
         'mode suitable for creating photo panoramas. Option `SCANS` (%d) is suitable '
         'for stitching materials under affine transformation, such as scans.' % modes)
parser.add_argument('--output', default = 'result.jpg',
    help = 'Resulting image. The default is `result.jpg`.')
parser.add_argument('--conf', type = float, default = 1.0,
    help = 'Stitcher panorama confidence threshold (setPanoConfidenceThresh). Default 1.0.')
parser.add_argument('--match-conf', type = float, default = 0.3,
    help = 'Feature-matcher inlier confidence used only for the used/dropped diagnostic. Default 0.3.')
parser.add_argument('img', nargs='+', help = 'input images')

__doc__ += '\n' + parser.format_help()


def report_used_images(imgs, names, match_conf=0.3):
    """Print which input images survive matching, so silently-dropped ones are visible.
    match_conf is the feature-matcher inlier confidence (typically 0.3-0.65),
    a different scale from the stitcher's own panoConfidenceThresh."""
    try:
        finder = cv.SIFT_create()
        features = [cv.detail.computeImageFeatures2(finder, img) for img in imgs]
        matcher = cv.detail.BestOf2NearestMatcher_create(False, match_conf)
        pairwise = matcher.apply2(features)
        matcher.collectGarbage()
        indices = cv.detail.leaveBiggestComponent(features, pairwise, match_conf)
        used = sorted(int(i) for i in np.array(indices).flatten())
        print("images used: %d of %d" % (len(used), len(imgs)))
        for i, name in enumerate(names):
            print("  %-40s %s" % (name, "USED" if i in used else "DROPPED"))
    except Exception as e:
        print("could not run match diagnostics:", e)


def main():
    args = parser.parse_args()

    # read input images
    imgs = []
    for img_name in args.img:
        img = cv.imread(cv.samples.findFile(img_name))
        if img is None:
            print("can't read image " + img_name)
            sys.exit(-1)
        imgs.append(img)

    report_used_images(imgs, args.img, args.match_conf)

    #![stitching]
    stitcher = cv.Stitcher.create(args.mode)
    stitcher.setPanoConfidenceThresh(args.conf)
    status, pano = stitcher.stitch(imgs)

    if status != cv.Stitcher_OK:
        print("Can't stitch images, error code = %d" % status)
        sys.exit(-1)
    #![stitching]

    cv.imwrite(args.output, pano)
    print("stitching completed successfully. %s saved!" % args.output)

    print('Done')


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()