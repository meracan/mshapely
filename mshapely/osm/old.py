  def _getOSMCoarse(self,geographicPath,projectedPath):
    """
    Extract osm coastline from zip file and simplify based on extent.
    This avoids unpacking the zip file.
    """
    osmPath=self.path['osmzip']
    bounds=self.domain.geo['geometry'].bounds
    extent=[np.floor(bounds[0]),np.floor(bounds[1]),np.ceil(bounds[2]),np.ceil(bounds[3])]
    # print(extent)
    # extent=[-60.0, 58.0, -40.0, 68.0]
    
    zipname = 'water-polygons-split-4326/water_polygons.shp'
    zipPath = "\"/vsizip/" + osmPath + "/" + zipname + "\""
    name = os.path.basename(osmPath)
    name = os.path.splitext(name)[0]
    
    # Transfer PBF to Shapefile - query only important coast
    pt1 = "{0} {1}".format(extent[0],extent[1])
    pt2 = "{0} {1}".format(extent[0],extent[3])
    pt3 = "{0} {1}".format(extent[2],extent[3])
    pt4 = "{0} {1}".format(extent[2],extent[1])
    
    
        
    
    # pg_sql = "\"SELECT ST_Union(ST_Intersection(ST_Buffer(ST_Transform(A.geometry,4326),0),B.geometry)) as geometry FROM simplified_water_polygons A,'{}'.'{}' B WHERE ST_Intersects(ST_Transform(A.geometry,4326), B.geometry) ;\"".format(domain,name)
    # pg_sql = "\"SELECT ST_Simplify(ST_Buffer(ST_Buffer(ST_Union(ST_Simplify(ST_Buffer(ST_Transform(A.geometry,3573),0),100)),-1000),1000),100) as geometry FROM simplified_water_polygons A,'{}'.'{}' B WHERE ST_Intersects(ST_Transform(A.geometry,3573), ST_Transform(SetSRID(B.geometry,4326),3573)) ;\"".format(domain,name)
    # pg_sql = "\"SELECT ST_Simplify(ST_Buffer(ST_Union(ST_Simplify(ST_Buffer(ST_Buffer(ST_Simplify(ST_Buffer(ST_Transform(A.geometry,3573),0),100),-1000),1000),100)),0),100) as geometry FROM simplified_water_polygons A,'{}'.'{}' B WHERE ST_Intersects(ST_Transform(A.geometry,3573), ST_Transform(SetSRID(B.geometry,4326),3573)) ;\"".format(domain,name)
    
    # pg_sql = "\"SELECT ST_Simplify(ST_Buffer(ST_Union(ST_Simplify(ST_Buffer(ST_Transform(A.geometry,3573),10),10)),-10),10) as geometry FROM simplified_water_polygons A,'{}'.'{}' B WHERE ST_Intersects(ST_Transform(A.geometry,3573), ST_Transform(SetSRID(B.geometry,4326),3573)) ;\"".format(domain,name)
    # pg_sql = "\"With one AS(SELECT ST_Simplify(ST_Buffer(ST_Buffer(ST_Simplify(ST_Buffer(ST_Transform(A.geometry,3573),100),10),-1000),1000),100) as geometry FROM simplified_water_polygons A,'{}'.'{}' B WHERE ST_Intersects(ST_Transform(A.geometry,3573), ST_Transform(SetSRID(B.geometry,4326),3573))) SELECT one.geometry from one WHERE one.geometry is not null;\"".format(domain,name)
    
    
    
    # pg_sql = "\"With one AS(SELECT Simplify(ST_Transform(geometry,3573),{5}) as geo FROM water_polygons WHERE ST_Intersects(geometry, ST_GeomFromText('POLYGON(({0}, {1}, {2}, {3}, {0}))', 4326))) SELECT Simplify(ST_Buffer(ST_Buffer(ST_Union(one.geo),-{4}),{4}),{5}) FROM one WHERE one.geo is not null;\"".format(pt1,pt2,pt3,pt4,self.maxDensity*0.1,self.maxDensity*0.05)
    # pg_sql = "\"With one AS(SELECT Simplify(ST_Transform(geometry,3573),10) as geo FROM water_polygons WHERE ST_Intersects(geometry, ST_GeomFromText('POLYGON(({0}, {1}, {2}, {3}, {0}))', 4326))) SELECT ST_UnaryUnion(ST_Collect(ST_Simplify(ST_Buffer(ST_Buffer(one.geo,-100),99),10))) FROM one WHERE one.geo is not null;\"".format(pt1,pt2,pt3,pt4)
    pg_sql = "\"With one AS(SELECT Simplify(ST_Transform(geometry,3573),100) as geo FROM water_polygons WHERE ST_Intersects(geometry, ST_GeomFromText('POLYGON(({0}, {1}, {2}, {3}, {0}))', 4326))) SELECT ST_Simplify(ST_Buffer(ST_Buffer(ST_UnaryUnion(ST_Collect(ST_Simplify(ST_Buffer(ST_Buffer(one.geo,-1000),1000),100))),-2000),2000),200) FROM one WHERE one.geo is not null;\"".format(pt1,pt2,pt3,pt4)
    
    
    command = "ogr2ogr -skipfailures -f \"GeoJSON\" {0} -nlt POLYGON -dialect \"SQLITE\" -sql {1} {2}".format(projectedPath,pg_sql,zipPath)
    print(command)
    subprocess.call(command, shell=True)
    
  # def _getOSM(self,geographicPath,projectedPath):
  #   self._extractOSM(geographicPath,projectedPath,isPolygon=True)
  
  # def _getOSMCoarse(self,geographicPath,projectedPath):
    # self._extractOSM(geographicPath,projectedPath,coarse=True,isPolygon=True)
  
  # def _extractOSM(self,geographicPath,projectedPath,coarse=False,isPolygon=False):
  #   """
  #   Extract osm coastline from zip file based on extent.
  #   This requires gdal (ogr2ogr).
  #   This avoids unpacking the zip file.
  #   """
  #   osmPath=self.path['osmzip']
  #   bounds=self.domain.geo['geometry'].bounds
  #   extent=[np.floor(bounds[0]),np.floor(bounds[1]),np.ceil(bounds[2]),np.ceil(bounds[3])]
    
  #   extraPolygon=""
  #   if isPolygon:
  #     extraPolygon="-nlt POLYGON"
    
  #   zipname = 'water-polygons-split-4326/water_polygons.shp'
  #   zipPath = "\"/vsizip/" + osmPath + "/" + zipname + "\""
  #   name = os.path.basename(osmPath)
  #   name = os.path.splitext(name)[0]
    
  #   # Transfer PBF to Shapefile - query only important coast
  #   pt1 = "{0} {1}".format(extent[0],extent[1])
  #   pt2 = "{0} {1}".format(extent[0],extent[3])
  #   pt3 = "{0} {1}".format(extent[2],extent[3])
  #   pt4 = "{0} {1}".format(extent[2],extent[1])
    
  #   pg_sql=None
  #   if coarse:
  #     pg_sql = "\"With one AS(SELECT Simplify(ST_Buffer(ST_Buffer(Simplify(ST_Transform(geometry,3573),100),-1000),1000),100) as geo FROM water_polygons WHERE ST_Intersects(geometry, ST_GeomFromText('POLYGON(({0}, {1}, {2}, {3}, {0}))', 4326))) SELECT ST_Transform(ST_Union(one.geo),4326) FROM one WHERE one.geo is not null;\"".format(pt1,pt2,pt3,pt4)
  #   else:
  #     pg_sql = "\"SELECT * FROM water_polygons WHERE ST_Intersects(geometry, ST_GeomFromText('POLYGON(({0}, {1}, {2}, {3}, {0}))', 4326));\"".format(pt1,pt2,pt3,pt4)
    
  #   command = "ogr2ogr -skipfailures -f \"GeoJSON\" {0} {3}  -dialect \"SQLITE\" -sql {1} {2}".format(geographicPath,pg_sql,zipPath,extraPolygon)
  #   print(command)
  #   subprocess.call(command, shell=True)
    
    
    
    # pg_sql = "\"SELECT ST_Transform(geometry,3573) FROM water_polygons WHERE ST_Intersects(geometry, ST_GeomFromText('POLYGON(({0}, {1}, {2}, {3}, {0}))', 4326));\"".format(pt1,pt2,pt3,pt4)
    
    # "WITH one AS ( SELECT 1 ) "
    # pg_sql = "\"SELECT Simplify(ST_Buffer(water_polygons.geometry,0.000001),0.000001) FROM water_polygons, '../data/example2domain.geojson'.example2domain poly  WHERE ST_Intersects(water_polygons.geometry, poly.geometry);\""
    # pg_sql = "\"SELECT water_polygons.geometry FROM water_polygons, '../data/example2domain.geojson'.example2domain poly WHERE ST_Intersects(water_polygons.geometry, poly.geometry);\""
    # command = "ogr2ogr -skipfailures -f \"GeoJSON\" {0} -nln {1} -t_srs \"+proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m\" -dialect \"SQLITE\" -sql {2} {3} {4}".format(outPath,name,pg_sql,zipPath,"../data/example2domain.geojson")
    
    # Works
    
    
    # command = "ogr2ogr -progress -skipfailures -f \"GeoJSON\" {0} -progress -nln {1} -dialect \"SQLITE\" -sql {2} {3}".format(outOSM,name,pg_sql,zipPath)
    # print(command)
    # subprocess.call(command, shell=True)
    
    # os.remove(paths['osmCoarseproj'])
    # command = "ogr2ogr -progress -skipfailures -f \"GeoJSON\" {0} -progress -nln {1} -dialect \"SQLITE\" -sql {2} {3}".format(paths['osmCoarseproj'],name,pg_sql_t,paths['osmCoarse'])
    # print(command)
    # subprocess.call(command, shell=True)
    
    
      def _getosmDomain(self,geographicPath,projectedPath):
    """
    Extract osm coastline using the domain.
    It will only keep the largest Polygon.
    """
    geo = self.osmsim.proj['geometry']
    minDensity = self.minDensity
    # cB = self.cB
    domain = self.domain.proj['geometry']
    # t=tqdm(total=len(geo))
    # _polygons=[]
    # for x in np.arange(0,len(geo),400):
    #   xn=np.minimum(len(geo),x+400)
    #   polygons=[]
    #   for polygon in list(geo)[x:xn]:
    #     if(polygon.intersects(domain)):
    #       # pol = polygon
    #       if not polygon.is_empty:
    #         # polygons.append(pol)
    #         polygons.append(polygon.buffer(0.01))
    #     t.update(1)
    #   _polygons.append(polygons)
        
      # if _polygons is None:
      #   print(len(polygons))
      #   _polygons=unary_union(polygons)
      # else:
        
      #   _polygons=_polygons.union(unary_union(polygons))
    # t.close()
    # geo=GeometryCollection(_polygons)
    # t=tqdm(total=6)  
    # geo=_polygons
    # geo=unary_union(geo);t.update(1)
    # geo=geo.buffer(0.01);t.update(1)
    # geo=geo.simplify(1);t.update(1)
    t=tqdm(total=4)
    geo=geo.simplify(100);t.update(1)
    geo=geo.buffer(1);t.update(1)
    geo=geo.simplify(100);t.update(1)
    geo=geo.intersection(domain);t.update(1)
    geo.write(projectedPath)
    # geo=geo.buffer(0.01);t.update(1)
    # geo=geo.simplify(10);t.update(1)
    
    t.close()
    # t=tqdm(total=1)  
    # geo=geo.simplify(10);t.update(1)
    # geo=geo.buffer(0.01);t.update(1)
    # geo=geo.simplify(0.1);t.update(1)
    # from shapely.prepared import prep
    # geo=cascaded_union(geo);t.update(1)
    # geo=geo.intersection(domain);t.update(1)
    # geo=geo.buffer(0.01);t.update(1)
    # geo=geo.simplify(0.1);t.update(1)
    # geo=geo.largest();t.update(1)
    # geo=geo.simplify(0.1);
    # t.close()
    
    return geo
    
