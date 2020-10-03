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

    def __init__(self, gb_title: str, left_layout: QLayout,
                 right_layout: QLayout=None):

        super().__init__(gb_title)
        self.set_left_layout()
        self.set_right_layout()

        main_layout = QHBoxLayout()
        main_layout.addLayout(self.left_layout)
        main_layout.addLayout(self.right_layout)
        self.setLayout(main_layout)

    def set_left_layout(self, layout: QLayout):
        
        delete_replace_widget(self.left_layout, layout)
        self.left_layout = layout

    def set_right_layout(self, metadata: Dict[str, Any]=None,
                         layout: QLayout=None):

        right_layout = QVBoxLayout()

        if not metadata and not layout:
            right_layout.addStretch()
            right_layout.addWidget(_('Nothing to preview.'))
            right_layout.addStretch()
        else:
            if metadata:

                if metadata['title']
                    title_wgt = QLabel(metadata["title"])
                    title_wgt.setStyleSheet('font-size: 16pt;' \
                                            'font-weight: bold;')

                    right_layout.addWidget(title_wgt)

                if metadata['subtitle']:
                    subtitle_wgt = QLabel(subtitle)
                    subtitle_wgt.setStyleSheet('font-style: italic;' \
                                               'color: gray;')
                    subtitle_lyt = QHBoxLayout()
                    subtitle_lyt.addWidget(title_wgt)
                    subtitle_lyt.addWidget(subtitle_wgt)

                    right_layout.addLayout(sub_title_lyt)

                if metadata['details']:
                    details_wgt = DisclosureTree('Details',
                                                 metadata['details'])

                    right_layout.addWidget(details_wgt)

                if metadata['description']:
                    description_wgt = QLabel(metadata['description'])
                    description_wgt.setWordWrap(true)

                    right_layout.addWidget(description_wgt)

            if layout:
                right_layout.addLayout(layout)

        replace_delete_widget(self.right_layout, layout)
        self.right_layout = right_layout
