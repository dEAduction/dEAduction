import sys
from pathlib import Path
from typing import  Dict, List

from PySide2.QtCore import    ( Qt,
                                Slot)
from PySide2.QtGui  import      QPixmap
from PySide2.QtWidgets import ( QApplication,
                                QGridLayout,
                                QGroupBox,
                                QFileDialog,
                                QPushButton,
                                QTextEdit,
                                QLineEdit,
                                QListWidget,
                                QWidget,
                                QLabel,
                                QLayout,
                                QListWidgetItem,
                                QTreeWidget,
                                QTreeWidgetItem,
                                QVBoxLayout,
                                QHBoxLayout)

from deaduction.dui.utils import set_selectable


class DisclosureTree(QTreeWidget):
    # An implementation of a disclosure triangle.
    # https://stackoverflow.com/questions/63862724/
    # qtreeview-dynamic-height-according-to-content-disclosure-triangle

    def __init__(self, title: str, data: Dict[str, str]):

        super().__init__()

        # ─────────────────── Add content ────────────────── #

        self.setColumnCount(2)
        parent_item = QTreeWidgetItem(self, [f'{title} : '])
        parent_item.set_selectable(False)
        self.addTopLevelItem(parent_item)

        for key, val in data.items():
            item = QTreeWidgetItem(parent_item, [f'{key} : ', val])
            parent_item.addChild(item)

            # Cosmetics
            item.set_selectable(False)
            item.setTextAlignment(0, Qt.AlignRight)

        # ──────────────────── Cosmetics ─────────────────── #

        # Hide header
        self.header().hide()

        # No background
        self.setStyleSheet('background-color: transparent;')

        # Dynamically change height when widget is collapsed or expanded
        # You have to update the maximum height of the widget, based on
        # its contents. For each top item you need to get the height for
        # that row using rowHeight() and do the same recursively for
        # child items whenever the item is expanded. Also, you need to
        # overwrite the sizeHint and minimumSizeHint.
        self.expanded.connect(self.update_height)
        self.collapsed.connect(self.update_height)

    def update_height(self):
        self.setMaximumHeight(self.sizeHint().height())

    def get_height(self, parent=None):
        height = 0
        if not parent:
            parent = self.rootIndex()
        for row in range(self.model().rowCount(parent)):
            child = self.model().index(row, 0, parent)
            height += self.rowHeight(child)
            if self.isExpanded(child) and self.model().hasChildren(child):
                    height += self.get_height(child)
        return height

    def sizeHint(self):
        hint = super().sizeHint()
        hint.setHeight(self.get_height() + self.frameWidth() * 2)
        return hint

    def minimumSizeHint(self):
        return self.sizeHint()


##################
# Helper classes #
##################


class LauncherLayout(QHBoxLayout):

    def __init__(self, chooser_title:  str, chooser:  QWidget,
                       previewer_title: str, previewer: QWidget):

        super().__init__()

        chooser_gb        = QGroupBox(chooser_title)
        chooser_gb_layout = QVBoxLayout()
        chooser_gb_layout.addWidget(chooser)
        chooser_gb.setLayout(chooser_gb_layout)

        previewer_gb        = QGroupBox(previewer_title)
        previewer_gb_layout = QVBoxLayout()
        previewer_gb_layout.addWidget(previewer)
        previewer_gb.setLayout(previewer_gb_layout)
        
        self.setContentsMargins(0, 0, 0, 0)
        self.addWidget(chooser_gb)
        self.addWidget(previewer_gb)


class PreviewerHeader(QWidget):

    def __init__(self, title: str, long_text: str, details: Dict[str, str]=None,
                 subtitle: str=None):

        super().__init__()

        main_layout = QVBoxLayout()

        # Title
        title_wgt = QLabel(title)
        title_wgt.setStyleSheet('font-size: 18pt;'\
                                'font-weight: bold;')

        # Subtitle
        if subtitle:
            subtitle_wgt = QLabel(f'({subtitle})')
            sub_title_lyt = QHBoxLayout()
            sub_title_lyt.addWidget(title_wgt)
            sub_title_lyt.addWidget(subtitle_wgt)
            main_layout.addLayout(sub_title_lyt)
        else:
            main_layout.addWidget(title_wgt)

        # Info disclosure triangle
        if details:
            details= DisclosureTree('Details', details)
            main_layout.addWidget(details)

        # Long text
        long_text_wgt = QLabel(long_text)
        long_text_wgt.setWordWrap(True)
        main_layout.addWidget(long_text_wgt)

        main_layout.addStretch()
        self.setLayout(main_layout)


#############
# Launchers #
#############


