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


import cv2
import numpy as np
import dlib
import os
import sys
import tobiiglasses
from collections import OrderedDict
from tobiiglasses.aoi.dnn.model import AOI_DNN_Model
from tobiiglasses.aoi.model import AOI
from tobiiglasses.aoi.model import AOI_Item

FACIAL_LANDMARKS_IDXS = OrderedDict([
        ("mouth", (48, 67)),
        ("right_eyebrow", (17, 21)),
        ("left_eyebrow", (22, 26)),
        ("right_eye", (36, 41)),
        ("left_eye", (42, 47)),
        ("nose", (27, 35)),
        ("jaw", (0, 16))
        ])

FILENAME_SHAPE_PREDICTOR = os.path.join(tobiiglasses.aoi.dnn.__path__[0], 'data', 'shape_predictor_68_face_landmarks.dat')
FILENAME_FACE_LANDMARKS = os.path.join(tobiiglasses.aoi.dnn.__path__[0], 'data', 'facial_landmarks_68markup.png')
FACE_FEATURES_POINTS = np.array( [[132, 60], [330, 620], [515, 615], [675, 50]]) #ids = 17, 3, 13, 26

class Face:

    def __init__(self, left, top, right, bottom, face_landmarks):
        self.__left__ = left
        self.__top__ = top
        self.__right__ = right
        self.__bottom__ = bottom
        self.__landmarks__ = face_landmarks

        self.__mouth__ = face_landmarks['mouth']
        self.__right_eyebrow__ = face_landmarks['right_eyebrow']
        self.__left_eyebrow__ = face_landmarks['left_eyebrow']
        self.__right_eye__ = face_landmarks['right_eye']
        self.__left_eye__ = face_landmarks['left_eye']
        self.__nose__ = face_landmarks['nose']
        self.__jaw__ = face_landmarks['jaw']

    @property
    def top(self):
        return self.__top__

    @property
    def right(self):
        return self.__right__

    @property
    def left(self):
        return self.__left__

    @property
    def bottom(self):
        return self.__bottom__

    @property
    def landmarks(self):
        return self.__landmarks__

    @property
    def mouth(self):
        return self.__mouth__

    @property
    def right_eyebrow(self):
        return self.__right_eyebrow__

    @property
    def left_eyebrow(self):
        return self.__left_eyebrow__

    @property
    def right_eye(self):
        return self.__right_eye__

    @property
    def left_eye(self):
        return self.__left_eye__

    @property
    def jaw(self):
        return self.__jaw__

    @property
    def nose(self):
        return self.__nose__


class FaceLandmarksDetector:

    def __init__(self, filename_shape_predictor):
        self.__detector__ = dlib.get_frontal_face_detector()
        self.__predictor__ = dlib.shape_predictor(filename_shape_predictor)

    def getFaces(self, opencvMat):
        gray = cv2.cvtColor(opencvMat, cv2.COLOR_BGR2GRAY)
        faces = self.__detector__(gray)
        Faces = []
        for face in faces:
            landmarks = self.__predictor__(gray, face)
            FACE_LANDMARKS_XY = {}
            for (name, (i, j)) in FACIAL_LANDMARKS_IDXS.items():
                FACE_LANDMARKS_XY[name] = []
                for k in range(i, j+1):
                    x = landmarks.part(k).x
                    y = landmarks.part(k).y
                    FACE_LANDMARKS_XY[name].append((x,y))
            Faces.append( Face(face.left(), face.top(), face.right(), face.bottom(), FACE_LANDMARKS_XY) )
        return Faces


class AOI_Face_Model(AOI):

    def __init__(self):
        AOI.__init__(self, 'face', FILENAME_FACE_LANDMARKS, FACE_FEATURES_POINTS)
        self.__detector__ = FaceLandmarksDetector(FILENAME_SHAPE_PREDICTOR)

    def getDetectedItems(self, opencvMat):
        faces = self.__detector__.getFaces(opencvMat)
        AOI_Items = []
        i=0
        for face in faces:
            i+=1
            detected_features_points = np.array([[face.landmarks['right_eyebrow'][0][0], face.landmarks['right_eyebrow'][0][1]],
                                                 [face.landmarks['jaw'][7][0], face.landmarks['jaw'][7][1]],
                                                 [face.landmarks['jaw'][9][0], face.landmarks['jaw'][9][1]],
                                                 [face.landmarks['left_eyebrow'][4][0], face.landmarks['left_eyebrow'][4][1]]
                                                ])
            landmarks = []
            for name in face.landmarks.keys():
                for p in face.landmarks[name]:
                    landmarks.append( [p[0], p[1]])

            AOI_Items.append( AOI_Item(self.__label__ + '_' + str(i), detected_features_points, landmarks, 100.0) )

        return AOI_Items
