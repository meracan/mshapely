# Introduction

#### Chain approach

#### General Attributes and Methods


#### object.np
```
  Returns numpy array of the object. 
  The array contains coordinates(xy) and parent ids.
  
  Output
  ------ 
  ndarray: 2D array. 
   shape: Varies depending on the object and parameters. 
```
Examples
```python
>>> Point(0,0).np
[[0. 0.]]

>>> LineString([[0,0],[1,0],[2,0]]).np
[[0. 0. 0.]
 [1. 1. 0.]
 [2. 2. 0.]]

>>> Polygon([[0,0],[1,0],[2,0],[0,0]]).np
[[0. 0. 0. 0.]
 [0. 1. 1. 0.]
 [0. 2. 2. 0.]
 [0. 0. 0. 0.]]

>>> MultiPoint([[0,0],[1,0],[2,0],[0,0]]).np
[[0. 0. 0.]
 [1. 1. 0.]
 [2. 2. 0.]
 [3. 0. 0.]]
 
>>> MultiLineString([[[0,0],[1,0]],[[2,0],[3,0]]]).np
[[0. 0. 0. 0.]
 [0. 1. 1. 0.]
 [1. 0. 2. 0.]
 [1. 1. 3. 0.]]
 
>>> MultiPolygon([Polygon([[0,0],[1,0],[2,0],[0,0]])]).np
[[0. 0. 0. 0. 0.]
 [0. 0. 1. 1. 0.]
 [0. 0. 2. 2. 0.]
 [0. 0. 0. 0. 0.]]
 
```

#### object.xy
```
  Returns the xy coordinates of the object.
  Output
  ------ 
  ndarray: 2D array. 
   shape:(npoint,2)
```
Examples
```python
>>> Point(0,0).xy
[[0. 0.]]

>>> LineString([[0,0],[1,0],[2,0]]).xy
[[0. 0.]
 [1. 0.]
 [2. 0.]]

>>> Polygon([[0,0],[1,0],[2,0],[0,0]]).xy
[[0. 0.]
 [1. 0.]
 [2. 0.]
 [0. 0.]]
 
>>> MultiPoint([[0,0],[1,0],[2,0],[0,0]]).xy
[[0. 0.]
 [1. 0.]
 [2. 0.]
 [0. 0.]]
 
>>> MultiLineString([[[0,0],[1,0]],[[2,0],[3,0]]]).xy
[[0. 0.]
 [1. 0.]
 [2. 0.]
 [3. 0.]]
 
>>> MultiPolygon([Polygon([[0,0],[1,0],[2,0],[0,0]])]).xy
[[0. 0.]
 [1. 0.]
 [2. 0.]
 [0. 0.]]
```


#### object._np([,isNorm,onPoint])
```
  Returns the numpy array of the object with special requirements.
  Parameters
  ----------
  isNorm: bool,optional
    If True, returns normal vectors information
  onPoint: bool,optional
    If True,computes normal vectors from point.
    If False, computer normal vector from segment
    Default is True.
  
  Output
  ------ 
  ndarray: 2D array. 
   shape: Varies depending on the object and parameters. 
```

Examples
```python
>>> LineString([[0,0],[1,0],[2,0]])._np()
[[0. 0. 0.]
 [1. 1. 0.]
 [2. 2. 0.]]
 
>>> LineString([[0,0],[1,0],[2,0]])._np(isNorm=True)
[[ 0.  0.  0.  0.  1.  0.  0.]
 [ 1.  1.  0.  0. -1.  1.  0.]
 [ 2.  2.  0.  0.  1.  2.  0.]]

>>> LineString([[0,0],[1,0],[2,0]])._np(isNorm=True,onPoint=False)
[[ 0.   0.5  0.   0.  -1.   0.   0. ]
 [ 1.   1.5  0.   0.  -1.   1.   0. ]
 [ 2.   1.   0.   0.   1.   2.   0. ]]

```
#### object.write(path[,schema,properties,type])
```
  """
  Write to file
  
  Parameters
  ----------
  path: str
  schema: dict,optional
   Schema is used for shapefiles. 
   Creates on automatically unless specified.
  properties: list,optional
   Length must be equal to length of the object.
  type: enum, optional
   "shp","geojson". Default is "geojson"
  """
```
Examples
```python
>>> path_p_geo="test_io.point.geojson"
>>> path_p_shp="test_io.point.shp"
>>> Point((0,0)).write(path_p_geo,type="geojson").write(path_p_shp,type="shp")
```
#### object.delete(path) or mshapely.io.delete(path)
```
  """
  Delete file. 
  Deleting shapefiles will delete associate files.
  
  Parameters
  ----------
  path: str
  """
```
Examples
```python
>>> path_p_shp="test_io.point.shp"
>>> Point((0,0)).write(path_p_shp,type="shp").delete(path_p_shp)
```

#### object.resample(maxLength)
```
  Resample object using equal segment length. 
  The segment is automatically calculated using the maxLength or smaller segment.
  
  Parameters
  ----------
  maxLength: float,optional
    Default is 1.0.
```
Examples
```python
>>> LineString([(0,0),(10,0)]).resample()
LINESTRING (0 0, 1 0, 2 0, 3 0, 4 0, 5 0, 6 0, 7 0, 8 0, 9 0, 10 0)
```

#### object.dresample(density[,minDensity,maxDensity,growth])
```
  Resample object using a 2D density growth field. 
  The length of the segments are automatically calculated based on the density growth field.
  The growth of the field depends on the density points and growth factor.
  
  Parameters
  ----------
  density: ndarray
   shape:(n,3)
       n:n density points
       3:x,y,density
  minDensity:float,optional
    Smallest segment length. Default is 1.0.
  maxDensity:float,optional
    Largest segment length. Default is 10.0.
  growth:float,optional
    Density growth factor. Default is 1.2.
    
```
Examples
```python
>>> LineString([(0,0),(30,0)]).dresample(np.array([[0,0,1]]), minDensity=1.0, maxDensity=5.0, growth=1.2)
LINESTRING (0 0, 1 0, 2.2 0, 3.64 0, 5.368 0, 7.4416 0, 9.929919999999999 0, 12.915904 0, 16.49908479999999 0, 20.56560332814453 0, 25.28280166407226 0, 30 0)
```
[![dresample.1](img/dresample.1.png)](img/dresample.1.png)
```python
>>> LineString([(0,0),(30,0)]).dresample(np.array([[0,0,1]]), minDensity=1.0, maxDensity=5.0, growth=1.2)
LINESTRING (0 0, 1 0, 2.2 0, 3.64 0, 5.368 0, 7.4416 0, 9.929919999999999 0, 12.915904 0, 16.49908479999999 0, 20.56560332814453 0, 25.28280166407226 0, 30 0)
```
[![dresample.2](img/dresample.2.png)](img/dresample.2.png)
```python
>>> LineString([(0,0),(30,0)]).dresample(np.array([[0,0,1]]), minDensity=1.0, maxDensity=5.0, growth=1.2)
LINESTRING (0 0, 1 0, 2.2 0, 3.64 0, 5.368 0, 7.4416 0, 9.929919999999999 0, 12.915904 0, 16.49908479999999 0, 20.56560332814453 0, 25.28280166407226 0, 30 0)
```
[![dresample.3](img/dresample.3.png)](img/dresample.3.png)

#### object.dresample()
#### object.removeHoles()
#### object.largest()
#### object.dsimplify()
#### object.inearest()
#### object.correct()
#### object.plot()
#### object.savePlot()