def dsimplify_Polygon__(polygon,points,minDensity=1,maxDensity=10,mingrowth=1.2,coarse=None):
  """
  Simplify polygons and remove points by respecting minimum density field.
  It mainly uses the buffer/unbuffer techniques for different density area/zone.
  
  Parameters
  ----------
  polyon:Polygon
  points:ndarray
    shape(npoint,3)
  minDensity:float
  maxDensity:float
  growth:float
  cB:float
    Correction buffer
  
  Notes
  -----
  Correction buffers are used to correc geometric issues.
  
  TODO: points should be replace by features to include points,lines and polygons
    
  """
  
  
  
  points = dsimplify_Point(points,minDensity=1,maxDensity=10,mingrowth=1.2)
  
  xy = points[:, [0, 1]]
  density = points[:, 2]
  # growth = points[:, 3]
  udensity = np.unique(density)
  
  
  
  
  steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4,4E4,7E4,1E5,2E5,4E5,7E5],dtype=np.float32)
  # steps = np.array([10,20,40,70,100,200,400,700,1000,2000,4000,7000,1E4,2E4],dtype=np.float32)
  steps=steps[steps<polygon.length]
  maxDensity=np.minimum(maxDensity,polygon.length*0.1)
  
  
  n= np.maximum(np.floor(np.log(maxDensity/minDensity)/np.log(mingrowth)-1),1)
  maxDistance = (minDensity*np.power(mingrowth,n+1)-minDensity)/(mingrowth-1)
  
  polygon =polygon
  opolygon=polygon
  
  def getZones(tpolygon,d):
    ozones=[]
    zones=[]
    for unique in udensity:
      mps=MultiPoint(xy[density==unique]).buffer(d)
      _n=np.floor(np.log(d*(mingrowth-1)/unique+1)/np.log(mingrowth))
      _d = np.maximum(minDensity,unique*np.power(mingrowth,_n))


      ozone=tpolygon.intersection(mps)
      zone=ozone.buffer(-_d*0.2).buffer(_d*0.2).removeHoles(cArea(_d*0.1)).simplify(_d*0.01)
      
      ozones.append(zone.getExterior().union(mps.buffer(-_d*0.2)))
      # ozones.append(mps)
      zones.append(zone)
    
    ozones=cascaded_union(ozones)
    zones=cascaded_union(zones)
    # zones.plot("o-")
    return zones,ozones
  
  
  def process(domain,newdomain,prev,d,outline=None):
    if outline is not None:
      newzones=outline.difference(prev).buffer(1)
      
      if not newzones.is_empty: 
        newdomain=newdomain.union(newzones).buffer(0.01).simplify(1)
      return newdomain,prev
      
    zones,ozones = getZones(domain,d)
    if newdomain is None:return zones,ozones
    if zones.is_empty:return newdomain,prev
    newzones=zones.difference(prev).buffer(1)
    # if i==11:newzones.plot("o-")
    if not ozones.is_empty:prev=ozones
    if newzones.is_empty: return newdomain,prev
    newdomain=newdomain.union(newzones).buffer(0.01).simplify(1)
    # if i==11:newdomain.plot("o-")
    return newdomain,prev
  
  
  steps=steps[steps>=minDensity]
  steps=steps[steps<maxDistance]
  ndomain=None
  prev=None
  _dd=None
  t=tqdm(total=len(steps), unit_scale=True)
  for i,d in enumerate(steps):
    if(i%8==0):
      _nn=np.floor(np.log(d*(mingrowth-1)/minDensity+1)/np.log(mingrowth))
      _dd = np.maximum(minDensity,minDensity*np.power(mingrowth,_nn))
      opolygon=opolygon.simplify(_dd*0.01)
    ndomain,prev=process(opolygon,ndomain,prev,d)
    # ndomain.plot()
    t.update(1)
  t.close()
  
  # prev.plot("o-")
  # ndomain.plot("o-")
  t=tqdm(total=1, unit_scale=True)  
  outline=polygon.simplify(_dd*0.1)
  outline=outline.buffer(-maxDensity*0.1).buffer(maxDensity*0.1)
  if not outline.is_empty:
    outline=outline.removeHoles(cArea(maxDensity*0.1)).simplify(maxDensity*0.01)
    
    ndomain,prev=process(None,ndomain,prev,maxDistance,outline)
  t.update(1);t.close()  
  # ndomain.plot("o-")
  
  
  return ndomain