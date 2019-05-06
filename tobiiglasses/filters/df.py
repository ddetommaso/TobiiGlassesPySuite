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

from tobiiglasses.filters.models import DataFrameFilter
from tobiiglasses.gazedata import GazeData

class TimestampFilter(DataFrameFilter):
    def __init__(self, ts_list):
        DataFrameFilter.__init__(self)
        self.__ts_list__ = ts_list

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        if len(tslist_to_exclude) > 0:
            res = list(set(self.__ts_list__) - set(tslist_to_exclude))
        else:
            res = self.__ts_list__
        return df[GazeData.Timestamp].isin(res)

    def getIntervalDuration(self):
        ts_list = self.getTimestamps()
        return (ts_list[-1] - ts_list[0])

    def getTimestamps(self):
        return self.__ts_list__


class SingleTimestamp(TimestampFilter):
    def __init__(self, ts):
        TimestampFilter.__init__(self, [ts])

class BetweenTimestamps(TimestampFilter):
    def __init__(self, t1, t2):
        TimestampFilter.__init__(self, list(range(int(t1),int(t2)+1)))

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        return df[GazeData.Timestamp].between(self.__ts_list__[0], self.__ts_list__[-1])

class SingleLoggedEvent(DataFrameFilter):
    def __init__(self, logged_event):
        DataFrameFilter.__init__(self)
        self.__event__ = logged_event

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        return df[GazeData.LoggedEvents] == self.__event__

class AroundLoggedEvents(DataFrameFilter):
    def __init__(self, logged_event, offset):
        DataFrameFilter.__init__(self)
        self.__logged_event__ = logged_event
        self.__offset__ = offset

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        event_index = []
        f = SingleLoggedEvent(self.__logged_event__)
        res, ts_logged_events = f.getFilteredData(df, columns=[GazeData.Timestamp, GazeData.LoggedEvents])
        ts_list = []
        for i in range(0, len(ts_logged_events)):
            if i==len(ts_logged_events):
                break
            if self.__offset__ >= 0:
                t_from = df[GazeData.Timestamp] >= ts_logged_events[i]
                t_to = df[GazeData.Timestamp] <= ts_logged_events[i] + self.__offset__
            else:
                t_from = df[GazeData.Timestamp] >= ts_logged_events[i] + self.__offset__
                t_to = df[GazeData.Timestamp] <= ts_logged_events[i]

            a = df[t_from & t_to]
            ts_list.extend( list(a[GazeData.Timestamp]) )

        f = TimestampFilter(ts_list)
        return f.__filter_condition__(df, tslist_to_exclude, columns)


class BetweenLoggedEvents(DataFrameFilter):
    def __init__(self, from_loggedevent, to_loggedevent):
        DataFrameFilter.__init__(self)
        self.__from__ = from_loggedevent
        self.__to__ = to_loggedevent

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        event_index = []
        f = SingleLoggedEvent(self.__from__)
        res, ts_from = f.getFilteredData(df, columns=[GazeData.Timestamp, GazeData.LoggedEvents])
        f = SingleLoggedEvent(self.__to__)
        res, ts_to = f.getFilteredData(df, columns=[GazeData.Timestamp, GazeData.LoggedEvents])
        ts_list = []
        for i in range(0, len(ts_from)):
            if i==len(ts_from) or i==len(ts_to):
                break
            t_from = df[GazeData.Timestamp] >= ts_from[i]
            t_to = df[GazeData.Timestamp] <= ts_to[i]
            a = df[t_from & t_to]
            ts_list.extend( list(a[GazeData.Timestamp]) )

        f = TimestampFilter(ts_list)
        return f.__filter_condition__(df, tslist_to_exclude, columns)
