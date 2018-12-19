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

import tobiiglasses.recordings
import tobiiglasses.tobii_utils

p = tobiiglasses.tobii_utils.get_all_recordings("data/projects/pdrd7ov/recordings")
print(p[0].getAttributes()[1])

#s = recordings.Recording("data/projects","pdrd7ov","xcoyhhz")
#print(s.project.getCreationDate())
#print(s.recording.getCreationDate())
#rec = TobiiRecording ( source_dir , rec_id = recording_id )
