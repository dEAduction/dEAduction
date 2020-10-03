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


class AbstractCourseExerciseChooser(QGroupBox):

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
