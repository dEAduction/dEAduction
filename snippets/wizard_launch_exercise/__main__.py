import sys

from PySide2.QtGui     import   QPixmap
from PySide2.QtWidgets import ( QApplication,
                                QHBoxLayout,
                                QFileDialog,
                                QLabel,
                                QLineEdit,
                                QListWidget,
                                QListWidgetItem,
                                QPushButton,
                                QVBoxLayout,
                                QWizard,
                                QWizardPage)


class SelectCoursePage(QWizardPage):

    def __init__(self):
        super().__init__()
        self.selected_course = None

        # Selection
        selected_course_lyt = QHBoxLayout()
        self.selected_course_wgt = QLineEdit()
        selected_course_lyt.addWidget(QLabel('Selected course'))
        selected_course_lyt.addWidget(self.selected_course_wgt)

        browse_lyt = QHBoxLayout()
        browse_lyt.addWidget(QPushButton('Browse files'))
        browse_lyt.addStretch()

        selection_lyt = QVBoxLayout()
        selection_lyt.addLayout(selected_course_lyt)
        selection_lyt.addLayout(browse_lyt)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(selection_lyt)
        self.setLayout(main_layout)
        
        # Cosmetics
        self.setTitle('Select course')
        self.setSubTitle('Select a d∃∀aduction course, represented by a L∃∀N file.')


class SelectExercisePage(QWizardPage):
    pass


class PaintballWizzard(QWizard):
    
    def __init__(self):
        super().__init__()
        self.addPage(SelectCoursePage())
        self.addPage(SelectExercisePage())

        self.setWindowTitle('d∃∀duction — Select course and exercise')

if __name__ == '__main__':
    app = QApplication()

    paintballwizzard = PaintballWizzard()
    paintballwizzard.show()

    sys.exit(app.exec_())
