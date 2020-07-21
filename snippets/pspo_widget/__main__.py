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

    def __init__(self, tag: str, proofstatepo, comment):
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
        if tag not in ['modified', 'new']:
            raise ValueError("ProofStatePOLayout.tag must be one of "
                             f"'modified' or 'new'. Tag: {tag}.")
        elif tag == 'new':
            icon_path = Path('icon_new.png')
        elif tag == 'modified':
            icon_path = Path('icon_modified.png')

        icon_widget = QLabel()
        icon_pixmap = QPixmap(str(icon_path.resolve()))
        icon_pixmap = icon_pixmap.scaledToWidth(10)
        icon_widget.setPixmap(icon_pixmap)
        self.addWidget(icon_widget, 0, 0)

    # Set the central caption
    @property
    def proofstatepo(self):
        return self._proofstatepo

    @proofstatepo.setter
    def proofstatepo(self, proofstatepo):
        caption = QLabel(proofstatepo.caption)
        self.addWidget(caption, 0, 1)

    # Set comment
    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, comment):
        comment_widget = QLabel('') if not comment else QLabel(comment)
        self.addWidget(comment_widget, 0, 2)


class _ProofStatePOTEST:
    def __init__(self, caption):
        self.caption = caption


def main():
    app = QApplication([])

    tag = 'new'
    pspo = _ProofStatePOTEST('x: X')
    comment = 'dépend de f'
    pspolyt = ProofStatePOLayout(tag, pspo, comment)

    wdw = QWidget()
    wdw.setLayout(pspolyt)
    wdw.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
