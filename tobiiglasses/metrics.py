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

from tobiiglasses.filters.df import BetweenTimestamps
from tobiiglasses.events import GazeEvents
import numpy as np
import pandas as pd

class Stats:
    def __init__(self, df):
        self.__stats__ = df.describe()

    def __repr__(self):
        return str(self.__stats__)

    def quart25(self):
        return self.__stats__['25%']

    def quart50(self):
        return self.__stats__['50%']

    def quart75(self):
        return self.__stats__['75%']

    def count(self):
        return self.__stats__['count']

    def max(self):
        return self.__stats__['max']

    def mean(self):
        return self.__stats__['mean']

    def median(self):
        return self.quart50()

    def min(self):
        return self.__stats__['min']

    def std(self):
        return self.__stats__['std']


class Fixations_Metrics:
    def __init__(self, df):
        self.__fixations_df__ = df
        self.__ts_list__ = df[GazeEvents.Timestamp]

    def __filter__(self, ts_filter):
        if ts_filter is None:
            return (self.__fixations_df__, self.__ts_list__)
        return ts_filter.getFilteredData(self.__fixations_df__)

    def getFixationsCount(self, ts_filter=None):
        df, ts_list = self.__filter__(ts_filter)
        return len(df.values)

    def getFixationDurationStats(self, ts_filter=None):
        df, ts_list = self.__filter__(ts_filter)
        return Stats(pd.to_numeric(df[GazeEvents.EventDuration]))

    def getFixationsXStats(self, ts_filter=None):
        df, ts_list = self.__filter__(ts_filter)
        return Stats(pd.to_numeric(df[GazeEvents.Fixation_X]))

    def getFixationsYStats(self, ts_filter=None):
        df, ts_list = self.__filter__(ts_filter)
        return Stats(pd.to_numeric(df[GazeEvents.Fixation_X]))

    def getAOIs_TTFF(self, ts_onset=0):
        ts_filter = BetweenTimestamps(t1=ts_onset, t2=self.__ts_list__.iloc[-1])
        df, ts_list = self.__filter__(ts_filter)
        aois = df.AOI.unique()
        aois_ttff = {}
        for item in aois:
            res = df.loc[df.AOI == item, GazeEvents.Timestamp]
            if res.count() > 0:
                aois_ttff[item] = res.iloc[0] - ts_list[0]
            else:
                aois_ttff[item] = None
        return aois_ttff

    def getAOIs_FirstFixationDuration(self, ts_onset=0):
        ts_filter = BetweenTimestamps(t1=ts_onset, t2=self.__ts_list__.iloc[-1])
        df, ts_list = self.__filter__(ts_filter)
        aois = df.AOI.unique()
        aois_ffd = {}
        for item in aois:
            res = df.loc[df.AOI == item, GazeEvents.EventDuration]
            if res.count() > 0:
                aois_ffd[item] = res.iloc[0]
            else:
                aois_ffd[item] = None
        return aois_ffd

    def getAOIs_TotalFixationDuration(self, ts_filter=None):
        df, ts_list = self.__filter__(ts_filter)
        aois = df.AOI.unique()
        aois_tfd = {}
        tot = df.loc[:, GazeEvents.EventDuration].sum()
        for item in aois:
            aoi_sum = df.loc[df.AOI == item, GazeEvents.EventDuration].sum()
            if aoi_sum > 0:
                aois_tfd[item] = aoi_sum
            else:
                aois_tfd[item] = 0
        return aois_tfd

    def getAOIs_FixationCount(self, ts_filter=None):
        df, ts_list = self.__filter__(ts_filter)
        aois = df.AOI.unique()
        aois_tfd = {}
        for item in aois:
            aoi_count = len(df.loc[df.AOI == item])
            aois_tfd[item] = aoi_count
        return aois_tfd

    def getAOIs_FixationDurationStats(self, ts_filter=None):
        df, ts_list = self.__filter__(ts_filter)
        aois = df.AOI.unique()
        aois_tfd = {}
        for item in aois:
            aoi_df = df.loc[df.AOI == item]
            aoi_stats = Stats(pd.to_numeric(aoi_df[GazeEvents.EventDuration]))
            aois_tfd[item] = aoi_stats
        return aois_tfd
