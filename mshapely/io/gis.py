import os
import sys
import fiona
import json
from shapely.geometry import mapping, shape,GeometryCollection
from geojson import Feature, FeatureCollection, dump


class GIS(object):
  def __init__(self,geometry,properties=None,schema=None):
    if geometry.is_empty:raise Exception("geometry is empty")
    self.geometry =geometry
    self.schema = self.getSchema(geometry, schema)
    self.properties = self.getProperties(geometry, properties)

  def getSchema(self,geometry, schema):
    if schema is not None: return schema
    return {'geometry': geometry.type, "properties": {"id": "int:10"}}
    
  def getProperties(self,geometry, properties):
    if properties is not None: return properties
    geometry = self._cgeometry(geometry)
    return [dict(id=i) for i, f in enumerate(geometry)]


  def write(self,path):
    """
    Write GIS file
    """
    ext=os.path.splitext(path)[1]
    if ext == '.shp': return self.writeShapefile(path)
    if ext == '.geojson':return self.writeGeoJSON(path)
    
    raise Exception("Method does not exist{}".format(ext))
  
  @staticmethod
  def read(path):
    """
    Read GIS file
    """
    if not os.path.exists(path):raise Exception("File {0} does not exist".format(os.path.abspath(path)))  
    ext = os.path.splitext(path)[1]
    if ext==".shp":return GIS.readShapefile(path)
    if ext==".geojson":return GIS.readGeoJSON(path)
    
    raise Exception("Method does not exist{}".format(ext))
  
  @staticmethod
  def delete(path): 
    """
    Delete GIS file
    """
    if os.path.exists(path):
      name,ext=os.path.splitext(path)
      if ext==".shp":
        os.remove(path)
        os.remove(name+".shx")
        os.remove(name+".dbf")
        os.remove(name+".cpg")
      elif ext==".geojson":
        os.remove(path)

  @staticmethod
  def _cgeometry(geometry):
    geometry= geometry if isinstance(geometry, (list,GeometryCollection)) else [geometry]
    return geometry
    
  def writeShapefile(self,path):
    """
    Write to shapefile
    """    
    schema=self.schema
    geometry = self._cgeometry(self.geometry)
    properties = self.properties
    with fiona.collection(path, "w", "ESRI Shapefile", schema) as shapefile:
      for geometry, property in zip(geometry, properties):
        shapefile.write({'geometry': mapping(geometry),
                         'properties': property
                         })
    
  def writeGeoJSON(self,path):
    """
    Write to geojson
    """    
    schema=self.schema
    geometry = self._cgeometry(self.geometry)
    
    properties = self.properties
    
    features = []
    features = [Feature(geometry=geo, properties=property) for geo, property in zip(geometry, properties)]
      
    with open(path, 'w') as f:
      collection=FeatureCollection(features)
      collection['schema']=schema
      dump(collection, f)
 
  @staticmethod
  def readShapefile(path):
    """
    Read shapefile
    """       
    # Get Feature/Geometry in memory for Shapely.
    if not os.path.isfile(path):raise Exception("File {0} does not exist".format(os.path.abspath(path)))
    
    with fiona.collection(path, 'r') as input:
      geometry = GeometryCollection([shape(shp['geometry']) for shp in input])  # Save geometry
      properties = [shp['properties'] for shp in input]  # Save properties
      return GIS(geometry,properties,input.schema.copy())
  
  @staticmethod
  def readGeoJSON(path):
    """
    Read geojson
    """     
    if not os.path.isfile(path):raise Exception("File {0} does not exist".format(os.path.abspath(path)))
    
    with open(path) as f:
      collection=json.load(f)
      schema = collection.get("schema",{})
      features = collection["features"]
      geometry = GeometryCollection([shape(feature["geometry"]) for feature in features])
      properties = [feature['properties'] for feature in features]  # Save properties
      return GIS(geometry,properties,schema)
    