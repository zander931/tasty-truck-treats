import json
import re
import os
import sys
from typing import Tuple


def check_empty_file(file_name: str):
    empty_file = os.stat(file_name).st_size == 0
    if empty_file:
        sys.exit(0)


def read_file(file_name: str) -> str:
    """Read the contents of the raw text file produced from pylint in github actions"""
    
    try:
        with open(file_name) as file:
            content = file.read()
            check_empty_file(file_name)

    except FileNotFoundError:
        print("File not found")
        sys.exit(0)

    return content


def obtain_files(content: str) -> list:
    """Obtain the .py files pylint has linted"""
    score_regex = r"(Your code has been rated at \d*\d.\d\d.\d\d)"
    list_files = re.split(score_regex, content)

    return list_files


def obtain_file_name(file: str) -> Tuple[list, str]:
    """Obtain the names of .py files"""
    file_name_regex = r"(.*py)\n"
    file_name = re.findall(file_name_regex, file)[0]
    return file_name


def obtain_scores(file: list) -> float:
    """Obtain the scores given by pylint for each file and convert to percentage"""
    try:
        score_line = re.findall(r"\d*\d.\d\d.\d\d", file)[0]
        score = round(float(score_line[0:4]) * 10, 1)

    except IndexError:
        score = 100

    return score


def obtain_errors(file_info: list) -> list:
    file_info = file_info.split("\n")
    discounted_strings = ("-", "Your code", ".", "*")
    error_list = []

    error_list = [error for error in file_info if not error.startswith(discounted_strings) and error != ""]

    return error_list


def prepare_dict(list_files: list) -> Tuple[dict, list]:
    """Prepare the dictionary with error and score data for each file"""
    scores_list = []
    files_dic: dict = {"files": []}
    list_files = list_files[:-1]  # remove unwanted element

    for i in range(0, len(list_files), 2):

        file_name = obtain_file_name(list_files[i])

        score = obtain_scores(list_files[i + 1])
        scores_list.append(score)

        errors = obtain_errors(list_files[i])

        files_dic["files"].append({"file_name": file_name, "errors": errors, "score": round(score, 1)})

    return files_dic, scores_list


def add_avg_score(files_dic: dict, scores_list: list) -> dict:
    """Calculate and add the average score of files to the dictionary"""
    avg_score = sum(scores_list) / len(scores_list)
    files_dic["average_score"] = round(avg_score, 1)
    return files_dic


def create_json(files_dic: dict, output_path: str):
    """Create a json from the dictionary"""
    with open(output_path, "w") as write_file:
        json.dump(files_dic, write_file, indent=1)


if __name__ == "__main__":
    """Takes a raw text output of pylint and converts to json format with a separate entry for each file"""
    content = read_file("code_review/report.txt")
    list_files = obtain_files(content)
    files_dic, scores_list = prepare_dict(list_files)
    files_dic = add_avg_score(files_dic, scores_list)
    create_json(files_dic, "code_review/report.json")
