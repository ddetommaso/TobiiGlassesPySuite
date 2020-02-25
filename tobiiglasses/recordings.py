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
import csv
import gzip
import numpy as np
import pandas as pd
import cv2
import tobiiglasses.entities
from tobiiglasses.entities import TobiiRecording, TobiiSegment
from tobiiglasses.gazedata import GazeData
from tobiiglasses.events import GazeEvents
from tobiiglasses.exporter import RawCSV, ExtendedRawCSV
from tobiiglasses.video import VideoFramesAndMappedGaze, VideoAndGaze

class Recording:

    def __init__(self, root_dir, project_id, recording_id):
        recordings_path = tobiiglasses.entities.get_recordings_path(root_dir, project_id)
        self.__recording__ = TobiiRecording(recordings_path, recording_id)
        self.__segment_data__ = {}
        self.__segment_events__ = {}
        self.__segment_ids__ = []
        self.__loadSegmentIDs__()

    def __exportData_CSV__(self, filepath=None, filename=None, csv_suffix='', segment_id=None, exporter=None):
        segment_ids = self.__getSegmentIDs__(segment_id)
        for s_id in segment_ids:
            gazedata = self.getGazeData(s_id)
            (filepath, filename) = self.__getFileParams__('csv', s_id, filepath, filename, csv_suffix)
            e = exporter(filepath, filename, gazedata)
            e.toCSV()

    def __getFileParams__(self, extension, segment_id=None, filepath=None, filename=None, suffix=''):
        if segment_id is None:
            segment_id = 1
        if filepath is None:
            filepath = "."
        if filename is None:
            filename = "%s-S%s-%s.%s" % (self.getParticipantName(), str(segment_id), suffix, extension)
        return (filepath, filename)

    def __getSegmentIDs__(self, segment_id=None):
        segment_ids = []
        if segment_id is None:
            segment_ids.extend(self.__segment_ids__)
        else:
            segment_ids.append(segment_id)
        return segment_ids

    def __loadSegmentIDs__(self):
        self.__segment_ids__.extend(range(1, self.__recording__.getSegmentsN() + 1))

    def exportFull(self, fixation_filter, filepath=None, filename='output.avi', segment_id=1, fps=25.0, width=1920, height=1080, aoi_models=[]):
        fixations = self.getFixations(fixation_filter, ts_filter=None, segment_id=segment_id)
        if filepath is None:
            filepath = "."
        logging.info('Exporting video with mapped fixations in file %s in folder %s' % (filename, filepath))
        data = self.getGazeData(segment_id)
        f = self.__recording__.getSegment(segment_id).getVideoFilename()
        cap = cv2.VideoCapture(f)
        framesAndGaze = iter(VideoFramesAndMappedGaze(data, cap, fps))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename,fourcc, fps, (width,height))
        for frame, x, y, ts in framesAndGaze:
            (fx, fy, duration) = fixations.getClosestFixation(ts)
            for model in aoi_models:
                model.apply(frame, ts, fx, fy, fixations)
                model.drawAOIsBox(frame, ts)

            if fx>0 and fy>0:
                color = (0,0,255)
                for model in aoi_models:
                    aoi_id = model.getAOI(ts, fx, fy)
                    if not aoi_id is None:
                        color = (0,255,0)
                        cv2.putText(frame, aoi_id, (fx, fy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.circle(frame,(fx,fy), 30, color , 2)
            out.write(frame)
        cap.release()
        model.exportHeatmap()
        (filepath, filename) = self.__getFileParams__('csv', segment_id, filepath, 'dave', 'Fixations')
        fixations.exportCSV(filepath, filename, ts_filter=None)



    def exportCSV_ExtendedRawData(self, filepath=None, filename=None, segment_id=None):
        self.__exportData_CSV__(filepath, filename, 'eRaw', segment_id, ExtendedRawCSV)

    def exportCSV_Fixations(self, fixation_filter, filepath=None, filename=None, ts_filter=None, segment_id=None):
        logging.info('Exporting fixations on %s' % filepath)
        fixations = self.getFixations(fixation_filter, ts_filter, segment_id)
        (filepath, filename) = self.__getFileParams__('csv', segment_id, filepath, filename, 'Fixations')
        fixations.exportCSV(filepath, filename, ts_filter=ts_filter)
        return fixations

    def exportCSV_RawData(self, filepath=None, filename=None, segment_id=1):
        self.__exportData_CSV__(filepath, filename, 'Raw', segment_id, RawCSV)

    def exportVideoAndGaze(self, filepath=None, filename='output.avi', segment_id=1, fps=25.0, width=1920, height=1080, aoi_dnn_models=[]):
        logging.info('Exporting video with mapped gaze in file %s in folder %s' % (filename, filepath))
        data = self.getGazeData(segment_id)
        f = self.__recording__.getSegment(segment_id).getVideoFilename()
        cap = cv2.VideoCapture(f)
        framesAndGaze = iter(VideoFramesAndMappedGaze(data, cap, fps))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename,fourcc, fps, (width,height))
        for frame, x, y, ts in framesAndGaze:
            for model in aoi_dnn_models:
                model.apply(frame, ts, x, y)
                model.drawAOIsBox(frame, ts)

            if x>0 and y>0:
                color = (0,0,255)
                aoi_id = model.getAOI(ts, x, y)
                if not aoi_id is None:
                    color = (0,255,0)
                    cv2.putText(frame, aoi_id, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.circle(frame,(x,y), 30, color , 2)
            out.write(frame)
        cap.release()
        model.exportHeatmap()

    def getFixations(self, fixation_filter, ts_filter=None, segment_id=None):
        segment_ids = self.__getSegmentIDs__(segment_id)
        for s_id in segment_ids:
            gaze_data = self.getGazeData(s_id)
            gaze_events = self.getGazeEvents(s_id)
            gaze_events.filterFixations(fixation_filter, gaze_data.toDataFrame(), ts_filter)
        return gaze_events

    def getGazeData(self, segment_id=1):
        segment = self.__recording__.getSegment(segment_id)
        if not segment_id in self.__segment_data__.keys():
            self.__segment_data__[segment_id] = GazeData(segment)
        return self.__segment_data__[segment_id]

    def getGazeEvents(self, segment_id):
        segment = self.__recording__.getSegment(segment_id)
        if not segment_id in self.__segment_events__.keys():
            self.__segment_events__[segment_id] = GazeEvents()
            events = self.getGazeData(segment_id).getLoggedEvents()
            for ts, value in events.items():
                self.__segment_events__[segment_id].addLoggedEvent(ts, value)
        return self.__segment_events__[segment_id]

    def getParticipantName(self):
        return self.__recording__.getParticipant().getName()

    def replay(self, segment_id, fps=25):
        logging.info('Replaying video with mapped gaze...')
        data = self.getGazeData(segment_id)
        f = self.__recording__.getSegment(segment_id).getVideoFilename()
        cap = cv2.VideoCapture(f)
        framesAndGaze = iter(VideoFramesAndMappedGaze(data, cap, fps))
        for frame, x, y, ts in framesAndGaze:
            if x>0 and y>0:
                cv2.circle(frame,(int(x),int(y)), 30, (0,0,255), 2)
            cv2.imshow('Frame',frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def saveVideoSnapshot(self, filename, ts, segment_id, fps=25):
        logging.info('Saving snapshot from video recording in %s ' % filename)
        f = self.__recording__.getSegment(segment_id).getVideoFilename()
        cap = cv2.VideoCapture(f)
        framesAndGaze = iter(VideoFramesAndMappedGaze(data, cap, fps))
        for frame, x, y, _ts in framesAndGaze:
            if _ts > ts:
                cv2.imwrite(filename,frame)
                break
        cap.release()
