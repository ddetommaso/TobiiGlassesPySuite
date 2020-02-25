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
import matplotlib.path as mplPath
from tobiiglasses.aoi.heatmaps import Heatmap

class AOI_Item:

    def __init__(self, aoi_id, detected_features_points, landmarks, aoi_score):
        self.aoi_id = aoi_id
        self.detected_features_points = detected_features_points
        self.landmarks = landmarks
        self.aoi_score = aoi_score


class AOI:

    def __init__(self, label, snapshot_filename, features_points):
        self.__label__ = label
        self.__snapshot_filename__ = snapshot_filename
        self.__snapshot__ = cv2.imread(snapshot_filename)
        self.__aoi_regions__ = {}
        self.__aoi_hits__ = {}
        self.__features_points__ = features_points

    def apply(self, opencvMat, ts, gaze_x, gaze_y, gaze_events):
        for item in self.getDetectedItems(opencvMat):
            detected_features_points = item.detected_features_points
            aoi_id = item.aoi_id
            if not aoi_id in self.__aoi_regions__.keys():
                self.__aoi_regions__[aoi_id] = {}
                self.__aoi_hits__[aoi_id] = {}

            H, status = cv2.findHomography(self.__features_points__, detected_features_points)
            rows, cols, ch = self.__snapshot__.shape

            bounding_box_src = np.array([[0,0,1], [0, rows-1,1], [cols-1, rows-1,1], [cols-1, 0,1]])
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
                gaze_events.setAOI(ts, aoi_id, item.aoi_score)

            self.showLandmarks(opencvMat, item.landmarks)

    def getDetectedItems(self, opencvMat):
        raise NotImplementedError( "AOIs should have implemented getDetectedItems() method" )

    def contains(self, ts, aoi_id, gaze_x, gaze_y):
        res = False
        if ts in self.__aoi_regions__[aoi_id].keys():
            res = mplPath.Path(self.__aoi_regions__[aoi_id][ts]).contains_point((gaze_x, gaze_y))
        return res

    def drawAOIsBox(self, opencvMat, ts, color=(0, 255, 0)):
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

    def exportHeatmap(self, filename='heatmap.png'):
        H = Heatmap()
        gazepoints = []
        for aoi_id in self.__aoi_hits__.keys():
            gazepoints.extend(list(self.__aoi_hits__[aoi_id].values()))
        rows, cols, ch = self.__snapshot__.shape
        dispsize = (int(cols), int(rows))
        H.draw(gazepoints, dispsize, self.__snapshot_filename__, savefilename=filename)

    def showLandmarks(self, opencvMat, landmarks, color=(0, 0, 255)):
        for (x,y) in landmarks:
            cv2.circle(opencvMat, (x, y), 2, (0, 0, 255), -1)
