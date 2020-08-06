"""
#########################################################
# context_widgets_classes.py : exercise context widgets #
#########################################################

    Provide widgets classes for an exercise's context, that is its
    target, objects (e.g. f:X->Y a function) and properties (e.g. f is
    continuous). Those widgets will be instanciated in
    ExerciseCentralWidget, which is itself instanciated as an attribute
    of ExerciseMainWindow. Provided classes:
        - ProofStatePOWidget;
        - ProofStatePOWidgetItem;
        - TargetWidget.

Author(s)      : Kryzar <antoine@hugounet.com>
Maintainers(s) : Kryzar <antoine@hugounet.com>
Date           : July 2020

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

from pathlib import Path
from typing  import Tuple

from PySide2.QtGui     import ( QBrush,
                                QColor,
                                QIcon)
from PySide2.QtWidgets import ( QHBoxLayout,
                                QLabel,
                                QWidget,
                                QListWidget,
                                QListWidgetItem)

from deaduction.pylib.mathobj import ProofStatePO

################################
# ProofStatePO widgets classes #
################################

# A usefull class.


class _TagIcon(QIcon):
    """
    A class which creates a QIcon (self) depending on the tag (one of
    '+', '=', '≠') given as an argument of self.__init__. It
    automatically associates the right icon to the right tag and raises
    an exception if the tag given as an argument of self.__init__ is
    invalid.
    """

    def __init__(self, tag: str):
        """
        Init self with a tag given as a str.

        :param tag: One of '+', '=', '≠'.
        """
        icons_folder = Path('share/graphical_resources/icons/')

        if tag not in ['=', '+', '≠']:
            # TODO: catch the exception below?
            raise ValueError('tag must be one of "=", "+", "≠". tag: {tag}.')
        elif tag == '=':
            super().__init__('')  # No icon, empty icon trick
            return None
        elif tag == '+':
            icon_path = icons_folder / 'tag_plus.png'
        elif tag == '≠':
            icon_path = icons_folder / 'tag_different.png'

        super().__init__(str(icon_path.resolve()))


# Classes for the two main widgets in 'Context' area of the exercise
# window. Class ProofStatePOWidget is a parent widget containing
# a list of ProofStatePOWidgetItem. Both 'Objects' and 'Properties'
# widgets use those same two classes.


class ProofStatePOWidgetItem(QListWidgetItem):
    """
    Objects (e.g. f:X->Y a function) and properties (e.g. f is
    continuous) are coded as instances of the class ProofStatePO.
    The class ProofStatePOWidgetItem is the widget in charge of
    containing an instance of the class ProofStatePO and displaying it.

    :attribute proofstatepo (ProofStatePo): The instance of the class
        ProofStatePO self is initiated with.
    :attribute tag (str): The current tag (e.g. '+', '=' or '≠', see
        _TagIcon) of self.proofstatepo.
    """

    def __init__(self, proofstatepo: ProofStatePO, tag: str):
        """
        One creates a ProofStatePOWidgetItem with a ProofStatePO and
        a tag (e.g. '+', '=' or '≠', see _TagIcon). The tag is not an
        attribute or method of the ProofStatePO, it varies at each
        new goal and is given by the function compare in
        mathobj/proof_state. However, we keep both proofstatepo and
        tag as class attributes.

        :param proofstatepo: The ProofStatePO one wants to display.
        :param tag: The tag of proofstatepo.
        :return: An instance of the class ProofStatePOWidgetItem.
        """

        super().__init__()

        self.proofstatepo = proofstatepo
        self.tag          = tag

        self.setIcon(_TagIcon(tag))
        caption =    f'{proofstatepo.format_as_utf8()} : ' \
                     f'{proofstatepo.math_type.format_as_utf8()}'
        self.setText(caption)

    def __eq__(self, other):
        """
        Define the operator == for the class ProofStatePOWidgetItem.
        Do not delete! It is usefull to check if a given instance of
        the class ProofStatePOWidgetItem is in a list of instances of
        this class (the 'for item in pspo_list:' test).

        :param other: An instance of the class ProofStatePOWidgetItem.
        :return: A boolean.
        """

        return self is other  # Brutal but that is what we need.

    def mark_user_selected(self, yes: bool=True):
        """
        Change self's background to green if yes or to normal color
        (e.g. white in light mode) if not yes. Note that this method
        does nothing else ; in particular, it does not add / remove
        self to / from ExerciseMainWindow.current_selection.

        :param yes: See paragraph above.
        """

        self.setBackground(QBrush(QColor('limegreen')) if yes else QBrush())


class ProofStatePOWidget(QListWidget):
    """
    A container class to display an ordered list of ProofStatePO. 

    :attribute items ([ProofStatePOWidgetItem]): The list of instances
        of the class ProofStatePOWidgetItem created in self.__init__.
        This attribute makes accessing them painless.
    """

    def __init__(self, tagged_proofstatepos: [Tuple[ProofStatePO, str]]=[]):
        """
        Given a list of tagged ProofStatePO (hence the tuple), create
        an orderred list of instances of the class
        ProofStatePOWidgetItem and display it.

        :param tagged_proofstatepos: A list of instances of the class
            ProofStatePO with their current tags (e.g. '+', '=' or
            '≠', see _TagIcon).
        :return: An instance of the class ProofStatePOWidget.
        """

        super().__init__()

        self.items = []

        for proofstatepo, tag in tagged_proofstatepos:
            item = ProofStatePOWidgetItem(proofstatepo, tag)
            self.addItem(item)
            self.items.append(item)


##########################
# Target widgets classes #
##########################

# Classes to display the target in the main exercise window.


class _TargetLabel(QLabel):
    """
    This class should not be used outside of this module. It is just
    a QWidget displaying both the tag and the target. The role of
    TargetWidget will just be to arrange this _TargetLabel in layouts.
    """

    def __init__(self, target: ProofStatePO=None, tag: str=None):
        """
        Init self with a target on the right and a tag (e.g. '+', '='
        or '≠', see _TagIcon) on the left. If those are None, display
        an empty tag and '…' in place of the target.

        :param target: The target to be displayed.
        :param tag: The tag associated to target.
        """
        super().__init__()

        # Display
        #   ∀ x ∈ X, ∃ ε, …
        # and not
        #   H : ∀ x ∈ X, ∃ ε, …
        # where H might be the lean name of the target. That's what
        # the .math_type is for.
        self.setText(target.math_type.format_as_utf8() if target else '…')

        # TODO: add tag, using _TagIcon will work

        self.setStyleSheet('font-size: 32pt;')


class TargetWidget(QWidget):
    """
    A class to display a tagged target and store both the target
    and the tag ass attributes. To display a target in
    ExerciseCentralWidget, use this class and not _TargetLabel, for
    it also sets layouts and keeps the target and its current tag as
    attributes.

    :attribute target: The target one wants to display.
    :attribute tag: The tag associated to target.
    """

    def __init__(self, target: ProofStatePO=None, tag: str=None):
        """"
        Init self with a target on the right and a tag (e.g. '+', '='
        or '≠', see _TagIcon) on the left. If those are None, display
        an empty tag and '…' in place of the target. Not the same as
        _TargetLabel.

        :param target: The target to be displayed.
        :param tag: The tag associated to target.
        """

        super().__init__()

        self.target = target
        self.tag =    tag

        main_layout = QHBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(_TargetLabel(self.target, self.tag))
        main_layout.addStretch()
        self.setLayout(main_layout)
