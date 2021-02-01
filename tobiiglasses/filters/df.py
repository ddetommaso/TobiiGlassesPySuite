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
import tobiiglasses.gazedata
import tobiiglasses.events

class TimestampFilter(DataFrameFilter):
    def __init__(self, ts_list):
        DataFrameFilter.__init__(self)
        self.__ts_list__ = ts_list

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        if len(tslist_to_exclude) > 0:
            res = list(set(self.__ts_list__) - set(tslist_to_exclude))
        else:
            res = self.__ts_list__
        return df[tobiiglasses.gazedata.GazeData.Timestamp].isin(res)

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
        return df[tobiiglasses.gazedata.GazeData.Timestamp].between(self.__ts_list__[0], self.__ts_list__[-1])

class SingleLoggedEvent(DataFrameFilter):
    def __init__(self, logged_event):
        DataFrameFilter.__init__(self)
        self.__event__ = logged_event

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        return df[tobiiglasses.gazedata.GazeData.LoggedEvents] == self.__event__

class SingleJSONEvent(DataFrameFilter):
    def __init__(self, json_event):
        DataFrameFilter.__init__(self)
        self.__event__ = json_event

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        return df[tobiiglasses.events.GazeEvents.JSONEvents] == self.__event__

class AOI_Filter(DataFrameFilter):
    def __init__(self, aoi_labels=[]):
        DataFrameFilter.__init__(self)
        self.__aoi_labels__ = aoi_labels

    def __filter_condition__(self, df):
       if len(self.__aoi_labels__) > 0:
           return df[tobiiglasses.events.GazeEvents.AOI].isin(self.__aoi_labels__)
       else:
           return df[tobiiglasses.events.GazeEvents.AOI].notna()


class AroundLoggedEvents(DataFrameFilter):
    def __init__(self, logged_event, offset):
        DataFrameFilter.__init__(self)
        self.__logged_event__ = logged_event
        self.__offset__ = offset

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        event_index = []
        f = SingleLoggedEvent(self.__logged_event__)
        res, ts_logged_events = f.getFilteredData(df, columns=[tobiiglasses.gazedata.GazeData.Timestamp, tobiiglasses.gazedata.GazeData.LoggedEvents])
        ts_list = []
        for i in range(0, len(ts_logged_events)):
            if i==len(ts_logged_events):
                break
            if self.__offset__ >= 0:
                t_from = df[tobiiglasses.gazedata.GazeData.Timestamp] >= ts_logged_events[i]
                t_to = df[tobiiglasses.gazedata.GazeData.Timestamp] <= ts_logged_events[i] + self.__offset__
            else:
                t_from = df[tobiiglasses.gazedata.GazeData.Timestamp] >= ts_logged_events[i] + self.__offset__
                t_to = df[tobiiglasses.gazedata.GazeData.Timestamp] <= ts_logged_events[i]

            a = df[t_from & t_to]
            ts_list.extend( list(a[tobiiglasses.gazedata.GazeData.Timestamp]) )

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
        res, ts_from = f.getFilteredData(df, columns=[tobiiglasses.gazedata.GazeData.Timestamp, tobiiglasses.gazedata.GazeData.LoggedEvents])
        f = SingleLoggedEvent(self.__to__)
        res, ts_to = f.getFilteredData(df, columns=[tobiiglasses.gazedata.GazeData.Timestamp, tobiiglasses.gazedata.GazeData.LoggedEvents])
        ts_list = []
        for i in range(0, len(ts_from)):
            if i==len(ts_from) or i==len(ts_to):
                break
            t_from = df[tobiiglasses.gazedata.GazeData.Timestamp] >= ts_from[i]
            t_to = df[tobiiglasses.gazedata.GazeData.Timestamp] <= ts_to[i]
            a = df[t_from & t_to]
            ts_list.extend( list(a[tobiiglasses.gazedata.GazeData.Timestamp]) )

        f = TimestampFilter(ts_list)
        return f.__filter_condition__(df, tslist_to_exclude, columns)

class BetweenJSONEvents(DataFrameFilter):
    def __init__(self, from_jsonevent, to_jsonevent):
        DataFrameFilter.__init__(self)
        self.__from__ = from_jsonevent
        self.__to__ = to_jsonevent
        self.__interval_duration__ = None
        self.__ts_to__ = None
        self.__ts_from__ = None

    @property
    def interval_duration(self):
        return self.__interval_duration__

    @property
    def ts_from(self):
        return self.__ts_from__

    @property
    def ts_to(self):
        return self.__ts_to__

    def __filter_condition__(self, df, tslist_to_exclude=[], columns=None):
        event_index = []
        f = SingleJSONEvent(self.__from__)
        res, self.__ts_from__ = f.getFilteredData(df, columns=[tobiiglasses.gazedata.GazeData.Timestamp, tobiiglasses.events.GazeEvents.JSONEvents])
        f = SingleJSONEvent(self.__to__)
        res, self.__ts_to__ = f.getFilteredData(df, columns=[tobiiglasses.gazedata.GazeData.Timestamp, tobiiglasses.events.GazeEvents.JSONEvents])
        ts_list = []
        for i in range(0, len(self.__ts_from__)):
            if i==len(self.__ts_from__) or i==len(self.__ts_to__):
                break
            t_from = df[tobiiglasses.gazedata.GazeData.Timestamp] >= self.__ts_from__[i]
            t_to = df[tobiiglasses.gazedata.GazeData.Timestamp] <= self.__ts_to__[i]
            a = df[t_from & t_to]
            ts_list.extend( list(a[tobiiglasses.gazedata.GazeData.Timestamp]) )

        f = TimestampFilter(ts_list)
        self.__interval_duration__ = f.getIntervalDuration()
        return f.__filter_condition__(df, tslist_to_exclude, columns)
