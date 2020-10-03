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
            self.setLayout(main_layout)
        elif not left_layout and right_layout:
            left_layout = QVBoxLayout()
            left_layout.addStretch()
            left_layout.addWidget(_('Nothing to choose from.'))
            left_layout.addStretch()
        elif left_layout and not right_layout:
            right_layout = QVBoxLayout()
            right_layout.addStretch()
            right_layout.addWidget(_('Nothing to preview.'))
            right_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
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
