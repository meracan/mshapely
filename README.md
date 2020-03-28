# MERACAN Shapely
A shapely wrapper to manipulate spatial data for Marine Energy Resource Assessment Canada.
Mesh generation is currently intertwine with mshapely. There is a plan to extract it and create a seperate package.


## Installation
This library was only tested using conda.
It requires shapely,fiona,gdal and gmsh.
These packages might cause issues with pip.
```bash
conda create -n mshapely python=3.8
conda activate mshapely

conda install -c conda-forge numpy scipy fiona shapely pyproj requests gdal geojson tqdm matplotlib gmsh 
# git clone https://github.com/meracan/mshapely.git
# pip install -e ./mshapely

# On AWS VM
sudo yum install mesa-libGL


```


### Usage
```python
import mshapely
```
### User Guide and Examples
[Docs](doc/README.md)

###



### Testing

```bash
conda install pytest
mkdir ../data
pytest
```

For developers and debugging:
```bash
mkdir ../data
cd mshapely
conda activate mshapely
PYTHONPATH=../mshapely/ python3 test/test_io.py
PYTHONPATH=../mshapely/ python3 test/test_tonumpy.py
PYTHONPATH=../mshapely/ python3 test/test_transformation.py
PYTHONPATH=../mshapely/ python3 test/test_resample.py
PYTHONPATH=../mshapely/ python3 test/test_spatial.py
PYTHONPATH=../mshapely/ python3 test/test_buffer.py
PYTHONPATH=../mshapely/ python3 test/test_osmshoreline.py

PYTHONPATH=../mshapely/ python3 doc/doc_mshapely.py
PYTHONPATH=../mshapely/ python3 doc/doc_osm.py
```
###  


[### License](LICENSE)