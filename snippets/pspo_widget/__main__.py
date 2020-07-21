import sys
from PySide2.QtWidgets import QApplication, QGridLayout, QLabel


class ProofStatePOLayout(QGridLayout):

    # Visually it looks like this:
    # -----------------------------------------------------------------
    # | tag icon | Some math. object or prop.        | (Some comment) |
    # -----------------------------------------------------------------
    # Indexes:
    #    (0, 0)                 (0, 1)                    (0, 2)

    def __init__(self, tag: str, proofstatepo, comment):
        super().__init__(self)
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

        # TODO

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


def main():
    app = QApplication([])

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
