
from shapely.geometry import mapping, shape, Point, LineString, Polygon,MultiPoint,MultiLineString,MultiPolygon,GeometryCollection

import mshapely

def test_plot():
    Point(0,0).buffer(10).plot().savePlot("../data/test_plot_polygon.png")
    Point(0,0).buffer(10).to(Point).plot().savePlot("../data/test_plot_point.png")
    Point(0,0).buffer(10).plot().to(Point).plot().savePlot("../data/test_plot_pp.png")
    LineString([(0,0),(10,0)]).resample().plot(type="o-").savePlot("../data/test_plot_linestring.png")

if __name__ == "__main__":
  test_plot()