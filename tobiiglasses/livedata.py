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

import logging
import os
import math
import numpy as np
import json

class LiveData:

    def __init__(self):
        self.__livedatajson__ = [] # List of livedata json objects (defined in livedatajson.py)
        self.__gazedata__ = GazeData()

    def addJSONItem(self, json_item):
        sample = self.getLiveDataJSONFromJSON(json_item)
        self.__livedatajson__.append(sample)
        self.__gazedata__.add(sample)

    def decodeJSON(self, json_item):

        if TobiiJSONProperties.PupilCenter.key in json_item:
            return PupilCenter(json_item)
        elif TobiiJSONProperties.PupilDiameter.key in json_item:
            return PupilDiameter(json_item)
        elif TobiiJSONProperties.GazeDirection.key in json_item:
            return GazeDirection(json_item)
        elif TobiiJSONProperties.GazePosition.key in json_item:
            return GazePosition(json_item)
        elif TobiiJSONProperties.GazePosition3d.key in json_item:
            return GazePosition3d(json_item)
        elif TobiiJSONProperties.APISynch_ETS.key in json_item:
            return APISynch(json_item)

            """
            2. to add other conditions
            """

        else:
            return None

    def getGazeData(self):
        return self.__gazedata__

    def getLiveDataJSON(self):
        return self.__livedatajson__

    def getLiveDataJSONFromJSON(self, json_item):
        return json.loads(json_item, object_hook=self.decodeJSON)

