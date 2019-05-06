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

import pandas as pd
import numpy as np
import tobiiglasses
import logging
import os
from sortedcontainers import SortedList, SortedDict
from tobiiglasses.gazedata import GazeItem, GazeData
from tobiiglasses.filters.df import TimestampFilter
from tobiiglasses.exporter import FixationsCSV


class GazeEvents:
    Timestamp = "Timestamp"
    LoggedEvents = "Logged Events"
    GazeType = "Gaze Type"
    EventIndex = "Event Index"
    EventDuration = "Event Duration"
    Fixation_X = "Fixation X"
    Fixation_Y = "Fixation Y"
    AOI = "AOI"
    AOI_Distance = "AOI Distance"
    Saccade_Start_X = "Saccade Start X"
    Saccade_Start_Y = "Saccade Start Y"
    Saccade_End_X = "Saccade End X"
    Saccade_End_Y = "Saccade End Y"

    InputFixationFilterX = GazeData.GazePixelX
    InputFixationFilterY = GazeData.GazePixelY

    def __init__(self):
        self.__events__ = SortedDict({})
        self.__init_datatypes__()
        self.__fixation_index__ = 0
        self.__saccade_index__ = 0
        self.__ts_processed__ = []

    def __getitem__(self, key):
        return self.__events__[key]

    def __getFilteredGazeData__(self, gazedata_df, ts_filter=None):
        if ts_filter is None:
            ts_filter = TimestampFilter(list(gazedata_df[GazeData.Timestamp]))
        df, ts_list = ts_filter.getFilteredData(gazedata_df, self.__ts_processed__)
        self.__ts_processed__.extend(ts_list)
        return df, ts_list

    def __init_datatypes__(self):
        self.__events__[GazeEvents.Timestamp] = GazeItem(GazeEvents.Timestamp, np.dtype('float'))
        self.__events__[GazeEvents.LoggedEvents] = GazeItem(GazeEvents.LoggedEvents, np.dtype(object))
        self.__events__[GazeEvents.GazeType] = GazeItem(GazeEvents.GazeType, np.dtype(object))
        self.__events__[GazeEvents.Fixation_X] = GazeItem(GazeEvents.Fixation_X, np.dtype('u4'))
        self.__events__[GazeEvents.Fixation_Y] = GazeItem(GazeEvents.Fixation_Y, np.dtype('u4'))
        self.__events__[GazeEvents.EventIndex] = GazeItem(GazeEvents.EventIndex, np.dtype('u4'))
        self.__events__[GazeEvents.EventDuration] = GazeItem(GazeEvents.EventDuration, np.dtype('u4'))
        self.__events__[GazeEvents.AOI] = GazeItem(GazeEvents.AOI, np.dtype(object))
        self.__events__[GazeEvents.AOI_Distance] = GazeItem(GazeEvents.AOI_Distance, np.dtype('f2'))
        self.__events__[GazeEvents.Saccade_Start_X] = GazeItem(GazeEvents.Saccade_Start_X, np.dtype('f2'))
        self.__events__[GazeEvents.Saccade_Start_Y] = GazeItem(GazeEvents.Saccade_Start_Y, np.dtype('f2'))
        self.__events__[GazeEvents.Saccade_End_X] = GazeItem(GazeEvents.Saccade_End_X, np.dtype('f2'))
        self.__events__[GazeEvents.Saccade_End_Y] = GazeItem(GazeEvents.Saccade_End_Y, np.dtype('f2'))

    def addFixation(self, ts, index, duration, fixation_x, fixation_y, aoi=None):
        self.__events__[GazeEvents.Timestamp][ts] = ts
        self.__events__[GazeEvents.GazeType][ts] = "Fixation"
        self.__events__[GazeEvents.EventIndex][ts] = index
        self.__events__[GazeEvents.EventDuration][ts] = duration
        self.__events__[GazeEvents.Fixation_X][ts] = fixation_x
        self.__events__[GazeEvents.Fixation_Y][ts] = fixation_y

    def addLoggedEvent(self, ts, logged_event):
        self.__events__[GazeEvents.Timestamp][ts] = ts
        self.__events__[GazeEvents.LoggedEvents][ts] = logged_event

    def addSaccade(self, ts, index, duration, saccade_start_x, saccade_start_y, saccade_end_x, saccade_end_y):
        self.__events__[GazeEvents.Timestamp][ts] = ts
        self.__events__[GazeEvents.GazeType][ts] = "Saccade"
        self.__events__[GazeEvents.EventIndex][ts] = index
        self.__events__[GazeEvents.EventDuration][ts] = duration
        self.__events__[GazeEvents.Saccade_Start_X][ts] = saccade_start_x
        self.__events__[GazeEvents.Saccade_Start_Y][ts] = saccade_start_y
        self.__events__[GazeEvents.Saccade_End_X][ts] = saccade_end_x
        self.__events__[GazeEvents.Saccade_End_Y][ts] = saccade_end_y

    def exportCSV(self, filepath, filename, ts_filter=None):
        fixations_df = self.toDataFrame(ts_filter).dropna(subset=[GazeEvents.Fixation_X, GazeEvents.Fixation_Y])
        exp = FixationsCSV(filepath, filename, fixations_df)
        exp.toCSV()

    def exportDF(self, filepath, filename, ts_filter=None):
        logging.info('Exporting gaze events in %s' % filename)
        path = os.path.join(filepath, filename)
        self.toDataFrame(ts_filter).dropna(subset=[GazeEvents.Fixation_X, GazeEvents.Fixation_Y]).to_pickle(path)

    def filterFixations(self, fixation_filter, gazedata_df, ts_filter=None, aoi_model=None):
        df, ts_list = self.__getFilteredGazeData__(gazedata_df, ts_filter)
        if not df.empty:
            x = pd.Series(df[GazeEvents.InputFixationFilterX])
            y = pd.Series(df[GazeEvents.InputFixationFilterY])
            fixation_filter.setData(x,y)
            fixation_filter.filter(self)

    def getFixations(self, ts_filter=None):
        df = self.toDataFrame(ts_filter)
        return df.loc[df[GazeEvents.GazeType] == 'Fixation']

    def getSaccades(self, ts_filter=None):
        df = self.toDataFrame(ts_filter)
        return df.loc[df[GazeEvents.GazeType] == 'Saccade']

    def getFixationsAsNumpy(self, ts_filter):
        fixations_df = self.toDataFrame(ts_filter).dropna(subset=[GazeEvents.Fixation_X, GazeEvents.Fixation_Y])
        x = fixations_df[GazeEvents.Fixation_X].values
        y = fixations_df[GazeEvents.Fixation_Y].values
        ts_list = fixations_df[GazeEvents.Timestamp].values.tolist()
        return (ts_list, x, y)

    def getTimestamps(self):
        return list(self.__events__[GazeEvents.Timestamp].values())

    def setAOI(self, ts, aoi_label, aoi_distance):
        self.__events__[GazeEvents.AOI][ts] = aoi_label
        self.__events__[GazeEvents.AOI_Distance][ts] = aoi_distance

    def toDataFrame(self, ts_filter=None):
        table = {}
        for label, data in self.__events__.items():
            table[label] = pd.Series(data.getData(), dtype=object)
        df = pd.DataFrame(table)
        if ts_filter is None:
            return df
        else:
            filtered_df, ts_list = ts_filter.getFilteredData(df)
            return filtered_df

    def to_pickle(self, filename, ts_filter=None):
        self.toDataFrame(ts_filter).to_pickle(filename)
