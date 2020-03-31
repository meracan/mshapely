# Density Field object
Density Field object is used to resample (Multi)LineString and (Multi)Polygon based on density values.

The density field is based on density points. Density points contain xy coordinates, density and growth values.
The density value indicates the required length for the xy location. 
The density increases in the field based on the density point information.

For example, here are two density points:\
P1=(x=0,y=0,density=1,growth=1.2)\
P2=(x=5,y=0,density=1,growth=1.05)

P1 is located x=0 and y=0 with a density value of 1.0 and growth of 1.2.\
P2 is located x=5 and y=0 with a density value of 1.0 and growth of 1.05.

From these two points, here is the density field.

[![density.1](img/density.1.png)](img/density.1.png)

As shown in the image, the density grows from two density points. 
Notice that the growth is diffrent from the two points since they have two different growth values.

The density field automatically removes uninfluential points. For example, here are three density points:\
P1=(x=0,y=0,density=1,growth=1.2)\
P2=(x=5,y=0,density=1,growth=1.05)\
P3=(x=2.5,y=0,density=10,growth=1.05)

P3 will automatically be deleted since its has no inluence in the field.

#### Theory
The density field is created from density points. 
Here is examplte of a density point(blue) and a density field location(red).

[![diagram](img/diagram.png)](img/diagram.png)

*d*=density point value\
*g*=growth point value\
*n*=n factor\
*D*=field density\
*l*=length or distance from density point to desnity field location

The density grows using the following equation:
[![getD_n](img/getD_n.png)](img/getD_n.png)

If n is unknown and D is known:
[![getn_D](img/getn_D.png)](img/getn_D.png)

To calculate the length or distance from density point to density field location, the sum needs to be calculated:

[![getl_n_sum](img/getl_n_sum.png)](img/getl_n_sum.png)

To simplify, the sum can be converted to closed form:

[![getclosedform](img/getclosedform.png)](img/getclosedform.png)

or

[![getl_n](img/getl_n.png)](img/getl_n.png)

If n is unknown and l is known:

[![getn_l](img/getn_l.png)](img/getn_l.png)


### Init,Attributes and Methods 
#### mshapely.DF(array[,minDensity=None,maxDensity=None,minGrowth=None])
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
  
  Attributes
  ----
  dp: ndarray
```

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
### densityField.plot()
### densityField.savePlot()
```

```