class GazeData:

    def __init__(self):
        self.ts = []
        self.gidx = {} # keys: timestamp in milliseconds, values: gidx
        self.logged_events = {} # keys: ts, values: event type
        self.experiment_vars = {} # keys: var_name, values: {keys: ts,  values: var_value}
        self.gp_x = {} # keys: gidx, values: gp_x
        self.gp_y = {}
        self.gp3 = {}
        self.gd_left = {}
        self.gd_right = {}
        self.gp3_depth = {}
        self.vergence = {}
        self.version = {}
        self.tilt = {}
        self.aoi = {}

    def add(self, livedatajson_item):

        if livedatajson_item is None:
            return

        if livedatajson_item.s.getValue() != 0: # Discard invalid samples
            return

        ts = livedatajson_item.ts.getValue()/1000.0 # Transform Tobii timestamp from us in ms

        if len(self.ts) > 0:
            if ts != self.ts[-1]:
                if ts >= self.ts[-1]:
                    self.ts.append(ts)
                else:
                    for j in range(1, len(self.ts)):
                        if ts > self.ts[-1 - j]:
                            self.ts.insert(len(self.ts) -1 - j,ts)
                            break
        else:
            self.ts.append(ts)

        if isinstance(livedatajson_item, APISynch):
            tvalue = livedatajson_item.type.getValue()
            tag = livedatajson_item.tag.getValue()
            if tvalue != "JsonEvent":
                if tvalue.startswith('#') and tvalue.endswith('#'):
                    if not tvalue[1:-1] in self.experiment_vars.keys():
                        self.experiment_vars[tvalue[1:-1]] = {}
                    self.experiment_vars[tvalue[1:-1]][ts] = tag
                else:
                    self.logged_events[ts] = tvalue
        else:
            gidx = livedatajson_item.gidx.getValue()
            self.gidx[ts] = gidx

        if isinstance(livedatajson_item, GazePosition):
            self.gp_x[gidx] = livedatajson_item.gp.getValue()[0]
            self.gp_y[gidx] = livedatajson_item.gp.getValue()[1]

        elif isinstance(livedatajson_item, GazePosition3d):
            self.gp3[gidx] = [ livedatajson_item.gp3.getValue()[0],
                               livedatajson_item.gp3.getValue()[1],
                               livedatajson_item.gp3.getValue()[2]]

            self.gp3_depth[gidx] = (self.gp3[gidx][0]**2 + self.gp3[gidx][1]**2 + self.gp3[gidx][2]**2)**0.5
            self.tilt[gidx] = math.atan(self.gp3[gidx][1]/self.gp3[gidx][2])*180./math.pi

        elif isinstance(livedatajson_item, GazeDirection):
            if livedatajson_item.eye.getValue() == "left":
                self.gd_left[gidx] = [ livedatajson_item.gd.getValue()[0],
                                       livedatajson_item.gd.getValue()[1],
                                       livedatajson_item.gd.getValue()[2]]
                self.version[gidx] = math.acos(self.gd_left[gidx][2])*180./math.pi

            elif livedatajson_item.eye.getValue() == "right":
                self.gd_right[gidx] = [livedatajson_item.gd.getValue()[0],
                                       livedatajson_item.gd.getValue()[1],
                                       livedatajson_item.gd.getValue()[2]]

            if gidx in self.gd_left.keys() and gidx in self.gd_right.keys():
                left_eye_dir = np.array([self.gd_left[gidx][0],self.gd_left[gidx][1], self.gd_left[gidx][2]])
                right_eye_dir = np.array([self.gd_right[gidx][0],self.gd_right[gidx][1], self.gd_right[gidx][2]])
                self.vergence[gidx] = math.acos( np.dot(left_eye_dir, right_eye_dir)/(np.linalg.norm(left_eye_dir)*np.linalg.norm(right_eye_dir)) )*180./math.pi


    def getGazePositions(self):
        gidx_filtered = dict(filter(lambda x: x[1] in self.gp_x.keys(), self.gidx.items()))
        time = list(gidx_filtered.keys())
        time.sort()
        return time, gidx_filtered, self.gp_x, self.gp_y

    def getExperimentalVarNames(self):
        return self.experiment_vars.keys()

    # Rows between t1 and t2 timestamps
    def ts_gidx_filter(self, t1, t2):
        #logging.info('Filtering gaze samples between t1: %d and t2: %d' % (t1, t2))
        return {k: v for k,v in self.gidx.items() if k>=t1 and k<=t2}

    def logged_events_filter(self, events_array):
        return {k: v for k,v in self.logged_events.items() if v in events_array}

    def logged_events_gidx_filter(self, from_event, to_event):
        gidx_filtered = {}
        res = self.logged_events_filter([from_event, to_event])
        if len(res) % 2 != 0:
            return None
        ts = list(res.keys())
        ts.sort()
        for i in range(1,len(ts)):
            ts_from = ts[i-1]
            ts_to = ts[i]
            gidx_filtered.update(self.ts_gidx_filter(ts_from, ts_to))
        return gidx_filtered


class TobiiJSONProperty:

    def __init__(self, json_key, py_type):
        self.key = json_key
        self.py_type = py_type

    def asValue(self, value):
        if type(self.py_type) is list:
            ret = []
            for i in range(0, len(value)):
                ret.append( self.py_type[i](value[i]) )
        else:
            ret = self.py_type(value)
        return ret

class TobiiJSONProperties:

    APISynch_ETS = TobiiJSONProperty("ets", str)
    APISynch_TAG = TobiiJSONProperty("tag", str)
    APISynch_Type = TobiiJSONProperty("type", str)
    Eye = TobiiJSONProperty("eye", str)
    GazeIndex = TobiiJSONProperty("gidx", int)
    GazeDirection = TobiiJSONProperty("gd", [float, float, float])
    GazePosition = TobiiJSONProperty("gp", [float, float])
    GazePosition3d = TobiiJSONProperty("gp3", [float, float, float])
    MEMS_Accelerometer = TobiiJSONProperty("acc", [float, float, float])
    MEMS_Gyroscope = TobiiJSONProperty("gy", [float, float, float])
    PupilCenter = TobiiJSONProperty("pc", [float, float, float])
    PupilDiameter = TobiiJSONProperty("pd", float)
    PTS = TobiiJSONProperty("pts", int)
    PV = TobiiJSONProperty("pv", int)
    Status = TobiiJSONProperty("s", int)
    SynchPort_Dir = TobiiJSONProperty("dir", str)
    SynchPort_Sig = TobiiJSONProperty("sig", str)
    Timestamp = TobiiJSONProperty("ts", int)
    VTS = TobiiJSONProperty("vts", int)

