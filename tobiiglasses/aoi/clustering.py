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

import itertools
import numpy as np
import joblib
from scipy import linalg
from scipy.misc import imread
import matplotlib.pyplot as plt
import matplotlib as mpl

from sklearn import mixture
from sklearn.cluster import DBSCAN as DB

from model import AOI_Model

class AOI_ClusterModel(AOI_Model):
    COLORS_LIST = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta']

    def __init__(self, n_clusters=None, cluster_labels=[], sorted_key=None):
        self.__n_clusters__ = n_clusters
        self.__cluster_labels__ = cluster_labels
        self.__sorted_key__ = sorted_key
        self.__initvars__()

    def __initvars__(self):
        self.__model__ = None
        self.__means__ = None
        self.__ordered_means__ = None
        self.__covariances__ = None
        self.__X__ = None
        self.__labels__ = None

    def __indexOf__(self, ordered_means, value):
        i = 0
        for m in ordered_means:
            if value[0] == ordered_means[i][0] and ordered_means[i][1]:
                return i
            i+=1
        return -1

    def __assignColorLabels__(self, labels):
        newlabels = []
        for l in labels:
            newlabels.append(AOI_ClusterModel.COLORS_LIST[l])
        return newlabels

    def __assignsLabels__(self, means, labels, cluster_labels, sorted_key):
        if not self.__sorted_key__  is None and len(self.__cluster_labels__) != self.__n_clusters__:
            raise ValueError('The AOI filter requires an equal numbers of clusters and labels')
        self.__ordered_means__ = []
        for m in sorted(means, key=sorted_key):
            self.__ordered_means__.append( m.astype(np.float16))
        new_labels = []
        for item in labels:
            m = means[item].astype(np.float16)
            new_labels.append(cluster_labels[self.__indexOf__(self.__ordered_means__, m)])
        return new_labels

    def __color_iter__(self):
        return itertools.cycle(AOI_ClusterModel.COLORS_LIST)

    def __draw_ellipse__(self, mean, covar, color, cplot):
        v, w = linalg.eigh(covar)
        v = 2. * np.sqrt(2.) * np.sqrt(v)
        u = w[0] / linalg.norm(w[0])
        angle = np.arctan(u[1] / u[0])
        angle = 180. * angle / np.pi  # convert to degrees
        ell = mpl.patches.Ellipse(mean, v[0], v[1], 180. + angle, color=color)
        ell.set_clip_box(cplot.bbox)
        ell.set_alpha(0.5)
        cplot.add_artist(ell)

    def __clustering__(self, X):
        """
        to assign:
        self.__X__, self.__n_clusters__, self.__labels__, self.__means__, self.__covariances__
        """
        raise NotImplementedError( "AOIs should have implemented a fit function" )

    def __getAOI_Distance__(self, fixation_x, fixation_y, cluster_mean):
        c = np.array((cluster_mean[0], cluster_mean[1]))
        x = np.array((fixation_x, fixation_y))
        return np.linalg.norm(x-c)

    def getCentroid(self, aoi_label):
        return (self.__means__[aoi_label][0], self.__means__[aoi_label][1])

    def getEllipseParams(self, aoi_label):
        v, w = linalg.eigh(self.__covariances__[aoi_label])
        v = 2. * np.sqrt(2.) * np.sqrt(v)
        u = w[0] / linalg.norm(w[0])
        angle = np.arctan(u[1] / u[0])
        angle = 180. * angle / np.pi  # convert to degrees
        return (v[0], v[1], angle+180.0)

    def fit(self, gaze_events, ts_filter):
        self.__initvars__()
        ts_list, x, y = gaze_events.getFixationsAsNumpy(ts_filter)
        self.__X__ = np.column_stack((x,y))
        (self.__model__,self.__means__, self.__covariances__, self.__labels__) = self.__clustering__(self.__X__)
        #self.__scores__ = self.__model__.score_samples(self.__X__)
        if not self.__sorted_key__ is None:
            self.__labels__ = self.__assignsLabels__(self.__means__, self.__labels__, self.__cluster_labels__, self.__sorted_key__)
        color_labels = self.__assignColorLabels__(self.__labels__)
        i = 0
        for ts in ts_list:
            gaze_events.setAOI(ts, color_labels[i], self.__getAOI_Distance__(self.__X__[i][0], self.__X__[i][1], self.__means__[self.__labels__[i]]))
            i+=1

    def saveModel(self, filename):
        joblib.dump(self.__model__, filename)

    def plot(self, title, background_image=None, width=1920, height=1080):
        cplot = plt.gca()
        img = None
        if not background_image is None:
            img = imread(background_image)
        for i, (mean, covar, color) in enumerate(zip(self.__means__, self.__covariances__, self.__color_iter__())):
            mean = list(map(np.float16, mean))
            if not np.any(self.__labels__ == i):
                continue
            plt.scatter(self.__X__[self.__labels__ == i, 0], self.__X__[self.__labels__ == i, 1], 1 , color=color, zorder=1)
            self.__draw_ellipse__(mean, covar, color, cplot)
            if not self.__ordered_means__ is None:
                plt.text(mean[0], mean[1], self.__cluster_labels__[self.__indexOf__(self.__ordered_means__, mean)], fontsize=12, bbox=dict(facecolor='red', alpha=0.5))
        plt.xlim(0, width)
        plt.ylim(0, height)
        plt.gca().invert_yaxis()
        plt.xticks(())
        plt.yticks(())
        plt.title(title)
        if not background_image is None:
            plt.imshow(img, zorder=0)
        return plt


class GaussianMixture(AOI_ClusterModel):

    def __init__(self, n_clusters, cluster_labels=[], sorted_key=None):
        AOI_ClusterModel.__init__(self, n_clusters, cluster_labels, sorted_key)

    def __clustering__(self, X):
        model = mixture.GaussianMixture(n_components=self.__n_clusters__, covariance_type='full').fit(X)
        labels = model.predict(X)
        proba = model.predict_proba(X)
        return (model, model.means_, model.covariances_, labels)


class DBSCAN(AOI_ClusterModel):

    def __init__(self, eps, min_samples):
        AOI_ClusterModel.__init__(self)
        self.__eps__ = eps
        self.__min_samples__ = min_samples

    def __clustering__(self, X):
        model = DB(eps=self.__eps__, min_samples=self.__min_samples__).fit(X)
        core_samples_mask = np.zeros_like(model.labels_, dtype=bool)
        core_samples_mask[model.core_sample_indices_] = True
        labels = model.labels_
        unique_labels = set(labels)
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        self.__n_clusters__ = n_clusters_
        covariances = []
        means = []
        for label in unique_labels:
            if label == -1:
                continue
            class_member_mask = (labels == label)
            xy = X[class_member_mask & core_samples_mask]
            covariances.append(np.cov(np.stack((xy[:,0], xy[:,1]))))
            means.append([np.mean(xy[:,0]), np.mean(xy[:,1])])
        return (model, means, covariances, labels)
