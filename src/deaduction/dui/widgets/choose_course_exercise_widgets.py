"""
#######################################################################
# choose_course_exercise_widgets.py : course/exercise chooser widgets #
#######################################################################

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : October 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""


class AbstractCExChooser(QGroupBox):

    def __init__(self, gb_title: str, left_layout: QLayout=None,
                 right_layout: QLayout=None):

        super().__init__(gb_title)

        if not left_layout and not right_layout:
            main_layout = QVBoxLayout()
            main_layout.addStretch()
            main_layout.addWidget(_('Nothing to choose from.'))
            main_layout.addStretch()

            self.left_layout = QLayout()
            self.right_layout = QLayout()
            self.setLayout(main_layout)
        else:
            if left_layout:
                self.left_layout = left_layout
            else:
                left_layout = QVBoxLayout()
                left_layout.addStretch()
                left_layout.addWidget(_('Nothing to browse.'))
                left_layout.addStretch()

                self.left_layout = QLayout()

            if right_layout:
                self.right_layout = right_layout
            else:
                right_layout = QVBoxLayout()
                right_layout.addStretch()
                right_layout.addWidget(_('Nothing to preview.'))
                right_layout.addStretch()

                self.right_layout = QLayout()

        main_layout = QHBoxLayout()
        main_layout.addLayout(self.left_layout)
        main_layout.addLayout(self.right_layout)
        self.setLayout(main_layout)

    def set_left_layout(self, layout: QLayout):
        
        delete_replace_widget(self.left_layout, layout)
        self.left_layout = layout

    def set_right_layout(self, cls_metadata: Dict[str, Any]=None,
                         layout: QLayout=None):

        right_layout = QVBoxLayout()

        if cls_metadata:

            cls_metadata_lyt = QVBoxLayout()

            if cls_metadata_lyt_data['title']
                title_wgt = QLabel(cls_metadata_lyt_data["title"])
                title_wgt.setStyleSheet('font-size: 16pt;' \
                                        'font-weight: bold;')
                self.cls_metadata_lyt.addWidget(title_wgt)

            if cls_metadata_lyt_data['subtitle']:
                subtitle_wgt = QLabel(subtitle)
                subtitle_wgt.setStyleSheet('font-style: italic;' \
                                           'color: gray;')
                subtitle_lyt = QHBoxLayout()
                subtitle_lyt.addWidget(title_wgt)
                subtitle_lyt.addWidget(subtitle_wgt)

                cls_metadata_lyt.addLayout(sub_title_lyt)

            if cls_metadata_lyt_data['details']:
                details_wgt = DisclosureTree('Details',
                                             cls_metadata_lyt_data['details'])

                cls_metadata_lyt.addWidget(details_wgt)

            if cls_metadata_lyt_data['description']:
                description_wgt = QLabel(cls_metadata_lyt_data['description'])
                description_wgt.setWordWrap(true)

                cls_metadata_lyt.addWidget(description_wgt)

            right_layout.addLayout(cls_metadata_lyt)

        if right_layout:
            right_layout.addLayout(layout)

        replace_delete_widget(self.right_layout, layout)
        self.right_layout = layout
