# mshapely testing
[Pytest](https://docs.pytest.org/en/latest/) is used to test mshapely code.

### Installation
```bash
conda activate mshapely
conda install pytest
```
### Tests
```bash
conda activate mshapely
cd mshapely
mkdir ../data
pytest
```
### Developement and debugging:
```bash
cd mshapely
conda activate mshapely
PYTHONPATH=../mshapely/ pytest
PYTHONPATH=../mshapely/ python3 test/test_io.py
PYTHONPATH=../mshapely/ python3 test/test_linalg.py
PYTHONPATH=../mshapely/ python3 test/test_spatial.py
PYTHONPATH=../mshapely/ python3 test/test_density.py
PYTHONPATH=../mshapely/ jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser
```


