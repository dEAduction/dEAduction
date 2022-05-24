"""
# Classes for displaying a proof tree. #

Author(s)     : F Le Roux
Maintainer(s) : F. Le Roux
Created       : 03 2022 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the dEAduction team

This file is part of dEAduction.

    dEAduction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    dEAduction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
from typing import Union, Optional
from PySide2.QtWidgets import (QApplication, QLayout, QVBoxLayout, QWidget,
                               QSizePolicy)
from PySide2.QtWidgets import QScrollArea
from PySide2.QtCore import Slot, QSettings, QEvent
from PySide2.QtGui import QPainter

import sys

import deaduction.pylib.config.vars as cvars

from deaduction.dui.elements.proof_tree.proof_tree_primitives import \
    ContextWidget, TargetWidget, PureContextWidget, SubstitutionContextWidget, \
    TargetSubstitutionArrow, paint_layout

global _

if __name__ != "__main__":
    from deaduction.pylib.mathobj import MathObject
else:
    def _(x):
        return x

    class MathObject:
        pass

    class GoalNode:
        pass


log = logging.getLogger(__name__)


########################
# Abstract Goal blocks #
########################
class AbstractGoalBlock:
    """
    A generic class for dealing with the logical part of WidgetGoalBlock.
    An AbstractGoalBlock may have one target and two context lists,
    corresponding to new context element to be displayed before / after the
    target.
    - rw = None / "rw" / "implicit_rw".
    """
    merge = True  # Set to False to prevent any merging
    # goal_nb = 0

    def __init__(self, logical_parent, goal_node,
                 context1: [MathObject] = None,
                 target: MathObject = None, context2=None,
                 pure_context: tuple = None,
                 merge_up=False, merge_down=False, rw=None):

        self._context1 = context1 if context1 else []
        self._target = target
        self.context2 = context2 if context2 else []
        self.pure_context = pure_context if pure_context else ()

        self.logical_parent = logical_parent  # Usually set by parent
        self.logical_children = []
        # self.goal_nb = AbstractGoalBlock.goal_nb
        # AbstractGoalBlock.goal_nb += 1

        self.wanna_merge_up = merge_up
        self.wanna_merge_down = merge_down
        self.rw = rw

        self.goal_node = goal_node

    @property
    def goal_nb(self):
        return self.goal_node.goal_nb

    @property
    def step_nb(self):
        return self.goal_node.proof_step_nb

    def is_recursively_solved(self):
        return self.goal_node.is_recursively_solved()

    def is_recursively_sorry(self):
        return self.goal_node.is_recursively_sorry()

    @property
    def merge_up(self):
        """
        True if self's content should be merged with parent's.
        """
        return (AbstractGoalBlock.merge
                and self.wanna_merge_up and self.logical_parent is not None
                and self.logical_parent.wanna_merge_down
                and self.isEnabled() == self.logical_parent.isEnabled())

    @property
    def merge_down(self):
        """
        True if self's content should be merged with (lonely) child's.
        """
        return (AbstractGoalBlock.merge
                and self.wanna_merge_down and len(self.logical_children) == 1
                and self.logical_children[0].wanna_merge_up
                and self.isEnabled() == self.logical_children[0].isEnabled())

    @property
    def context1(self):
        """
        Fusion self 's _context with child's context. Note that this will call
        recursively to all descendant's _context, as far as they are IntroWGB.
        """
        if self.merge_down:
            return self._context1 + self.logical_children[0].context1
        else:
            return self._context1

    @property
    def target(self):
        if self.merge_down:
            return self.logical_children[0].target
        else:
            return self._target

    def set_invisible(self, yes=True):
        """
        This is used for instance for WGB corresponding to end of proof,
        which are not supposed to be displayed.
        """
        self._is_visible = not yes

    def is_visible(self, reference_level=-1):
        if self._is_visible is not None:
            return self._is_visible

        if reference_level == -1:
            reference_level = WidgetGoalBlock.rw_level
        return self.rw_level <= reference_level
        # and not self.merge_up

    @property
    def target_msg(self) -> callable:
        if self.merge_down:
            return self.logical_children[0].target_msg  # No parentheses!
        else:
            return self.goal_node.html_msg  # (callable)

    def add_logical_child(self, child):
        self.logical_children.append(child)


######################
# Widget Goal blocks #
######################
class WidgetGoalBlock(QWidget, AbstractGoalBlock):
    """
    A generic widget for displaying an AbstractGoalNode. It has four
    optional widgets:
     - one widget for showing some context objects in a horizontal layout,
     - another one for showing a target,
     - and a third one for showing a second context list under the target.
     - If all of these are None, then maybe the fourth one,
     pure_context_widget, is not.

    If self has a target_widget, then it has a children_layout inside to
    welcome children (and descendants). If not, children are passed to
    logical_parent.

    Self can be "merged up": in this case its information are displayed by
    one of its ascendant, and self's layout is never set. In particular,
    self has no target_widget and no children_layout.

    More generally, self should have a target_widget (and a children_layout) iff
    it is actually displayed.

    self.children_widget reflects the children WidgetGoalBlock that should
    really be displayed in self's children_layout.

    Note that instantiation does NOT set the layout: one has to call
    self.update_display().
    """
    rw_level = 1  # show rw but not implicit rw  # FIXME: not implemented
    proof_tree_window = None  # Set up by ProofTreeWindow

    def __init__(self, logical_parent, goal_node,
                 context1=None, target=None, context2=None, pure_context=None,
                 merge_down=False, merge_up=False, rw_level=0,
                 is_target_substitution=False):
        """
        rw_level =  0 if self is not a rw operation,
                    1 if self is a rw operation
                    2 if self is an implicit rw operation
        self will be displayed only if self.rw_level <= cls.rw_level.
        """
        assert (pure_context is None or (context1 is None and target is None
                                         and context2 is None))
        super().__init__()
        AbstractGoalBlock.__init__(self, logical_parent=logical_parent,
                                   goal_node=goal_node,
                                   context1=context1,
                                   target=target, context2=context2,
                                   pure_context=pure_context,
                                   merge_down=merge_down, merge_up=merge_up)
        # self should be displayed in self.parent_widget's children_layout
        self.parent_widget = None
        self._is_visible = None
        self.is_target_substitution = is_target_substitution

        # Main widgets containers:
        self.pure_context_widget: Optional[PureContextWidget] = None
        self.context1_widget: Optional[ContextWidget] = None
        self.target_widget: Optional[TargetWidget] = None
        self.context2_widget: Optional[ContextWidget] = None
        self.children_widgets = []
        self.target_substitution_arrow = None
        # self.max_nb_children_wdg = 1000000  # 1000000 = Infinity

        # Set main_layout with just one stretch
        self.main_layout = QVBoxLayout()
        self.main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        if self.logical_parent:  # Case of root
            self.logical_parent.add_logical_child(self)
        # if self.merge_up:
        #     self.logical_parent.update()
        # else:
        #     self.set_layout_without_children()
        # self.set_layout_without_children()
        # if not self.merge_up:
        #     self.set_layout_without_children()

    def __repr__(self):
        return self.context1, self.target, self.context2, self.pure_context

    # def paintEvent(self, event):
    #     """ For debugging. """
    #     painter = QPainter(self)
    #     paint_layout(painter, self)

    @property
    def children_layout(self):
        """
        Returns the layout that should welcome children widgets, or None if
        they should be passed to self's parent.
        """
        if self.is_visible() and self.target_widget \
                and not self.is_target_substitution:
            return self.target_widget.children_layout
        else:
            return None

    def set_layout_without_children(self):
        """
        Populate main_layout from scratch, but does NOT take care of children.
        """
        # TODO: put the cleaning part in a clean_layout method,
        #  and the special cases (pure_context, substitution) in
        #  corresponding subclasses.

        # Clear target and context. Context2_widget is a child of target_widget.
        for wdg in (self.pure_context_widget,
                    self.target_widget,
                    self.context1_widget):
            if wdg and self.main_layout.indexOf(wdg) != -1:
                self.main_layout.removeWidget(wdg)
                wdg.hide()  # FIXME: deleteLater() ?
            self.context1_widget = None
            self.context2_widget = None
            self.target_widget = None
            self.pure_context_widget = None

            self.children_widgets = []

        if not self.is_visible or self.merge_up:
            return

        # Create and insert new widgets (at pole position, in reverse order):
        if self.pure_context:
            premises, operator, conclusions, type_ = self.pure_context
            if type_ == "operator":
                self.pure_context_widget = PureContextWidget(premises,
                                                             operator,
                                                             conclusions)
            elif type_ == "substitution":
                self.pure_context_widget = SubstitutionContextWidget(premises,
                                                                     operator,
                                                                     conclusions
                                                                     )

            self.main_layout.insertWidget(0, self.pure_context_widget)
            return

        if self.target:
            self.target_widget = TargetWidget(parent_wgb=self,
                                              target=self.target,
                                              target_msg=self.target_msg,
                                              is_target_substitution=
                                              self.is_target_substitution)
            self.main_layout.insertWidget(0, self.target_widget)

        if self.context1:
            self.context1_widget = ContextWidget(self.context1)
            self.main_layout.insertWidget(0, self.context1_widget)

        if self.context2 and self.target_widget:
            self.context2_widget = ContextWidget(self.context2)
            self.children_layout.addWidget(self.context2_widget)

    @property
    def displayable_children(self):
        """
        Return the list of children that should be displayed (either here or
        by an ascendant).
        """
        return [child for child in self.logical_children if
                child.is_visible() and not child.merge_up]

    @property
    def descendants_not_displayed_by_self(self):
        """
        Return the ordered list of descendants that are not displayed by their
        parent, and should be displayed by one of self's ascendants.
        """
        if self.children_layout and not self.merge_up:
            # Self will handle descendants, except at most 1 TargetSubstitution
            return []
            # child for child in self.displayable_children if isinstance(child, TargetSubstitutionWGB)]
        else:
            descendants = []
            for child in self.logical_children:
                descendants.extend(child.descendants_not_displayed_by_self)
            return self.displayable_children + descendants

    @property
    def descendants_displayed_by_self(self):
        """
        Determine the ordered list of widgets that should be displayed in
        self.children_layout.
        """
        if not self.children_layout or self.merge_up:
            return []
        else:
            descendants = []
            for child in self.logical_children:
                descendants.extend(child.descendants_not_displayed_by_self)
            displayed_children = self.displayable_children
            # [child for child in self.displayable_children
            #                   if not isinstance(child, TargetSubstitutionWGB)]
            return displayed_children + descendants

    def add_widget_child(self, child):
        """
        Add the child if self has a children_layout, else call parent.This
        method is called when adding a logical child or by a child who
        delegates the display of its children widgets.
        """
        # FIXME: obsolete

        if not child.is_visible():
            return

        if self.children_layout:
            child.parent_widget = self
            self.children_widgets.append(child)
            self.children_layout.addWidget(child)
        else:
            self.logical_parent.add_widget_child(child)

    # def add_logical_child(self, child):
    #     """
    #     This method must be called to add a new child, but NOT to reset an
    #     existing child.
    #     """
    #     super().add_logical_child(child)
    #     # self.add_widget_child(child)  # Useless: set up by update_display

    def set_children_widgets(self):
        """
        Display directly descendants_to_be_displayed.
        """
        self.children_widgets = []
        if self.children_layout:
            for child in self.descendants_displayed_by_self:
                # log.debug(f"Putting wgb {child.goal_nb} in {self.goal_nb}'s "
                #           f"children layout")
                child.parent_widget = self
                self.children_widgets.append(child)
                self.target_widget.add_child_wgb(child)
                # self.children_layout.addWidget(child)
                # self.children_layout.setAlignment(child, Qt.AlignLeft)
            # log.debug(f"--> {self.children_layout.count()} displayed children")

    def is_conditionally_solved(self):
        """
        True if self is not solved but will be as soon as the descendant
        target are.
        """
        if self.is_recursively_solved() or not self.logical_children:
            return False
        if self.merge_down:
            return self.logical_children[0].is_conditionally_solved()
        else:
            return all([child.target or child.is_conditionally_solved() or
                        child.is_recursively_solved()
                        for child in self.logical_children])

    def is_no_more_goals(self):
        return self.goal_node.is_no_more_goals()

    def set_enabled(self, yes=True):
        """
        This allows re-implementation by subclasses, to handle EnabledEvents
        when widget is not visible.
        """
        self.setEnabled(yes)

    def enable_recursively(self, till_step_nb):
        """
        Recursively disable self from the indicated goal_node nb.
        Note that tree must be updated to adapt merging.
        """
        if self.step_nb > till_step_nb:
            self.set_enabled(False)
        else:
            self.set_enabled(True)
        for child in self.logical_children:
            child.enable_recursively(till_step_nb)

    def check_context1(self):
        """
        Check if context1_widget displays the content of context1.
        """
        if not self.context1:
            return self.context1_widget is None
        elif not self.context1_widget:
            return False

        if len(self.context1) != len(self.context1_widget.math_objects):
            return False
        tests = [math_obj in self.context1 for math_obj in
                 self.context1_widget.math_objects]
        return all(tests)

    def check_context2(self):
        """
        Check if context1_widget displays the content of context1.
        """
        if not self.context2:
            return self.context2_widget is None
        elif not self.context2_widget:
            return False
        if len(self.context2) != len(self.context2_widget.math_objects):
            return False
        tests = [math_obj in self.context2 for math_obj in
                 self.context2_widget.math_objects]
        return all(tests)

    def check_pure_context(self):
        if not self.pure_context:
            return not self.pure_context_widget
        elif not self.pure_context_widget:
            return False
        else:
            pcw = self.pure_context_widget
            premises, operator, conclusions, type_ = self.pure_context
            tests = [premises == pcw.premises,
                     operator == pcw.operator,
                     conclusions == pcw.conclusions,
                     type_ == pcw.type_]
            return all(tests)

    def check_target(self):
        """
        Check if target_widget displays the content of target.
        """
        if not self.target_widget:
            return self.target is None
        else:
            return self.target == self.target_widget.target

            # return (self.target == self.target_widget.target and
            #         self.target_substitution_arrow ==
            #         self.target_widget.target_substitution_arrow)

    def check_children(self):
        """
        Check if children_widget displays descendants_to_be_displayed.
        """
        return self.children_widgets == self.descendants_displayed_by_self

    def is_up_to_date(self):
        """
        Check if display is coherent with datas. Specifically,
        compare the contents of
        - context1 and context1_widget,
        - target and target_widget,
        - context2 and context2_widget,
        - descendants_to_be_displayed and children_widgets.
        """
        return all([self.check_pure_context(),
                    self.check_context1(),
                    self.check_target(),
                    self.check_context2(),
                    self.check_children()
                    ])

    def update_display(self):
        # log.debug(f"Updating WGB for nb {self.goal_nb}: {self.goal_node}...")
        if self.target_widget:
            self.target_widget.set_status()
        if self.is_up_to_date():
            # log.debug("... is up to date")
            return
        else:
            # log.debug("...setting layout and children")
            self.set_layout_without_children()
            self.set_children_widgets()

    def update_display_recursively(self):
        """
        Update children, then self.
        """
        for child in self.logical_children:
            child.update_display_recursively()

        self.update_display()

    def set_as_current_target(self, yes=True, blinking=True):
        """
        If self has a target_widget, then its target will be set as current.
        If not, then self is inside a children_layout, of some target_widget
        of some ascendant, and this target_widget should be set as current.
        """
        if self.target_widget:
            self.target_widget.set_as_current_target(yes, blinking)
            # TODO: set visible in scroll area
        elif yes and self.logical_parent:
            self.logical_parent.set_as_current_target(True, blinking)

    def set_current_target_recursively(self, goal_nb, blinking=True):
        if self.goal_nb == goal_nb:
            self.set_as_current_target(yes=True, blinking=blinking)
        else:
            self.set_as_current_target(False)

        for child in self.logical_children:
            child.set_current_target_recursively(goal_nb, blinking=blinking)

    def make_visible(self, wdg: QWidget):
        """
        Recursively call to parent to make wgb visible in the scrollArea.
        """
        parent = self.parent()
        while not hasattr(parent, "ensureWidgetVisible"):
            if not hasattr(parent, "parent"):
                log.warning("Ensure visible failed!")
                return
            parent = parent.parent()

        parent.ensureWidgetVisible(wdg, ymargin=100)

    def parent_wgb(self):
        parent = self.parent()
        while parent and not isinstance(parent, WidgetGoalBlock):
            parent = parent.parent()
        return parent


