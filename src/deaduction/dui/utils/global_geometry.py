
from PySide2.QtCore import QRect
from PySide2.QtWidgets import QWidget


def global_geometry(wdg: QWidget, geometry: QRect) -> QRect:
    """
    Return the QRect in global coordinates that corresponds to geometry in
    wdg coordinates.
    """

    top_left = geometry.topLeft()
    bottom_right = geometry.bottomRight()
    top_left_glob = wdg.mapToGlobal(top_left)
    bottom_right_glob = wdg.mapToGlobal(bottom_right)

    global_geo = QRect(top_left_glob, bottom_right_glob)

    return global_geo
