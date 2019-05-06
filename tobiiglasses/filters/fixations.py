# Copyright (C) 2019  Davide De Tommaso
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>
#


# Implementation of the I-DT algorithm as described in:
#
# Dario D. Salvucci and Joseph H. Goldberg. 2000. Identifying fixations and
# saccades in eye-tracking protocols. In Proceedings of the 2000 symposium
# on Eye tracking research & applications (ETRA '00). ACM, New York, NY, USA,
# 71-78. DOI=http://dx.doi.org/10.1145/355017.355028

import pandas as pd
import numpy as np
import logging
import math
from tobiiglasses.filters.models import FixationsFilter

FIXATION_MAX_DURATION = 1000

class FilterDT(FixationsFilter):
    def __init__(self, dispersion_threshold=10, duration_threshold=100):
        FixationsFilter.__init__(self)
        self.__dispersion_threshold__ = dispersion_threshold
        self.__duration_threshold__ = duration_threshold

    def __init_time_window__(self, ts, start_index):
        ts_list = []
        for stop_index in range(start_index, len(ts)):
            ts_list.append(ts[stop_index])
            if ts[stop_index]-ts[start_index] >= self.__duration_threshold__:
                break
        return (ts_list, stop_index)

    def __getCentroid__(self, x, y):
        return (np.mean(x), np.mean(y))

    def __getEuclideanDispersion__(self, x, y):
        cx, cy = self.__getCentroid__(x, y)
        c = [cx, cy]
        points = np.column_stack([x, y])
        dist = (points - c)**2
        dist = np.sum(dist, axis=1)
        dist = np.sqrt(dist)
        return max(dist)

    # dispersion defined as in the paper
    def __getDispersion__(self, x, y):
        return (max(x) - min(x)) + (max(y) - min(y))

    def filter(self, gaze_events):
        logging.info("FilterDT is processing gaze data ...")
        n_samples = self.__x__.size
        fixations_x = []
        fixations_y = []
        fixations_duration = []
        fixations_index = []
        start_index = 0
        ts = self.__x__.keys()
        while start_index < n_samples-1:
            (ts_list, stop_index) = self.__init_time_window__(ts, start_index)
            d = self.__getEuclideanDispersion__( self.__x__[ts_list], self.__y__[ts_list])
            if d <= self.__dispersion_threshold__:
                while True:
                    d = self.__getEuclideanDispersion__(self.__x__[ts_list], self.__y__[ts_list])
                    if stop_index == n_samples - 1:
                        break
                    elif d > self.__dispersion_threshold__:
                        break
                    else:
                        stop_index += 1
                        ts_list.append(ts[stop_index])
                ts_list.pop(-1)
                cx,cy = self.__getCentroid__(self.__x__[ts_list], self.__y__[ts_list])
                dur = ts_list[-1] - ts_list[0]
                if dur > FIXATION_MAX_DURATION:
                    dur = FIXATION_MAX_DURATION
                self.__addFixation__(ts_list[0], dur, cx, cy, gaze_events)
                start_index = stop_index
            else:
                start_index += 1