class GoalSolvedWGB(WidgetGoalBlock):
    """
    This WGB reflects GoalNode.goal_solved, a fake goal node with target
    "goal solved". It should remain invisible.
    """
    def __init__(self, logical_parent, goal_node):
        target = goal_node.goal.target.math_type
        super().__init__(logical_parent, goal_node, target=target)
        # self.set_invisible()


class ByCasesWGB(WidgetGoalBlock):
    """
    Display of one sub-case of a proof by cases.
    """
    def __init__(self, logical_parent, goal_node, target, context):
        super().__init__(logical_parent, goal_node,
                         target=target, context2=context,
                         merge_down=False, merge_up=False)


class IntroWGB(WidgetGoalBlock):
    """
    Display of introduction of elements to prove universal props.
    Try to merge with parent and child.
    """
    def __init__(self, logical_parent, goal_node, context=None, target=None):
        super().__init__(logical_parent, goal_node, context, target,
                         merge_down=True, merge_up=True)


class IntroImpliesWGB(WidgetGoalBlock):
    """
    Display of introduction of elements to prove universal props or
    implications. Try to merge with parent but not child.
    """
    def __init__(self, logical_parent, goal_node, context=None, target=None):
        super().__init__(logical_parent, goal_node, context, target,
                         merge_down=False, merge_up=True)


