import sys,os,urllib,subprocess
import numpy as np
import requests
from tqdm import tqdm
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import transform
from functools import partial
import pyproj

from .. import mshapely
from ..io import writeGeometry


class OSM(object):
  """
  OSM instance prepares the osm coastline using spatial manipulation for gmsh, such as
  downloading,extracting,simplifying and resampling for gmsh.
  
  Parameters
  ----------
  The instance requires one object parameter that contains input and output variables.
  
  obj: object
    path: object
      osm:path, input
      domain:path,input
      density:path,input
      osmDomain:path,output
      osmSimplify:path,output
      osmResample:path,output
    minDensity:float,input
    maxDensity:float,input
    growth:float,input
    
  Note
  ----
  Any spatial manipulation is performed on the LAEA projection (north pole).
  Results are converted back to geographic coordinates.
  """
  def __init__(self,obj):
    self.path = obj['path']
    
    self.minDensity = minDensity= obj['minDensity']
    self.maxDensity = obj['maxDensity']
    self.growth = obj['growth']
    self.cB = minDensity * 0.01
    
    self.laea = "+proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m"
    self.p1=p1=pyproj.Proj(init='epsg:4326')
    self.p2=p2=pyproj.Proj(self.laea)
    self.tolaea = partial(pyproj.transform,p1,p2)
    self.togeo = partial(pyproj.transform,p2,p1)
    
    self.reset()
  
  def reset(self):
    # Input
    self._osm=None
    self._domain=None
    self._density=None
    
    # Ouput
    self._osmDomain=None
    self._osmSimplify=None
    self._osmResample=None  

  def _get(self,name,f):
    """
    Property wrapper to read/write outfile files. 
    If file does not exist, it will run the function and than write to file.
    If file exist, it will read directly from file.
    """
    output=self._projPath(self.path[name])
    if not os.path.exists(output):
      if(f.__name__=="_transform"):
        path=self.path[name]
        collection=mshapely.readGeometry(path)
        geo=collection['geometry']
        properties=collection['properties']
        geo = f(geo)
        geo.write(output,properties=properties,type="geojson")
      else:
        geo = f()
        geo.write(output,type="geojson")
        transform(self.togeo, geo).write(self.path[name],type="geojson")
      
    return mshapely.readGeometry(output)
  
  """
  Below is the proerties that uses the _get wrapper
  """
  @property
  def osm(self):
    if self._osm is None:
      self._osm = self._get('osm',self._transform)['geometry']
    return self._osm  
  @property
  def domain(self):
    if self._domain is None:
      self._domain = self._get('domain',self._transform)['geometry']
    return self._domain

  @property
  def density(self):
    if self._density is None:
      collection = self._get('density',self._transform)
      xy = collection['geometry'].xy
      density = [o['density'] for o in collection['properties']]
      self._density = np.column_stack((xy,density))
    return self._density

  @property
  def osmDomain(self):
    if self._osmDomain is None:
      self._osmDomain = self._get('osmDomain',self._getosmDomain)['geometry']
    return self._osmDomain

  @property
  def osmSimplify(self):
    if self._osmSimplify is None:
      self._osmSimplify = self._get('osmSimplify',self._getosmSimplify)['geometry']
    return self._osmSimplify
  
  @property
  def osmResample(self):
    print("here")
    if self._osmResample is None:
      self._osmResample = self._get('osmResample',self._getosmResample)['geometry']
    return self._osmResample

  
  def _projPath(self,path):
    """
    Get projected path of the output 
    """
    return "{}.proj.geojson".format(os.path.splitext(path)[0]) 
  def _geoPath(self,path):
    """
    Get geographic path of the output 
    """
    return "{}.geojson".format(os.path.splitext(path)[0]) 

  def _transform(self,geo):
    """
    Transform geographic to projection
    """
    tolaea=self.tolaea
    return transform(tolaea, geo)

  def _getosmDomain(self):
    """
    Extract osm coastline using the domain.
    It will only keep the largest Polygon.
    """
    geo = self.osm
    minDensity = self.minDensity
    cB = self.cB
    domain = self.domain
    t=tqdm(total=6)
    geo=geo.simplify(0.1);t.update(1)
    geo=geo.buffer(0.01);t.update(1)
    geo=geo.simplify(0.1);t.update(1)
    geo=geo.intersection(domain);t.update(1)
    geo=geo.largest().buffer(0.01);t.update(1)
    geo=geo.simplify(0.1);t.update(1);t.close()
    
    return geo

  def _getosmSimplify(self):
    """
    Simplify osm shoreline based on density field
    """
    geo=self.osmDomain
    geo=geo.dsimplify(self.density,self.minDensity,self.maxDensity,self.growth)
    geo=geo.largest()
    # geo.plot()
    # geo.savePlot("../data/example1.simplify.png")
    return geo
    
  def _getosmResample(self):
    """
    Resample osm shoreline using interior nearest points and density growth field.
    """
    geo=self.osmSimplify
    # geo=geo.largest()
    density=geo.inearest(maxDistance=self.maxDensity,angle=30.0)
    density[:,2]=density[:,2]*0.2
    density = np.concatenate((density,self.density)) # Combine inearest and density growth field
    
    geo=geo.dresample(density,minDensity=self.minDensity,maxDensity=self.maxDensity,growth=self.growth)
    # geo.plot()
    # geo.savePlot('../data/test_fetch.png')
    # geo=MultiPoint(geo.xy)
    
    return geo
    
  @staticmethod
  def downloadOSM(folder,overwrite=False):
    """
    Download OSM coastline file (600MB). 
    This geometry is splitted into partions (simarlar to a kdtree).
    """
    http = 'https://osmdata.openstreetmap.de/download/water-polygons-split-4326.zip'
    name = os.path.basename(http)
    osmPath =os.path.join(folder,name)
    
    if not os.path.exists(osmPath) or overwrite:
      response = requests.get(http, stream=True)
      total_length = int(response.headers.get('content-length', 0))
      t=tqdm(total=total_length, unit='iB', unit_scale=True)
      with open(osmPath, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
          if chunk: # filter out keep-alive new chunks
            t.update(len(chunk))
            f.write(chunk)
      t.close()
    return osmPath

  @staticmethod
  def extractOSM(osmPath,outPath,extent):
    """
    Extract osm coastline from zip file based on extent.
    This requires gdal (ogr2ogr).
    This avoids unpacking the zip file.
    """
    zipname = 'water-polygons-split-4326/water_polygons.shp'
    zipPath = "\"/vsizip/" + osmPath + "/" + zipname + "\""
    name = os.path.basename(osmPath)
    name = os.path.splitext(name)[0]
    
    # Transfer PBF to Shapefile - query only important coast
    pt1 = "{0} {1}".format(extent[0],extent[1])
    pt2 = "{0} {1}".format(extent[0],extent[3])
    pt3 = "{0} {1}".format(extent[2],extent[3])
    pt4 = "{0} {1}".format(extent[2],extent[1])
    pg_sql = "\"SELECT * FROM water_polygons WHERE ST_Intersects(geometry, ST_GeomFromText('POLYGON(({0}, {1}, {2}, {3}, {0}))', 4326));\"".format(pt1,pt2,pt3,pt4)
    command = "ogr2ogr -skipfailures -f \"GeoJSON\" {0} -nln {1} -dialect \"SQLITE\" -sql {2} {3}".format(outPath,name,pg_sql,zipPath)
    print(command)
    subprocess.call(command, shell=True)
  
  @staticmethod
  def write(*args,**kwargs):
    writeGeometry(*args, **kwargs)