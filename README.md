<p align="center">
  <h1 align="center">🌟 TrainCV 🌟</h1>
  <p align="center">No-code Labeling and Training Toolkit for Computer Vision<p>
  <p align="center">With <b>Improved Labelme</b> for Image Labeling<p>
</p>

![](https://i.imgur.com/waxVImv.png)

## TODO

This project is **under development**. Please consider everything here unstable. There are a lot of features need to be added in the future.

You can request new features through [this contact form](https://aicurious.io/contact/).

- [x] **Labeling:** Integrate labelme
- [x] **Labeling:** UI for textbox labeling (OCR, labels + positions)
- [x] **Labeling:** Group objects (can be used in key-value matching problems)
- [x] **Labeling:** Auto-labeling with YOLOv5
- [ ] **Labeling:** Tracking for video labeling
- [ ] **Training:** Project + Experiment management
- [ ] **Training:** Object detection
- [ ] **Training:** Image classification
- [ ] **Training:** Image segmentation
- [ ] **Training:** Instance segmentation
- [ ] **Training:** Add docker support for training
- [ ] **Deployment:** Export to ONNX
- [ ] **Deployment:** Export to TFLite
- [ ] **Deployment:** Export to TensorRT
- [ ] CI/CD for Pypi package publishment
- [ ] Unit tests
- [ ] Documentation


## I. Install and run

- Requirements: Python >= 3.8
- Recommended: Miniconda/Anaconda <https://docs.conda.io/en/latest/miniconda.html>

- Create environment:

```
conda create -n traincv python=3.8
conda activate traincv
```

- **(For macOS only)** Install PyQt5 using Conda:

```
conda install -c conda-forge pyqt==5.15.7
```

- Install traincv:

```
pip install traincv
```

- Run app:

```
traincv_app
```

Or

```
python -m traincv.app
```

## II. Development

- Generate resources:

```
pyrcc5 -o traincv/resources/resources.py traincv/resources/resources.qrc
```

- Run app:

```
python traincv/app.py
```

## III. References

- labelme
- gpu_util
- Icons: Flat Icons
