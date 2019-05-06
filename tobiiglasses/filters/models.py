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

import pandas as pd
import math
from sortedcontainers import SortedList, SortedDict
from tobiiglasses.gazedata import GazeData

class FixationsFilter:

    def __init__(self):
        self.__x__ = None
        self.__y__ = None
        self.__fixation_index__ = 0
        self.__saccade_index__ = 0

    def filter(self, gaze_events):
        pass

    def setData(self, x, y):
        self.__x__ = x.astype('float')
        self.__y__ = y.astype('float')
        self.__validation_check__()

    def __addFixation__(self, ts, duration, fixation_x, fixation_y, gaze_events):
        if math.isnan(fixation_x) or math.isnan(fixation_y) or math.isinf(fixation_x) or math.isinf(fixation_y):
            pass
        else:
            gaze_events.addFixation(ts, self.__fixation_index__, int(duration), int(fixation_x), int(fixation_y))
            self.__fixation_index__+=1

    def __addSaccade__(self, ts, duration, saccade_start_x, saccade_start_y, saccade_end_x, saccade_end_y, gaze_events):
        gaze_events.addSaccade(ts, self.__saccade_index__, duration, saccade_start_x, saccade_start_y, saccade_end_x, saccade_end_y)
        self.__saccade_index__+=1

    def __validation_check__(self):
        if self.__x__ is None or self.__y__ is None:
            raise ValueError('The FixationFilter requires to set first x and y as pandas Series, please verify the correct use of setData()')
        if not isinstance(self.__x__, pd.core.series.Series):
            raise ValueError('The FixationFilter requires (x) variables as pandas Series')
        elif not isinstance(self.__y__, pd.core.series.Series):
            raise ValueError('The FixationFilter requires (y) variables as pandas Series')
        if len(self.__x__) != len(self.__y__):
            raise ValueError('The FixationFilter needs variables (x) and (y) with the same size')


class DataFrameFilter(object):

    def __init__(self):
        pass

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        raise NotImplementedError( "DataFrameFilter should have implemented a filter condition" )

    def getFilteredData(self, df, tslist_to_exclude=[], columns=None):
        if columns is None:
            columns = list(df.columns.values)
        res = df.filter(items=columns)
        df_filtered = res[self.__filter_condition__(res, tslist_to_exclude, columns)]
        return (df_filtered, df_filtered[GazeData.Timestamp].values)
