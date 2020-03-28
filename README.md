# MERACAN Shapely
A shapely wrapper to manipulate spatial data for Marine Energy Resource Assessment Canada.



## Installation


This library was only tested using anaconda. 
Shapely and gdal might cause issues with pip only.
```bash
# To be able to run gmsh
sudo yum install mesa-libGL

conda create -n mshapely python=3.8
conda activate mshapely

conda install -c conda-forge numpy scipy fiona shapely gdal geojson tqdm matplotlib gmsh python-gmsh

# To plot mesh

git clone https://github.com/meracan/mshapely.git
pip install -e ./mshapely

```


## Usage
```python
import mshapely
```
[### User Guide and Examples](doc/README.md)




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