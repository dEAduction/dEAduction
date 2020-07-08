"""
A dummy dEAduction main window interface. 
"""

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, \
                                QHBoxLayout, QVBoxLayout, QGridLayout, \
                                QLineEdit, QListWidget, QWidget, QGroupBox, \
                                QLabel
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
import sys

GOAL = "∀ x ∈ X, x ∈ (f⁻¹⟮B ∪ B'⟯) <=> x ∈ f⁻¹⟮B⟯ ∪ (f⁻¹⟮B'⟯)"

class Goal(QPushButton):

    def __init__(self, goal):
        super().__init__()
        self.setText(goal)
        self._initUI()

    def _initUI(self):
        self.setFont(QFont('Fira Code', 24))
        self._resize_width()
        self.setFlat(True)

    def _resize_width(self):
        txt_width = self.fontMetrics().boundingRect(self.text()).width()
        self.setFixedWidth(txt_width + 40)


class ToolsList(QListWidget):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setAlternatingRowColors(True)


class ExerciseWindow(QWidget):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):

        def _init_logic_buttons():
            buttons_grid = QGridLayout()

            NO =                QPushButton('NO')
            AND =               QPushButton('AND')
            OR =                QPushButton('OR')
            Implies =           QPushButton('→')
            Equivalence =       QPushButton('↔')
            Forall =            QPushButton('∀')
            Exists =            QPushButton('∃')
            P_contraposition =  QPushButton('Proof by contraposition')
            P_absurd =          QPushButton('Proof by absurd')
            P_induction =       QPushButton('Proof by induction')

            buttons_positions = {
                    NO: (1, 1),
                    AND: (1, 2),
                    OR: (1, 3),
                    Implies: (1, 4),
                    Equivalence: (1, 5),
                    Forall: (1, 6),
                    Exists: (1, 7),
                    P_contraposition: (2, 1),
                    P_absurd: (2, 2),
                    P_induction: (2, 3)}

            for button, position in buttons_positions.items():
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
        goal_layout = QHBoxLayout()
        logic_buttons = _init_logic_buttons()   # already contains buttons
        main_layout = QVBoxLayout()
        workspace_layout = QHBoxLayout()
        propobj_layout = QVBoxLayout()
        tools_layout = QVBoxLayout()

        # Create QGroupBox to have titles
        propobj_gb = QGroupBox('Properties and objects')
        tools_gb = QGroupBox('Tools (affect goal, prop. and obj.)')

        # Put widgets in layouts and group boxes
        goal_layout.addStretch()
        goal_layout.addWidget(goal)
        goal_layout.addStretch()
        # Add space below goal
        goal_layout.setContentsMargins(0, 10, 0, 30) #LTRB
        propobj_layout.addWidget(objects)
        propobj_layout.addWidget(properties)
        tools_layout.addLayout(logic_buttons)
        tools_layout.addWidget(statements)
        propobj_gb.setLayout(propobj_layout)
        tools_gb.setLayout(tools_layout)
        workspace_layout.addWidget(propobj_gb)
        workspace_layout.addWidget(tools_gb)

        # Don't forget me
        main_layout.addLayout(goal_layout)
        main_layout.addLayout(workspace_layout)
        self.setWindowTitle("L'union des images réciproque est l'image "\
                "réciproque de l'union — d∃∀duction")
        self.setLayout(main_layout)
        self.resize(1200, 800)
        self.show()


def main():
    app = QApplication()

    main_window = ExerciseWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
