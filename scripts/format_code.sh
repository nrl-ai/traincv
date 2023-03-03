find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -name "./build/*" \
    -not -name "./dist/*" \
    -not -path "./traincv/trainer/models/yolov5/*" \
    | xargs black -l 79 --experimental-string-processing

find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -name "./build/*" \
    -not -name "./dist/*" \
    -not -path "./traincv/trainer/models/yolov5/*" \
    | xargs isort