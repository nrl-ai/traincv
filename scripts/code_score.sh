find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -path "./trainme/models/yolov5/*" \
    | xargs pylint