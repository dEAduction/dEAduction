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
from typing import Optional
from PySide2.QtWidgets import (QApplication, QLayout, QVBoxLayout, QWidget,
                               QSizePolicy)
from PySide2.QtWidgets import QScrollArea
from PySide2.QtCore import Slot, QSettings, QTimer, Signal
from PySide2.QtGui import QPainter

import sys
from functools import partial

import deaduction.pylib.config.vars as cvars

from deaduction.dui.elements.proof_tree.proof_tree_primitives import \
    BlinkingLabel, ProofTitleLabel, RawLabelMathObject, \
    ContextWidget, TargetWidget, OperatorContextWidget,\
    SubstitutionContextWidget, TargetSubstitutionLabel, paint_layout

global _

if __name__ != "__main__":
    from deaduction.pylib.mathobj import MathObject, ContextMathObject
    from deaduction.pylib.proof_tree import GoalNode, RootGoalNode, \
        VirtualBrotherAuxGoalNode
else:  # For debugging only
    def _(x):
        return x

    class MathObject:
        pass

    class GoalNode:
        pass

    class RootGoalNode:
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
    target. This class handles the merging of several GoalNodes into a single
    WidgetGoalBlock. More precisely, we want to avoid repeating the target
    at each step: for instance when introducing several variables (and
    maybe a hypothesis) in a row, the new target will be displayed only after
    the last intro. This is obtained by properties merge_up / merge_down : when
    self.merge_down is True,
    self's widget will not be displayed, but instead its context1 will
    be added to its (single) child's context1 (see property context1), and its
    target will be displayed instead of parent's target.

    :param rw:  None / "rw" / "implicit_rw", according to the level of rw that
    should be displayed. This is not implemented yet (all rw are displayed).
    """
    merge = True  # Set to False to prevent any merging

    def __init__(self, logical_parent, goal_node,
                 context1: [MathObject] = None,
                 target: MathObject = None, context2=None,
                 pure_context: tuple = None,
                 merge_up=False, merge_down=False, rw=0):

        self._context1 = context1 if context1 else []
        self.target = target
        self.context2 = context2 if context2 else []
        self.pure_context = pure_context if pure_context else ()

        self.logical_parent = logical_parent
        self.logical_children = []

        self.wanna_merge_up = merge_up
        self.wanna_merge_down = merge_down
        self.rw = rw

        self.goal_node = goal_node
        self._is_visible = None

    @property
    def goal_nb(self):
        return self.goal_node.goal_nb

    @property
    def step_nb(self):
        return self.goal_node.proof_step_nb

    def is_recursively_solved(self, truncate=False):
        return self.goal_node.is_recursively_solved(truncate)

    def is_no_more_goals(self):
        return self.goal_node.is_no_more_goals()

    def is_recursively_sorry(self, truncate=False):
        return self.goal_node.is_recursively_sorry(truncate)

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
        If merge_up is True, then fusion self 's _context with parent's
        context. Note that this will call recursively to all ancestors'
        _context, as far as they are IntroWGB.
        """
        if self.merge_up:
            return self.logical_parent.context1 + self._context1
        else:
            return self._context1

    def set_invisible(self, yes=True):
        """
        This is used for instance for WGB corresponding to end of proof,
        which are not supposed to be displayed.
        """
        self._is_visible = not yes

    def is_visible(self, reference_level=-1):
        if self._is_visible is not None:
            return self._is_visible

        if reference_level == -1:  # Unused
            reference_level = WidgetGoalBlock.rw_level
        return self.rw_level <= reference_level

    @property
    def target_msg(self) -> callable:
        if self.merge_down:
            return self.logical_children[0].target_msg  # No parentheses!
        else:
            return self.goal_node.html_msg

    def add_logical_child(self, child):
        """
        This should reflect the ProofTree (as opposed to parent.child in the
        QWidget meaning).
        """
        self.logical_children.append(child)


