"""
A dummy dEAduction main window interface. 
"""

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, \
                                QHBoxLayout, QVBoxLayout, QGridLayout, \
                                QLineEdit, QListWidget, QWidget
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
import sys

GOAL = "∀ x ∈ X, x ∈ (f⁻¹⟮B ∪ B'⟯) → x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)"

class Goal(QLineEdit):
    def __init__(self, goal):
        super().__init__()
        self.goal = goal
        self.setText(goal)
        self._initUI()

    def _initUI(self):
        self.setAlignment(Qt.AlignCenter)
        font = QFont('Fira Code', 20)
        self.setFont(font)

class ToolsList(QListWidget):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setAlternatingRowColors(True)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):

        def _init_logic_buttons():
            buttons_grid = QGridLayout()

            NO = QPushButton('NO')
            OR = QPushButton('OR')
            AND = QPushButton('AND')
            FORALL = QPushButton('∀')
            EXISTS = QPushButton('∃')
            IMPLIES = QPushButton('→')
            EQUIVALENCE = QPushButton('↔')

            buttons = [NO, OR, AND, FORALL, EXISTS, IMPLIES, EQUIVALENCE]
            positions = [(i, j) for i in range(4) for j in range(3)]

            for position, button in zip(positions, buttons):
                buttons_grid.addWidget(button, *position)

            return buttons_grid

        # Create widgets
        objects = ToolsList()
        objects.addItem('X : ensemble')
        objects.addItem('Y : ensemble')
        objects.addItem('f : X → Y')
        objects.addItem('x ∈ X')
        objects.addItem('A : partie de X')
        objects.addItem('B : partie de X')

        properties = ToolsList()
        properties.addItem('f est une fonction de remplissage')
        properties.addItem("transitivité de l'union")

        statements = ToolsList()
        statements.addItem("image")
        statements.addItem("image réciproque")
        statements.addItem("union")
        statements.addItem("hypothèse de Riemann généralisée")

        goal = Goal(GOAL)

        # Create layouts
        logic_buttons = _init_logic_buttons()   # already contains buttons
        main_VBox = QVBoxLayout()
        workspace_HBox = QHBoxLayout()
        propobj_VBox = QVBoxLayout()
        statements_buttons_VBox = QVBoxLayout()

        # Put widgets in layouts
        propobj_VBox.addWidget(objects)
        propobj_VBox.addWidget(properties)
        statements_buttons_VBox.addWidget(statements)
        statements_buttons_VBox.addLayout(logic_buttons)
        workspace_HBox.addLayout(propobj_VBox)
        workspace_HBox.addLayout(statements_buttons_VBox)
        main_VBox.addWidget(goal)
        main_VBox.addLayout(workspace_HBox)

        # Don't forget me
        self.setWindowTitle("L'union des images réciproque est l'image "\
                "réciproque de l'union — d∃∀duction")
        self.setLayout(main_VBox)
        self.resize(1200, 800)
        self.show()


def main():
    app = QApplication()
    main_window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