class PureContextWGB(WidgetGoalBlock):

    def __init__(self, logical_parent, goal_node,
                 premises, operator, conclusions):
        super().__init__(logical_parent, goal_node,
                         pure_context=(premises, operator, conclusions,
                                       "operator"))
        # TODO: merge with child PureContextWGB if child's premises == self's
        #  conclusion


class SubstitutionWGB(WidgetGoalBlock):

    def __init__(self, logical_parent, goal_node,
                 premises, rw_item, conclusions):
        super().__init__(logical_parent, goal_node,
                         pure_context=(premises, rw_item, conclusions,
                                       "substitution"))
        # TODO: merge with child SubstitutionWGB if child's premises == self's
        #  conclusion


class TargetSubstitutionWGB(WidgetGoalBlock):
    """
    A class to display a re-writing occurring in the target. The display
    should be like:

    V Proof of target before rw
    |  <Some children wgt prior to rw >     |
    |                                       | <rw_item, e.g. f(x)=y>
    |                                       v
    V Proof of target after rw
    |
    |
    | <status msg>

    """
    def __init__(self, logical_parent, goal_node, rw_item, target=None):
        if not target:
            target = goal_node.goal.target.math_type
        super().__init__(logical_parent, goal_node, target=target,
                         is_target_substitution=True)
        self.substitution_arrow = TargetSubstitutionArrow(rw_item)

    def set_enabled(self, yes=True):
        self.substitution_arrow.setEnabled(yes)
        if self.target_widget:
            self.target_widget.title_label.setEnabled(yes)
            self.target_widget.status_label.setEnabled(yes)

