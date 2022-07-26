find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -path "./core/models/yolov5/*" \
    | xargs pylint