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

from tobiiglasses.gazedata import GazeData

class VideoAndGaze:

    def __init__(self, opencvMat, x, y, ts):
        self.opencvMat = opencvMat
        self.x = x
        self.y = y
        self.ts = ts

class VideoFramesAndMappedGaze:

    def __init__(self, gazedata, videoCapture, fps=25):
        self.__cap__ = videoCapture
        if (self.__cap__.isOpened() == False):
            print("Error opening video stream or file")
            raise IOError
        self.__current_frameAndMappedGaze__ = None
        self.__df__ = gazedata.toDataFrame()
        self.__vts__ = gazedata.getVTS()
        self.__vts_list__ = self.__vts__.keys()
        self.__frame_duration__ = int(1000/fps)
        self.__current_time__ = self.__vts_list__[0]
        self.__i__ = 0

    def __iter__(self):
        return self

    def __next__(self):
        if (self.__cap__.isOpened()):
            ret, frame = self.__cap__.read()
            if ret == True:
                if self.__current_time__ > self.__vts_list__[self.__i__]:
                    if self.__i__ < len(self.__vts_list__) - 1:
                        self.__i__+=1
                delay = int(self.__vts__[self.__vts_list__[self.__i__]])
                T = self.__df__.index[self.__df__.index.get_loc(self.__current_time__+self.__i__, method='nearest')]
                x = self.__df__.at[T, GazeData.GazePixelX]
                y = self.__df__.at[T, GazeData.GazePixelY]
            else:
                raise StopIteration
            self.__current_time__ += self.__frame_duration__
            return (frame, x, y, T)
        else:
            raise StopIteration
