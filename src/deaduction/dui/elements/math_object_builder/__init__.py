"""
#############################################
# __init__.py :  #
#############################################

This module provides a gui to construct a math object.
The idea is to build it recursively by choosing elements in menu or by 
pushing buttons. In particular, the unknown elements, that remains to be 
built, are represented by a "metavar button", with a menu to access the 
possible elements.
For instance, to build the property
    A⊂B => C⊂D
usr first chooses "implies" in the menu from the main metavar button.
Then the display changes to
    ?0  =>  ?1
where ?0 and ?1 are new metavar buttons, whose menu is filtered to display 
only elements whose type fits (here, propositions). Then usr select 
"inclusion" in the first menu, the display becomes
    ?00 ⊂ ?01 => ?1
and the menu associated to ?00 only displays sets. And so on.

Metavar menus are constructed by incorporating context elements and elements 
from the building_patterns dictionaries.

Author(s)      : Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Maintainers(s) : Frédéric Le Roux <frederic.le-roux@imj-prg.fr>
Date           : December 2022

Copyright (c) 2022 the dEAduction team

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

import logging

from functools import partial
from typing import Optional, Union, Any
from copy import copy

from PySide2.QtCore import Signal, Slot, Qt, QObject

from PySide2.QtWidgets import (QToolButton, QPushButton, QLabel, QWidget,
                               QMenu, QAction, QMainWindow,
                               QToolBar, QHBoxLayout, QVBoxLayout, QLineEdit,
                               QGroupBox, QApplication)

if __name__ == '__main__':
    import deaduction.pylib.config.i18n

from deaduction.pylib.math_display.pattern_parser import tree_from_str
from deaduction.pylib.mathobj import MathObject
from deaduction.pylib.pattern_math_obj import PatternMathObject, MetaVar
from deaduction.pylib.math_display.new_display import latex_shape
from deaduction.dui.elements.proof_tree.proof_tree_primitives import RawLabelMathObject

from deaduction.pylib.math_display.display import abstract_string_to_string
from deaduction.pylib.math_display.display_math import shallow_latex_to_text
from deaduction.pylib.math_display.display_data import needs_paren

log = logging.getLogger(__name__)

global _

##########################
# Building pattern dicts #
##########################
# The building pattern dict contains the patterns that are used to filter 
#  metavars menus. It is a dict of dict, the first order keys will be used
#  as sub-menus. The second order keys will be used as menu items.
#  The values are couples (symbol (for display), pattern string).
building_str_patterns = dict()

# ∧, ∨, ¬, ⇒, ⇔, ∀, ∃, =, ↦
building_str_patterns['logic'] = {
    'and': ('∧', "PROP_AND: PROP()(?0: PROP, ?1: PROP)"),
    'or': ('∨', "PROP_OR: PROP()(?0: PROP, ?1: PROP)"),
    'not': ('¬', "PROP_NOT: PROP()(?0: PROP)"),
    'implies': ('⇒', "PROP_IMPLIES: PROP()(?0: PROP, ?1: PROP)"),
    'iff': ('⇔', "PROP_IFF: PROP()(?0: PROP, ?1: PROP)"),
    'for all': ('∀', "QUANT_∀: PROP()(?0, ?1: ?0, ?2: PROP)"),
    'exists': ('∃', "QUANT_∃: PROP()(?0, ?1: ?0, ?2: PROP)"),
    'equal': ('=', "PROP_EQUAL: PROP()(?0, ?1)"),
    'maps to': ('↦', "APP(?0: FUNCTION(?1, ?2), ?3: ?1)"),
}

building_str_patterns['set_theory'] = {
    'belongs': ('∈', "PROP_BELONGS: PROP()(?0, ?1: SET(?2))"),
    'included': ('⊂', "PROP_INCLUDED: PROP()(?0: SET(?2), ?1: SET(?2) )")
}

building_str_patterns['numbers'] = {
    'number': ('012', "*NUMBER"),
    'name': ('x', "******NAME")
}

building_patterns = dict()

# Debug
# mvarbuttons = []


def string_to_pattern():
    """
    Create a copy of building_str_pattern dict but where the string patterns
    are converted into patterns.
    """
    for title, dic in building_str_patterns.items():
        building_patterns[title] = dict()
        for pretty_name, (symbol, str_pattern) in dic.items():
            tree = tree_from_str(str_pattern)
            metavars = []
            pattern = PatternMathObject.from_tree(tree, metavars)
            building_patterns[title].update({pretty_name: (symbol,
                                                           str_pattern,
                                                           pattern)})


string_to_pattern()


def process_string(string: str):
    abstract_string = shallow_latex_to_text(string, text_depth=0)
    display = abstract_string_to_string(abstract_string, format_='html',
                                        use_color=True, no_text=True)
    return display
    

def widget_for_item(item, math_object: MathObject) \
        -> (Any, bool):
    """
    Return either a QLabel, or a PatternTree, or a list of such.
    """
    pt_or_wdg = None
    parentheses = False

    if isinstance(item, str):
        item = process_string(item)
        pt_or_wdg = QLabel(item)
        pt_or_wdg.setTextFormat(Qt.RichText)
        # self.layout().addWidget(widget)
    elif isinstance(item, MathObject):
        pt_or_wdg = PatternTree(item)

    elif isinstance(item, tuple) or isinstance(item, int):
        child = math_object.descendant(item)
        pt_or_wdg = PatternTree(child)
        if needs_paren(math_object, child, item):
            parentheses = True
    elif callable(item):
        new_item = item(math_object)
        pt_or_wdg = widget_for_item(new_item, math_object)

    elif isinstance(item, list):
        shape_wdg = ShapeWdg(math_object, shape=item)
        pt_or_wdg = shape_wdg.list_
        # pt_or_wdg = [widget_for_item(sub_item, math_object) for sub_item in
        #              item]

    return pt_or_wdg, parentheses


class ShapeWdg:
    """
    A class for computing and  storing a list of strings and PatternTrees
    corresponding to the shape of a PatternMathObject.
    """

    def __init__(self, pattern_math_object: PatternMathObject, shape=None):
        self._shape = shape
        self.pattern_math_object = pattern_math_object
        self.list = [Union[QLabel, PatternTree]]
        self.wdg = QWidget()

        self.compute_list()
        self.compute_wdg()
        print("Wdg computed")

    def extend(self, item):
        if isinstance(item, list):
            self.list.extend(item)
        else:
            self.list.append(item)

    def shape(self):
        return self._shape if self._shape else latex_shape(
                                                    self.pattern_math_object)

    def compute_list(self):
        self.list = []

        force_parentheses = False
        for item in self.shape():
            if item == r'\parentheses':
                force_parentheses = True
            else:
                pt_or_wdg, parentheses = widget_for_item(item,
                                                         self.pattern_math_object)
                if pt_or_wdg:
                    if parentheses or force_parentheses:
                        self.extend(QLabel("("))
                    self.extend(pt_or_wdg)
                    if parentheses or force_parentheses:
                        self.extend(QLabel(")"))
                force_parentheses = False

    def pattern_tree_sublist(self):
        return [item for item in self.list if isinstance(item, PatternTree)]

    def pattern_sub_widgets(self):
        return [item.wdg for item in self.pattern_tree_sublist()]

    def compute_wdg(self):
        wdg = self.wdg
        lyt = QHBoxLayout()
        for item in self.list:
            sub_wdg = item.wdg if isinstance(item, PatternTree) else item
            # FIXME:
            lyt.addWidget(sub_wdg)
            # sub_wdg.show()

        wdg.setLayout(lyt)

    def update(self):
        # new_list =[]
        changed = False
        sub_widgets = self.pattern_sub_widgets()
        for item in self.list:
            if isinstance(item, PatternTree):
                item.update()
                # if item.update():
                #     self.wdg.layout().replaceWidget(item.wdg)

        #  fixme BOURRIN:
        self.wdg = QWidget()
        self.compute_wdg()

        # new_sub_widgets = self.sub_widgets()
        # for sub_wdg, new_sub_wdg in zip(sub_widgets, new_sub_widgets):
        #     if new_sub_wdg is not sub_wdg:
        #         changed = True
        #         self.wdg.layout().replaceWidget(sub_wdg, new_sub_wdg)
        # self.wdg.update()
        # return changed


class PatternTree(QObject):
    """
    A class for storing widgets associated with PatterMathObject,
    which represents a MathObject under construction.
    """

    modified = Signal()

    def __init__(self, math_object: MathObject):
        super(PatternTree, self).__init__()
        self.math_object = math_object
        self.shape_wdg: Optional[ShapeWdg] = None
        self.wdg = self.wdg_from_math_object()
        self.parent = None

    def has_unmatched_metavars(self):
        math_object = self.math_object
        return isinstance(math_object, PatternMathObject) \
            and math_object.non_matched_mvars()

    def set_as_parent(self):
        for pattern_tree in self.children_pattern_tree:
            pattern_tree.parent = self
            pattern_tree.modified.connect(self.modified)

    def wdg_from_math_object(self):
        """
        Compute self.wdg. There are three cases :
        (1) self is an unmatched metavar,
        (2) self is a PatternMathObject with unmatched metavars,
        (3) self has no unmatched metavars.
        """

        math_object = self.math_object
        if isinstance(math_object, MetaVar):
            if not math_object.matched_math_object:
                return MetavarButton(self)
            else:
                math_object = math_object.matched_math_object

        if self.has_unmatched_metavars():
            assert isinstance(math_object, PatternMathObject)
            self.shape_wdg = ShapeWdg(math_object)
            self.set_as_parent()
            return self.shape_wdg.wdg

        else:
            return RawLabelMathObject(math_object)

    @property
    def children_pattern_tree(self):
        if self.shape_wdg:
            return [item for item in self.shape_wdg.list
                    if isinstance(item, PatternTree)]
        else:
            return []

    def wdg_state(self):
        """
        Return either MetavarButton, RawLabelMathObject, or QWidget.
        """
        return type(self.wdg)

    # def update_parent(self):
    #     if self.parent:
    #         self.parent.update_parent()
    #     else:
    #         self.update()

    def is_complete(self):
        return self.wdg_state() == RawLabelMathObject

    def is_up_to_date(self):
        """
        True iff no metavar has been matched since creation of self's wdg.
        """
        if self.wdg_state() == RawLabelMathObject:
            return True
        elif self.wdg_state() == MetavarButton:
            return not self.math_object.matched_math_object
        elif not self.has_unmatched_metavars():
            # Self can be completed, but is not a RawLabelMathObject
            return False
        else:
            return all([child.is_up_to_date()
                        for child in self.children_pattern_tree])

    def update(self) -> bool:
        """
        Update self, return True if some update has been done.
        """
        if self.is_up_to_date():
            return False
        elif self.is_complete():
            return False
        elif self.wdg_state() == MetavarButton:
            self.wdg = self.wdg_from_math_object()
        elif not self.has_unmatched_metavars():  # Self can be completed!
            if isinstance(self.math_object, PatternMathObject):
                self.math_object = self.math_object.apply_matching()
            self.wdg = self.wdg_from_math_object()
        else:  # Some child is not up-to-date
            self.shape_wdg.update()
            self.wdg.deleteLater()
            self.wdg = self.shape_wdg.wdg


class PatternMenu(QMenu):
    """
    Provide the menu associated to a given metavar, where entries are filtered
    to fit the metavar type.
    """
    building_patterns = building_patterns
    context_objects = []

    substitute_metavar = Signal()

    def __init__(self, metavar_button, include_context=True):
        super().__init__()
        self.metavar_button = metavar_button
        self.include_context = include_context
        self.populate_menu_with_context()
        self.populate_menu()
        self.metavar.clear_matching()  # IMPORTANT

    @property
    def metavar(self):
        return self.metavar_button.metavar

    def action_from_pattern(self, str_pattern) -> QAction:
        """
        Return the QAction corresponding to the given pattern
        """
        action = QAction()
        action.str_pattern = str_pattern
        action.triggered.connect(partial(self.substitute, action))
        return action

    def action_from_math_object(self, math_object):
        action = QAction()
        action.math_object = math_object
        action.triggered.connect(partial(self.substitute, action))
        return action

    def populate_menu_with_context(self):
        context_menu = QMenu(_("Context"))
        for mo in context:
            action = self.action_from_math_object(mo)
            action.setText(mo.to_display(format_='utf8'))
            ################################
            # Enable only if match metavar #
            ################################
            action.setEnabled(self.metavar.match(mo, do_matching=False))
            context_menu.addAction(action)

        self.addMenu(context_menu)

    def populate_menu(self):
        # TODO: add context objects if self.include_context

        # TODO: filter
        for title, dic in self.building_patterns.items():
            new_menu = QMenu(title)
            for pretty_name, (symbol, str_pattern, pattern) in dic.items():
                action_text = pretty_name + (' ' + symbol if symbol else '')
                action = self.action_from_pattern(str_pattern)
                action.setText(action_text)
                ################################
                # Enable only if match metavar #
                ################################
                # Fixme: refine this
                action.setEnabled(self.metavar.match(pattern,
                                                     do_matching=False))
                new_menu.addAction(action)

            self.addMenu(new_menu)

    @Slot()
    def substitute(self, action):
        if hasattr(action, 'str_pattern'):
            tree = tree_from_str(action.str_pattern)
            metavars = []
            new_pattern = PatternMathObject.from_tree(tree, metavars)
        elif hasattr(action, 'math_object'):
            new_pattern = action.math_object
        self.metavar.matched_math_object = new_pattern
        self.metavar_button.modified.emit()


class MetavarButton(QPushButton):
    """

    """

    def __init__(self, metavar_pattern_tree, include_context=True):
        super().__init__()
        self.pattern_tree = metavar_pattern_tree
        self.setText("?")
        # self.setPopupMode(QToolButton.InstantPopup)
        self.setMenu(PatternMenu(self, include_context))

        # mvarbuttons.append(self)
    # def update_parent(self):
    #     self.pattern_tree.update_parent()

    @property
    def metavar(self):
        return self.pattern_tree.math_object

    @property
    def modified(self):
        return self.pattern_tree.modified

    # def matched_object_widget(self) -> Optional[QWidget]:
    #     math_object = self.metavar.matched_math_object
    #     if not math_object:
    #         return
    #     return PatternWidget(math_object)
    #
    # def update_display(self):
    #     """
    #     If self has a matched_math_object, replace self in parent by the
    #     widget showing the matched_math_object.
    #     """
    #     parent = self.parent()
    #     if not parent:
    #         return
    #     layout = parent.layout()
    #     new_widget = self.matched_object_widget()
    #     if new_widget:
    #         # layout.addWidget(new_widget)
    #         index = layout.indexOf(self)
    #         # item = layout.itemAt(index)
    #         layout.insertWidget(index, new_widget)
    #         layout.removeWidget(self)
    #         self.deleteLater()


