"""
A dummy dEAduction main window interface. 
"""

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, \
                                QHBoxLayout, QVBoxLayout, QGridLayout, \
                                QLineEdit, QListWidget, QWidget, QGroupBox, \
                                QLabel, QDesktopWidget
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeView                          
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QColor, QBrush, QIcon
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


class Statement(QTreeWidgetItem):

    def __init__(self, parent, titles):
        super().__init__(parent, titles)
        self._initUI()

    def _initUI(self):
        self.setExpanded(True)
        self.setForeground(1, QBrush(QColor('gray')))
        # Note: align the second column on the right is ugly, see
        # self.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)

    def setUnselectable(self):
        # Thanks Florian
        # There is no method for this so we use a QFlag
        flags = self.flags()
        new_flags = flags & ~Qt.ItemIsSelectable
        self.setFlags(new_flags)


class StatementNode(Statement):

    def __init__(self, parent, title):
        super().__init__(parent, [title])
        self._set_icon()
        self.setUnselectable()

    def _set_icon(self):
        icon = QIcon('icon.png')
        self.setIcon(0, icon)

class PropobjList(QListWidget):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setAlternatingRowColors(True)


class ExerciseWindow(QMainWindow):

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
                    ('p_absurd', QPushButton('Proof by contradicton')),
                    ('p_cases', QPushButton('Cases disjunction')),
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
        anneaux_ideaux = StatementNode(statements, 'Anneaux et idéaux')
        Statement(anneaux_ideaux, ['Définition anneau', 'Définition 1.1'])
        Statement(anneaux_ideaux, ['Définition idéal', 'Définition 1.7'])
        Statement(anneaux_ideaux, ["Existence d'un idéal maximal", 'Théorème'])
        noetherianite = StatementNode(statements, 'Noetherianité')
        Statement(noetherianite, ['Transfert de Noethérianité', ''])
        Statement(noetherianite, ['Principal implique noethérien', 'Proposition 2.3'])
        statements.resizeColumnToContents(0)


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
        self.setCentralWidget(main_layout)
        self.show()


def main():
    app = QApplication()
    tool_buttons = ['NO', 'AND', 'OR', 'implies', 'equivalence', 'forall', \
            'exists', 'p_contraposition', 'p_absurd', 'p_cases', 'p_induction']
    main_window = ExerciseWindow(tool_buttons)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
