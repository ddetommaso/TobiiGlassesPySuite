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
import math
import os
import re
import numpy as np
import pandas as pd
import tobiiglasses.entities
import tobiiglasses.utils
from sortedcontainers import SortedList, SortedDict
from tobiiglasses.livedata import *

logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.DEBUG)

class GazeItem:
    def __init__(self, label, dtype):
        self.__label__ = label
        self.__data__ = SortedDict({})
        self.__dtype__ = dtype

    def __getitem__(self, key):
        return self.__data__[key]

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def getData(self):
        return self.__data__

    def getLabel(self):
        return self.__label__

    def getType(self):
        return self.__dtype__

    def keys(self):
        return list(self.__data__.keys())

    def pop(self, key):
        self.__data__.pop(key)

    def values(self):
        return list(self.__data__.values())

class GazeData:
    Timestamp = "Timestamp"
    Gidx = "Gaze Index"
    LoggedEvents = "Logged Events"
    GazePositionX = "Gaze Position X"
    GazePositionY = "Gaze Position Y"
    Gaze3DPositionX = "Gaze 3D Position X"
    Gaze3DPositionY = "Gaze 3D Position Y"
    Gaze3DPositionZ = "Gaze 3D Position Z"
    Depth = "Gaze Depth"
    Tilt = "Gaze Tilt"
    Vergence = "Gaze Vergence"
    Version = "Gaze Version"
    GazeDirectionX_Left = "Gaze Direction Left X"
    GazeDirectionY_Left = "Gaze Direction Left Y"
    GazeDirectionZ_Left = "Gaze Direction Left Z"
    GazeDirectionX_Right = "Gaze Direction Right X"
    GazeDirectionY_Right = "Gaze Direction Right Y"
    GazeDirectionZ_Right = "Gaze Direction Right Z"
    GazePixelX = "Gaze Pixel X"
    GazePixelY = "Gaze Pixel Y"
    PupilCenterX_Left = "Pupil Center Left X"
    PupilCenterY_Left = "Pupil Center Left Y"
    PupilCenterZ_Left = "Pupil Center Left Z"
    PupilCenterX_Right = "Pupil Center Right X"
    PupilCenterY_Right = "Pupil Center Right Y"
    PupilCenterZ_Right = "Pupil Center Right Z"
    PupilDiameter_Left = "Pupil Diameter Left"
    PupilDiameter_Right = "Pupil Diameter Right"


    def __init__(self, segment):
        self.__gazedata__ = {}
        self.__gd_right__ = {}
        self.__gd_left__ = {}
        self.__experiment_vars__ = {} # keys: var_name, values: {keys: ts,  values: var_value}
        self.__experiment_vars_headers__ = []
        self.__rec_id__ = None
        self.__pa_name__ = None
        self.__pr_name__ = None
        self.__segment__ = segment
        self.__vts__ = SortedDict({})
        self.__init_datatypes__()
        self.__importGazeData__(segment)
        self.__importExpVars__()

    def __addItem__(self, livedatajson_item):
        if livedatajson_item is None:
            return
        if livedatajson_item.s.getValue() != 0: # Discard invalid samples
            return
        ts = livedatajson_item.ts.getValue()/1000.0

        if isinstance(livedatajson_item, VTS):
            self.__vts__[ts] = livedatajson_item.vts.getValue()/1000.0
            return
        else:
            self.__gazedata__[GazeData.Timestamp][ts] = ts # Conversion in milliseconds
        if isinstance(livedatajson_item, APISynch):
            tvalue = livedatajson_item.type.getValue()
            tag = livedatajson_item.tag.getValue()
            if tvalue != "JsonEvent":

                if tvalue.startswith('#') and tvalue.endswith('#'):
                    var_name = tvalue[1:-1]
                    if not var_name in self.__experiment_vars__.keys():
                        self.__experiment_vars__[var_name] = SortedDict({})
                    self.__experiment_vars__[var_name][ts] = tag

                elif tvalue.startswith('@') and tvalue.endswith('@'):
                    vars_list = eval(tvalue[1:-1])
                    values_list = eval(tag)
                    for i in range(0, len(vars_list)):
                        var_name = vars_list[i]
                        value = values_list[i]
                        if not var_name in self.__experiment_vars__.keys():
                            self.__experiment_vars__[var_name] = SortedDict({})
                        self.__experiment_vars__[var_name][ts] = value
                else:
                    self.__gazedata__[GazeData.LoggedEvents][ts] = tvalue

            else:
                self.__gazedata__[GazeData.Timestamp].pop(ts)
            return
        else:
            gidx = livedatajson_item.gidx.getValue()
            self.__gazedata__[GazeData.Gidx][ts] = gidx
        if isinstance(livedatajson_item, GazePosition):
            self.__gazedata__[GazeData.GazePositionX][ts] = livedatajson_item.gp.getValue()[0]
            self.__gazedata__[GazeData.GazePositionY][ts] = livedatajson_item.gp.getValue()[1]
            self.__gazedata__[GazeData.GazePixelX][ts] = int(1920*self.__gazedata__[GazeData.GazePositionX][ts])
            self.__gazedata__[GazeData.GazePixelY][ts] = int(1080*self.__gazedata__[GazeData.GazePositionY][ts])
            return
        elif isinstance(livedatajson_item, GazePosition3d):
            self.__gazedata__[GazeData.Gaze3DPositionX][ts] = livedatajson_item.gp3.getValue()[0]
            self.__gazedata__[GazeData.Gaze3DPositionY][ts] = livedatajson_item.gp3.getValue()[1]
            self.__gazedata__[GazeData.Gaze3DPositionZ][ts] = livedatajson_item.gp3.getValue()[2]
            self.__gazedata__[GazeData.Depth][ts] = (self.__gazedata__[GazeData.Gaze3DPositionX][ts]**2 + self.__gazedata__[GazeData.Gaze3DPositionY][ts]**2 + self.__gazedata__[GazeData.Gaze3DPositionZ][ts]**2)**0.5
            self.__gazedata__[GazeData.Tilt][ts] = math.atan(self.__gazedata__[GazeData.Gaze3DPositionY][ts]/self.__gazedata__[GazeData.Gaze3DPositionZ][ts])*180./math.pi
            return
        elif isinstance(livedatajson_item, GazeDirection):
            if livedatajson_item.eye.getValue() == "left":
                self.__gazedata__[GazeData.GazeDirectionX_Left][ts] = livedatajson_item.gd.getValue()[0]
                self.__gazedata__[GazeData.GazeDirectionY_Left][ts] = livedatajson_item.gd.getValue()[1]
                self.__gazedata__[GazeData.GazeDirectionZ_Left][ts] = livedatajson_item.gd.getValue()[2]
                self.__gazedata__[GazeData.Version][ts] = math.acos(self.__gazedata__[GazeData.GazeDirectionZ_Left][ts])*180./math.pi
                self.__gd_left__[gidx] = np.array([self.__gazedata__[GazeData.GazeDirectionX_Left][ts],self.__gazedata__[GazeData.GazeDirectionY_Left][ts], self.__gazedata__[GazeData.GazeDirectionZ_Left][ts]])
                return
            elif livedatajson_item.eye.getValue() == "right":
                self.__gazedata__[GazeData.GazeDirectionX_Right][ts] = livedatajson_item.gd.getValue()[0]
                self.__gazedata__[GazeData.GazeDirectionY_Right][ts] = livedatajson_item.gd.getValue()[1]
                self.__gazedata__[GazeData.GazeDirectionZ_Right][ts] = livedatajson_item.gd.getValue()[2]
                self.__gazedata__[GazeData.Version][ts] = math.acos(self.__gazedata__[GazeData.GazeDirectionZ_Right][ts])*180./math.pi
                self.__gd_right__[gidx] = np.array([self.__gazedata__[GazeData.GazeDirectionX_Right][ts], self.__gazedata__[GazeData.GazeDirectionY_Right][ts], self.__gazedata__[GazeData.GazeDirectionZ_Right][ts]])
            try:
                self.__gazedata__[GazeData.Vergence][ts] = math.acos( np.dot(self.__gd_left__[gidx], self.__gd_right__[gidx])/(np.linalg.norm(self.__gd_left__[gidx])*np.linalg.norm(self.__gd_right__[gidx])) )*180./math.pi
            except:
                pass
        elif isinstance(livedatajson_item, PupilCenter):
            if livedatajson_item.eye.getValue() == "left":
                self.__gazedata__[GazeData.PupilCenterX_Left][ts] = livedatajson_item.pc.getValue()[0]
                self.__gazedata__[GazeData.PupilCenterY_Left][ts] = livedatajson_item.pc.getValue()[1]
                self.__gazedata__[GazeData.PupilCenterZ_Left][ts] = livedatajson_item.pc.getValue()[2]
                return
            elif livedatajson_item.eye.getValue() == "right":
                self.__gazedata__[GazeData.PupilCenterX_Right][ts] = livedatajson_item.pc.getValue()[0]
                self.__gazedata__[GazeData.PupilCenterY_Right][ts] = livedatajson_item.pc.getValue()[1]
                self.__gazedata__[GazeData.PupilCenterZ_Right][ts] = livedatajson_item.pc.getValue()[2]
                return
        elif isinstance(livedatajson_item, PupilDiameter):
            if livedatajson_item.eye.getValue() == "left":
                self.__gazedata__[GazeData.PupilDiameter_Left][ts] = livedatajson_item.pd.getValue()
                return
            elif livedatajson_item.eye.getValue() == "right":
                self.__gazedata__[GazeData.PupilDiameter_Right][ts] = livedatajson_item.pd.getValue()
                return

    def __decodeJSON__(self, json_item):
        if TobiiJSONProperties.PupilCenter.key in json_item:
            item = PupilCenter(json_item)
        elif TobiiJSONProperties.PupilDiameter.key in json_item:
            item = PupilDiameter(json_item)
        elif TobiiJSONProperties.GazeDirection.key in json_item:
            item = GazeDirection(json_item)
        elif TobiiJSONProperties.GazePosition.key in json_item:
            item = GazePosition(json_item)
        elif TobiiJSONProperties.GazePosition3d.key in json_item:
            item = GazePosition3d(json_item)
        elif TobiiJSONProperties.APISynch_ETS.key in json_item:
            item = APISynch(json_item)
        elif TobiiJSONProperties.VTS.key in json_item:
            item = VTS(json_item)
        else:
            item = None
        self.__addItem__(item)

    def __importExpVars__(self):
        self.__experiment_vars_headers__ = []
        for k,v in self.__experiment_vars__.items():
            current_var = None
            self.__gazedata__[k] = GazeItem(k, np.dtype(str))
            self.__experiment_vars_headers__.append(k)
            for ts in self.__gazedata__[GazeData.Timestamp].getData().values():
                try:
                    current_var = v[ts]
                except:
                    pass
                self.__gazedata__[k][ts] = current_var

    def __importGazeData__(self, segment):
        filepath = segment.getSegmentPath()
        logging.info('Importing segment %s in %s' % (segment.getId(), filepath))
        tobiiglasses.utils.import_json_items_from_gzipfile(filepath, tobiiglasses.entities.TobiiSegment.livedata_filename, self.__decodeJSON__)

    def __init_datatypes__(self):
        self.__gazedata__[GazeData.Timestamp] = GazeItem(GazeData.Timestamp, np.dtype('float'))
        self.__gazedata__[GazeData.Gidx] = GazeItem(GazeData.Gidx, np.dtype('u4'))
        self.__gazedata__[GazeData.LoggedEvents] = GazeItem(GazeData.LoggedEvents, np.dtype(object))
        self.__gazedata__[GazeData.GazePositionX] = GazeItem(GazeData.GazePositionX, np.dtype('float'))
        self.__gazedata__[GazeData.GazePositionY] = GazeItem(GazeData.GazePositionY, np.dtype('float'))
        self.__gazedata__[GazeData.GazePixelX] = GazeItem(GazeData.GazePixelX, np.dtype('u4'))
        self.__gazedata__[GazeData.GazePixelY] = GazeItem(GazeData.GazePixelY, np.dtype('u4'))
        self.__gazedata__[GazeData.Gaze3DPositionX] = GazeItem(GazeData.Gaze3DPositionX, np.dtype('float'))
        self.__gazedata__[GazeData.Gaze3DPositionY] = GazeItem(GazeData.Gaze3DPositionY, np.dtype('float'))
        self.__gazedata__[GazeData.Gaze3DPositionZ] = GazeItem(GazeData.Gaze3DPositionZ, np.dtype('float'))
        self.__gazedata__[GazeData.Depth] = GazeItem(GazeData.Depth, np.dtype('float'))
        self.__gazedata__[GazeData.Vergence] = GazeItem(GazeData.Vergence, np.dtype('float'))
        self.__gazedata__[GazeData.Version] = GazeItem(GazeData.Version, np.dtype('float'))
        self.__gazedata__[GazeData.Tilt] = GazeItem(GazeData.Tilt, np.dtype('float'))
        self.__gazedata__[GazeData.GazeDirectionX_Left] = GazeItem(GazeData.GazeDirectionX_Left, np.dtype('float'))
        self.__gazedata__[GazeData.GazeDirectionY_Left] = GazeItem(GazeData.GazeDirectionY_Left, np.dtype('float'))
        self.__gazedata__[GazeData.GazeDirectionZ_Left] = GazeItem(GazeData.GazeDirectionZ_Left, np.dtype('float'))
        self.__gazedata__[GazeData.GazeDirectionX_Right] = GazeItem(GazeData.GazeDirectionX_Right, np.dtype('float'))
        self.__gazedata__[GazeData.GazeDirectionY_Right] = GazeItem(GazeData.GazeDirectionY_Right, np.dtype('float'))
        self.__gazedata__[GazeData.GazeDirectionZ_Right] = GazeItem(GazeData.GazeDirectionZ_Right, np.dtype('float'))
        self.__gazedata__[GazeData.PupilCenterX_Left] = GazeItem(GazeData.PupilCenterX_Left, np.dtype('float'))
        self.__gazedata__[GazeData.PupilCenterY_Left] = GazeItem(GazeData.PupilCenterY_Left, np.dtype('float'))
        self.__gazedata__[GazeData.PupilCenterZ_Left] = GazeItem(GazeData.PupilCenterZ_Left, np.dtype('float'))
        self.__gazedata__[GazeData.PupilCenterX_Right] = GazeItem(GazeData.PupilCenterX_Right, np.dtype('float'))
        self.__gazedata__[GazeData.PupilCenterY_Right] = GazeItem(GazeData.PupilCenterY_Right, np.dtype('float'))
        self.__gazedata__[GazeData.PupilCenterZ_Right] = GazeItem(GazeData.PupilCenterZ_Right, np.dtype('float'))
        self.__gazedata__[GazeData.PupilDiameter_Left] = GazeItem(GazeData.PupilDiameter_Left, np.dtype('float'))
        self.__gazedata__[GazeData.PupilDiameter_Right] = GazeItem(GazeData.PupilDiameter_Right, np.dtype('float'))

    def getData(self):
        return self.__gazedata__.values

    def getExpVarsHeaders(self):
        return self.__experiment_vars_headers__

    def getLoggedEvents(self):
        return self.__gazedata__[GazeData.LoggedEvents].getData()

    def getTimestamps(self):
        return self.__gazedata__[GazeData.Timestamp].values()

    def getVTS(self):
        return self.__vts__

    def toDataFrame(self):
        table = {}
        for label, data in self.__gazedata__.items():
            table[label] = pd.Series(data.getData(), dtype=object)
        return pd.DataFrame(table)

    def to_pickle(self, filename):
        self.toDataFrame().to_pickle(filename)
