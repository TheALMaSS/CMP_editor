from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen
from node import Node


class CatchCropNode(Node):
    """Hands the field over to a catch crop, mid-plan.

    The _CC crops do not simply end: they start a second crop on the same field, which keeps
    growing after the parent's operations are finished. This node replaces the END node in those
    crops, so it takes no outgoing arrows.

    `catch_crop` is "conventional" or "organic" -- ALMaSS maps those to tov_DKCatchCrop and
    tov_DKOCatchCrop. The words are stored rather than the C++ enum names so that renaming an
    enum cannot invalidate saved crop files.
    """

    _counter = 0

    def __init__(self, catch_crop="conventional"):
        super().__init__("Hand off to\ncatch crop")

        self.catch_crop = catch_crop

        self.vertical_offset_name = 0
        self.vertical_offset_id = -30
        self.padding_vertical = 60
        self.padding_horizontal = 100

        # Like END, this node terminates the graph, so it carries no date range.
        # The id must be unique -- it is how ALMaSS resolves nodes, and duplicates corrupt the
        # crop file -- so number it rather than hardcoding one string for every such node.
        CatchCropNode._counter += 1
        self.id_text.setPlainText(f"CatchCrop{CatchCropNode._counter}")
        self.adjust_size()

    def paint(self, painter, option, widget):
        # A distinct green, so it does not read as an ordinary grey operation.
        painter.setBrush(QColor("#CDE8CF"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, self.width, self.height), 10, 10)

        if self.isSelected():
            pen_color = QColor("#007BFF")
            pen_width = 3
        else:
            pen_color = QColor("#000000")
            pen_width = 1

        painter.setPen(QPen(pen_color, pen_width))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(0, 0, self.width, self.height), 10, 10)
