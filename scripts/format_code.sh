black -l 79 --exclude="trainme/models/yolov5" .

find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -path "./trainme/models/yolov5/*" \
    | xargs isort