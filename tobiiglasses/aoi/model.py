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

class AOI_Model:

    def fit(self, gaze_events, ts_filter):
        """
        For each fixation point in gaze_events (GazeEvents object) to assign an AOI using
        event.setAOI(ts, aoi_label, aoi_distance)
        """
        raise NotImplementedError( "AOIs should have implemented a fit function" )

    def plot(self, title, background_image=None, width=1920, height=1080):
        """
        Method for returning a static plot (matplotlib.pyplot) displaying AOIs
        """
        raise NotImplementedError( "AOIs should have implemented a fit function" )

    def savePlot(self, title='no title', filename='plot.pdf', background_image=None, width=1920, height=1080):
        p = self.plot(title, background_image, width, height)
        p.savefig(filename, format='pdf')
        p.gca().clear()

    def showPlot(self, title='no title', background_image=None, width=1920, height=1080):
        p = self.plot(title, background_image, width, height)
        p.show()
        p.gca().clear()
