import sys
from pathlib import Path
from typing import  Dict, List, Any

from PySide2.QtCore import    ( Qt,
                                Slot)
from PySide2.QtGui  import    ( QFontDatabase,
                                QFont,
                                QPixmap)
from PySide2.QtWidgets import ( QApplication,
                                QButtonGroup,
                                QCheckBox,
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
                                QTextEdit,
                                QTreeWidget,
                                QTreeWidgetItem,
                                QVBoxLayout,
                                QHBoxLayout)

from deaduction.dui.utils import ( replace_delete_widget,
                                   set_selectable)


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


class LauncherGroupBox(QGroupBox):

    def __init__(self, title: str, left_lyt: QLayout,
                 right_lyt: QLayout):

        super().__init__(title)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_lyt)
        main_layout.addLayout(right_lyt)

        self.setLayout(main_layout)


class PreviewerHeaderLayout(QVBoxLayout):

    def __init__(self, title: str, long_text: str, details: Dict[str, str]=None,
                 subtitle: str=None):

        super().__init__()

        # Title
        title_wgt = QLabel(title)
        title_wgt.setStyleSheet('font-size: 16pt;'\
                                'font-weight: bold;')

        # Subtitle
        if subtitle:
            subtitle_wgt = QLabel(subtitle)
            subtitle_wgt.setStyleSheet('font-style: italic; color: gray;')
            sub_title_lyt = QHBoxLayout()
            sub_title_lyt.addWidget(title_wgt)
            sub_title_lyt.addWidget(subtitle_wgt)
            self.addLayout(sub_title_lyt)
        else:
            self.addWidget(title_wgt)

        # Info disclosure triangle
        if details:
            details= DisclosureTree('Details', details)
            self.addWidget(details)

        # Long text
        long_text_wgt = QLabel(long_text)
        long_text_wgt.setWordWrap(True)
        self.addWidget(long_text_wgt)

        self.addStretch()


class GoalPreviewerLayout(QVBoxLayout):

    def __init__(self):

        super().__init__()

        # ─────────────────── Check boxes ────────────────── #

        self.code_mode_checkbox   = QCheckBox('L∃∀N mode')
        checkbox_lyt = QHBoxLayout()
        checkbox_lyt.addStretch()
        checkbox_lyt.addWidget(self.code_mode_checkbox)

        self.code_mode_checkbox.clicked.connect(self.toggle_code_mode)

        # ───────────────── Friendly widget ──────────────── #

        self.friendly_wgt = QWidget()
        friendly_wgt_lyt = QVBoxLayout()
        friendly_wgt_lyt.setContentsMargins(0, 0, 0, 0)

        propobj_lyt = QHBoxLayout()
        objects, properties         = QListWidget(), QListWidget()
        objects_lyt, properties_lyt = QVBoxLayout(), QVBoxLayout()
        objects_lyt.addWidget(QLabel('Objects:'))
        properties_lyt.addWidget(QLabel('Properties:'))
        objects.setFont(QFont('Fira Code'))
        properties.setFont(QFont('Fira Code'))
        objects.addItems(['X : a set', 'x : X'])
        properties.addItems(['X is compact'])
        objects_lyt.addWidget(objects)
        properties_lyt.addWidget(properties)
        propobj_lyt.addLayout(objects_lyt)
        propobj_lyt.addLayout(properties_lyt)

        target_wgt = QLineEdit('Shit fuck X is continuous over Riemann')
        target_wgt.setFont(QFont('Fira Code'))

        friendly_wgt_lyt.addLayout(propobj_lyt)
        friendly_wgt_lyt.addWidget(QLabel('Target:'))
        friendly_wgt_lyt.addWidget(target_wgt)

        self.friendly_wgt.setLayout(friendly_wgt_lyt)

        # ─────────────────── Code widget ────────────────── #

        self.code_wgt = QTextEdit()
        self.code_wgt.setReadOnly(True)
        self.code_wgt.setFont(QFont('Menlo'))
        self.code_wgt.setText('Lean code goes here')

        # ──────────────────── Organize ──────────────────── #
        self.code_mode_checkbox.setChecked(False)
        self.friendly_wgt.show()
        self.code_wgt.hide()

        self.addWidget(self.friendly_wgt)
        self.addWidget(self.code_wgt)
        self.addLayout(checkbox_lyt)

    @Slot()
    def toggle_code_mode(self):

        if self.code_mode_checkbox.isChecked():
            self.friendly_wgt.hide()
            self.code_wgt.show()
        else:
            self.friendly_wgt.show()
            self.code_wgt.hide()


#############
# Launchers #
#############


