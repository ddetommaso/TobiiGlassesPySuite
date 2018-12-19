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

import json_utils
import datetime
import os

class Segment:
    video_filename = "fullstream.mp4"
    livedata_filename = "livedata.json.gz"
    segment_filename = "segment.json"

    def __init__(self, segment_dir, segment_id):
        self.segment_dir = segment_dir
        self.segment_id = segment_id
        json_utils.JSON_File(segment_dir, Segment.segment_filename).load(self.json_segment_hook)

    def json_segment_hook(self, item):
        self.seg_length_us = int(item["seg_length_us"])
        self.seg_calibrated = bool(item["seg_calibrated"])
        self.seg_t_start = datetime.datetime.strptime(item["seg_t_start"], '%Y-%m-%dT%H:%M:%S+%f')
        self.seg_t_stop = datetime.datetime.strptime(item["seg_t_stop"], '%Y-%m-%dT%H:%M:%S+%f')

    def getVideoFilepath(self):
        return os.path.join(self.segment_dir, Segment.video_filename)

    def getLiveDataFilepath(self):
        return os.path.join(self.segment_dir, Segment.livedata_filename)
