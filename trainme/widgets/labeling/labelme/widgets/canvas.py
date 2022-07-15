from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWheelEvent

from .. import utils
from ..shape import Shape

CURSOR_DEFAULT = QtCore.Qt.ArrowCursor
CURSOR_POINT = QtCore.Qt.PointingHandCursor
CURSOR_DRAW = QtCore.Qt.CrossCursor
CURSOR_MOVE = QtCore.Qt.ClosedHandCursor
CURSOR_GRAB = QtCore.Qt.OpenHandCursor

MOVE_SPEED = 5.0


class Canvas(QtWidgets.QWidget):

    zoom_request = QtCore.pyqtSignal(int, QtCore.QPoint)
    scroll_request = QtCore.pyqtSignal(int, int)
    new_shape = QtCore.pyqtSignal()
    selection_changed = QtCore.pyqtSignal(list)
    shape_moved = QtCore.pyqtSignal()
    drawing_polygon = QtCore.pyqtSignal(bool)
    vertex_selected = QtCore.pyqtSignal(bool)

    CREATE, EDIT = 0, 1
    CREATE, EDIT = 0, 1

    # polygon, rectangle, line, or point
    _create_mode = "polygon"

    _fill_drawing = False

    def __init__(self, *args, **kwargs):
        self.epsilon = kwargs.pop("epsilon", 10.0)
        self.double_click = kwargs.pop("double_click", "close")
        if self.double_click not in [None, "close"]:
            raise ValueError(
                "Unexpected value for double_click event: {}".format(
                    self.double_click
                )
            )
        self.num_backups = kwargs.pop("num_backups", 10)
        super(Canvas, self).__init__(*args, **kwargs)
        # Initialise local state.
        self.mode = self.EDIT
        self.shapes = []
        self.shapes_backups = []
        self.current = None
        self.selected_shapes = []  # save the selected shapes here
        self.selected_shapes_copy = []
        # self.line represents:
        #   - create_mode == 'polygon': edge from last point to current
        #   - create_mode == 'rectangle': diagonal line of the rectangle
        #   - create_mode == 'line': the line
        #   - create_mode == 'point': the point
        self.line = Shape()
        self.prev_point = QtCore.QPoint()
        self.prev_move_point = QtCore.QPoint()
        self.offsets = QtCore.QPoint(), QtCore.QPoint()
        self.scale = 1.0
        self.pixmap = QtGui.QPixmap()
        self.visible = {}
        self._hide_backround = False
        self.hide_backround = False
        self.h_hape = None
        self.prev_h_shape = None
        self.h_vertex = None
        self.prev_h_vertex = None
        self.h_edge = None
        self.prev_h_edge = None
        self.moving_shape = False
        self.snapping = True
        self.h_shape_is_selected = False
        self._painter = QtGui.QPainter()
        self._cursor = CURSOR_DEFAULT
        # Menus:
        # 0: right-click without selection and dragging of shapes
        # 1: right-click with selection and dragging of shapes
        self.menus = (QtWidgets.QMenu(), QtWidgets.QMenu())
        # Set widget options.
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.show_cross_line = True

    def fill_drawing(self):
        return self._fill_drawing

    def set_fill_drawing(self, value):
        self._fill_drawing = value

    @property
    def create_mode(self):
        return self._create_mode

    @create_mode.setter
    def create_mode(self, value):
        if value not in [
            "polygon",
            "rectangle",
            "circle",
            "line",
            "point",
            "linestrip",
        ]:
            raise ValueError("Unsupported create_mode: %s" % value)
        self._create_mode = value

    def store_shapes(self):
        shapes_backup = []
        for shape in self.shapes:
            shapes_backup.append(shape.copy())
        if len(self.shapes_backups) > self.num_backups:
            self.shapes_backups = self.shapes_backups[-self.num_backups - 1:]
        self.shapes_backups.append(shapes_backup)

    @property
    def is_shape_restorable(self):
        # We save the state AFTER each edit (not before) so for an
        # edit to be undoable, we expect the CURRENT and the PREVIOUS state
        # to be in the undo stack.
        if len(self.shapes_backups) < 2:
            return False
        return True

    def restore_shape(self):
        # This does _part_ of the job of restoring shapes.
        # The complete process is also done in app.py::undoShapeEdit
        # and app.py::load_shapes and our own Canvas::load_shapes function.
        if not self.is_shape_restorable:
            return
        self.shapes_backups.pop()  # latest

        # The application will eventually call Canvas.load_shapes which will
        # push this right back onto the stack.
        shapes_backup = self.shapes_backups.pop()
        self.shapes = shapes_backup
        self.selected_shapes = []
        for shape in self.shapes:
            shape.selected = False
        self.update()

    def enterEvent(self, ev):
        self.override_cursor(self._cursor)

    def leaveEvent(self, ev):
        self.un_highlight()
        self.restore_cursor()

    def focusOutEvent(self, ev):
        self.restore_cursor()

    def is_visible(self, shape):
        return self.visible.get(shape, True)

    def drawing(self):
        return self.mode == self.CREATE

    def editing(self):
        return self.mode == self.EDIT

    def set_editing(self, value=True):
        self.mode = self.EDIT if value else self.CREATE
        if not value:  # Create
            self.un_highlight()
            self.deselect_shape()

    def un_highlight(self):
        if self.h_hape:
            self.h_hape.highlight_clear()
            self.update()
        self.prev_h_shape = self.h_hape
        self.prev_h_vertex = self.h_vertex
        self.prev_h_edge = self.h_edge
        self.h_hape = self.h_vertex = self.h_edge = None

    def selected_vertex(self):
        return self.h_vertex is not None

    def selected_edge(self):
        return self.h_edge is not None

    # QT Overload
    def mouseMoveEvent(self, ev):
        """Update line with last point and current coordinates."""
        try:
            pos = self.transform_pos(ev.localPos())
        except AttributeError:
            return

        self.prev_move_point = pos
        self.repaint()
        self.restore_cursor()

        # Polygon drawing.
        if self.drawing():
            self.line.shape_type = self.create_mode

            self.override_cursor(CURSOR_DRAW)
            if not self.current:
                return

            if self.out_off_pixmap(pos):
                # Don't allow the user to draw outside the pixmap.
                # Project the point to the pixmap's edges.
                pos = self.intersection_point(self.current[-1], pos)
            elif (
                self.snapping
                and len(self.current) > 1
                and self.create_mode == "polygon"
                and self.close_enough(pos, self.current[0])
            ):
                # Attract line to starting point and
                # colorise to alert the user.
                pos = self.current[0]
                self.override_cursor(CURSOR_POINT)
                self.current.highlight_vertex(0, Shape.NEAR_VERTEX)
            if self.create_mode in ["polygon", "linestrip"]:
                self.line[0] = self.current[-1]
                self.line[1] = pos
            elif self.create_mode == "rectangle":
                self.line.points = [self.current[0], pos]
                self.line.close()
            elif self.create_mode == "circle":
                self.line.points = [self.current[0], pos]
                self.line.shape_type = "circle"
            elif self.create_mode == "line":
                self.line.points = [self.current[0], pos]
                self.line.close()
            elif self.create_mode == "point":
                self.line.points = [self.current[0]]
                self.line.close()
            self.repaint()
            self.current.highlight_clear()
            return

        # Polygon copy moving.
        if QtCore.Qt.RightButton & ev.buttons():
            if self.selected_shapes_copy and self.prev_point:
                self.override_cursor(CURSOR_MOVE)
                self.bounded_move_shapes(self.selected_shapes_copy, pos)
                self.repaint()
            elif self.selected_shapes:
                self.selected_shapes_copy = [
                    s.copy() for s in self.selected_shapes
                ]
                self.repaint()
            return

        # Polygon/Vertex moving.
        if QtCore.Qt.LeftButton & ev.buttons():
            if self.selected_vertex():
                self.bounded_move_vertex(pos)
                self.repaint()
                self.moving_shape = True
            elif self.selected_shapes and self.prev_point:
                self.override_cursor(CURSOR_MOVE)
                self.bounded_move_shapes(self.selected_shapes, pos)
                self.repaint()
                self.moving_shape = True
            return

        # Just hovering over the canvas, 2 possibilities:
        # - Highlight shapes
        # - Highlight vertex
        # Update shape/vertex fill and tooltip value accordingly.
        self.setToolTip(self.tr("Image"))
        for shape in reversed([s for s in self.shapes if self.is_visible(s)]):
            # Look for a nearby vertex to highlight. If that fails,
            # check if we happen to be inside a shape.
            index = shape.nearest_vertex(pos, self.epsilon / self.scale)
            index_edge = shape.nearest_edge(pos, self.epsilon / self.scale)
            if index is not None:
                if self.selected_vertex():
                    self.h_hape.highlight_clear()
                self.prev_h_vertex = self.h_vertex = index
                self.prev_h_shape = self.h_hape = shape
                self.prev_h_edge = self.h_edge
                self.h_edge = None
                shape.highlight_vertex(index, shape.MOVE_VERTEX)
                self.override_cursor(CURSOR_POINT)
                self.setToolTip(self.tr("Click & drag to move point"))
                self.setStatusTip(self.toolTip())
                self.update()
                break
            elif index_edge is not None and shape.can_add_point():
                if self.selected_vertex():
                    self.h_hape.highlight_clear()
                self.prev_h_vertex = self.h_vertex
                self.h_vertex = None
                self.prev_h_shape = self.h_hape = shape
                self.prev_h_edge = self.h_edge = index_edge
                self.override_cursor(CURSOR_POINT)
                self.setToolTip(self.tr("Click to create point"))
                self.setStatusTip(self.toolTip())
                self.update()
                break
            elif shape.contains_point(pos):
                if self.selected_vertex():
                    self.h_hape.highlight_clear()
                self.prev_h_vertex = self.h_vertex
                self.h_vertex = None
                self.prev_h_shape = self.h_hape = shape
                self.prev_h_edge = self.h_edge
                self.h_edge = None
                self.setToolTip(
                    self.tr("Click & drag to move shape '%s'") % shape.label
                )
                self.setStatusTip(self.toolTip())
                self.override_cursor(CURSOR_GRAB)
                self.update()
                break
        else:  # Nothing found, clear highlights, reset state.
            self.un_highlight()
        self.vertex_selected.emit(self.h_vertex is not None)

    def add_point_to_edge(self):
        shape = self.prev_h_shape
        index = self.prev_h_edge
        point = self.prev_move_point
        if shape is None or index is None or point is None:
            return
        shape.insert_point(index, point)
        shape.highlight_vertex(index, shape.MOVE_VERTEX)
        self.h_hape = shape
        self.h_vertex = index
        self.h_edge = None
        self.moving_shape = True

    def remove_selected_point(self):
        shape = self.prev_h_shape
        index = self.prev_h_vertex
        if shape is None or index is None:
            return
        shape.remove_point(index)
        shape.highlight_clear()
        self.h_hape = shape
        self.prev_h_vertex = None
        self.moving_shape = True  # Save changes

    # QT Overload
    def mousePressEvent(self, ev):
        pos = self.transform_pos(ev.localPos())
        if ev.button() == QtCore.Qt.LeftButton:
            if self.drawing():
                if self.current:
                    # Add point to existing shape.
                    if self.create_mode == "polygon":
                        self.current.add_point(self.line[1])
                        self.line[0] = self.current[-1]
                        if self.current.is_closed():
                            self.finalise()
                    elif self.create_mode in ["rectangle", "circle", "line"]:
                        assert len(self.current.points) == 1
                        self.current.points = self.line.points
                        self.finalise()
                    elif self.create_mode == "linestrip":
                        self.current.add_point(self.line[1])
                        self.line[0] = self.current[-1]
                        if int(ev.modifiers()) == QtCore.Qt.ControlModifier:
                            self.finalise()
                elif not self.out_off_pixmap(pos):
                    # Create new shape.
                    self.current = Shape(shape_type=self.create_mode)
                    self.current.add_point(pos)
                    if self.create_mode == "point":
                        self.finalise()
                    else:
                        if self.create_mode == "circle":
                            self.current.shape_type = "circle"
                        self.line.points = [pos, pos]
                        self.set_hiding()
                        self.drawing_polygon.emit(True)
                        self.update()
            elif self.editing():
                if self.selected_edge():
                    self.add_point_to_edge()
                elif (
                    self.selected_vertex()
                    and int(ev.modifiers()) == QtCore.Qt.ShiftModifier
                ):
                    # Delete point if: left-click + SHIFT on a point
                    self.remove_selected_point()

                group_mode = int(ev.modifiers()) == QtCore.Qt.ControlModifier
                self.select_shape_point(pos, multiple_selection_mode=group_mode)
                self.prev_point = pos
                self.repaint()
        elif ev.button() == QtCore.Qt.RightButton and self.editing():
            group_mode = int(ev.modifiers()) == QtCore.Qt.ControlModifier
            if not self.selected_shapes or (
                self.h_hape is not None
                and self.h_hape not in self.selected_shapes
            ):
                self.select_shape_point(pos, multiple_selection_mode=group_mode)
                self.repaint()
            self.prev_point = pos

    # QT Overload
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            menu = self.menus[len(self.selected_shapes_copy) > 0]
            self.restore_cursor()
            if (
                not menu.exec_(self.mapToGlobal(ev.pos()))
                and self.selected_shapes_copy
            ):
                # Cancel the move by deleting the shadow copy.
                self.selected_shapes_copy = []
                self.repaint()
        elif ev.button() == QtCore.Qt.LeftButton:
            if self.editing():
                if (
                    self.h_hape is not None
                    and self.h_shape_is_selected
                    and not self.moving_shape
                ):
                    self.selection_changed.emit(
                        [x for x in self.selected_shapes if x != self.h_hape]
                    )

        if self.moving_shape and self.h_hape:
            index = self.shapes.index(self.h_hape)
            if (
                self.shapes_backups[-1][index].points
                != self.shapes[index].points
            ):
                self.store_shapes()
                self.shape_moved.emit()

            self.moving_shape = False

    def end_move(self, copy):
        assert self.selected_shapes and self.selected_shapes_copy
        assert len(self.selected_shapes_copy) == len(self.selected_shapes)
        if copy:
            for i, shape in enumerate(self.selected_shapes_copy):
                self.shapes.append(shape)
                self.selected_shapes[i].selected = False
                self.selected_shapes[i] = shape
        else:
            for i, shape in enumerate(self.selected_shapes_copy):
                self.selected_shapes[i].points = shape.points
        self.selected_shapes_copy = []
        self.repaint()
        self.store_shapes()
        return True

    def hide_background_shapes(self, value):
        self.hide_backround = value
        if self.selected_shapes:
            # Only hide other shapes if there is a current selection.
            # Otherwise the user will not be able to select a shape.
            self.set_hiding(True)
            self.update()

    def set_hiding(self, enable=True):
        self._hide_backround = self.hide_backround if enable else False

    def can_close_shape(self):
        return self.drawing() and self.current and len(self.current) > 2

    # QT Overload
    def mouseDoubleClickEvent(self, ev):
        # We need at least 4 points here, since the mousePress handler
        # adds an extra one before this handler is called.
        if (
            self.double_click == "close"
            and self.can_close_shape()
            and len(self.current) > 3
        ):
            self.current.pop_point()
            self.finalise()

    def select_shapes(self, shapes):
        self.set_hiding()
        self.selection_changed.emit(shapes)
        self.update()

    def select_shape_point(self, point, multiple_selection_mode):
        """Select the first shape created which contains this point."""
        if self.selected_vertex():  # A vertex is marked for selection.
            index, shape = self.h_vertex, self.h_hape
            shape.highlight_vertex(index, shape.MOVE_VERTEX)
        else:
            for shape in reversed(self.shapes):
                if self.is_visible(shape) and shape.contains_point(point):
                    self.set_hiding()
                    if shape not in self.selected_shapes:
                        if multiple_selection_mode:
                            self.selection_changed.emit(
                                self.selected_shapes + [shape]
                            )
                        else:
                            self.selection_changed.emit([shape])
                        self.h_shape_is_selected = False
                    else:
                        self.h_shape_is_selected = True
                    self.calculate_offsets(point)
                    return
        self.deselect_shape()

    def calculate_offsets(self, point):
        left = self.pixmap.width() - 1
        right = 0
        top = self.pixmap.height() - 1
        bottom = 0
        for s in self.selected_shapes:
            rect = s.bounding_rect()
            if rect.left() < left:
                left = rect.left()
            if rect.right() > right:
                right = rect.right()
            if rect.top() < top:
                top = rect.top()
            if rect.bottom() > bottom:
                bottom = rect.bottom()

        x1 = left - point.x()
        y1 = top - point.y()
        x2 = right - point.x()
        y2 = bottom - point.y()
        self.offsets = QtCore.QPoint(x1, y1), QtCore.QPoint(x2, y2)

    def bounded_move_vertex(self, pos):
        index, shape = self.h_vertex, self.h_hape
        point = shape[index]
        if self.out_off_pixmap(pos):
            pos = self.intersection_point(point, pos)
        shape.move_vertex_by(index, pos - point)

    def bounded_move_shapes(self, shapes, pos):
        if self.out_off_pixmap(pos):
            return False  # No need to move
        o1 = pos + self.offsets[0]
        if self.out_off_pixmap(o1):
            pos -= QtCore.QPoint(min(0, o1.x()), min(0, o1.y()))
        o2 = pos + self.offsets[1]
        if self.out_off_pixmap(o2):
            pos += QtCore.QPoint(
                min(0, self.pixmap.width() - o2.x()),
                min(0, self.pixmap.height() - o2.y()),
            )
        # XXX: The next line tracks the new position of the cursor
        # relative to the shape, but also results in making it
        # a bit "shaky" when nearing the border and allows it to
        # go outside of the shape's area for some reason.
        # self.calculateOffsets(self.selectedShapes, pos)
        dp = pos - self.prev_point
        if dp:
            for shape in shapes:
                shape.move_by(dp)
            self.prev_point = pos
            return True
        return False

    def deselect_shape(self):
        if self.selected_shapes:
            self.set_hiding(False)
            self.selection_changed.emit([])
            self.h_shape_is_selected = False
            self.update()

    def delete_selected(self):
        deleted_shapes = []
        if self.selected_shapes:
            for shape in self.selected_shapes:
                self.shapes.remove(shape)
                deleted_shapes.append(shape)
            self.store_shapes()
            self.selected_shapes = []
            self.update()
        return deleted_shapes

    def delete_shape(self, shape):
        if shape in self.selected_shapes:
            self.selected_shapes.remove(shape)
        if shape in self.shapes:
            self.shapes.remove(shape)
        self.store_shapes()
        self.update()

    def duplicate_selected_shapes(self):
        if self.selected_shapes:
            self.selected_shapes_copy = [s.copy() for s in self.selected_shapes]
            self.bounded_shift_shapes(self.selected_shapes_copy)
            self.end_move(copy=True)
        return self.selected_shapes

    def bounded_shift_shapes(self, shapes):
        # Try to move in one direction, and if it fails in another.
        # Give up if both fail.
        point = shapes[0][0]
        offset = QtCore.QPoint(2.0, 2.0)
        self.offsets = QtCore.QPoint(), QtCore.QPoint()
        self.prev_point = point
        if not self.bounded_move_shapes(shapes, point - offset):
            self.bounded_move_shapes(shapes, point + offset)

    # QT Overload
    def paintEvent(self, event):
        if not self.pixmap or self.pixmap.width() == 0 or self.pixmap.height() == 0:
            return super(Canvas, self).paintEvent(event)

        p = self._painter
        p.begin(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offset_to_center())

        p.drawPixmap(0, 0, self.pixmap)
        Shape.scale = self.scale
        for shape in self.shapes:
            if (shape.selected or not self._hide_backround) and self.is_visible(
                shape
            ):
                shape.fill = shape.selected or shape == self.h_hape
                shape.paint(p)
        if self.current:
            self.current.paint(p)
            self.line.paint(p)
        if self.selected_shapes_copy:
            for s in self.selected_shapes_copy:
                s.paint(p)

        if (
            self.fill_drawing()
            and self.create_mode == "polygon"
            and self.current is not None
            and len(self.current.points) >= 2
        ):
            drawing_shape = self.current.copy()
            drawing_shape.add_point(self.line[1])
            drawing_shape.fill = True
            drawing_shape.paint(p)

        # Draw mouse coordinates
        if self.show_cross_line:
            pen = QtGui.QPen(QtGui.QColor("#000000"), 2, Qt.SolidLine)
            p.setPen(pen)
            p.setOpacity(1.0)
            p.drawLine(QtCore.QPoint(self.prev_move_point.x() - 1, 0),
                       QtCore.QPoint(self.prev_move_point.x() - 1, self.pixmap.height()))
            p.drawLine(QtCore.QPoint(0, self.prev_move_point.y() - 1),
                       QtCore.QPoint(self.pixmap.width(), self.prev_move_point.y() - 1))
            pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 2, Qt.SolidLine)
            p.setPen(pen)
            p.setOpacity(1.0)
            p.drawLine(QtCore.QPoint(self.prev_move_point.x() + 1, 0),
                       QtCore.QPoint(self.prev_move_point.x() + 1, self.pixmap.height()))
            p.drawLine(QtCore.QPoint(0, self.prev_move_point.y() + 1),
                       QtCore.QPoint(self.pixmap.width(), self.prev_move_point.y() + 1))

        p.end()

    def transform_pos(self, point):
        """Convert from widget-logical coordinates to painter-logical ones."""
        return point / self.scale - self.offset_to_center()

    def offset_to_center(self):
        s = self.scale
        area = super(Canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QtCore.QPoint(x, y)

    def out_off_pixmap(self, p):
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w - 1 and 0 <= p.y() <= h - 1)

    def finalise(self):
        assert self.current
        self.current.close()
        self.shapes.append(self.current)
        self.store_shapes()
        self.current = None
        self.set_hiding(False)
        self.new_shape.emit()
        self.update()

    def close_enough(self, p1, p2):
        # d = distance(p1 - p2)
        # m = (p1-p2).manhattanLength()
        # print "d %.2f, m %d, %.2f" % (d, m, d - m)
        # divide by scale to allow more precision when zoomed in
        return utils.distance(p1 - p2) < (self.epsilon / self.scale)

    def intersection_point(self, p1, p2):
        # Cycle through each image edge in clockwise fashion,
        # and find the one intersecting the current line segment.
        # http://paulbourke.net/geometry/lineline2d/
        size = self.pixmap.size()
        points = [
            (0, 0),
            (size.width() - 1, 0),
            (size.width() - 1, size.height() - 1),
            (0, size.height() - 1),
        ]
        # x1, y1 should be in the pixmap, x2, y2 should be out of the pixmap
        x1 = min(max(p1.x(), 0), size.width() - 1)
        y1 = min(max(p1.y(), 0), size.height() - 1)
        x2, y2 = p2.x(), p2.y()
        d, i, (x, y) = min(self.intersecting_edges((x1, y1), (x2, y2), points))
        x3, y3 = points[i]
        x4, y4 = points[(i + 1) % 4]
        if (x, y) == (x1, y1):
            # Handle cases where previous point is on one of the edges.
            if x3 == x4:
                return QtCore.QPoint(x3, min(max(0, y2), max(y3, y4)))
            else:  # y3 == y4
                return QtCore.QPoint(min(max(0, x2), max(x3, x4)), y3)
        return QtCore.QPoint(x, y)

    def intersecting_edges(self, point1, point2, points):
        """Find intersecting edges.

        For each edge formed by `points', yield the intersection
        with the line segment `(x1,y1) - (x2,y2)`, if it exists.
        Also return the distance of `(x2,y2)' to the middle of the
        edge along with its index, so that the one closest can be chosen.
        """
        (x1, y1) = point1
        (x2, y2) = point2
        for i in range(4):
            x3, y3 = points[i]
            x4, y4 = points[(i + 1) % 4]
            denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            nua = (x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)
            nub = (x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)
            if denom == 0:
                # This covers two cases:
                #   nua == nub == 0: Coincident
                #   otherwise: Parallel
                continue
            ua, ub = nua / denom, nub / denom
            if 0 <= ua <= 1 and 0 <= ub <= 1:
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                m = QtCore.QPoint((x3 + x4) / 2, (y3 + y4) / 2)
                d = utils.distance(m - QtCore.QPoint(x2, y2))
                yield d, i, (x, y)

    # These two, along with a call to adjustSize are required for the
    # scroll area.
    # QT Overload
    def sizeHint(self):
        return self.minimumSizeHint()

    # QT Overload
    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(Canvas, self).minimumSizeHint()

    # QT Overload
    def wheelEvent(self, ev: QWheelEvent):
        mods = ev.modifiers()
        delta = ev.angleDelta()
        if QtCore.Qt.ControlModifier == int(mods):
            # with Ctrl/Command key
            # zoom
            self.zoom_request.emit(delta.y(), ev.pos())
        else:
            # scroll
            self.scroll_request.emit(delta.x(), QtCore.Qt.Horizontal)
            self.scroll_request.emit(delta.y(), QtCore.Qt.Vertical)
        ev.accept()

    def move_by_keyboard(self, offset):
        if self.selected_shapes:
            self.bounded_move_shapes(
                self.selected_shapes, self.prev_point + offset
            )
            self.repaint()
            self.moving_shape = True

    # QT Overload
    def keyPressEvent(self, ev):
        modifiers = ev.modifiers()
        key = ev.key()
        if self.drawing():
            if key == QtCore.Qt.Key_Escape and self.current:
                self.current = None
                self.drawing_polygon.emit(False)
                self.update()
            elif key == QtCore.Qt.Key_Return and self.can_close_shape():
                self.finalise()
            elif modifiers == QtCore.Qt.AltModifier:
                self.snapping = False
        elif self.editing():
            if key == QtCore.Qt.Key_Up:
                self.move_by_keyboard(QtCore.QPoint(0.0, -MOVE_SPEED))
            elif key == QtCore.Qt.Key_Down:
                self.move_by_keyboard(QtCore.QPoint(0.0, MOVE_SPEED))
            elif key == QtCore.Qt.Key_Left:
                self.move_by_keyboard(QtCore.QPoint(-MOVE_SPEED, 0.0))
            elif key == QtCore.Qt.Key_Right:
                self.move_by_keyboard(QtCore.QPoint(MOVE_SPEED, 0.0))

    # QT Overload
    def keyReleaseEvent(self, ev):
        modifiers = ev.modifiers()
        if self.drawing():
            if int(modifiers) == 0:
                self.snapping = True
        elif self.editing():
            if self.moving_shape and self.selected_shapes:
                index = self.shapes.index(self.selected_shapes[0])
                if (
                    self.shapes_backups[-1][index].points
                    != self.shapes[index].points
                ):
                    self.store_shapes()
                    self.shape_moved.emit()

                self.moving_shape = False

    def set_last_label(self, text, flags):
        assert text
        self.shapes[-1].label = text
        self.shapes[-1].flags = flags
        self.shapes_backups.pop()
        self.store_shapes()
        return self.shapes[-1]

    def undo_last_line(self):
        assert self.shapes
        self.current = self.shapes.pop()
        self.current.set_open()
        if self.create_mode in ["polygon", "linestrip"]:
            self.line.points = [self.current[-1], self.current[0]]
        elif self.create_mode in ["rectangle", "line", "circle"]:
            self.current.points = self.current.points[0:1]
        elif self.create_mode == "point":
            self.current = None
        self.drawing_polygon.emit(True)

    def undo_last_point(self):
        if not self.current or self.current.is_closed():
            return
        self.current.pop_point()
        if len(self.current) > 0:
            self.line[0] = self.current[-1]
        else:
            self.current = None
            self.drawing_polygon.emit(False)
        self.update()

    def load_pixmap(self, pixmap, clear_shapes=True):
        self.pixmap = pixmap
        if clear_shapes:
            self.shapes = []
        self.update()

    def load_shapes(self, shapes, replace=True):
        if replace:
            self.shapes = list(shapes)
        else:
            self.shapes.extend(shapes)
        self.store_shapes()
        self.current = None
        self.h_hape = None
        self.h_vertex = None
        self.h_edge = None
        self.update()

    def set_shape_visible(self, shape, value):
        self.visible[shape] = value
        self.update()

    def override_cursor(self, cursor):
        self.restore_cursor()
        self._cursor = cursor
        QtWidgets.QApplication.setOverrideCursor(cursor)

    def restore_cursor(self):
        QtWidgets.QApplication.restoreOverrideCursor()

    def reset_state(self):
        self.restore_cursor()
        self.pixmap = None
        self.shapes_backups = []
        self.update()

    def set_show_cross_line(self, enabled):
        self.show_cross_line = enabled
