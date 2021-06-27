import shapefile
import numpy as np

class PointGenerator:
    def __init__(self, country):
        sf = shapefile.Reader("data/gis_osm_roads_free_1.shp")
        self.points = []
        for shape in sf.iterShapes():
            self.points.extend(shape.points)

    def get_random_points(self, size):
        rand_indices = np.random.randint(len(self.points), size=size)
        return [self.points[i] for i in rand_indices]





