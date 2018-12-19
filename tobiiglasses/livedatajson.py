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

import json

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
