import sys
import matplotlib as mpl
from matplotlib import figure

from matplotlib.backends.backend_agg import FigureCanvasAgg
from PySide2 import QtGui, QtCore, QtWidgets

from PySide2.QtWidgets import ( QWidget,
                                QLineEdit,
                                QVBoxLayout,
                                QLabel )

def mathTex_to_QPixmap(mathTex, fs):

    #---- set up a mpl figure instance ----
    fig = figure.Figure()
    fig.patch.set_facecolor('none')
    fig.set_canvas(FigureCanvasAgg(fig))
    renderer = fig.canvas.get_renderer()

    #---- plot the mathTex expression ----
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_facecolor('none')
    t = ax.text(0, 0, f"${mathTex}$", ha='left', va='bottom', fontsize=fs)

    #---- fit figure size to text artist ----
    fwidth, fheight = fig.get_size_inches()
    fig_bbox = fig.get_window_extent(renderer)

    text_bbox = t.get_window_extent(renderer)

    tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
    tight_fheight = text_bbox.height * fheight / fig_bbox.height

    fig.set_size_inches(tight_fwidth, tight_fheight)

    #---- convert mpl figure to QPixmap ----
    buf, size = fig.canvas.print_to_buffer()
    qimage = QtGui.QImage.rgbSwapped(QtGui.QImage(buf, size[0], size[1], QtGui.QImage.Format_ARGB32))
    qpixmap = QtGui.QPixmap(qimage)

    return qpixmap

class Test_Window(QWidget):
    def __init__(self):
        super().__init__()

        self.w_entry  = QLineEdit("\int_a^b f(x)dx")
        self.w_label  = QLabel()
        self.w_layout = QVBoxLayout()

        self.w_layout.addWidget(self.w_entry)
        self.w_layout.addWidget(self.w_label)

        self.setLayout(self.w_layout)

        self.w_entry.textChanged.connect(self._update_label)

    def _update_label(self):
        math = self.w_entry.text()
        qpp  = mathTex_to_QPixmap(math, 15)

        self.w_label.setPixmap(qpp)

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    ww  = Test_Window()
    ww.show()

    #label.setPixmap(pixmap)    
    #label.show()

    app.exec_()
