import cv2
from PyQt5 import QtCore
from .utils import opencv as ocvutil


class OCVTracker():

    def __init__(self, *args, **kwargs):
        self.shape = None
        self.prevImage = None

    def getRectForTracker(self, img, shape):
        qrect = shape.boundingRect()
        tl = qrect.topLeft()
        h = qrect.height()
        w = qrect.width()
        rect = (tl.x(), tl.y(), w, h)
        return [int(_) for _ in rect]

    def initTracker(self, qimg, shape):
        status = False
        self.shape = shape
        if qimg.isNull() or not shape:
            print("No object initialized")
            return status
        else:
            fimg = ocvutil.qtImg2CvMat(qimg)
            fimg = cv2.cvtColor(fimg, cv2.COLOR_BGR2GRAY)
            self.prevImage = fimg
            status = True
        return status

    def updateTracker(self, qimg):
        shape = self.shape.copy()
        assert (shape and shape.label ==
                self.shape.label), "Invalid tracker state!"
        status = False
        if qimg is None:
            print("No image to update tracker")
            return shape, status

        mimg = ocvutil.qtImg2CvMat(qimg)
        mimg = cv2.cvtColor(mimg, cv2.COLOR_BGR2GRAY)

        p1 = (int(self.shape.points[0].x()), int(self.shape.points[0].y()))
        p2 = (int(self.shape.points[1].x()), int(self.shape.points[1].y()))
        prevBox = (p1[0], p1[1], p2[0] - p1[0], p2[1] - p1[1])

        self.tracker = cv2.TrackerKCF_create()
        self.tracker.init(self.prevImage, prevBox)
        success, box = self.tracker.update(mimg)

        if(success):
            shape.points = [
                QtCore.QPoint(box[0], box[1]),
                QtCore.QPoint(box[0] + box[2], box[1] + box[3])
            ]
            status = True
        else:
            print("Tracker failed")

        return shape, status


class Tracker:
    def __init__(self) -> None:
        self.prevImage = None
        self.prevShapes = None
        self.ocvTracker = OCVTracker()

    def update(self, prevShapes, prevImage):
        self.prevShapes = prevShapes
        self.prevImage = prevImage

    def get(self, img):
        if self.prevImage is None:
            return []

        newShapes = []
        for shape in self.prevShapes:
            if shape.shape_type != "rectangle":
                newShape.append(shape)
                continue
            self.ocvTracker.initTracker(self.prevImage, shape)
            newShape, _ = self.ocvTracker.updateTracker(img)
            newShapes.append(newShape)

        return newShapes
