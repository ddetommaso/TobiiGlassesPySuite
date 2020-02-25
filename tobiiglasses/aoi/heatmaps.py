#   Copyright (C) 2019  Davide De Tommaso
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>
#
# The following code is based on the PyGazeAnalyser/pygazeanalyser/gazeplotter.py
#   available at github.com/esdalmaijer/PyGazeAnalyser

import os
import argparse
import csv
import numpy
import matplotlib
from matplotlib import pyplot, image


class Heatmap:

    def draw_display(self, dispsize, imagefile=None):
        # construct screen (black background)
        screen = numpy.zeros((dispsize[1], dispsize[0], 3), dtype='float32')
        # if an image location has been passed, draw the image
        if imagefile != None:
            # check if the path to the image exists
            if not os.path.isfile(imagefile):
                raise Exception("ERROR in draw_display: imagefile not found at '%s'" % imagefile)
            # load image
            img = image.imread(imagefile)

            # width and height of the image
            w, h = len(img[0]), len(img)
            # x and y position of the image on the display
            x = int(dispsize[0] / 2 - w / 2)
            y = int(dispsize[1] / 2 - h / 2)
            # draw the image on the screen
            screen[y:y + h, x:x + w, :] += img
        # dots per inch
        dpi = 100.0
        # determine the figure size in inches
        figsize = (dispsize[0] / dpi, dispsize[1] / dpi)
        # create a figure
        fig = pyplot.figure(figsize=figsize, dpi=dpi, frameon=False)
        ax = pyplot.Axes(fig, [0, 0, 1, 1])
        ax.set_axis_off()
        fig.add_axes(ax)
        # plot display
        ax.axis([0, dispsize[0], 0, dispsize[1]])
        ax.imshow(screen)  # , origin='upper')

        return fig, ax

    def gaussian(self, x, sx, y=None, sy=None):
        # square Gaussian if only x values are passed
        if y == None:
            y = x
        if sy == None:
            sy = sx
        # centers
        xo = x / 2
        yo = y / 2
        # matrix of zeros
        M = numpy.zeros([y, x], dtype=float)
        # gaussian matrix
        for i in range(x):
            for j in range(y):
                M[j, i] = numpy.exp(
                    -1.0 * (((float(i) - xo) ** 2 / (2 * sx * sx)) + ((float(j) - yo) ** 2 / (2 * sy * sy))))

        return M

    def draw(self, gazepoints, dispsize, imagefile=None, alpha=0.5, savefilename=None, gaussianwh=200, gaussiansd=None):
        # IMAGE
        fig, ax = self.draw_display(dispsize, imagefile=imagefile)

        # HEATMAP
        # Gaussian
        gwh = gaussianwh
        gsdwh = gwh / 6 if (gaussiansd is None) else gaussiansd
        gaus = self.gaussian(gwh, gsdwh)
        # matrix of zeroes
        strt = int(gwh / 2)
        heatmapsize = dispsize[1] + 2 * strt, dispsize[0] + 2 * strt
        heatmap = numpy.zeros(heatmapsize, dtype=float)
        # create heatmap
        for i in range(0, len(gazepoints)):
            # get x and y coordinates
            x = strt + int(gazepoints[i][0]) - int(gwh / 2)
            y = strt + int(gazepoints[i][1]) - int(gwh / 2)
            # correct Gaussian size if either coordinate falls outside of
            # display boundaries
            if (not 0 < x < dispsize[0]) or (not 0 < y < dispsize[1]):
                hadj = [0, gwh];
                vadj = [0, gwh]
                if 0 > x:
                    hadj[0] = abs(x)
                    x = 0
                elif dispsize[0] < x:
                    hadj[1] = gwh - int(x - dispsize[0])
                if 0 > y:
                    vadj[0] = abs(y)
                    y = 0
                elif dispsize[1] < y:
                    vadj[1] = gwh - int(y - dispsize[1])
                # add adjusted Gaussian to the current heatmap
                try:
                    heatmap[y:y + vadj[1], x:x + hadj[1]] += gaus[vadj[0]:vadj[1], hadj[0]:hadj[1]] * 1
                except:
                    # fixation was probably outside of display
                    pass
            else:
                # add Gaussian to the current heatmap
                heatmap[y:y + gwh, x:x + gwh] += gaus * 1
        # resize heatmap
        heatmap = heatmap[strt:dispsize[1] + strt, strt:dispsize[0] + strt]
        # remove zeros
        lowbound = numpy.mean(heatmap[heatmap > 0])
        heatmap[heatmap < lowbound] = numpy.NaN
        # draw heatmap on top of image
        ax.imshow(heatmap, cmap='jet', alpha=alpha)

        # FINISH PLOT
        # invert the y axis, as (0,0) is top left on a display
        ax.invert_yaxis()
        # save the figure if a file name was provided
        if savefilename != None:
            fig.savefig(savefilename)

        return fig
