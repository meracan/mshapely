import os
import sys
import fiona
import json
from shapely.geometry import mapping, shape,GeometryCollection,\
  Point,Polygon,LineString,MultiPoint,MultiLineString,MultiPolygon
from geojson import Feature, FeatureCollection, dump

def writeGeometry(geometry, path, schema=None, properties=None, type="geojson"):
  """
  Write to file
  
  Parameters
  ----------
  geometry: 
  path: 
  schema: 
  properties: 
  type: 
  
  Example
  ------ 
  TODO
  """
  
  def getSchema(geometry, schema):
    if schema is not None: return schema
    return {'geometry': geometry[0].type, "properties": {"id": "int:10"}}
  
  def getProperties(geometry, properties):
    if properties is not None: return properties
    return [dict(id=i) for i, f in enumerate(geometry)]
  
  if geometry.is_empty:raise Exception("geometry is empty")

  geometry = geometry if isinstance(geometry, (list,GeometryCollection)) else [geometry]
  
  schema = getSchema(geometry, schema)
  properties = getProperties(geometry, properties)
  
  if type == 'shp':
    writeShapefile(dict(schema=schema, geometry=geometry, properties=properties), path)
  elif type == 'geojson':
    writeGeoJSON(dict(schema=schema, geometry=geometry, properties=properties), path)
  else:
    print("Type does not exist yet")


def writeShapefile(collection, output):
  """
  Write to shapefile
  
  Parameters
  ----------
  collection: 
  output: 
  
  Example
  ------ 
  TODO
  """    
  schema = collection['schema']
  geometry = collection['geometry']
  properties = collection['properties']
  with fiona.collection(output, "w", "ESRI Shapefile", schema) as shapefile:
    for geometry, property in zip(geometry, properties):
      shapefile.write({'geometry': mapping(geometry),
                       'properties': property
                       })

def writeGeoJSON(collection,output):
  schema = collection['schema']
  geometry = collection['geometry']
  properties = collection['properties']
  
  features = []
  for geo, property in zip(geometry, properties):
    features.append(Feature(geometry=geo, properties=property))
  
  with open(output, 'w') as f:
    collection=FeatureCollection(features)
    collection['schema']=schema
    dump(collection, f)
 
def readGeometry(path):
  if not os.path.isfile(path):
    sys.exit("File {0} does not exist".format(os.path.abspath(path)))  
  fileName, ext = os.path.splitext(path)
  if ext==".shp":return readShapefile(path)
  elif ext==".geojson":return readGeoJSON(path)
  
  sys.exit("File handler {0} does not exist".format(os.path.abspath(path)))  

def deleteGeometry(path): 
  if os.path.exists(path):
    name,ext=os.path.splitext(path)
    if ext==".shp":
      os.remove(path)
      os.remove(name+".shx")
      os.remove(name+".dbf")
      os.remove(name+".cpg")
    elif ext==".geojson":
      os.remove(path)
    
  
def readShapefile(shpPath):
  """
  Read collection from shapefile
  
  Parameters
  ----------
  collection: 
  output: 
  
  Example
  ------ 
  TODO
  """       
  # Get Feature/Geometry in memory for Shapely.
  if not os.path.isfile(shpPath):
    sys.exit("File {0} does not exist".format(os.path.abspath(shpPath)))
  
  with fiona.collection(shpPath, 'r') as input:
    geometry = GeometryCollection([shape(shp['geometry']) for shp in input])  # Save geometry
    properties = [shp['properties'] for shp in input]  # Save properties
    return dict(schema=input.schema.copy(), geometry=geometry, properties=properties)

def readGeoJSON(geoPath):
  """
  Read collection from shapefile
  
  Parameters
  ----------
  collection: 
  output: 
  
  Example
  ------ 
  TODO
  """     
  if not os.path.isfile(geoPath):
    sys.exit("File {0} does not exist".format(os.path.abspath(geoPath)))
  with open(geoPath) as f:
    collection=json.load(f)
    schema = collection.get("schema",{})
    features = collection["features"]
    geometry = GeometryCollection([shape(feature["geometry"]) for feature in features])
    properties = [feature['properties'] for feature in features]  # Save properties
    return dict(schema=schema, geometry=geometry, properties=properties)
  