"""
##############################################
# auto_steps.py : provide the AutoStep class #
##############################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 04 2021 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

# from dataclasses import dataclass
# from typing import Union

import deaduction.pylib.config.vars as cvars

from deaduction.pylib.mathobj import MathObject
# import deaduction.pylib.actions.logic
# import deaduction.pylib.actions.magic
import logging

log = logging.getLogger(__name__)
global _

##############################################
# Lists of all instances of the Action class #
##############################################
# LOGIC_BUTTONS = deaduction.pylib.actions.logic.__actions__
# PROOF_BUTTONS = deaduction.pylib.actions.proofs.__actions__
# MAGIC_BUTTONS = deaduction.pylib.actions.magic.__actions__
# # e.g. key = action_and, value = corresponding instance of the class Action
#
# LOGIC_BUTTONS_SYMBOLS = [LOGIC_BUTTONS[key].symbol for key in LOGIC_BUTTONS]
# PROOF_BUTTONS_SYMBOLS = [PROOF_BUTTONS[key].symbol for key in PROOF_BUTTONS]
# MAGIC_BUTTONS_SYMBOLS = [MAGIC_BUTTONS[key].symbol for key in MAGIC_BUTTONS]



# BUTTONS_SYMBOLS = LOGIC_BUTTONS_SYMBOLS \
#                   + MAGIC_BUTTONS_SYMBOLS \
#                   + PROOF_BUTTONS_SYMBOLS


button_dict = {
               '∀': "forall",
               '∃': "exists",
               '→': "implies",
               '⇒': "implies",
               '∧': "and",
               '∨': "or",
               'prove∀': "prove_forall",
               'prove∃': "prove_exists",
               'prove→': "prove_implies",
               'prove⇒': "prove_implies",
               'prove∧': "prove_and",
               'prove∨': "prove_or",
               'use∀': "use_forall",
               'use∃': "use_exists",
               'use→': "use_implies",
               'use⇒': "use_implies",
               'use∧': "use_and",
               'use∨': "use_or",
               '↔': "iff",
               '⇔': "iff",
               '¬': "not",
               '=': "equal",
               "CQFD": "assumption",
               'compute': "assumption",
               '↦': "map",
               'proof': 'proof_methods',
               'new': 'new_object',
               'object': 'new_object',
               '+': 'sum',
                'simp': 'simplify',
                '>>': 'transitivity',
                'comm': 'commute',
                'assoc': 'associativity',
                'triangle': 'triangular_inequality',
               }


def recursive_display(user_input):
    """
    Recursively replace in user_input, which may be a list, a string or a
    MathObject,
    the MathObject by their display.
    """
    if isinstance(user_input, list):
        return [recursive_display(item) for item in user_input]
    elif isinstance(user_input, MathObject):
        return user_input.to_display(format_='lean')
    elif isinstance(user_input, int):
        return user_input
    else:  # Probably a string
        return str(user_input)


class UserAction:
    """
    A class for storing usr actions for one step.
    Button name is the action name (e.g. "action_and --> name = "and")
    Statement name is the end of the lean_name (e.g. definition.inclusion)
        so that lean_name.endswith(statement_name) is True.
    """
    selection = None  # [ContextMathObject] or [str]
    target_selected = None
    button_name = ""  # str
    statement = None  # Optional[Statement]
    _statement_name = ""  # str
    user_input = None  # Union[int, str]
    prove_or_use = ""  # "" / "prove" / "use"

    def __init__(self,
                 selection=None,
                 button_name=None,
                 statement=None,
                 statement_name=None,
                 user_input=None,
                 target_selected=False):
        if selection is None:
            selection = []
        if user_input is None:
            user_input = []
        self.selection = selection
        self.button_name = button_name
        self.statement = statement
        self._statement_name = statement_name
        if isinstance(user_input, str) and user_input.isdecimal():
            user_input = int(user_input)
        self.user_input = user_input
        self.target_selected = target_selected

    @classmethod
    def simple_action(cls, symbol):
        user_action = cls(button_name=symbol)
        return user_action

    @classmethod
    def from_proof_step(cls, proof_step):
        return proof_step.user_action
        # return cls(selection=proof_step.selection,
        #            button_name=proof_step.button_name,
        #            statement_name=proof_step.statement_lean_name,
        #            user_input=proof_step.user_input,
        #            target_selected=proof_step.target_selected)

    def __repr__(self) -> str:
        msg = f"UserAction with {len(self.selection)} selected objects, " \
              f"button name = {self.button_name}, statement name = " \
              f"{self.statement_name}, user input = {self.user_input}," \
              f"target selected = {self.target_selected}"
        return msg

    @property
    def statement_name(self):
        if self.statement:
            return self.statement.lean_name
        else:
            return self._statement_name

    def prove_or_use_button_name(self):
        name = self.button_name
        # if name not in ("forall", "exists", "implies", "and", "or"):
        #     return
        if not name:
            return None
        if self.prove_or_use and not (name.startswith("use_")
                                      or name.startswith("prove_")):
            name = self.prove_or_use + '_' + name
        return name

    def button_name_adapted_to_mode(self, mode=None):
        """
        Return the button name that corresponds to self.button_name adapted
        to mode : without prefix 'prove_' / 'use_' if the unified buttons are
        displayed, with prefix in the opposite case. Note that the returned
        name may not be adapted if self.prove_or_use is None.
        """

        name = self.button_name
        if not name:
            return ""

        if not mode:
            mode = cvars.get('logic.button_use_or_prove_mode')

        adapted_name = name
        if mode in ('display_switch', 'display_both'):
            adapted_name = self.prove_or_use_button_name()
        elif mode == 'display_unified':
            adapted_name = name.replace('use_', '')
            adapted_name = adapted_name.replace('prove_', '')

        return adapted_name


class AutoStep(UserAction):
    """
    A class to store one step of proof in deaduction, namely one user_action
    and deaduction's response. . Attributes error_msg,
    success_msg also allow to store deaduction's answer to the step; this is
    useful for debugging, e.g comparing actual answer to answer in a
    stored exercise.
    Data is stored in a string format, which is independent of the objects
    of the interface, which is crucial for saving.
    AutoStep may be created:
    - either from a raw string; this is a useful way to get them from
    metadata in the Lean file (see the exercise.refined_auto_steps property);
    - either from ProofStep; this is the way AutoStep are systematically
    computed and stored during exercise solving.
    AutoStep are used for testing.

    :attribute raw_string: A single string that contains all information.
    Other attributes may be computed from this string by the "from_string"
    method.

    :attribute selection: a list of string represented selected objects of
    the context, e.g. @P1, @O2 for property n°1, object n°2 of the context.

    :attribute button: A button symbol or equivalent (cf BUTTON_SYMBOLS,
    button_dict).

    :attribute statement: statement short name,
    e.g. definition.intersection_two_sets

    :attribute user_input: list of integers converted into string.
    """
    # Inputs:
    # selection:  [str]
    # button_name:     str
    # statement:  str
    # user_input: [str]

    raw_string: str = ""  # FIXME: obsolete

    # Response:
    error_type: int = 0  # 0 = WrongUserInput, 1 = FailedRequestError
    error_msg: str = ""
    success_msg: str = ""

    error_dic = {-1: '',
                 0: '',
                 1: 'WrongUserInput',
                 2: 'FailedRequestError',
                 3: 'Timeout',
                 4: 'UnicodeDecodeError',
                 5: 'No proof state',
                 6: 'File unchanged',
                 7: 'Action cancelled',
                 10: 'unknown error'}

    def __init__(self, selection, button_name, statement_name, user_input,
                 target_selected, raw_string,
                 error_type, error_msg, success_msg):

        UserAction.__init__(self, selection, button_name, None,
                            statement_name, user_input, target_selected)
        self.raw_string = raw_string
        self.error_type = error_type
        self.error_msg = error_msg
        self.success_msg = success_msg

    def __repr__(self):
        user_input = ("+".join([str(s) for s in self.user_input]) if
                      self.user_input else "")
        action = (self.button_name if self.button_name else
                  self.statement_name if self.statement_name else "??")
        msg = (self.error_msg if self.error_msg else self.success_msg if
               self.success_msg else "??")

        return user_input + " -> " + action + " : " + msg

    @classmethod
    def from_toml_data(cls, toml_data):
        """
        Return an AutoStep from toml data from the Lean file.
        User_input must be processed:
        - lists, coming from the calculator, are replaced by
        MathObject (either placeholders or from Lean code)
        - decimal strings are replaced by integers.
        """

        if toml_data.get('user_input'):
            user_input = [[MathObject.place_holder() if new_item == '_'
                           else MathObject.raw_lean_code(new_item)
                           for new_item in item]
                          if isinstance(item, list)
                          else int(item) if (isinstance(item, str)
                                             and item.isdecimal())
                          else item
                          for item in toml_data.get('user_input')]
        else:
            user_input = []
        selection = toml_data.get('selection')
        button_name = toml_data.get('button')
        if button_name == "and":
            button_name = "use_and" if selection else "prove_and"
        elif button_name == "or":
            button_name = "use_or" if selection else "prove_or"
        elif button_name == "implies":
            button_name = "use_implies" if selection else "prove_implies"
        elif button_name == "forall":
            button_name = "use_forall" if selection else "prove_forall"
        elif button_name == "exists":
            button_name = "use_exists" if selection else "prove_exists"
        # print(toml_data)

        error_msg = toml_data.get('error_msg')
        if not error_msg:
            error_msg = ""
        success_msg = toml_data.get('success_msg')
        if not success_msg:
            success_msg = ""
        return cls(selection=selection,
                   button_name=button_name,
                   statement_name=toml_data.get('statement'),
                   user_input=user_input,
                   target_selected=bool(toml_data.get('target_selected')),
                   raw_string='',
                   error_type=0,
                   error_msg=error_msg,
                   success_msg=success_msg)

    @classmethod
    def from_string(cls, string):
        """
        Analyze a string to extract an AutoStep instance, e.g.
        coming from a history or test file.

        The string should contain a button symbol (e.g. '∀')
        xor a statement name (e.g. 'definition.inclusion').
        Items are separated by spaces, and the last item should represents
        an action, i.e. a statement name or a button symbol.
         e.g. the following sequence of strings may be passed to the
        "from.string" method:
            ∀ success=Objet_x_ajouté_au_contexte,
            ∀ success=Objet_x'_ajouté_au_contexte,
            ⇒ success=propriété_H0_ajoutée_au_contexte,
            @P3 @P2 ⇒ success=propriété_H3_ajoutée_au_contexte,
            @P4 @P1 ⇒ success=propriété_H4_ajoutée_au_contexte,
            Goal!

        cf some history files for more elaborated examples.
        FIXME: should not be used anymore.
        """

        string.replace("\\n", " ")
        button = None
        statement_name = None
        button_or_statement_rank = None
        error_type = 0
        error_msg = ""
        success_msg = ""
        target_selected = None

        # Split at spaces and remove unnecessary spaces
        items = [item.strip() for item in string.split(' ') if item]
        for item in items:
            if item.startswith('definition') \
                    or item.startswith('theorem') \
                    or item.startswith('exercise'):
                statement_name = item
                button_or_statement_rank = items.index(item)
            # elif item in BUTTONS_SYMBOLS:
            #     button = item
            #     button_or_statement_rank = items.index(item)
            elif item in button_dict.values():
                button = item
                button_or_statement_rank = items.index(item)
            elif item in button_dict:
                button = button_dict[item]
                button_or_statement_rank = items.index(item)
            elif item in ('WrongUserInput', 'WUI'):
                error_type = 1
                items[items.index(item)] = ''  # item is not user_input
            elif item in ('FailedRequestError', 'FRE'):
                error_type = 2
                items[items.index(item)] = ''
            elif item.startswith('error='):
                error_msg = item[len('error='):].replace('_', ' ')
                items[items.index(item)] = ''
            elif item.startswith('e='):
                error_msg = item[len('e='):].replace('_', ' ')
                items[items.index(item)] = ''
            elif item.startswith('success='):
                success_msg = item[len('success='):].replace('_', ' ')
                items[items.index(item)] = ''
            elif item.startswith('s='):
                success_msg = item[len('s='):].replace('_', ' ')
                items[items.index(item)] = ''
            elif item.startswith('target') or item.startswith(_('target')):
                target_selected = True

        if not button and not statement_name:
            return None

        selection = items[:button_or_statement_rank]
        try:
            selection.remove('target')
            selection.remove(_('target'))
        except ValueError:
            pass

        # Remaining non-trivial items are user input
        # Some of them, between [ ], must be gathered in a single list item
        user_input = []
        calc_item = None
        for item in items[button_or_statement_rank+1:]:
            if not item:
                continue
            elif item == '[':  # Start a list item
                calc_item = []
                user_input.append(calc_item)
            elif item == ']':  # End a list item
                calc_item = None
            else:
                new_item = item.replace('__', ' ')
                if new_item.isdecimal() and calc_item is None:
                    new_item = int(new_item)
                if calc_item is not None:
                    # Encode in a MathObject
                    if new_item == '_':
                        new_item = MathObject.place_holder()
                    else:
                        new_item = MathObject.raw_lean_code(new_item)
                    calc_item.append(new_item)
                else:
                    user_input.append(new_item)

        # user_input = [item.replace('__', ' ')
        #               for item in items[button_or_statement_rank+1:] if item]
        # user_input = [int(item) if item.isdecimal() else item
        #               for item in user_input]

        return cls(selection, button, statement_name, user_input,
                   target_selected, string, error_type, error_msg, success_msg)

    @classmethod
    def from_proof_step(cls, proof_step, emw):
        """
        Convert proof_step to the corresponding AutoStep, e.g. for use as
        with auto_test. This method is supposed to be some kind of inverse to
        the from_string() classmethod.
        
        :param proof_step: instance of ProofStep 
        :param emw:         ExerciseMainWindow
        :return: 
        """

        user_action: UserAction = proof_step.user_action
        ###############################################
        # Store selected context obj in a list: [str] #
        ###############################################
        selection = []
        if user_action.selection:
            # log.debug("Analysing selection...")
            for math_object in user_action.selection:
                # log.debug(f"Searching {math_object.display_name}")
                # log.debug(f"in {[mo.display_name for mo in emw.objects]}")
                # log.debug(f"& {[mo.display_name for mo in emw.properties]}")
                if math_object in emw.objects:
                    item_str = "@O" + str(emw.objects.index(math_object)+1)
                elif math_object in emw.properties:
                    item_str = "@P" + str(emw.properties.index(math_object)+1)
                elif math_object.info.get("user_input"):
                    # Artificial object created from user_input:
                    #  do not save (will be retrieved from user_input).
                    item_str = None
                else:
                    item_str = math_object.display_name
                    log.debug(f"Object {item_str} not found")
                if item_str is not None:
                    selection.append(item_str)

        # Target selected ? Obsolete
        # if user_action.target_selected:
        #     selection.append("target")

        ####################################
        # Store action: button / statement #
        ####################################
        # Button: '∧', '∨', '¬', '⇒', '⇔', '∀', '∃', 'compute', 'CQFD',
        #         'proof_methods', 'new_objects', 'apply'
        button = user_action.prove_or_use_button_name()

        if button is None:
            button = ''

        # Statement: short Lean name
        statement = user_action.statement.lean_short_name \
            if user_action.statement else ''

        if not (button or statement):
            return None
        elif button and statement:
            log.warning("Bad ProofStep with both button AND statement")
            log.debug("Removing statement")
            statement = ''
        ######################################
        # Store user inputs: list of int/str #
        ######################################
        # Some user_input items are themselves lists
        #  (e.g. coming from Calculator)
        #  they are stored as '[ <item1> <item2> ... ]'
        # (1) Flatten list items
        # user_input = []
        # for item in user_action.user_input:
        #     if isinstance(item, list):
        #         user_input.append('[')
        #         user_input.extend(item)
        #         user_input.append(']')
        #     else:
        #         user_input.append(item)
        # # (2) Replace by str
        # user_input_str = [item.to_display(format_='lean')
        #                   if isinstance(item, MathObject)
        #                   else str(item) for item in user_input]
        # # (3) Replace spaces inside items by '__'
        # user_input_str = [item.replace(' ', '__')
        #                   for item in user_input_str]

        # error_msg = proof_step.error_msg
        # if error_msg:
        #     error_msg = error_msg.split(',')[0]  # No ',' allowed in AutoStep
        #     error_msg = 'error=' + error_msg.replace(' ', '_')
        # success_msg = proof_step.success_msg
        # if success_msg:
        #     success_msg = success_msg.split(',')[0]
        #     success_msg = 'success=' + success_msg.replace(' ', '_')

        # Computing string
        # string = ''
        # if selection:
        #     string = ' '.join(selection) + ' '
        # string += button + statement
        # if user_input_str:
        #     # Replace spaces by '__' to be able to retrieve items
        #     string += ' ' + ' '.join(user_input_str)
        # if proof_step.is_error():
        #     string += ' ' + AutoStep.error_dic[proof_step.error_type]
        #     string += ' ' + error_msg
        # if success_msg:
        #     string += ' ' + success_msg

        user_input = recursive_display(user_action.user_input)
        string = ""  # FIXME: obsolete
        target_selected = proof_step.target_selected

        return cls(selection, button, statement, user_input,
                   target_selected,
                   string, proof_step.error_type, proof_step.error_msg,
                   proof_step.success_msg)

    def toml_repr(self):
        """
        Return a dict to be saved into metadata in a Lean file by the
        toml.dumps() method.
        """

        statement_name = self.statement_name
        statement_name = '.'.join(statement_name.split('.')[-2:])
        total_dict = {'selection':  self.selection,
                     'target_selected': self.target_selected,
                     'button': self.button_name,
                     'statement': statement_name,
                     'user_input': self.user_input,
                     'error_msg': self.error_msg,
                     'success_msg': self.success_msg
                     }
        self_dict = {key:value for key, value in total_dict.items() if value}
        return self_dict


if __name__ == '__main__':
    pass
    # print(BUTTONS_SYMBOLS)
    # french result :
    # ['∧', '∨', '¬', '⇒', '⇔', '∀', '∃', 'Calculer', 'CQFD', 'Méthodes De
    # Preuve', 'Nouvel Objet', 'Appliquer']
    # Rather use english equivalents given in the above
    # button_dict dictionary.

