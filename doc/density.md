# Density Field object
This object is used to resample (Multi)LineString and (Multi)Polygon based on a density field.

#### mshapely.DensityField(array[,minDensity=None,maxDensity=None,growth=None])
```
  Density field object.
  This object is used to resample (Multi)LineString and (Multi)Polygon based on a density field.
  
  Parameters
  ----------
  array: 2D ndarray
    shape: (npoint,4) : [[x,y,density,growth]] 
      x:x-coordinate
      y:y-coordinate
      density:density value
      growth:growth factor
  minDensity: float,
    Default minDensity of the field. If None, it takes minimum value of array-density
  maxDensity: float,
    Default maxDensity of the field. If None, it takes maximum value of array-density
  growth:float,
    Default growth of the field. If None,it will take minimum value of array-growth
  
  Note
  ----
  
  Attributes
  ----
  _x: ndarray
```
## Methods
### densityField.plot()
### densityField.savePlot()
### densityField.add(array)


```
  Add density values to object.
  
  Note
  ----
  
  
  Parameters
  ----------
  array: 2D ndarray or feature
    shape: (npoint,4) : [[x,y,density,growth]] 
      x:x-coordinate
      y:y-coordinate
      density:density value
      growth:growth factor
    
  minDensity: float,
    Default minDensity of the field. If None, it takes minimum value of array-density
  maxDensity: float,
    Default maxDensity of the field. If None, it takes maximum value of array-density
  growth:float,
    Default growth of the field. If None,it will take minimum value of array-growth
  
  Note
  ----
  
  Attributes
  ----
  _x: ndarray

```

```

```