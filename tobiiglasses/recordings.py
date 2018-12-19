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
import livedata
import events
import os
import csv
import numpy as np
from entities import TobiiProject, TobiiRecording, TobiiParticipant, TobiiSegment

class Recording:

    def __init__(self, projects_dir, project_id, recording_id):
        self.project_dir = os.path.join(projects_dir, project_id)
        self.project = TobiiProject(projects_dir, project_id)
        self.recording = TobiiRecording(self.project_dir, recording_id)


"""
class Recording:

    def __init__(self, filepath=None, filename=None):
        self.__livedata__ = livedata.LiveData()
        self.__gazeevents__ = {} # keys: gidx, values: GazeEvent

        if not filepath is None and not filename is None:
            self.importFromJSONFile(filepath, filename)

    def __init__(self, source_dir, recording_id):
        self.rec_id = recording_id
        self.participant_name

    def addGazeEvent(self, gidx, gaze_event):
        self.__gazeevents__[gidx] = gaze_event

    def addJSONItem(self, json_item):
        self.__livedata__.addJSONItem(json_item)

    def getLiveData(self):
        return self.__livedata__

    def getGazeEvent(self, gidx):
        return self.__gazeevents__[gidx]

    def getGazeEvents(self):
        return self.__gazeevents__

    def importFromJSONFile(self, filepath, filename):
        logging.info('Importing from JSON file %s in %s' % (filename, filepath))
        with open(os.path.join(filepath, filename)) as f:
            for item in f:
                self.addJSONItem(item)
"""