######################
# Widget Goal blocks #
######################
class WidgetGoalBlock(QWidget, AbstractGoalBlock):
    """
    A generic widget for displaying an AbstractGoalNode. It has several
    optional widgets:
     - context1_widget for showing some context objects in a horizontal layout,
     - target_widget for showing a target,
     - context2_widget for showing a second context list under the target.
     - If all of these are None, then maybe the fourth one,
     pure_context_widget, is not None. It is designed to display a step that
     operates purely on the context (the target remains unchanged),
     like a modus ponens.

    If self has a target_widget, then it has a children_layout inside to
    welcome children (and descendants). If not, children are passed for
    display to logical_parent.

    Self can be "merged up": in this case its information are displayed by
    one of its ascendant, and self's layout is never set. In particular,
    self has no target_widget and no children_layout. See AbstractGoalBlock.

    More generally, self should have a target_widget (and a children_layout) iff
    it is actually displayed.

    self.children_widget reflects the children WidgetGoalBlock that should
    really be displayed in self's children_layout, see the method
    descendant_displayed_by_self.

    The attributes proof_title_label and status_label are QLabel that
    respectively display the target ("Proof of ...") and the status of this
    target (solved or to be completed). Both will be passed to the
    TargetWidget; this is the main sub-widget, it handles the display of
    target, context1, and (inductively)  all the children widgets.

    Note that instantiation does NOT set the layout: one has to call
    self.update_display(), that in turn calls set_layout_without_children()
    and set_children(). In particular the above mentioned sub-widgets
    are created only by the set_layout_without_children method.

    Attribute pure_context is a tuple
    (premises: [MathObject], operator: MathObject or Statement,
    conclusions: [MathObject], type_: "operator", "substitution" or
    "no_operator").
    """
    rw_level = 1  # show rw but not implicit rw  # FIXME: not implemented
    proof_tree_window = None  # Set up by ProofTreeWindow
    garbage_collector: [QWidget] = []  # Not used

    def __init__(self, logical_parent, goal_node,
                 context1: [MathObject] = None,
                 target: MathObject = None,
                 context2: [MathObject] = None,
                 pure_context: tuple = None,
                 merge_down=False, merge_up=False, rw_level=0,
                 is_target_substitution=False):

        # The following is not implemented:
        # rw_level =  0 if self is not a rw operation,
        #             1 if self is a rw operation
        #             2 if self is an implicit rw operation
        # self will be displayed only if self.rw_level <= cls.rw_level.

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
        self._is_root_node_or_substituted = None

        # Main widgets containers:
        self.pure_context_widget: Optional[ContextWidget] = None
        self.context1_widget: Optional[ContextWidget] = None
        self.target_widget: Optional[TargetWidget] = None
        if self.target:
            self.status_label = BlinkingLabel(self.status_msg)
            self.proof_title_label = ProofTitleLabel(self.target_msg)
        else:
            self.status_label = None
            self.proof_title_label = None
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

        self.outcomes = [PureContextWGB.from_outcome(virtual_node, self)
                         for virtual_node in goal_node.outcomes]

    def __repr__(self):
        return self.context1, self.target, self.context2, self.pure_context

    def delete_garbage(self):
        # Not used.
        log.debug(f"Deleting {len(self.garbage_collector)} widgets...")
        for wdg in self.garbage_collector:
            try:
                wdg.deleteLater()
            except RuntimeError:
                log.warning("(Already deleted)")

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

    def parent_wgb(self):
        """
        This returns the first ancestor, in the QWidget meaning, which is a
        WGB.
        """
        parent = self.parent()
        while parent and not isinstance(parent, WidgetGoalBlock):
            parent = parent.parent()
        return parent

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

    def status_msg(self, truncate=False) -> Optional[str]:
        """
        Compute the status msg for this part of the proof, to be displayed at
        the end of the block. This method is passed to the BlinkingLabel that
        will display the status_msg as a callable, so that it will be adapted
        as the proof goes on.
        """

        if self.is_recursively_solved(truncate):
            if self.is_no_more_goals():
                msg = _("THE END")
            elif self.is_recursively_sorry(truncate):
                msg = _("(admitted)")
            elif self.is_root_node_or_substituted:
                msg = _("QED!!")
            else:
                msg = _("Goal!")  # + str(self.goal_nb)  # debug
        elif self.is_conditionally_solved():
            msg = None
        else:
            msg = _("( ... under construction... )")
        # log.debug(f"Status msg for goal nb {self.parent_wgb.goal_nb} is {msg}")

        return msg

    def set_layout_without_children(self):
        """
        Populate main_layout from scratch, but does NOT take care of children.
        The WGB should either be
        - a pure context WGB, in which case the
        attribute pure_context is provided, but no target (nor context1/2).
        A pure context WGB can be of type operator, substitution,
        or no operator.
        - or a target WGB, in which case a target is provided and a
        target_widget will be created, of type TargetWidget. context1 and
        context2 may be provided.
        """
        # TODO: put the cleaning part in a clean_layout method,
        #  and the special cases (pure_context, substitution) in
        #  corresponding subclasses.
        # FIXME: fix memory leak??

        # Clear target and context. Context2_widget is a child of target_widget.
        for wdg in (self.pure_context_widget,
                    self.target_widget,
                    self.context1_widget):
            if wdg and self.main_layout.indexOf(wdg) != -1:
                self.main_layout.removeWidget(wdg)
                self.garbage_collector.append(wdg)  # FIXME: deleteLater()?
                wdg.hide()
            self.context1_widget = None
            self.context2_widget = None
            self.target_widget = None
            self.pure_context_widget = None

            self.children_widgets = []

        if not self.is_visible or self.merge_down:
            return

        # Create and insert new widgets (at pole position, in reverse order):
        if self.pure_context:
            premises, operator, conclusions, type_ = self.pure_context
            if type_ == "operator":
                self.pure_context_widget = OperatorContextWidget(premises,
                                                                 operator,
                                                                 conclusions)
            elif type_ == "substitution":
                self.pure_context_widget = SubstitutionContextWidget(premises,
                                                                     operator,
                                                                     conclusions
                                                                     )
            elif type_ == "no operator":
                self.pure_context_widget = ContextWidget(math_objects=
                                                         conclusions)

            self.main_layout.insertWidget(0, self.pure_context_widget)
            return

        if self.target:
            # self.status_label = BlinkingLabel(self.status_msg)
            # self.proof_title_label = ProofTitleLabel(self.target_msg)
            if not self.is_target_substitution:
                log.debug(f"Creating TargetWidget for goal nb {self.goal_nb}.")
                wdg = TargetWidget(parent_wgb=self,
                                   target=self.target,
                                   status_label=self.status_label,
                                   title_label=self.proof_title_label)
                self.target_widget = wdg
                self.main_layout.insertWidget(0, self.target_widget)

        if self.context1:
            self.context1_widget = ContextWidget(self.context1)
            self.main_layout.insertWidget(0, self.context1_widget)

        if self.context2 and self.target_widget:
            self.context2_widget = ContextWidget(self.context2)
            self.children_layout.add_to_content(self.context2_widget)

    # ───────────────────── Add children methods ──────────────────── #
    @property
    def displayable_children(self):
        """
        Return the list of children that should be displayed (either here or
        by an ascendant).
        """
        return [child for child in self.logical_children if
                child.is_visible() and not child.merge_down]

    @property
    def descendants_not_displayed_by_self(self):
        """
        Return the ordered list of descendants that are not displayed by their
        parent, and should be displayed by one of self's ascendants.
        """
        if self.children_layout and not self.merge_down:  # Redundant
            # Self will handle descendants
            return []
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
        if not self.children_layout or self.merge_down:
            return []
        else:
            descendants = []
            for child in self.logical_children:
                descendants.extend(child.descendants_not_displayed_by_self)
            return self.displayable_children + descendants

    def add_child_widget(self, child):
        """
        Add one new child to self.children_layout.
        """
        if self.children_layout:
            log.debug(f"Putting wgb {child.goal_nb} in {self.goal_nb}'s "
                      f"children layout")
            child.parent_widget = self
            self.children_widgets.append(child)
            self.target_widget.add_child_wgb(child)
            if child.outcomes:
                for outcome in child.outcomes:
                    outcome.set_layout_without_children()
                    self.children_widgets.append(outcome)
                    self.target_widget.add_child_wgb(outcome)

    def set_children_widgets(self):
        """
        Display directly descendants_to_be_displayed, if self has a
        children_layout (which should be a layout in self.target_widget).
        Descendants are passed to the target_widget method add_child_wgb().
        """
        self.children_widgets = []
        # if self.children_layout:
        for child in self.descendants_displayed_by_self:
            self.add_child_widget(child)
            # child.parent_widget = self
            # self.children_widgets.append(child)
            # self.target_widget.add_child_wgb(child)
            # if child.outcomes:
            #     for outcome in child.outcomes:
            #         outcome.set_layout_without_children()
            #         self.children_widgets.append(outcome)
            #         self.target_widget.add_child_wgb(outcome)

            # self.target_widget.disclose_or_not()

    # ───────────────────── Enabling methods ──────────────────── #
    def set_enabled(self, yes=True):
        """
        This allows re-implementation by subclasses, to handle EnabledEvents
        when widget is not visible.
        """
        self.setEnabled(yes)

    def enable_recursively(self, till_step_nb) -> bool:
        """
        Recursively disable self from the indicated goal_node nb.
        Note that tree must be updated to adapt merging.
        Return True iff self is enabled and also all its descendant (this is
        not used anymore).
        """
        if self.step_nb > till_step_nb:
            enable = False
        else:
            enable = True

        self.set_enabled(enable)

        # Enable descendants recursively, and get info
        descendants_enabled = [child.enable_recursively(till_step_nb)
                               for child in self.logical_children]

        # Disable status_label if some descendant is disabled
        if self.status_label:
            # self.status_label.setEnabled(all(descendants_enabled))
            self.status_label.enable_or_disable()

        return enable and all(descendants_enabled)

    # ───────────────────── Update methods ──────────────────── #
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
        """
        Check if self.pure_context_widget displays the content of
        self.pure_context.
        """
        if not self.pure_context:
            return not self.pure_context_widget
        elif not self.pure_context_widget:
            return False
        else:
            pcw = self.pure_context_widget
            premises, operator, conclusions, type_ = self.pure_context
            tests = [premises == pcw.pure_premises,
                     operator == pcw.operator,
                     conclusions == pcw.pure_conclusions,
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

    def check_children(self):
        """
        Check if children_widget coincides with descendants_to_be_displayed.
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
                    self.check_context2()
                    ])

    def update_children(self):
        """
        Update children. Generic case should be that there is just one or two
        new widgets to add.
        """
        old_wdgs = self.children_widgets
        new_wdgs = self.descendants_displayed_by_self
        if self.check_children():
            return

        elif len(old_wdgs) >= len(new_wdgs):
            # Oddly enough, this case happens often, with nb = 2.
            # log.warning(f"Odd children widgets nb {len(old_wdgs)} >= "
            #             f"{len(new_wdgs)}, resetting all")
            self.set_layout_without_children()
            self.set_children_widgets()
        else:  # Now len(old_wdgs) < len(new_wdgs)
            # Check existing widgets
            nb = len(old_wdgs)
            if old_wdgs != new_wdgs[:nb]:
                # log.warning(f"Odd {nb} children widgets, resetting all")
                self.set_layout_without_children()
                self.set_children_widgets()
            else:
                # log.debug("Adding child wdg, generic case")
                for wdg in new_wdgs[nb:]:
                    self.add_child_widget(wdg)

    def update_display(self):
        """
        Check if self correctly displays the information containde in its
        attribute target, context1, context2, pure_context, and its children.
        If not, the methods set_layout_without_children() and
        set_children_widgets() are called. They will create from scratch the
        necessary sub-widgets and insert children widgets.
        """
        # log.debug(f"Updating WGB for nb {self.goal_nb}: {self.goal_node}...")
        if not self.is_up_to_date():
            log.debug(f"Updating WGB for goal_nb {self.goal_nb}")
            self.set_layout_without_children()
            self.set_children_widgets()
        else:
            self.update_children()

        if self.target_widget:
            self.target_widget.update()
        #     self.target_widget.set_status()
        if self.status_label:
            self.status_label.set_msg()
            # log.debug(f"Status set for goal nb {self.goal_nb} :"
            #           f"{self.target_widget.status_msg}")

    def update_display_recursively(self):
        """
        Update children, then self.
        """
        for child in self.logical_children:
            child.update_display_recursively()

        self.update_display()

    # ───────────────────── Set current target methods ──────────────────── #
    def set_as_current_target(self, yes=True, blinking=True):
        """
        If self has a target_widget, then its target will be set as current.
        If not, then self is inside a children_layout, of some target_widget
        of some ascendant, and this target_widget should be set as current.
        If some widget is returned (blinking label, or proof title in case of
        history move), then it should be made visible in the ScrollArea.
        """
        if self.target_widget:
            wdg = self.target_widget.set_as_current_target(yes, blinking)
            return wdg
        elif yes and self.logical_parent:
            wdg = self.logical_parent.set_as_current_target(True, blinking)
            return wdg

    def unset_current_target_recursively(self):
        self.set_as_current_target(False)

        for child in self.logical_children:
            child.unset_current_target_recursively()

    def set_current_target_recursively(self, goal_nb, blinking=True) \
            -> Optional[QWidget]:
        """
        Make the status_msg of the current target blinks in boldface.
        The returned widget, if any, should be made visible by scrolling.
        """
        if self.goal_nb == goal_nb:
            wdg = self.set_as_current_target(yes=True, blinking=blinking)
            return wdg
        # else:
        #     self.set_as_current_target(False)

        for child in self.logical_children:
            wdg = child.set_current_target_recursively(goal_nb,
                                                      blinking=blinking)
            if wdg:
                return wdg

    # def make_visible(self, wdg: QWidget):
    #     """
    #     Recursively call to parent to make wgb visible in the scrollArea.
    #     """
    #     # FIXME: does not work??
    #     parent = self.parent()
    #     while not hasattr(parent, "ensureWidgetVisible"):
    #         if not hasattr(parent, "parent"):
    #             log.warning("Ensure visible failed!")
    #             return
    #         parent = parent.parent()
    #
    #     parent.ensureWidgetVisible(wdg, ymargin=100)

    @property
    def math_widgets(self) -> [RawLabelMathObject]:
        """
        Return all math widgets displayed by self which are not targets.
        This is used by the highlight_math_widgets() method.
        """
        wdgs = []
        for wdg in [self.pure_context_widget, self.context1_widget,
                    self.context2_widget]:
            if wdg:
                wdgs.extend(wdg.math_wdgs)

        return wdgs

    def highlight_math_widgets(self, math_object, yes):
        """
        Highlight all RawLabelMathObjects which are related to math_object.
        """
        if not isinstance(math_object, ContextMathObject):
            return
        for math_wdg in self.math_widgets:
            other = math_wdg.math_object
            if isinstance(other, ContextMathObject) and \
                    ( math_object == other
                      or math_object.is_descendant_of(other)
                      or other.is_descendant_of(math_object) ):
                math_wdg.highlight(yes)

    def recursively_highlight(self, math_object, yes):
        self.highlight_math_widgets(math_object, yes)
        for wgb in self.logical_children:
            wgb.recursively_highlight(math_object, yes)
        for wgb in self.outcomes:
            wgb.highlight_math_widgets(math_object, yes)

    @property
    def is_root_node_or_substituted(self):
        """
        True if self is either the WGB that reflects the root of the
        ProofTree, or a WGB obtained from this root WGB by substituting the
        target. In either case, the displayed target is the main target,
        and solving it closes the proof. This is used by self.status_msg to
        display the "QED!!" winning msg.
        """
        if self._is_root_node_or_substituted is None:
            test = (isinstance(self.goal_node, RootGoalNode) or
                    (isinstance(self, TargetSubstitutionWGB) and
                     self.parent_widget and
                     self.parent_widget.is_root_node_or_substituted))
            self._is_root_node_or_substituted = test
        return self._is_root_node_or_substituted


class GoalSolvedWGB(WidgetGoalBlock):
    """
    This WGB reflects GoalNode.goal_solved, a fake goal node with target
    "goal solved". It should remain invisible.
    """
    def __init__(self, logical_parent, goal_node):
        # target = goal_node.goal.target.math_type
        super().__init__(logical_parent, goal_node, target=None)
        # self.set_invisible()
        # self.hide()


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
    """
    Display either just some properties appearing in the context with no
    known origin(with no change in target), or a "modus ponens" involving an
    "operator, i.e. a logical step involving only the context and looking like
    P and (P => Q)  -----> Q.
    """
    def __init__(self, logical_parent, goal_node,
                 premises, operator, conclusions):
        if operator or premises:
            super().__init__(logical_parent, goal_node,
                             pure_context=(premises, operator, conclusions,
                                           "operator"))
        else:
            super().__init__(logical_parent, goal_node,
                             pure_context=(None, None, conclusions,
                                           "no operator"))

    @classmethod
    def from_outcome(cls, outcome: VirtualBrotherAuxGoalNode,
                     parent_wdg: WidgetGoalBlock):
        """
        Display a PureContextWGB after an auxiliary goal is solved, e.g. when
        applying "P => Q" to a target Q, target is replaced by P ; when this
        new target  is solved, this PureContextWGB is displayed, showing how
        the outcome Q is obtained.
        """
        operator = outcome.outcome_operator
        if operator:
            premises = outcome.premises
            conclusions = outcome.conclusions
            wgb = cls(parent_wdg, outcome, premises, operator, conclusions)
        else:
            main_premise = outcome.main_premise
            if main_premise:
                conclusions = [main_premise]
                wgb = cls(parent_wdg, outcome, None, None, conclusions)
            else:
                wgb = None
        return wgb


class SubstitutionWGB(WidgetGoalBlock):
    """
    A WGB showing a substitution (rewriting) occurring in the context.
    """
    def __init__(self, logical_parent, goal_node,
                 premises, rw_item, conclusions):
        super().__init__(logical_parent, goal_node,
                         pure_context=(premises, rw_item, conclusions,
                                       "substitution"))


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
    Actually the attributes (substitution_label, proof_title_label,
    status_label) will be displayed by the target_widget of an ancestor.
    """

    def __init__(self, logical_parent, goal_node, rw_item, target=None):
        if not target:
            target = goal_node.goal.target.math_type
        super().__init__(logical_parent, goal_node, target=target,
                         is_target_substitution=True)
        self.substitution_label = TargetSubstitutionLabel(rw_item)

    def set_enabled(self, yes=True):
        self.substitution_label.setEnabled(yes)
        # if self.target_widget:
        #     self.target_widget.title_label.setEnabled(yes)
        #     self.target_widget.status_label.setEnabled(yes)
        if self.proof_title_label:
            self.proof_title_label.setEnabled(yes)
        if self.status_label:
            self.status_label.setEnabled(yes)


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
    A widget for displaying the proof tree. This is also where all the styles of
    the different sub-widgets are set up.
    """

    action = None  # To be set to the QAction of exercise_toolbar

    def __init__(self, context=None, target=None):
        """
        Context and target are the elements of the initial goal, if any.
        """
        super().__init__()
        log.info("Creating new ProofTreeWindow")
        self.setWindowTitle(_("Global proof view"))
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

        # RawLabelMathObject.highlight_in_tree.connect(self.highlight)
        RawLabelMathObject.highlight_in_tree = self.highlight_from_math_wdg

        if settings.value("isVisible"):
            self.setVisible(bool(settings.value("isVisible")))

    def set_main_block(self, block: WidgetGoalBlock):
        self.main_block = block
        self.main_window.setWidget(block)
        self.current_wgb = block
        # self.main_block.set_as_current_target()

    def closeEvent(self, event):
        # Save window geometry
        settings = QSettings("deaduction")
        settings.setValue("proof_tree/geometry", self.saveGeometry())
        settings.setValue("isVisible", self.isVisible())
        event.accept()

        self.hide()
        if self.action:
            self.action.setChecked(False)
        # TODO: save tree state

    def update_display(self):
        if self.main_block:
            self.main_block.update_display_recursively()
            # self.main_block.delete_garbage()

    def unset_current_target(self):
        self.main_block.unset_current_target_recursively()

    def set_current_target(self, goal_nb, blinking=True) -> Optional[QWidget]:
        """
        Make the status_msg of the current target blinks in boldface.
        Returns either the current blinking status label, or the current
        proof title widget if no label is blinking (history move). The
        returned widget should be made visible by calling the make_visible()
        method.
        """
        wdg = self.main_block.set_current_target_recursively(goal_nb, blinking)
        return wdg

    @Slot()
    def toggle(self):
        """
        Toggle the window, i.e. make it visible / invisible.
        """
        self.setVisible(not self.isVisible())

    def make_visible(self, wdg):
        """
        Scroll to make wdg visible. We use a Qtimer because we have to wait
        that all widgets are shown, so that their size is determined, before
        calling ensureVisible.
        """
        def make_vis():
            # print("Pan!")
            self.main_window.ensureWidgetVisible(wdg, ymargin=100)
        QTimer.singleShot(0, make_vis)
        # self.main_window.ensureWidgetVisible(wdg)

    @Slot()
    def highlight(self, math_object, yes):
        """
        Highlight all instances of math_widgets  in the ProofTreeWidget which
        are related to math_object.
        """
        self.main_block.recursively_highlight(math_object, yes)

    def highlight_from_math_wdg(self, math_object, yes):
        self.highlight(math_object, yes)

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


def main():
    app = QApplication()
    # label_bf.setStyleSheet("{font-weight: bold;}")
    # pcw = HorizontalArrow(100)
    # pcw = SubstitutionArrow("f(x)=y mais aussi TOTO le clown")
    pcw = OperatorContextWidget(["y dans A"], "f(x)=y et aussi toto",
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

