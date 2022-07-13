# Train YOLOv5 Object Detection

## 0. Environment

```
conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorchy
pip install -r trainme/models/yolov5/requirements.txt
```

## 1. Data preparation

- How to prepare custom data for YOLOv5: <https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data>.


## 2. Train


```
cd trainme/models/yolov5
python train.py --img 418 --batch 16 --epochs 30 --data ../../../configs/yolov5-data.yaml --weights yolov5n.pt
```