# MERACAN Shapely
A shapely wrapper to manipulate spatial data for Marine Energy Resource Assessment Canada.



## Installation


This library was only tested using anaconda. 
Shapely and gdal might cause issues with pip only.
```bash
conda create -n mshapely python=3.8
conda activate mshapely
conda install -c conda-forge numpy scipy fiona shapely gdal geojson tqdm
git clone https://github.com/meracan/mshapely.git
pip install -e ./mshapely

```


## Usage
```python
import mshapely
```
### New Attributes and Methods
New attributes and methods was applied to all geometric instances.
- np
- xy
- _np()
- write()
- delete()
- resample()
- dresample()
- removeHoles()
- largest()
- dsimplify()
- inearest()
- correct()
- plot()
- savePlot()

### Examples
```python
# Examples
point = Point(0,0)
point.np
point.xy



{shapely.geometry}.write("path/to/file",type="shp|geojson")
{shapely.geometry}.delete("path/to/file")
{shapely.geometry}.resample(maxLength=1.0)
{shapely.geometry}.dresample(density, minDensity=1.0, maxDensity=10.0, growth=1.2)
{shapely.geometry}.removeHoles()
{shapely.geometry}.largest()
{shapely.geometry}.dsimplify()
{shapely.geometry}.inearest()
{shapely.geometry}.correct()
{shapely.geometry}.plot()
{shapely.geometry}.savePlot()

```

## Testing

```bash
conda install pytest
mkdir ../data
pytest
```



For developers and debugging:



```bash
mkdir ../s3
PYTHONPATH=../s3-netcdf/
PYTHONPATH=../mshapely/ python3 test/test_io.py

PYTHONPATH=../mshapely/ python3 test/test_tonumpy.py
PYTHONPATH=../mshapely/ python3 test/test_transformation.py
PYTHONPATH=../mshapely/ python3 test/test_resample.py
PYTHONPATH=../mshapely/ python3 test/test_spatial.py
PYTHONPATH=../mshapely/ python3 test/test_buffer.py
PYTHONPATH=../mshapely/ python3 test/test_osmshoreline.py
```

## Compilation
```bash
PYTHONPATH=../mshapely/ bash mshapely/cython/compile.sh

```

## TODO

1. Remove third dimension to norm