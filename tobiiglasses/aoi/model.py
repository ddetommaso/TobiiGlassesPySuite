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

import numpy as np
import cv2
import bisect
import os
import matplotlib.path as mplPath
from tobiiglasses.aoi.heatmaps import Heatmap

class AOI_Item:

    def __init__(self, aoi_id, detected_features_points, snapshot_filename, features_points,landmarks=[], aoi_score=100):
        self.aoi_id = aoi_id
        self.detected_features_points = detected_features_points
        self.snapshot_filename = snapshot_filename
        self.snapshot = cv2.imread(snapshot_filename)
        self.features_points = features_points
        self.landmarks = landmarks
        self.aoi_score = aoi_score


class AOI:

    def __init__(self):
        self.__aoi_regions__ = {}
        self.__aoi_hits__ = {}
        self.__aoi_items__ = {}

    def apply(self, opencvMat, ts, gaze_x, gaze_y, gaze_events=None):
        for item in self.getDetectedItems(opencvMat):
            detected_features_points = item.detected_features_points
            aoi_id = item.aoi_id
            if not aoi_id in self.__aoi_items__.keys():
                self.__aoi_items__[aoi_id] = item
            if not aoi_id in self.__aoi_regions__.keys():
                self.__aoi_regions__[aoi_id] = {}
                self.__aoi_hits__[aoi_id] = {}

            H, status = cv2.findHomography(item.features_points, detected_features_points)
            rows, cols, ch = item.snapshot.shape

            bounding_box_src = np.array([[item.features_points[0][0],item.features_points[0][1],1],
                                        [item.features_points[1][0], item.features_points[1][1],1],
                                        [item.features_points[3][0], item.features_points[3][1],1],
                                        [item.features_points[2][0], item.features_points[2][1],1]])
            bounding_box_dst = H.dot(bounding_box_src.T)

            bounding_box_dst = np.array([[bounding_box_dst[0,0]/bounding_box_dst[2,0], bounding_box_dst[1,0]/bounding_box_dst[2,0]],
                                             [bounding_box_dst[0,1]/bounding_box_dst[2,1], bounding_box_dst[1,1]/bounding_box_dst[2,1]],
                                             [bounding_box_dst[0,2]/bounding_box_dst[2,2], bounding_box_dst[1,2]/bounding_box_dst[2,2]],
                                             [bounding_box_dst[0,3]/bounding_box_dst[2,3], bounding_box_dst[1,3]/bounding_box_dst[2,3]] ])

            self.__aoi_regions__[aoi_id][ts] = bounding_box_dst


            if self.contains(ts, aoi_id, gaze_x, gaze_y):
                p = [gaze_x, gaze_y, 1]
                q = np.linalg.inv(H).dot(p)
                q /= q[2]
                self.__aoi_hits__[aoi_id][ts] = [q[0], q[1]]
                label_color = (0, 255, 0)
            else:
                label_color = (255, 0, 0)

            cv2.putText(opencvMat, aoi_id, (int(self.__aoi_regions__[aoi_id][ts][0][0]), int(self.__aoi_regions__[aoi_id][ts][0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

    def getDetectedItems(self, opencvMat):
        raise NotImplementedError( "AOIs should have implemented getDetectedItems() method" )

    def getClosestRegion(self, aoi_id, ts):
        ts_list = list(self.__aoi_regions__[aoi_id].keys())
        ts_index = bisect.bisect_left(ts_list, ts)
        if ts_index == 0:
            ts_closest = ts_list[ts_index]
        else:
            ts_closest = ts_list[ts_index-1]
        return self.__aoi_regions__[aoi_id][ts_closest]

    def contains(self, ts, aoi_id, gaze_x, gaze_y, threshold=10.0):
        res = False
        if aoi_id in self.__aoi_regions__.keys():
            if ts in self.__aoi_regions__[aoi_id].keys():
                res = mplPath.Path(self.__aoi_regions__[aoi_id][ts]).contains_point((gaze_x, gaze_y), radius=threshold)
            else:
                region = self.getClosestRegion(aoi_id, ts)
                if not region is None:
                    res = mplPath.Path(region).contains_point((gaze_x, gaze_y), radius=threshold)
        return res

    def drawAOIsBox(self, opencvMat, ts, color=(255, 0, 0)):
        for aoi_id in self.__aoi_regions__.keys():
            if ts in self.__aoi_regions__[aoi_id].keys():
                aoi_points = self.__aoi_regions__[aoi_id][ts]
                cv2.polylines(opencvMat, np.int32([aoi_points]), 1, color)

    def getAOIRegions(self, ts, aoi_id):
        if ts in self.__aoi_regions__[aoi_id].keys():
            return self.__aoi_regions__[aoi_id][ts]
        return None

    def getAOIHits(self, aoi_id):
        return self.__aoi_hits__[aoi_id]

    def getAOI(self, ts, gaze_x, gaze_y):
        for aoi_id in self.__aoi_regions__:
            if self.contains(ts, aoi_id, gaze_x, gaze_y) is True:
                return aoi_id
        return None

    def exportHeatmap(self, filepath='.'):
        H = Heatmap()
        for aoi_id, aoi_item in self.__aoi_items__.items():
            rows, cols, ch = aoi_item.snapshot.shape
            dispsize = (int(cols), int(rows))
            H.draw( list(self.__aoi_hits__[aoi_id].values()), dispsize, aoi_item.snapshot_filename, savefilename=(os.path.join(filepath, '%s_%s.png') % ('heatmap', aoi_id)) )

    def showLandmarks(self, opencvMat, landmarks, color=(0, 0, 255)):
        for (x,y) in landmarks:
            cv2.circle(opencvMat, (x, y), 2, (0, 0, 255), -1)
