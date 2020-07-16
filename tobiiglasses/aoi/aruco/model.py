#   Copyright (C) 2020  Davide De Tommaso
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


import cv2
import cv2.aruco as aruco
import numpy as np
import dlib
import os
import sys
import logging
import tobiiglasses
from collections import OrderedDict
from tobiiglasses.aoi.model import AOI, AOI_Item


class Aruco_Detector:

    def __init__(self, cameraMatrix, distCoeffs):
        self.__cameraMatrix__ = cameraMatrix
        self.__distCoeffs__ = distCoeffs

    def getCorners(self, opencvMat, aruco_dict):
        opencvMat = cv2.cvtColor(opencvMat, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(opencvMat, aruco_dict)
        return (corners, ids)

    def getDetectedFeatures(self, board, corners, ids):
        (valid, rvec, tvec) = board.estimatePose(corners, ids, self.__cameraMatrix__, self.__distCoeffs__)
        detected_features_points = None
        if valid > 0:
            imgpts, jac = cv2.projectPoints(board.feature_3dpoints, rvec, tvec, self.__cameraMatrix__, self.__distCoeffs__)
            detected_features_points = np.array([[int(imgpts[0][0][0]), int(imgpts[0][0][1])],
                                                 [int(imgpts[1][0][0]), int(imgpts[1][0][1])],
                                                 [int(imgpts[2][0][0]), int(imgpts[2][0][1])],
                                                 [int(imgpts[3][0][0]), int(imgpts[3][0][1])]  ])
        return detected_features_points


class AOI_Aruco:

    def __init__(self, aoi_label, aoi_id, aruco_detector, markerLength=0.1, markerSeparation=0.1, width=1920, height=1080, markers_x=3,  markers_y=2, aruco_dict=aruco.Dictionary_get(aruco.DICT_4X4_100)):
        self.aoi_label = aoi_label
        self.aoi_id = aoi_id
        self.markerLength = markerLength
        self.markerSeparation = markerSeparation
        self.__width__ = width
        self.__height__ = height
        self.__markers_x__ = markers_x
        self.__markers_y__ = markers_y
        self.__aruco_dict__ = aruco_dict
        self.__margin_size__ = 40

        if self.__markers_x__ > 1 and self.__markers_y__ > 1:
            self.feature_3dpoints = np.array( [[self.markerLength, self.__markers_y__*self.markerLength + (self.__markers_y__-1)*self.markerSeparation, 0.0],
                                               [(self.__markers_x__-1)*self.markerLength + (self.__markers_x__-1)*self.markerSeparation, self.__markers_y__*self.markerLength + (self.__markers_y__-1)*self.markerSeparation, 0.0],
                                               [self.markerLength, 0.0, 0.0],
                                               [(self.__markers_x__-1)*self.markerLength + (self.__markers_x__-1)*self.markerSeparation, 0.0, 0.0] ])

        elif self.__markers_x__ == 1 and self.__markers_y__ == 1:
            self.feature_3dpoints = np.array( [[0.0, self.markerLength, 0.0],
                                               [self.markerLength, self.markerLength, 0.0],
                                               [0.0, 0.0, 0.0],
                                               [self.markerLength, 0.0, 0.0] ])

        self.__aoi__ = aruco.GridBoard_create(markersX=self.__markers_x__,
                                   markersY=self.__markers_y__,
                                   markerLength=self.markerLength,
                                   markerSeparation=self.markerSeparation,
                                   dictionary=self.__aruco_dict__,
                                   firstMarker=aoi_id*self.__markers_x__*self.__markers_y__)

        corners, self.__ids__ = aruco_detector.getCorners(self.getCVMat(), self.__aruco_dict__)
        self.features_2dpoints = aruco_detector.getDetectedFeatures(self, corners, self.__ids__)

    def estimatePose(self, corners, ids, cameraMatrix, distCoeffs):
        rvec = np.array( [0.0, 0.0, 0.0] )
        tvec = np.array( [0.0, 0.0, 0.0] )
        (valid, rvec, tvec) = aruco.estimatePoseBoard(corners, ids, self.__aoi__, cameraMatrix, distCoeffs, rvec, tvec)
        return (valid, rvec, tvec)

    def exportAOI(self, filepath):
        img = self.getCVMat()
        if self.__markers_x__ > 1 and self.__markers_y__ > 1:
            cv2.rectangle(img,(self.features_2dpoints[0][0],self.features_2dpoints[0][1]-10),(self.features_2dpoints[3][0],self.features_2dpoints[3][1]+10),(255,255,255),-1)
        cv2.imwrite(os.path.join(filepath, self.getAOIFilename()), img)

    def getAOI(self):
        return self.__aoi__

    def getCVMat(self):
        img = np.zeros([self.__height__, self.__width__, 1],dtype=np.uint8)
        img.fill(255)
        self.__aoi__.draw((self.__width__, self.__height__), img, marginSize = self.__margin_size__)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        return img

    def getAOIFilename(self):
        return "aruco_%s.png" % self.aoi_label

class AOI_Aruco_Model(AOI):
    def __init__(self, cameraMatrix, distCoeffs, aruco_dict=aruco.DICT_4X4_100):
        AOI.__init__(self)
        self.__cameraMatrix__ = cameraMatrix
        self.__distCoeffs__ = distCoeffs
        self.__aoi_boards__ = {}
        self.__aruco_detector__ = Aruco_Detector(cameraMatrix, distCoeffs)
        self.__aruco_dict__ = aruco.Dictionary_get(aruco_dict)


    def getDetectedItems(self, opencvMat):
        (corners, ids) = self.__aruco_detector__.getCorners(opencvMat, self.__aruco_dict__)
        AOI_Items = []
        if ids is None:
            return AOI_Items
        for label, board in self.__aoi_boards__.items():
            filtered_corners = []
            filtered_ids = []
            for marker_id in ids:
                if marker_id in board.__ids__:
                    filtered_corners.append(corners[ids.tolist().index(marker_id)])
                    filtered_ids.append(marker_id)
            filtered_ids = np.asarray(filtered_ids, dtype=np.int32)
            filtered_corners = np.asarray(filtered_corners, dtype=np.float32)
            if len(filtered_ids) > 0:
                detected_features_points = self.__aruco_detector__.getDetectedFeatures(board, filtered_corners, filtered_ids)
                if detected_features_points is None:
                    break
                else:
                    item = AOI_Item(label, detected_features_points, board.getAOIFilename(), board.features_2dpoints)
                    AOI_Items.append(item)

        return AOI_Items

    def createArucoAOI(self, aoi_label, markerLength=0.1, markerSeparation=0.1, width=1920, height=1080, markers_x=3, markers_y=2, aruco_marker_id=-1):
        if aoi_label in self.__aoi_boards__.keys():
            logging.error('aoi_label is already present. AOI will not be created!')
        else:
            if aruco_marker_id == -1:
                self.__aoi_boards__[aoi_label] = AOI_Aruco(aoi_label, len(self.__aoi_boards__.keys()), self.__aruco_detector__, markerLength, markerSeparation, width, height, markers_x, markers_y, self.__aruco_dict__)
            else:
                self.__aoi_boards__[aoi_label] = AOI_Aruco(aoi_label, aruco_marker_id, self.__aruco_detector__, markerLength, markerSeparation, width, height, markers_x, markers_y, self.__aruco_dict__)
            self.__aoi_boards__[aoi_label].exportAOI('./')

    def exportArucoAOIs(self, filepath='./'):
        for label, board in self.__aoi_boards__.items():
            board.exportAOI(filepath)
