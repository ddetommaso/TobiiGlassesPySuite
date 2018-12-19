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

class GazeEvent:

    def __init__(self, eye_movement_type, eye_movement_type_index, gaze_event_duration):
        self.eye_movement_type = eye_movement_type
        self.eye_movement_type_index = eye_movement_type_index
        self.gaze_event_duration = gaze_event_duration

class FixationEvent(GazeEvent):

    def __init__(self, eye_movement_type_index, gaze_event_duration, fixation_x, fixation_y):
        GazeEvent.__init__(self, 'Fixation', eye_movement_type_index, gaze_event_duration)
        self.fixation_x = fixation_x
        self.fixation_y = fixation_y

class SaccadeEvent(GazeEvent):

    def __init__(self, eye_movement_type_index,
                       gaze_event_duration, start_x, start_y,
                       end_x, end_y):
        GazeEvent.__init__(self, 'Saccade', eye_movement_type_index, gaze_event_duration)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
