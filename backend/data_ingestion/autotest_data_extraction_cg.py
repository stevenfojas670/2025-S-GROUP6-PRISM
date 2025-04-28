"""
Created by Eli Rosales, 4/28/2025.

This script extracts the autotest service from Codegrade and exports
    - stdin.txt or stdin.json(if no text file is found)
    - stdout.txt or stdout.json(if no text file is found)
    - Execution command
    - Execution arguments
"""

# Neccessary Imports:
# codegrade: login and api interfacing
import codegrade

# API_Data: needed for extracting autotest from api
from extract_student_data_from_API import API_Data

# dotenv: import the dotenv vars for codegrade login
from dotenv import load_dotenv

# os: for loading the dotenv variables and making file directories
import os


# sys: error outputs
import sys


def mkdir(dir_path):
    """Create a directory if it does not already exist."""
    try:
        os.makedirs(dir_path, exist_ok=True)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return False
    return True


"""
def find_filepath():.
    Return the filepath of the autotest files in local directory.
    # all files will be downloaded/created in the same folder directory called "autotest files"
    folder = "autotest files"
    return os.path.join(os.getcwd(), folder)
"""


def find_filepath(folder_string):
    """Over load function for adding file to a specified folder."""
    # all files will be downloaded/created in the same folder directory called "autotest files"
    folder = "autotest files"
    return os.path.join(os.getcwd(), folder, folder_string)


def extract_data(client, tests):
    """Extract the input files/fixtures uploaded for each assignment."""
    for tuple in tests:
        assi_name = tuple[0]
        test = tuple[1]
        test_id = test.id

        # Go through the fixtures and get the contents
        fixtures = test.fixtures
        i = 0
        for fixture in fixtures:
            fixture_id = int(fixture.id)
            curr_autotest = client.auto_test.get_fixture(
                auto_test_id=test_id, fixture_id=fixture_id
            )
            curr_autotest = curr_autotest.decode("utf-8")
            filename = fixture.name
            foldername = "fixtures"
            foldername = os.path.join(assi_name, foldername)
            filepath = find_filepath(foldername)
            if not mkdir(filepath):
                return
            filepath = os.path.join(filepath, filename)
            with open(filepath, "w") as f:
                f.write(str(curr_autotest))
            i += 0


def main():
    """Login and populate the class attributes."""
    load_dotenv()
    client = codegrade.login(
        username=os.getenv("CG_USER"),
        password=os.getenv("CG_PASS"),
        tenant="University of Nevada, Las Vegas",
    )
    cg_data = API_Data(client)
    cg_data.course = cg_data.get_course(client)
    cg_data.assignments = cg_data.get_assignments()
    assignments = cg_data.assignments

    tests = []
    for assi in assignments:
        try:
            # UNREADABLE
            if assi.auto_test_id:
                test = client.auto_test.get(auto_test_id=assi.auto_test_id)
                tests.append((assi.name, test))
        except Exception as e:
            print(str(e), file=sys.stderr)

    extract_data(client, tests)


if __name__ == "__main__":
    main()
