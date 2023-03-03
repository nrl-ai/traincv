find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -name "./build/*" \
    -not -name "./dist/*" \
    -not -path "./traincv/trainer/models/yolov5/*" \
    | xargs pylint