# MERACAN Shapely (MShapely)
MShapely is a [Shapely](https://shapely.readthedocs.io/en/latest/manual.html) wrapper to enhance shapely functionalities and to manipulate spatial data for Marine Energy Resource Assessment Canada.

It provides extra functionality such as complex resampling, simplification, nearest nodes, etc. MShapely was mainly developed to help the development of complex 2-dimensional meshes for free-surface hydrodynamic models in coastal regions.

## Installation
This package was developed,tested and built using conda.
MShapely uses shapely,numpy,scipy,fiona and matplotlib.
Only tested with python >=3.6
```bash
conda create -n mshapely python=3.8
conda activate mshapely
conda install -c meracan mshapely
```
Local installation
```bash
conda create -n mshapely python=3.8
conda activate mshapely
conda install -c conda-forge numpy scipy fiona shapely pyproj requests geojson tqdm matplotlib
git clone https://github.com/meracan/mshapely.git
pip install -e ./mshapely
```
### Usage, user guide and examples
[Docs](doc/doc_mshapely.ipynb)

### Testing
[Docs](test/README.md)

### License
[License](LICENSE)