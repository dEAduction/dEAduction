"""
A dummy dEAduction main window interface. 
"""

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, \
                                QHBoxLayout, QVBoxLayout, QGridLayout, \
                                QLineEdit, QListWidget, QWidget, QGroupBox, \
                                QLabel
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeView                          
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


class PropobjList(QListWidget):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setAlternatingRowColors(True)


class ExerciseWindow(QWidget):

    def __init__(self, tool_buttons):
        super().__init__()
        self.tool_buttons = tool_buttons
        self._initUI()

    def _initUI(self):

        def _init_tool_buttons():

            # First logic buttons
            logic_buttons_layout = QHBoxLayout()

            logic_buttons = [('NO', QPushButton('NO')),
                                ('AND', QPushButton('AND')),
                                ('OR', QPushButton('OR')),
                                ('implies', QPushButton('→')),
                                ('equivalence', QPushButton('↔')),
                                ('forall', QPushButton('∀')),
                                ('exists', QPushButton('∃'))]

            for name, button in logic_buttons:
                if name in self.tool_buttons:
                    logic_buttons_layout.addWidget(button)

            # Then proof buttons
            proof_buttons_layout = QHBoxLayout()
            proof_buttons = [\
                    ('p_contraposition', QPushButton('Proof by contraposition')),
                    ('p_absurd', QPushButton('Proof by absurd')),
                    ('p_induction', QPushButton('Proof by induction'))]

            for name, button in proof_buttons:
                if name in self.tool_buttons:
                    proof_buttons_layout.addWidget(button)

            # Put it all together
            buttons_layout = QVBoxLayout()
            buttons_layout.addLayout(logic_buttons_layout)
            buttons_layout.addLayout(proof_buttons_layout)

            return buttons_layout

        # Create widgets
        objects = PropobjList()
        objects.addItem('X : ensemble')
        objects.addItem('Y : ensemble')
        objects.addItem('f : X → Y')
        objects.addItem('x ∈ X')
        objects.addItem('A : partie de X')
        objects.addItem('B : partie de X')

        properties = PropobjList()
        properties.addItem('f est une fonction de remplissage')
        properties.addItem("transitivité de l'union")

        statements = QTreeWidget()
        statements.setAlternatingRowColors(True)
        statements.setHeaderLabels(['Énoncé', 'Identifiant'])
        anneaux_ideaux = QTreeWidgetItem(statements, ['Anneaux et idéaux', ''])
        QTreeWidgetItem(anneaux_ideaux, ['Définition anneau', 'Définition 1.1'])
        QTreeWidgetItem(anneaux_ideaux, ['Définition idéal', 'Définition 1.7'])
        QTreeWidgetItem(anneaux_ideaux, ["Existence d'un idéal maximal", 'Théorème'])
        noetherianite = QTreeWidgetItem(statements, ['Noetherianité'])
        QTreeWidgetItem(noetherianite, ['Transfert de Noethérianité', 'Proposition 2.4'])
        QTreeWidgetItem(noetherianite, ['Principal implique noethérien', 'Proposition 2.3'])


        goal = Goal(GOAL)

        # Create layouts
        goal_layout = QHBoxLayout()
        logic_buttons = _init_tool_buttons()   # already contains buttons
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
    tool_buttons = ['NO', 'AND', 'OR', 'implies', 'equivalence', 'forall', \
            'exists', 'p_contraposition', 'p_absurd', 'p_induction']
    main_window = ExerciseWindow(tool_buttons)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
