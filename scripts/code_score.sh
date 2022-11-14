find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -name "./build/*" \
    -not -name "./dist/*" \
    -not -path "./trainme/trainer/models/yolov5/*" \
    | xargs pylint