class TobiiJSONAttribute:

    def __init__(self, tobii_property, json_sample):
        self.__tobii_property__ = tobii_property
        self.__value__ = self.__tobii_property__.asValue(json_sample[self.__tobii_property__.key])

    def getKey(self):
        return self.__tobii_property__.key

    def getType(self):
        return self.__tobii_property__.py_type

    def getValue(self):
        return self.__value__


class PupilCenter:

    def __init__(self, json_sample):
        self.ts = TobiiJSONAttribute(TobiiJSONProperties.Timestamp, json_sample)
        self.s = TobiiJSONAttribute(TobiiJSONProperties.Status, json_sample)
        self.gidx = TobiiJSONAttribute(TobiiJSONProperties.GazeIndex, json_sample)
        self.pc = TobiiJSONAttribute(TobiiJSONProperties.PupilCenter, json_sample)
        self.eye = TobiiJSONAttribute(TobiiJSONProperties.Eye, json_sample)


class PupilDiameter:

    def __init__(self, json_sample):
        self.ts = TobiiJSONAttribute(TobiiJSONProperties.Timestamp, json_sample)
        self.s = TobiiJSONAttribute(TobiiJSONProperties.Status, json_sample)
        self.gidx = TobiiJSONAttribute(TobiiJSONProperties.GazeIndex, json_sample)
        self.pd = TobiiJSONAttribute(TobiiJSONProperties.PupilDiameter, json_sample)
        self.eye = TobiiJSONAttribute(TobiiJSONProperties.Eye, json_sample)

class GazeDirection:

    def __init__(self, json_sample):
        self.ts = TobiiJSONAttribute(TobiiJSONProperties.Timestamp, json_sample)
        self.s = TobiiJSONAttribute(TobiiJSONProperties.Status, json_sample)
        self.gidx = TobiiJSONAttribute(TobiiJSONProperties.GazeIndex, json_sample)
        self.gd = TobiiJSONAttribute(TobiiJSONProperties.GazeDirection, json_sample)
        self.eye = TobiiJSONAttribute(TobiiJSONProperties.Eye, json_sample)

class GazePosition:

    def __init__(self, json_sample):
        self.ts = TobiiJSONAttribute(TobiiJSONProperties.Timestamp, json_sample)
        self.s = TobiiJSONAttribute(TobiiJSONProperties.Status, json_sample)
        self.gidx = TobiiJSONAttribute(TobiiJSONProperties.GazeIndex, json_sample)
        self.gp = TobiiJSONAttribute(TobiiJSONProperties.GazePosition, json_sample)


class GazePosition3d:

    def __init__(self, json_sample):
        self.ts = TobiiJSONAttribute(TobiiJSONProperties.Timestamp, json_sample)
        self.s = TobiiJSONAttribute(TobiiJSONProperties.Status, json_sample)
        self.gidx = TobiiJSONAttribute(TobiiJSONProperties.GazeIndex, json_sample)
        self.gp3 = TobiiJSONAttribute(TobiiJSONProperties.GazePosition3d, json_sample)

class APISynch:

    def __init__(self, json_sample):
        self.ts = TobiiJSONAttribute(TobiiJSONProperties.Timestamp, json_sample)
        self.s = TobiiJSONAttribute(TobiiJSONProperties.Status, json_sample)
        self.ets = TobiiJSONAttribute(TobiiJSONProperties.APISynch_ETS, json_sample)
        self.type = TobiiJSONAttribute(TobiiJSONProperties.APISynch_Type, json_sample)
        self.tag = TobiiJSONAttribute(TobiiJSONProperties.APISynch_TAG, json_sample)


"""
1. To define other packages from C.6.1.6 to  C.6.1.13


"""
