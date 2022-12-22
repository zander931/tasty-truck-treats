import re
from parse_raw_python import read_file, create_json


def split_on_new_line(content: str) -> list:
    """Splits the input text file on a new line

    Parameters
    ----------
    content : str
        contents of text

    Returns
    -------
    List[str]
        List of error messages
    """
    # split_on_error = r'\d+\serrors.and\s\d+\swarning.*\n\n'
    # split_content_on_error = re.split(split_on_error,content)
    file_path_regex = r'(?<!")(\.{1}\/.*js)(?!")'
    split_on_file_name = re.split(file_path_regex, content)

    return split_on_file_name


def obtain_errors(file_info: list) -> list:
    error_regex = r"\s*(\d+:\d+.*)"
    error_list = re.findall(error_regex, file_info)
    return error_list


def get_errors_warnings(error_message: str) -> dict:
    """Will get the number of error and warning messages

    Parameters
    ----------
    error_message : str
        A whole error message

    Returns
    -------
    dict
        dictionary containing the number of errors and the number of warnings
    """
    error_regex = r"(\d)\serror."
    warning_regex = r"(\d)\swarning."

    try:
        error_count = int(re.findall(error_regex, error_message)[0])  # get first digit of string
        warning_count = int(re.findall(warning_regex, error_message)[0])  # get first digit of string

    except IndexError:
        error_count = 0
        warning_count = 0

    return dict(errors=error_count, warnings=warning_count)


def count_statements(file_name: str, statements_list) -> int:
    """Will count the lines of code for the relevant file, ignoring comments, docstrings and blank lines

    Parameters
    ----------
    file_path : str
        The path of the file that will be counted

    Returns
    -------
    num_of_statements : str
        The lines of code count ignoring comments, docstrings and blank lines
    """

    try:
        with open(file_name) as file:
            content = file.read()

        num_of_statements = 0

        docstring = False
        for line in content.split("\n"):
            line = line.strip()

            if (
                line == ""
                or line.startswith("#")
                or docstring
                and not (line.startswith('"""') or line.startswith("'''"))
                or (line.startswith("'''") and line.endswith("'''") and len(line) > 3)
                or (line.startswith('"""') and line.endswith('"""') and len(line) > 3)
            ):
                continue

            # this is either a starting or ending docstring
            if line.startswith('"""') or line.startswith("'''"):
                docstring = not docstring
                continue

            num_of_statements += 1

        statements_list.append(num_of_statements)

    except FileNotFoundError:
        num_of_statements = sum(statements_list) / len(statements_list)

    return num_of_statements


def get_score(errors_warnings: dict, file_path: str, statements_list) -> float:
    """Will count the lines of code for the relevant file, ignoring comments, docstrings and blank lines

    Parameters
    ----------
    errors_warnings : dict
        A dictionary containing errors and warnings of the file

    Returns
    -------
    num_of_statements : str
        The lines of code count ignoring comments, docstrings and blank lines
    """

    statements = count_statements(file_path, statements_list)
    value = 100 - (
        (float(5 * errors_warnings.get("errors", 0) + errors_warnings.get("warnings", 0)) / statements) * 100
    )
    evaluation = max(0, value)

    return evaluation


def parse_split_content(split_content: list) -> dict:
    """Will parse a list of errors into a list of dictionaries containing
    key information about the errors

    Parameters
    ----------
    split_content : list
        List of individual error messages

    Returns
    -------
    dict
        dictionary containing key info about the file in question:
        - file_name: the file name
        - error_list: a list of the errors picked up on
        - score: a score (defined above) based on warnings and errors
        - warnings: number of warnings
        - errors: number of errors
    """
    files_dict = {"files": []}
    scores_list = []
    statements_list = []
    split_content = split_content[1:]

    for i in range(0, len(split_content), 2):
        file_path = split_content[i]
        error_list = obtain_errors(split_content[i + 1])
        errors_warnings = get_errors_warnings(split_content[i + 1])

        score = get_score(errors_warnings, file_path, statements_list)

        scores_list.append(score)

        combined_dictionary = dict(**{"file_name": file_path, "errors": error_list, "score": round(score, 1)})
        files_dict["files"].append(combined_dictionary)

    avg_score = round(sum(scores_list) / len(scores_list), 1)
    files_dict["average_score"] = avg_score
    return files_dict


if __name__ == "__main__":
    """Will read file from code_review_reports and parse into a json to be used in the airtable db."""
    content = read_file("code_review/report.txt")
    split_content = split_on_new_line(content)
    parsed_content = parse_split_content(split_content)
    create_json(parsed_content, "code_review/report.json")