class BuildingPatternWindow(QWidget):
    """
    A widget allowing usr to build a MathObject.
    """

    def __init__(self, initial_object=None, context=None):
        super().__init__()
        # Does not work: must use PatternMenu instances instead
        # PatternMenu.substitute_metavar.connect(self.update_display)

        # Logical data
        if context is None:
            context = []
        else:
            PatternMenu.context_objects = context
        if not initial_object:
            math_type = PatternMathObject.NO_MATH_TYPE
            metavar = PatternMathObject.new_metavar(math_type)
            initial_object = metavar

        self.pattern_tree = PatternTree(initial_object)
        self.pattern_tree.modified.connect(self.update_display)
        self.building_widget = self.pattern_tree.wdg

        self.history = []

        # Display widget
        self.display_wdg = QWidget()
        self.display_lyt = QHBoxLayout()
        self.display_lyt.addStretch()
        self.display_lyt.addWidget(self.building_widget)
        self.display_lyt.addStretch()
        self.display_wdg.setLayout(self.display_lyt)

        # Lean widget  TODO = connect modifications
        self.lean_wdg = QLineEdit(self.lean_display)
        group = QGroupBox("Lean code:")
        lean_lyt = QVBoxLayout()
        lean_lyt.addWidget(self.lean_wdg)
        group.setLayout(lean_lyt)

        # Layouts
        main_lyt = QVBoxLayout()
        main_lyt.addWidget(self.display_wdg)
        main_lyt.addWidget(group)
        self.setLayout(main_lyt)

    @property
    def math_object(self):
        if self.pattern_tree:
            return self.pattern_tree.math_object

    @Slot()
    def update_display(self):
        """
        """
        # fixme:
        # self.history.extend(copy(self.pattern_tree.math_object))
        self.pattern_tree.update()
        new_wdg = self.pattern_tree.wdg
        if self.building_widget is not new_wdg:
            self.display_lyt.replaceWidget(self.building_widget,
                                           new_wdg)
            self.display_wdg.update()
            self.building_widget.deleteLater()
            self.building_widget = new_wdg
        self.lean_wdg.setText(self.lean_display)

    @property
    def lean_display(self):
        string = self.math_object.to_display(format_='lean')
        return string


