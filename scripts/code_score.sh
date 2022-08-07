find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -path "./trainme/trainer/models/yolov5/*" \
    | xargs pylint