autopep8 --in-place --aggressive --aggressive \
         --max-line-length=100 --recursive \
         --ignore="E402" \
         --exclude="./trainme/models/yolov5/*,./trainme/app.py" \
         .

find . -type f -name "*.py" \
    -not -name "resources.py" \
    -not -path "./trainme/models/yolov5/*" \
    | xargs isort