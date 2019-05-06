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

import datetime
import logging
import os
import tobiiglasses.utils as utils

TOBII_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+%f'
PROJECTS_DIRNAME = "projects"
RECORDINGS_DIRNAME = "recordings"
SEGMENTS_DIRNAME = "segments"

def get_recordings_path(root_dir, project_id):
    return os.path.join(root_dir, PROJECTS_DIRNAME, project_id, RECORDINGS_DIRNAME)

def get_projects_path(root_dir):
    return os.path.join(root_dir, PROJECTS_DIRNAME)

def get_all_projects(root_dir):
    logging.info('Loading projects in %s' % root_dir)
    projects = []
    projects_path = os.path.join(root_dir, PROJECTS_DIRNAME)
    for item in os.listdir (projects_path):
        if os.path.isdir(os.path.join(projects_path, item)):
            projects.append(TobiiProject(projects_path, item))
    return projects

def get_all_recordings(root_dir, project_id):
    recordings_path = get_recordings_path(root_dir, project_id)
    logging.info('Loading recordings from %s' % recordings_path)
    recordings = []
    for item in os.listdir (recordings_path):
        if os.path.isdir(os.path.join(recordings_path, item)):
            recordings.append(TobiiRecording(recordings_path, item))
    return recordings

def get_all_segments(recordings_path, recording_id):
    segments_path = os.path.join(recordings_path, recording_id, SEGMENTS_DIRNAME)
    logging.info('Loading segments from %s' % segments_path)
    segments = []
    for item in os.listdir (segments_path):
        seg_path = os.path.join(segments_path, item)
        if os.path.isdir(seg_path):
            segments.append(TobiiSegment(seg_path))
    return segments

class TobiiRecording:
    rec_filename = "recording.json"

    def __init__(self, recordings_path, rec_id):
        self.__rec_id__ = rec_id
        self.__rec_path__ = os.path.join(recordings_path, rec_id)
        self.__project_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(self.__rec_path__)))
        res = utils.load_json_from_file(self.__rec_path__, TobiiRecording.rec_filename)
        self.__parse_json_rec__(res)
        self.__project__ = TobiiProject(os.path.dirname(self.__project_dir__), os.path.basename(self.__project_dir__))
        self.__participant__ = TobiiParticipant(self.__rec_path__)
        self.__segments__ = get_all_segments(recordings_path, self.__rec_id__)

    def __parse_json_rec__(self, item):
        self.__rec_created__ = datetime.datetime.strptime(item["rec_created"], TOBII_DATETIME_FORMAT)
        self.__rec_name__ = item["rec_info"]["Name"]
        self.__rec_length__ = int(item["rec_length"])
        self.__rec_segments__ = int(item["rec_segments"])
        self.__rec_et_samples__ = int(item["rec_et_samples"])
        self.__rec_et_valid_samples__ = int(item["rec_et_valid_samples"])

    def getAttributes(self):
        attr = []
        names = []
        names.append("Recording name"); attr.append(self.__rec_name__)
        names.append("Project name"); attr.append(self.__project__.getName())
        names.append("Creation Date"); attr.append(str(self.__rec_created__))
        names.append("Duration (s)"); attr.append(str(self.__rec_length__))
        names.append("Participant name"); attr.append(self.__participant__.getName())
        names.append("Segments nr"); attr.append(str(self.__rec_segments__))
        names.append("Et samples"); attr.append(str(self.__rec_et_samples__))
        names.append("Et valid samples"); attr.append(str(self.__rec_et_valid_samples__))
        return (names, attr)

    def getCreationDate(self):
        return self.__rec_created__

    def getEtSamples(self):
        return self.__rec_et_samples__

    def getEtValidSamples(self):
        return self.__rec_et_valid_samples__

    def getId(self):
        return self.__rec_id__

    def getLength(self):
        return self.__rec_length__

    def getName(self):
        return self.__rec_name__

    def getParticipant(self):
        return self.__participant__

    def getRecordingDir(self):
        return self.__rec_dir__

    def getSegment(self, segment_id):
        if segment_id > 0:
            return self.__segments__[segment_id-1]
        logging.error('Cannot get segment less or equal to zero')
        return None

    def getSegmentsN(self):
        return self.__rec_segments__


class TobiiProject:
    project_filename = "project.json"

    def __init__(self, projects_path, project_id):
        self.__project_id__ = project_id
        self.__project_path__ = os.path.join(projects_path, project_id)
        res = utils.load_json_from_file(self.__project_path__, TobiiProject.project_filename)
        self.__parse_json_pr__(res)

    def __parse_json_pr__(self, item):
        self.__pr_created__ = datetime.datetime.strptime(item["pr_created"], TOBII_DATETIME_FORMAT)
        try:
            self.__pr_name__ = item["pr_info"]["Name"]
        except:
            self.__pr_name__ = None

    def getCreationDate(self):
        return self.__pr_created__

    def getId(self):
        return self.__project_id__

    def getName(self):
        return self.__pr_name__



class TobiiParticipant:
    ppt_filename = "participant.json"

    def __init__(self, ppt_path):
        res = utils.load_json_from_file(ppt_path, TobiiParticipant.ppt_filename)
        self.__parse_json_ppt__(res)

    def __parse_json_ppt__(self, item):
        self.__ppt_name__ = item["pa_info"]["Name"]

    def getName(self):
        return self.__ppt_name__

class TobiiSegment:
    video_filename = "fullstream.mp4"
    livedata_filename = "livedata.json.gz"
    segment_filename = "segment.json"

    def __init__(self, segment_path):
        self.__segment_path__ = segment_path
        self.__segment_id__ = os.path.basename(segment_path)
        res = utils.load_json_from_file(segment_path, TobiiSegment.segment_filename)
        if res != None:
            self.__parse_json_seg__(res)

    def __parse_json_seg__(self, item):
        self.__seg_length_us__ = int(item["seg_length_us"])
        self.__seg_calibrated__ = bool(item["seg_calibrated"])
        self.__seg_t_start__ = datetime.datetime.strptime(item["seg_t_start"], TOBII_DATETIME_FORMAT)
        self.__seg_t_stop__ = datetime.datetime.strptime(item["seg_t_stop"], TOBII_DATETIME_FORMAT)

    def getId(self):
        return self.__segment_id__

    def getLengthUs(self):
        return self.__seg_length_us__

    def getLiveDataFilepath(self):
        return os.path.join(self.__segment_path__, self.__segment_id__)

    def getSegmentPath(self):
        return self.__segment_path__

    def getStartDateTime(self):
        return self.__seg_t_start__

    def getStopDateTime(self):
        return self.__seg_t_stop__

    def getVideoFilename(self):
        return os.path.join(self.__segment_path__, TobiiSegment.video_filename)

    def isCalibrated(self):
        return self.__seg_calibrated__