class SnippetsBuilder(QMainWindow):

    def __init__(self, context=None, initial_object=None):
        super().__init__()
        self.setWindowTitle("Building Math Object")

        self.central_wdg = BuildingPatternWindow(context=context,
                                                 initial_object=initial_object)
        self.setCentralWidget(self.central_wdg)

        self.tool_bar = QToolBar()
        self.addToolBar(self.tool_bar)


if __name__ == '__main__':
    TYPE = MathObject(node="TYPE", info={}, children=[],
                      math_type=MathObject.NO_MATH_TYPE)
    X = MathObject(node="LOCAL_CONSTANT", info={'name': 'X'}, children=[],
                   math_type=TYPE)
    set_X = MathObject(node="SET", info={}, children=[X],
                       math_type=TYPE)

    A = MathObject(node="LOCAL_CONSTANT", info={'name': 'A'}, children=[],
                   math_type=set_X)
    x = MathObject(node="LOCAL_CONSTANT", info={'name': 'x'}, children=[],
                   math_type=X)

    m1 = MetaVar(math_type=X)
    m2 = MetaVar(math_type=X)
    m3 = MetaVar(math_type=PatternMathObject.NO_MATH_TYPE)
    p = PatternMathObject(node="PROP_INCLUDED", info={}, children=[m1, m2],
                          math_type=MathObject.PROP)
    # m3.matched_math_object = p
    # m1.matched_math_object = x
    # m2.matched_math_object = A
    #
    # s = m3.to_display(format_="utf8")
    # print(s)

    context = [X, A, x]
    app = QApplication()
    main_window = SnippetsBuilder(context=context, initial_object=None)
    main_window.show()
    app.exec_()


