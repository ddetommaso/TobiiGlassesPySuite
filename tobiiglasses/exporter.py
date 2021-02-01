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
import pandas as pd
import tobiiglasses.gazedata
import tobiiglasses.events


class CSVFile(object):

    def __init__(self, filepath, filename):
        self.__filepath__ = filepath
        self.__filename__ = filename
        self.__headers__ = []

    def __exportDataFrame__(self, df):
        dest = os.path.join(self.__filepath__, self.__filename__)
        logging.info('Exporting data in %s' % dest)
        df.to_csv(dest, encoding='utf-8', header=True, columns=self.__headers__, index=False)
        df.to_pickle(os.path.join(self.__filepath__, 'data.pickle'))

    def getHeaders(self):
        return self.__headers__

    def setHeaders(self):
        return self.__headers__

    def toCSV(self):
        raise NotImplementedError( "CSVFile should have implemented toCSV method" )


class RawCSV(CSVFile):

    def __init__(self, filepath, filename, gazedata):
        CSVFile.__init__(self, filepath, filename)
        self.__gazedata__ = gazedata
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Timestamp)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Gidx)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.LoggedEvents)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.JSONEvents)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazePositionX)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazePositionY)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazePixelX)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazePixelY)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Gaze3DPositionX)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Gaze3DPositionY)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Gaze3DPositionZ)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Depth)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Vergence)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Version)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.Tilt)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazeDirectionX_Left)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazeDirectionY_Left)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazeDirectionZ_Left)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazeDirectionX_Right)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazeDirectionY_Right)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.GazeDirectionZ_Right)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilCenterX_Left)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilCenterY_Left)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilCenterZ_Left)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilCenterX_Right)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilCenterY_Right)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilCenterZ_Right)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilDiameter_Left)
        self.__headers__.append(tobiiglasses.gazedata.GazeData.PupilDiameter_Right)

    def toCSV(self):
        self.__exportDataFrame__(self.__gazedata__.toDataFrame())

class ExtendedRawCSV(RawCSV):

    def __init__(self, filepath, filename, gazedata):
        RawCSV.__init__(self, filepath, filename, gazedata)
        self.__headers__.extend(gazedata.getExpVarsHeaders())


class FilteredCSV(RawCSV):

    def __init__(self, filepath, filename, gazedata, events):
        RawCSV.__init__(self, filepath, filename, gazedata)
        self.__events__ = events
        self.__headers__.append(tobiiglasses.events.GazeEvents.EventIndex)
        self.__headers__.append(tobiiglasses.events.GazeEvents.GazeType)
        self.__headers__.append(tobiiglasses.events.GazeEvents.Fixation_X)
        self.__headers__.append(tobiiglasses.events.GazeEvents.Fixation_Y)
        self.__headers__.append(tobiiglasses.events.GazeEvents.EventDuration)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI_Mapped_Fixation_X)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI_Mapped_Fixation_Y)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI_Score)
        self.__gazedata__.importEvents(self.__events__)


class FixationsCSV(CSVFile):

    def __init__(self, filepath, filename, fixations_df):
        CSVFile.__init__(self, filepath, filename)
        self.__headers__.append(tobiiglasses.events.GazeEvents.Timestamp)
        self.__headers__.append(tobiiglasses.events.GazeEvents.EventIndex)
        self.__headers__.append(tobiiglasses.events.GazeEvents.GazeType)
        self.__headers__.append(tobiiglasses.events.GazeEvents.Fixation_X)
        self.__headers__.append(tobiiglasses.events.GazeEvents.Fixation_Y)
        self.__headers__.append(tobiiglasses.events.GazeEvents.EventDuration)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI_Mapped_Fixation_X)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI_Mapped_Fixation_Y)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI)
        self.__headers__.append(tobiiglasses.events.GazeEvents.AOI_Score)
        self.__fixations_df__ = fixations_df

    def toCSV(self):
        self.__exportDataFrame__(self.__fixations_df__)