# def changeEvent(self, event):
    #     if event.type is QEvent.EnabledChange:
    #         self.substitution_arrow.setEnabled(self.isEnabled())
    #         if self.target_widget:
    #             self.target_widget.title_label.setEnabled(self.isEnabled())


class EmptyWGB(WidgetGoalBlock):
    """
    A wgb which does not display anything, but reflects some (unimportant)
    goal node, e.g. splitting a context conjunction.
    """
    def __init__(self, logical_parent, goal_node):
        super().__init__(logical_parent, goal_node)


###############
# Main Window #
###############
class ProofTreeWindow(QWidget):
    """
    A widget for displaying the proof tree.
    """

    def __init__(self, context=None, target=None):
        """
        Context and target are the elements of the initial goal, if any.
        """
        super().__init__()
        self.setWindowTitle("Proof Tree")
        self.current_wgb = None
        settings = QSettings("deaduction")
        if settings.value("proof_tree/geometry"):
            self.restoreGeometry(settings.value("proof_tree/geometry"))

        main_layout = QVBoxLayout()
        self.main_window = QScrollArea()
        main_layout.addWidget(self.main_window)

        if context or target:
            main_block = WidgetGoalBlock(context, target)
            self.set_main_block(main_block)
        else:
            self.main_block: Optional[WidgetGoalBlock] = None

        self.setLayout(main_layout)

        WidgetGoalBlock.proof_tree_window = self

        self.set_style_sheet()

    def set_style_sheet(self):
        color_var = cvars.get("display.color_for_variables")
        color_prop = cvars.get("display.color_for_props")
        color_op = cvars.get("display.color_for_operator_props")
        new_border_width = "2px"
        old_border_width = "1px"
        op_border_width = "4px"
        old_border_style = "dashed"
        self.setStyleSheet("QLabel#new_obj:enabled {padding: 5px;"
                               f"border-width: {new_border_width};"
                               f"border-color: {color_var};"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "QLabel#new_obj:!enabled {padding: 5px;"
                                f"border-width: {new_border_width};"
                                "border-color: lightgrey;"
                                "border-style: solid;"
                                "border-radius: 10px;}"
                           "QLabel#old_obj:enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               f"border-color: {color_var};"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "QLabel#old_obj:!enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               "border-color: lightgrey;"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "QLabel#new_prop:enabled {padding: 5px;"
                               f"border-width: 2px;"
                               f"border-color: {color_prop};"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "QLabel#new_prop:!enabled {padding: 5px;"
                               f"border-width: {new_border_width};"
                               "border-color: lightgrey;"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "QLabel#old_prop:enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               f"border-color: {color_prop};"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "QLabel#old_prop:!enabled {padding: 5px;"
                               f"border-width: {old_border_width};"
                               "border-color: lightgrey;"
                               f"border-style: {old_border_style};"
                               "border-radius: 10px;}"
                           "OperatorLMO:enabled {padding: 5px;"
                               f"border-width: {op_border_width};"
                               f"border-color: {color_op};"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "OperatorLMO:!enabled {padding: 5px;" 
                               f"border-width: {op_border_width};"
                               "border-color: lightgrey;"
                               "border-style: solid;"
                               "border-radius: 10px;}"
                           "BlinkingLabel {font-style: italic;}"
                           # "RwItemLMO:enabled {padding: 5px;"
                           #     f"border-width: {old_border_width};"
                           #     f"border-color: {color_op};"
                           #     "border-style: solid;"
                           #     "border-radius: 10px;}"
                           # "RwItemLMO:!enabled {padding: 5px;"
                           #     f"border-width: {old_border_width};"
                           #     "border-color: lightgrey;"
                           #     "border-style: solid;"
                           #     "border-radius: 10px;}"
                           )

    def set_main_block(self, block: WidgetGoalBlock):
        self.main_block = block
        self.main_window.setWidget(block)
        self.current_wgb = block
        # self.main_block.set_as_current_target()

    def update_display(self):
        if self.main_block:
            self.main_block.update_display_recursively()

    def set_current_target(self, goal_nb, blinking=True):
        self.main_block.set_current_target_recursively(goal_nb, blinking)

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("proof_tree/geometry", self.saveGeometry())
        event.accept()
        self.hide()
        # TODO: save tree state

    @Slot()
    def toggle(self):
        self.setVisible(not self.isVisible())

    # def paintEvent(self, event):
    #     """ For debugging. """
    #     painter = QPainter(self)
    #     paint_layout(painter, self.main_block)


