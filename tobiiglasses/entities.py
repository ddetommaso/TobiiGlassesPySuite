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

import tobii_utils
import datetime
import os

TOBII_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+%f'

class TobiiRecording:
    rec_filename = "recording.json"

    def __init__(self, rec_dir):
        self.__rec_dir__ = rec_dir
        self.__project_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(rec_dir)))
        res = tobii_utils.load_json_from_file(rec_dir, TobiiRecording.rec_filename)
        self.__parse_json_rec__(res)
        self.__project__ = TobiiProject(self.__project_dir__)
        self.__participant__ = TobiiParticipant(rec_dir)
        self.__segments__ = []

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

    def getLength(self):
        return self.__rec_length__

    def getName(self):
        return self.__rec_name__

    def getRecordingDir(self):
        return self.__rec_dir__

    def getSegmentsN(self):
        return self.__rec_segments__


class TobiiProject:
    project_filename = "project.json"

    def __init__(self, project_dir):
        self.__project_dir__ = project_dir
        res = tobii_utils.load_json_from_file(project_dir, TobiiProject.project_filename)
        self.__parse_json_pr__(res)

    def __parse_json_pr__(self, item):
        self.__pr_created__ = datetime.datetime.strptime(item["pr_created"], TOBII_DATETIME_FORMAT)
        self.__pr_name__ = item["pr_info"]["Name"]

    def getCreationDate(self):
        return self.__pr_created__

    def getName(self):
        return self.__pr_name__


class TobiiParticipant:
    ppt_filename = "participant.json"

    def __init__(self, ppt_dir):
        res = tobii_utils.load_json_from_file(ppt_dir, TobiiParticipant.ppt_filename)
        self.__parse_json_ppt__(res)

    def __parse_json_ppt__(self, item):
        self.__ppt_name__ = item["pa_info"]["Name"]

    def getName(self):
        return self.__ppt_name__

class TobiiSegment:
    video_filename = "fullstream.mp4"
    livedata_filename = "livedata.json.gz"
    segment_filename = "segment.json"

    def __init__(self, segment_dir):
        self.__segment_dir__ = segment_dir
        res = tobii_utils.load_json_from_file(segment_dir, TobiiSegment.segment_filename)

    def __parse_json_seg__(self, item):
        self.__seg_length_us__ = int(item["seg_length_us"])
        self.__seg_calibrated__ = bool(item["seg_calibrated"])
        self.__seg_t_start__ = datetime.datetime.strptime(item["seg_t_start"], TOBII_DATETIME_FORMAT)
        self.__seg_t_stop__ = datetime.datetime.strptime(item["seg_t_stop"], TOBII_DATETIME_FORMAT)

    def isCalibrated(self):
        return self.__seg_calibrated__

    def getLengthUs(self):
        return self.__seg_length_us__

    def getLiveDataFilepath(self):
        return os.path.join(self.segment_dir, TobiiSegment.livedata_filename)

    def getStartDateTime(self):
        return self.__seg_t_start__

    def getStopDateTime(self):
        return self.__seg_t_stop__

    def getVideoFilepath(self):
        return os.path.join(self.segment_dir, TobiiSegment.video_filename)
