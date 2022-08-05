<p align="center">
  <h1 align="center">:star2: Train Me :star2:</h1>
  <p align="center">No-code Labeling and Training Toolkit for Computer Vision<p>
  <p align="center">With <b>Improved Labelme</b> for Image Labeling<p>
</p>

![](https://i.imgur.com/waxVImv.png)


## I. Install and run

- Requirements: Python >= 3.7
- Recommended: Miniconda/Anaconda <https://docs.conda.io/en/latest/miniconda.html>

- Create environment:

```
conda create -n trainme python=3.8
conda activate trainme
```

- **(For macOS only)** Install PyQt5 using Conda:

```
conda install -c conda-forge pyqt==5.15.7
```

- Install TrainMe:

```
pip install trainme-python
```

- Run app:

```
trainme_app
```

## II. Development

- Generate resources:

```
pyrcc5 -o trainme/resources/resources.py trainme/resources/resources.qrc
```

- Run app:

```
python trainme/app.py
```

## III. References

- labelme
- gpu_util
- Icons: Flat Icons