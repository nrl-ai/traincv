black -l 79 --experimental-string-processing --exclude="trainme/trainer/models/yolov5" .

find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -path "./trainme/trainer/models/yolov5/*" \
    | xargs isort