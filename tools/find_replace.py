"""
A dev tool to replace old metadata format by toml in Lean files.
"""


import os
import tomli_w


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


def starts_with_blank(s: str):
    return s.startswith(' ') or s.startswith('	')


def change_name(name: str) -> str:
    """
    e.g. PrettyName -> pretty_name
    Used to adapt keys of metadata to PEP8 format
    """
    if name.startswith('$'):  # macro: do not touch!!
        return name

    upper_case_alphabet = [chr(i) for i in range(65, 91)]
    for letter in upper_case_alphabet:
        name = name.replace(letter, '_' + letter.lower())
    # Finally remove the leading '_'
    if name.startswith('_'):
        name = name[1:]
    return name


def auto_step_dic_from_string(string: str):
    """
    Return a dic with data from string s in old fashioned style.
    Copied from AutoStep.
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
        elif item.startswith('target') or item.startswith('but'):
            target_selected = True

    if not button and not statement_name:
        return None

    selection = items[:button_or_statement_rank]
    try:
        selection.remove('target')
        selection.remove('but')
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
                calc_item.append(new_item)
            else:
                user_input.append(new_item)

    dic = {'selection':selection,
           'button': button,
           'statement': statement_name,
           'user_input': user_input,
           'target_selected': target_selected,
           'error_type': error_type,
           'error_msg': error_msg,
           'success_msg': success_msg}
    return {key: value for key, value in dic.items() if value}


def dic_seq_from_strings(strings: list[str]):
    """
    Return a list of dics from a list of strings.
    """
    return


def replace_auto_steps(auto_step_s: list[str]):
    """
    Turn a string corresponding to auto_steps old format to new format.
    All auto_step lines should be joined (by \\ or spaces)
    """
    auto_step_dics = [auto_step_dic_from_string(s) for s in auto_step_s]
    auto_step_dics = [s for s in auto_step_dics if s is not None]
    # print("Dics:")
    # print(auto_step_dics)
    toml_str = tomli_w.dumps({'auto_test': auto_step_dics})
    return toml_str


def format_(s):
    """
    Put quotation marks around strings.
    Replace "True" by "true", and so on.
    """
    if isinstance(s, list):
        return [format_(s_) for s_ in s]
    elif s in ("True", "true"):
        return 'true'
    elif s in ("False", "false"):
        return 'false'

    elif s.isdecimal():
        return s

    elif s.startswith('[') and s.endswith(']'):
        return s

    elif not s.startswith('"') and not s.startswith("'"):
        if not '"' in s:
            s = '"' + s + '"'
        elif not "'" in s:
            s = "'" + s + "'"
    return s


def new_display_line(line: str) -> str:
    key, value = line.split('-->')
    key = key.strip()
    value = value.strip()
    if value.startswith('(') and value.endswith(')'):
        value = '[' + value[1:-1] + ']'
    else:
        value = format_(value)
    new_line = key + ' = ' + value
    return new_line


def new_lines(field_name, field_contents) -> [str]:
    field_name = change_name(field_name)
    if field_name in ('display', 'settings'):
        lines = ['[' + field_name + ']']
        lines += list(map(new_display_line, field_contents))
    elif field_name == "auto_test":
        old_contents = " ".join(field_contents).split(",")  # join all lines
        # print("LINES:")
        lines = replace_auto_steps(old_contents)
        # print("LINES1")
        # print(lines)
        lines = lines.split('\n')
        # print("LINES2")
        # print(lines)
        # Remove blank lines and join selection
        stripped_lines = []
        complete_selection = ''
        for line in lines:
            if line == 'selection = [':
                complete_selection = line
            elif complete_selection:
                if  line == ']' and complete_selection.endswith(','):
                    complete_selection = complete_selection[:-1]
                if line != ', ':
                    line = line.strip()
                    complete_selection += ' ' + line
            elif line:
                stripped_lines.append(line)
            if complete_selection and line == ']':
                stripped_lines.append(complete_selection)
                complete_selection = ''
        # print("LINES3")
        # print(stripped_lines)
        lines = stripped_lines
        # print(new_content)
        # exit()
        # auto_steps = ['    "' + step.strip() + '",' for step in contents.split(
        #     ",")]
        # lines = [field_name + ' = ' + '['] + auto_steps + ['    ]']
    elif len(field_contents) == 1:
        lines = [field_name + ' = ' + format_(field_contents[0])]
    else:
        lines = [field_name + ' = ' + '"""'] \
                + field_contents \
                + ['"""']

    return lines


def find_replace(file_content:str) -> str:
    new_contents = []
    lines = file_content.splitlines()
    in_metadata = False
    idx = 0
    for line in lines:
        idx += 1

        if line.startswith("/- dEAduction"):  # Enter metadata
            new_contents.append(line)
            new_metadata_lines = []
            field_contents = []
            field_name = ""
            in_metadata = True
            settings = []
            display = []
            auto_test = []
            continue

        if not in_metadata:  # Just copy line
            new_contents.append(line)
            continue

        # From now on we are in metadata
        if line.startswith("-/"):  # Exit metadata
            new = new_lines(field_name, field_contents)
            if change_name(field_name) == 'display':
                display.extend(new)
            elif change_name(field_name) == 'settings':
                settings.extend(new)
            # elif change_name(field_name) == 'auto_test':
            #     auto_test.extend(new)
            else:
                new_metadata_lines.extend(new)
            if display:
                new_metadata_lines.extend(display)
            if settings:
                new_metadata_lines.extend(settings)
            # if auto_test:  # CLose auto_test
            #     auto_test.append(']')
            #     new_metadata_lines.extend(auto_test)
            new_contents.extend(new_metadata_lines)
            new_contents.append(line)
            in_metadata = False

            # print("New metadata:")
            # print('\n'.join(new_metadata_lines))

        elif in_metadata and not starts_with_blank(line):  # Metadata field name
            if field_name:  # Not the first field, close this field
                new = new_lines(field_name, field_contents)
                if change_name(field_name) == 'display':
                    display.extend(new)
                elif change_name(field_name) == 'settings':
                    settings.extend(new)
                # elif change_name(field_name) == 'auto_test':
                #     auto_test.extend(new)
                else:
                    new_metadata_lines.extend(new)
            # New field name:
            field_name = line.strip()
            field_contents = []
            if change_name(field_name) == "display":
                pass

        elif in_metadata and starts_with_blank(line):  # Metadata content
            striped_line = line.strip()
            # if field_name == "auto_test" and striped_line:
            #     pass  # TODO
                # striped_line = (',')
            if striped_line:
                field_contents.append(striped_line)

    return '\n'.join(new_contents)


def process_file(filepath):
    with open(filepath) as f:
        s = f.read()
        new_s = find_replace(s)
    # Uncomment the next 3 lines to actually modify the files:
    # new_filepath = filepath + 'new'  # Remove new to replace existing file
    # with open(new_filepath, "w") as f:
    #     f.write(new_s)
    print("------------------------------")
    print(new_s)


def brose(directory):
    excluded_list = ['Arithmetique.lean', 'Tutoriel.lean']
    excluded_list = []
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in files:
            if filename.endswith('.lean') and filename not in excluded_list:
                print(f"Processing {filename}")
                filepath = os.path.join(path, filename)
                process_file(filepath)


if __name__ == '__main__':
    # directory = "/home/leroux/PycharmProjects/dEAduction/snippets/find_replace"
    # dic = {'Toto': 'TOTO', 'est': 'is', 'idiot': 'a fool'}
    # find_replace(directory, dic)

    # file = "/home/leroux/PycharmProjects/dEAduction/src/deaduction/share/courses/Arithmetique.lean"
    # file = ("/home/leroux/PycharmProjects/dEAduction/src/deaduction/share"
    #         "/autotests_new/autotest_buttons/test_proof_buttons.lean")
    # process_file(filepath=file)
    # directory = "/home/leroux/PycharmProjects/dEAduction/src/deaduction/share/courses"
    # directory = "/home/leroux/VSCProjects/dEAduction-lean/src/exercises_deaduction_synchro"
    directory = ("/home/leroux/PycharmProjects/dEAduction/src/deaduction/share"
                 "/autotests_new/autotest_buttons")
    brose(directory)