class CourseGroupBox(QGroupBox):

    def __init__(self):

        super().__init__('Choose course (browse and preview')

        # ────────────── Choose course layout ────────────── #

        browse_btn = QPushButton('Browse files')
        browse_btn.clicked.connect(self.__browse_for_course)
        previous_courses_wgt = QListWidget()

        course_chooser_layout = QVBoxLayout()
        course_chooser_layout.addWidget(browse_btn)
        course_chooser_layout.addWidget(previous_courses_wgt)

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

        course_previewer_header_layout = PreviewerHeaderLayout(title, long_text, info)

        # ─────────────────── Main layout ────────────────── #

        main_layout = QHBoxLayout()
        main_layout.addLayout(course_chooser_layout)
        main_layout.addLayout(course_previewer_header_layout)
        self.setLayout(main_layout)


    @Slot()
    def __browse_for_course(self):

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('*.lean')

        if dialog.exec_():
            course_file_path = Path(dialog.selectedFiles()[0])


class ExerciseGroupBox(QGroupBox):

    def __init__(self):

        super().__init__('Choose exercise (browse and preview')

        # ──────────────── Exercise chooser ──────────────── #

        exercise_chooser_lyt = QVBoxLayout()
        exercise_chooser_lyt.addWidget(QListWidget())

        # ───────────────── Exercise header ──────────────── #

        title = 'Exercice 1.3.4'
        long_text = "Montrer que le groupe fondamental du cercle est "\
                    "isomorphe (comme groupe) à (Z, +)."
        subtitle = 'Le groupe fondamental de la sphère est trivial'

        exercise_previewer_header_layout = PreviewerHeaderLayout(title,
                                    long_text, subtitle=subtitle)

        # ────────────────── Preview goal ────────────────── #

        goal_previewer_layout = GoalPreviewerLayout()

        # ─────────────────── Main layout ────────────────── #

        exercise_previewer_layout = QVBoxLayout()
        exercise_previewer_layout.addLayout(exercise_previewer_header_layout)
        exercise_previewer_layout.addWidget(QWidget())
        exercise_previewer_layout.addLayout(goal_previewer_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(exercise_chooser_lyt)
        main_layout.addLayout(exercise_previewer_layout)
        self.setLayout(main_layout)


########################
# New launcher classes #
########################

class AbstractChooser(QGroupBox):

    def __init__(self, gb_title: str, preview_header_data: Dict[str, Any],
                 left_layout: QLayout, right_layout: QLayout, cls=None):

        super().__init__()
        self.cls = cls
        self.set_preview_header(preview_header_data)

        # ────────────── Layouts organization ────────────── #

        real_right_lyt = QVBoxLayout()
        real_right_lyt.addLayout(self.preview_header_lyt)
        real_right_lyt.addLayout(right_layout)

        self.setTitle(gb_title)
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(real_right_layout)
        self.setLayout(main_layout)

    def set_preview_header(self, preview_header_data: Dict[str, Any]):

        preview_header = QVBoxLayout()

        if preview_header_data['title']
            title_wgt = QLabel(preview_header_data["title"])
            title_wgt.setStyleSheet('font-size: 16pt;' \
                                    'font-weight: bold;')
            self.preview_header.addWidget(title_wgt)

        if preview_header_data['subtitle']:
            subtitle_wgt = QLabel(subtitle)
            subtitle_wgt.setStyleSheet('font-style: italic;' \
                                       'color: gray;')
            subtitle_lyt = QHBoxLayout()
            subtitle_lyt.addWidget(title_wgt)
            subtitle_lyt.addWidget(subtitle_wgt)

            preview_header.addLayout(sub_title_lyt)

        if preview_header_data['details']:
            details_wgt = DisclosureTree('Details',
                                         preview_header_data['details'])

            preview_header.addWidget(details_wgt)

        if preview_header_data['description']:
            description_wgt = QLabel(preview_header_data['description'])
            description_wgt.setWordWrap(true)

            preview_header.addWidget(description_wgt)

        self.preview_header = preview_header

###############
# Main window #
###############


class LaunchersMainWindow(QWidget):

    def __init__(self):

        super().__init__()

        course_cb =   CourseGroupBox()
        exercise_cb = ExerciseGroupBox()
        selection_zone_lyt = QVBoxLayout()
        selection_zone_lyt.addWidget(course_cb)
        selection_zone_lyt.addWidget(exercise_cb)

        buttons_lyt = QHBoxLayout()
        help_btn = QPushButton('Help')
        quit_btn = QPushButton('Quit')
        self.choose_this_course_btn = QPushButton('Start exercise')
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
