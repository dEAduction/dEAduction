from pathlib import Path
import sys
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QGridLayout, QLabel, QWidget


class ProofStatePOLayout(QGridLayout):

    # Visually it looks like this:
    # -----------------------------------------------------------------
    # | tag icon | Some math. object or prop.        | (Some comment) |
    # -----------------------------------------------------------------
    # Indexes:
    #    (0, 0)                 (0, 1)                    (0, 2)

    def __init__(self, tag: str, proofstatepo, comment=None):
        super().__init__()
        self.tag = tag
        self.proofstatepo = proofstatepo
        self.comment = comment

    # Set the tag icon. The right icon is properly set when the tag
    # (str) is changed.
    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag: str):
        if tag not in ['modified', 'new', None]:
            raise ValueError("ProofStatePOLayout.tag must be one of "
                             f"'modified', 'new' or None. Tag: {tag}.")

        self._tag = tag

        if tag == None:
            self.addWidget(QLabel(''))
            return None
        elif tag == 'new':
            icon_path = Path('icon_new.png')
        elif tag == 'modified':
            icon_path = Path('icon_modified.png')

        icon_widget = QLabel()
        icon_path = str(icon_path.resolve())
        icon_pixmap = QPixmap(icon_path)
        icon_pixmap = icon_pixmap.scaledToWidth(10)
        icon_widget.setPixmap(icon_pixmap)
        self.addWidget(icon_widget, 0, 0)

    # Set the central caption
    @property
    def proofstatepo(self):
        return self._proofstatepo

    @proofstatepo.setter
    def proofstatepo(self, proofstatepo):
        self._proofstatepo = proofstatepo

        caption = QLabel(proofstatepo.caption)
        self.addWidget(caption, 0, 1)

    # Set comment
    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, comment):
        self._comment = comment

        comment_widget = QLabel('') if not comment else QLabel(comment)
        self.addWidget(comment_widget, 0, 2)


class _ProofStatePOTEST:
    def __init__(self, caption):
        self.caption = caption


def main():
    app = QApplication([])

    tag1 = 'new'
    pspo1 = _ProofStatePOTEST('x: X')
    comment1 = None
    pspolyt1 = ProofStatePOLayout(tag1, pspo1, comment1)

    tag2 = 'modified'
    pspo2 = _ProofStatePOTEST('f: X -> Y')
    comment2 = 'dépend de f'
    pspolyt2 = ProofStatePOLayout(tag2, pspo2, comment2)

    tag3 = None
    pspo3 = _ProofStatePOTEST('B(x, eps): X')
    comment3 = 'dépend de x, dépend de eps'
    pspolyt3 = ProofStatePOLayout(tag3, pspo3, comment3)
    pspolyt3.tag == 'new'

    grid = QGridLayout()
    grid.addLayout(pspolyt1, 0, 0)
    grid.addLayout(pspolyt2, 1, 0)
    grid.addLayout(pspolyt3, 2, 0)

    wdw = QWidget()
    wdw.setLayout(grid)
    wdw.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
