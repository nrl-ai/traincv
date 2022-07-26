black -l 79 --experimental-string-processing --exclude="core/models/yolov5" .

find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -path "./core/models/yolov5/*" \
    | xargs isort