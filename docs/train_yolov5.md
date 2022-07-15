# Train YOLOv5 Object Detection

## 0. Environment

```shell
conda activate trainme
conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorch
conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cpuonly -c pytorch # For CPU
pip install -r trainme/models/yolov5/requirements.txt

# Fix OpenCV error
pip uninstall opencv-python opencv-contrib-python
pip install opencv-contrib-python-headless==4.4.0.46
```

## 1. Data preparation

- How to prepare custom data for YOLOv5: <https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data>.


## 2. Train


```shell
cd trainme/models/yolov5
python train.py --img 640 --batch 16 --epochs 30 --data ../../../configs/yolov5_data.yaml --weights yolov5n.pt
```

## 3. Use model for labeling

- Convert model


```shell
cd trainme/models/yolov5
python export.py --weights models/YOLOv5s.pt --include onnx
```

- Prepare a configuration file `model.yaml`:

```
model_path: ./model.onnx
input_width: 640
input_height: 640
score_threshold: 0.5
nms_threshold: 0.45
confidence_threshold: 0.45
classes:
  - example_class
```

- Press **L**, select the configuration file to load the model.
- Press **I** to run auto labeling with pretrained model.