def main():
    app = QApplication()
    # label_bf.setStyleSheet("{font-weight: bold;}")
    # pcw = HorizontalArrow(100)
    # pcw = SubstitutionArrow("f(x)=y mais aussi TOTO le clown")
    pcw = PureContextWidget(["y dans A"], "f(x)=y et aussi toto",
                                    ["f(x) dans A"])
    pcw.show()

    # main_window = ProofTreeWindow()
    # AbstractGoalBlock.merge = True
    #
    # context0 = ["X", "Y", "f"]
    # target0 = "f surjective ⇒ (∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A' ) )"
    # main_block = WidgetGoalBlock(logical_parent=None, goal_node = None,
    #                              context1=context0, target=target0)
    #
    # main_window.set_main_block(main_block)
    # main_window.show()
    #
    # # TODO: change to successive IntroBlocks:
    # intro1 = IntroImpliesWGB(logical_parent=main_block,
    #                          context=["f surjective"],
    #                          target="(∀A ⊂ Y, ∀A' ⊂ Y, ( f⁻¹(A) ⊂ f⁻¹(A')"
    #                                 " ⇒ A ⊂ A' ) )")
    # intro2a = IntroWGB(logical_parent=intro1,
    #                    context=["A"],
    #                    target="∀A' ⊂ Y, f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A'")
    # intro2b = IntroWGB(logical_parent=intro2a,
    #                    context=["A'"], target="f⁻¹(A) ⊂ f⁻¹(A') ⇒ A ⊂ A'")
    # intro3 = IntroImpliesWGB(logical_parent=intro2b,
    #                          context=["f⁻¹(A) ⊂ f⁻¹(A')"], target="A ⊂ A'")
    #
    # intro4 = IntroWGB(logical_parent=intro3,
    #                   context=["y"], target="y ∈ A => y ∈ A'")
    # intro5 = IntroWGB(logical_parent=intro4,
    #                          context=["y ∈ A"], target="y ∈ A'")
    # # intro2b.show()
    #
    #
    # operator = [(["y"], "f surjective", ["x", "y = f(x)"]),
    #             (["y ∈ A"], "y = f(x)", ["f(x) ∈ A"]),
    #             (["f(x) ∈ A"], "definition image réciproque", ["x ∈ f⁻¹(A)"]),
    #             (["x ∈ f⁻¹(A)"], "f⁻¹(A) ⊂ f⁻¹(A')", ["x ∈ f⁻¹(A')"]),
    #             (["x ∈ f⁻¹(A')"], "definition image réciproque", ["f(x) ∈ A'"]),
    #             (["f(x) ∈ A'"], "y = f(x)", ["y ∈ A'"])]
    # previous_block = intro5
    # # op = operator[0]
    # # pure_block0 = PureContextWGB(logical_parent=None,
    # #                              premises=op[0],
    # #                              operator=op[1],
    # #                              conclusions=op[2])
    # # pure_block0.show()
    # for op in operator:
    #     pure_block = PureContextWGB(previous_block,
    #                                 premises=op[0],
    #                                 operator=op[1],
    #                                 conclusions=op[2])
    #     previous_block.add_logical_child(pure_block)
    #     previous_block = pure_block
    #
    # # case_block1 = ByCasesWGB(logical_parent=previous_block,
    # #                          context=["y ∈ A"], target="First case: y ∈ A")
    # # case_block2 = ByCasesWGB(logical_parent=previous_block,
    # #                          context=["y ∉ A"], target="Second case: y ∉ A")
    # # case_block1.show()
    # # previous_block.set_children([case_block1, case_block2])
    # #
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