class CourseLauncher(QWidget):

    def __init__(self):

        super().__init__()

        # ────────────── Choose course layout ────────────── #

        browse_btn = QPushButton('Browse files')
        browse_btn.clicked.connect(self.__browse_for_course)
        previous_courses_wgt = QListWidget()

        course_chooser = QWidget()
        choose_course_lyt = QVBoxLayout()
        choose_course_lyt.addWidget(browse_btn)
        choose_course_lyt.addWidget(previous_courses_wgt)
        course_chooser.setLayout(choose_course_lyt)

        # ────────────── Preview course layout ───────────── #

        title = 'Topologie algébrique'
        long_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit." \
                'Mauris tempus congue turpis mollis consequat. Nulla finibus tempor' \
                'pharetra. Duis accumsan nisl tincidunt lacus aliquet, vel sodales nunc' \
                'blandit. Phasellus ligula tortor, venenatis in quam in, pretium' \
                'faucibus dolor. Morbi quis orci in mauris scelerisque ultricies at ut' \
                'augue. In et libero quis arcu tincidunt vestibulum. Etiam at odio eget' \
                'felis interdum tincidunt. Aenean neque metus, semper vitae metus vitae,' \
                'euismod dictum lectus. Pellentesque vel turpis metus. Phasellus sed' \
                'eros vel quam viverra sagittis. Class aptent taciti sociosqu ad litora' \
                'torquent per conubia nostra, per inceptos himenaeos. Aliquam bibendum' \
                'ipsum arcu, eu condimentum massa ultricies et. Fusce facilisis felis' \
                'dictum nunc placerat, ut malesuada lectus maximus. Nam dignissim orci' \
                'ipsum, id luctus mauris iaculis condimentum. Aliquam arcu eros, tempor' \
                'vitae vulputate eget, viverra quis metus.'
        info = {'Name': 'Frédéric Le Roux',
                'Year': '2020-2021',
                'Level': 'M1',
                'Path': '~/Who/Wants/To/Live/Forever/topalg.lean'}

        course_previewer_header = PreviewerHeader(title, long_text, info)

        # ─────────────────── Main layout ────────────────── #

        main_layout = LauncherLayout(
                'Choose course (browse files or previous course)',
                course_chooser,
                'Preview course',
                course_previewer_header)
        self.setLayout(main_layout)


    @Slot()
    def __browse_for_course(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        if dialog.exec_():
            course_file_path = Path(dialog.selectedFiles()[0])


class ExerciseLauncher(QWidget):

    def __init__(self):

        super().__init__()

        # ───────────────── Choose exercise ──────────────── #

        exercise_chooser = QListWidget()

        # ───────────────── Exercise header ──────────────── #

        title = 'Exercice 1.3.4'
        long_text = "Montrer que le groupe fondamental du cercle est "\
                    "isomorphe (comme groupe) à (Z, +)."
        subtitle = 'Le groupe fondamental de la sphère est trivial'

        exercise_previewer_header = PreviewerHeader(title, long_text, subtitle=subtitle)

        # ────────────────── Preview goal ────────────────── #

        preview_goal_lyt = QVBoxLayout()

        preview_goal_lyt.addWidget(QLabel('Objects:'))
        goal_objects = QListWidget()
        goal_objects.addItems(['X : a set', 'x : X'])
        preview_goal_lyt.addWidget(goal_objects)

        preview_goal_lyt.addWidget(QLabel('Properties:'))
        goal_properties = QListWidget()
        goal_properties.addItems(['X is compact'])
        preview_goal_lyt.addWidget(goal_properties)
        
        preview_goal_lyt.addWidget(QLabel('Target:'))
        goal_target = QLineEdit('Shit fuck X is continuous over Riemann')
        preview_goal_lyt.addWidget(goal_target)

        # ─────────────────── Main layout ────────────────── #

        exercise_previewer = QWidget()
        exercise_previewer_layout = QVBoxLayout()
        exercise_previewer_layout.setSpacing(0)
        exercise_previewer_layout.addWidget(exercise_previewer_header)
        exercise_previewer_layout.addStretch()
        exercise_previewer_layout.addLayout(preview_goal_lyt)
        exercise_previewer.setLayout(exercise_previewer_layout)

        main_layout = LauncherLayout(
                'Choose exercise (from the list)',
                exercise_chooser,
                'Preview exercise',
                exercise_previewer)
        self.setLayout(main_layout)


###############
# Main window #
###############


class LaunchersMainWindow(QWidget):

    def __init__(self):

        super().__init__()

        course_cap =   CourseLauncher()
        exercise_cap = ExerciseLauncher()
        selection_zone_lyt = QVBoxLayout()
        selection_zone_lyt.setContentsMargins(0, 0, 0, 0)
        selection_zone_lyt.addWidget(course_cap)
        selection_zone_lyt.addWidget(exercise_cap)

        buttons_lyt = QHBoxLayout()
        help_btn = QPushButton('Help')
        quit_btn = QPushButton('Quit')
        self.choose_this_course_btn = QPushButton('Launch exercise')
        buttons_lyt.addWidget(help_btn)
        buttons_lyt.addWidget(quit_btn)
        buttons_lyt.addStretch()
        buttons_lyt.addWidget(self.choose_this_course_btn)

        # ─────────────────── Main layout ────────────────── #
        
        main_lyt = QVBoxLayout()
        main_lyt.addLayout(selection_zone_lyt)
        main_lyt.addLayout(buttons_lyt)
        self.setLayout(main_lyt)

        # ─────────────────────── UI ─────────────────────── #

        self.setWindowTitle('d∃∀duction — Choose course and exercise')


if __name__ == '__main__':
    app = QApplication()

    blanquistes_du_nil = LaunchersMainWindow()
    blanquistes_du_nil.show()

    sys.exit(app.exec_())
