<p align="center">
  <h1 align="center">:star2: Train Me :star2:</h1>
  <p align="center">No-code Labeling and Training Toolkit for Computer Vision<p>
  <p align="center">With <b>Improved Labelme</b> for Image Labeling<p>
</p>

![](https://i.imgur.com/waxVImv.png)


## I. Install and run

- Requirements: Python 3.x

- Install:

```
pip install git+https://github.com/vietanhdev/trainme.git
```

- Run TrainMe App:

```
trainme_app
```

## II. Development

### 1. Environment setup

- Install Miniconda: <https://docs.conda.io/en/latest/miniconda.html>. Please ensure to **add Miniconda to the PATH** when installing.

- Restart the system after installing Conda.

- Create a new Python environment:

```
conda create -n trainme python=3.8
```

- Activate the Python environment (need to run everytime on a new Terminal/Bash):

```
conda activate trainme
```

- Install Python requirements:

```
conda activate trainme
pip install -r requirements.txt
```

- For macOS, please use:

```
conda activate trainme
pip install -r requirements-macos.txt
conda install -c conda-forge pyqt
```

- Generate resource and UI:

```
pyrcc5 -o trainme/resources/resources.py trainme/resources/resources.qrc
```

### 2. Run program

```
conda activate trainme
python trainme/app.py
```

## III. References

- labelme
- gpu_util
- Icons: Flat Icons