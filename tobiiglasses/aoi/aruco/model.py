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

    def getCorners(self, opencvMat, auro_dict):
        opencvMat = cv2.cvtColor(opencvMat, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(opencvMat, auro_dict)
        return (corners, ids)

    def getDetectedFeatures(self, board, corners, ids):
        (pose, rvec, tvec) = board.estimatePose(corners, ids, self.__cameraMatrix__, self.__distCoeffs__)
        detected_features_points = None
        if pose[0] > 0:
            imgpts, jac = cv2.projectPoints(board.feature_3dpoints, rvec, tvec, self.__cameraMatrix__, self.__distCoeffs__)
            detected_features_points = np.array([[int(imgpts[0][0][0]), int(imgpts[0][0][1])],
                                                 [int(imgpts[1][0][0]), int(imgpts[1][0][1])],
                                                 [int(imgpts[2][0][0]), int(imgpts[2][0][1])],
                                                 [int(imgpts[3][0][0]), int(imgpts[3][0][1])]  ])
        return detected_features_points


class AOI_Aruco:
    MARKERS_X = 3
    MARKERS_Y = 2
    ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_4X4_50)

    def __init__(self, aoi_label, aoi_id, aruco_detector, markerLength=0.1, markerSeparation=0.1):
        self.aoi_label = aoi_label
        self.aoi_id = aoi_id
        self.markerLength = markerLength
        self.markerSeparation = markerSeparation
        self.feature_3dpoints = np.array( [[self.markerLength, 0.0, 0.0],
                                           [2*self.markerLength + 2*self.markerSeparation, 0.0, 0.0],
                                           [self.markerLength, 2*self.markerLength + self.markerSeparation, 0.0],
                                           [2*self.markerLength + 2*self.markerSeparation, 2*self.markerLength + self.markerSeparation, 0.0]])

        self.__aoi__ = aruco.GridBoard_create(markersX=AOI_Aruco.MARKERS_X,
                                   markersY=AOI_Aruco.MARKERS_Y,
                                   markerLength=self.markerLength,
                                   markerSeparation=self.markerSeparation,
                                   dictionary=AOI_Aruco.ARUCO_DICT,
                                   firstMarker=aoi_id*AOI_Aruco.MARKERS_X*AOI_Aruco.MARKERS_Y)

        corners, ids = aruco_detector.getCorners(self.getCVMat(), AOI_Aruco.ARUCO_DICT)
        self.features_2dpoints = aruco_detector.getDetectedFeatures(self, corners, ids)

    def estimatePose(self, corners, ids, cameraMatrix, distCoeffs):
        rvec = np.array( [0.0, 0.0, 0.0] )
        tvec = np.array( [0.0, 0.0, 0.0] )
        pose = aruco.estimatePoseBoard(corners, ids, self.__aoi__, cameraMatrix, distCoeffs, rvec, tvec)
        return (pose, rvec, tvec)

    def exportAOI(self, filepath):
        img = self.getCVMat()
        cv2.rectangle(img,(self.features_2dpoints[0][0],self.features_2dpoints[0][1]),(self.features_2dpoints[3][0],self.features_2dpoints[3][1]),(255,255,255),-1)
        cv2.imwrite(os.path.join(filepath, self.getAOIFilename()), img)

    def getAOI(self):
        return self.__aoi__

    def getCVMat(self, width=1920, height=1080):
        img = np.zeros([height, width, 1],dtype=np.uint8)
        img.fill(255)
        self.__aoi__.draw((width, height), img, 40)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        return img

    def getAOIFilename(self):
        return "aruco_%s.png" % self.aoi_label

class AOI_Aruco_Model(AOI):
    def __init__(self, cameraMatrix, distCoeffs):
        AOI.__init__(self)
        self.__cameraMatrix__ = cameraMatrix
        self.__distCoeffs__ = distCoeffs
        self.__aoi_boards__ = {}
        self.__aruco_detector__ = Aruco_Detector(cameraMatrix, distCoeffs)


    def getDetectedItems(self, opencvMat):
        (corners, ids) = self.__aruco_detector__.getCorners(opencvMat, AOI_Aruco.ARUCO_DICT)
        AOI_Items = []
        for label, board in self.__aoi_boards__.items():
            detected_features_points = self.__aruco_detector__.getDetectedFeatures(board, corners, ids)
            if detected_features_points is None:
                break
            else:
                AOI_Items.append( AOI_Item(label, detected_features_points, board.getAOIFilename(), board.features_2dpoints) )
        return AOI_Items

    def createArucoAOI(self, aoi_label, markerLength=0.1, markerSeparation=0.1):
        if aoi_label in self.__aoi_boards__.keys():
            logging.error('aoi_label is already present. AOI will not be created!')
        else:
            self.__aoi_boards__[aoi_label] = AOI_Aruco(aoi_label, len(self.__aoi_boards__.keys()), self.__aruco_detector__, markerLength, markerSeparation)

    def exportArucoAOIs(self, filepath='./'):
        for label, board in self.__aoi_boards__.items():
            board.exportAOI(filepath)
