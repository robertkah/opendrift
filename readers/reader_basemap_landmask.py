#!/usr/bin/env python

from datetime import datetime, timedelta

import numpy as np
from mpl_toolkits.basemap import Basemap
try:
    import matplotlib.nxutils as nx
    has_nxutils = True  # For matplotlib version < 1.2
except:
    from matplotlib.path import Path
    has_nxutils = False  # For matplotlib version >= 1.2

from readers import Reader


class Reader(Reader):

    name = 'basemap_landmask'
    return_block = False  # Vector based, so checks only individual points

    # Variables (CF standard names) which
    # can be provided by this model/reader
    variables = ['land_binary_mask']

    def __init__(self, llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat,
                 resolution='i', projection='cyl'):

        # Set up Basemap
        self.map = Basemap(llcrnrlon, llcrnrlat,
                           urcrnrlon, urcrnrlat,
                           resolution=resolution, projection=projection)

        # Store proj4 string
        self.proj4 = self.map.proj4string

        # Run constructor of parent Reader class
        super(Reader, self).__init__()

        # Depth
        self.depths = None

        # Time
        self.start_time = None
        self.end_time = None
        self.time_step = None

        # Read and store min, max and step of x and y
        self.xmin, self.ymin = self.lonlat2xy(llcrnrlon, llcrnrlat)
        self.xmax, self.ymax = self.lonlat2xy(urcrnrlon, urcrnrlat)
        self.delta_x = None
        self.delta_y = None

        # Extract polygons for faster checking of stranding
        if has_nxutils is True:
            self.polygons = [p.boundary for p in self.map.landpolygons]
        else:
            self.polygons = [Path(p.boundary) for p in self.map.landpolygons]

    def get_variables(self, requestedVariables, time=None,
                      x=None, y=None, depth=None, block=False):

        if isinstance(requestedVariables, str):
            requestedVariables = [requestedVariables]

        self.check_arguments(requestedVariables, time, x, y, depth)

        x, y = self.xy2lonlat(x, y)
        points = np.c_[x, y]

        insidePoly = np.array([False]*len(x))
        if has_nxutils is True:
            for polygon in self.polygons:
                insidePoly[nx.points_inside_poly(points, polygon)] = True
        else:
            for polygon in self.polygons:
                insidePoly += np.array(polygon.contains_points(points))

        variables = {}
        variables['land_binary_mask'] = insidePoly

        return variables