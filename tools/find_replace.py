"""
A dev tool to replace old metadata format by toml in Lean files.
"""


import os


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
    else:
        if len(field_contents) == 1:
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
            else:
                new_metadata_lines.extend(new)
            if display:
                new_metadata_lines.extend(display)
            if settings:
                new_metadata_lines.extend(settings)
            new_contents.extend(new_metadata_lines)
            new_contents.append(line)
            in_metadata = False

            print("New metadata:")
            print('\n'.join(new_metadata_lines))

        elif in_metadata and not starts_with_blank(line):  # Metadata field name
            if field_name:  # Not the first field
                new = new_lines(field_name, field_contents)
                if change_name(field_name) == 'display':
                    display.extend(new)
                elif change_name(field_name) == 'settings':
                    settings.extend(new)
                else:
                    new_metadata_lines.extend(new)
            field_name = line.strip()
            field_contents = []
            if change_name(field_name) == "display":
                pass

        elif in_metadata and starts_with_blank(line):  # Metadata content
            striped_line = line.strip()
            if striped_line:
                field_contents.append(striped_line)

    return '\n'.join(new_contents)


def process_file(filepath):
    with open(filepath) as f:
        s = f.read()
        new_s = find_replace(s)
    with open(filepath, "w") as f:
        f.write(new_s)
    # print("------------------------------")
    # print(new_s)


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
    # file = "/home/leroux/PycharmProjects/dEAduction/src/deaduction/share/courses/snippets/arithmetique_bookproof_part2_chap4.lean"
    # process_file(filepath=file)
    # directory = "/home/leroux/PycharmProjects/dEAduction/src/deaduction/share/courses"
    directory = "/home/leroux/VSCProjects/dEAduction-lean/src/exercises_deaduction_synchro"
    brose(directory)

