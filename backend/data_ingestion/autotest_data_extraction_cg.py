"""
Created by Eli Rosales, 4/22/2025.

This script extracts the autotest service from Codegrade and exports 
    - stdin.txt or stdin.json(if no text file is found)
    - Expected outputs
    - Execution command
    - Execution arguments
"""

# Neccessary Imports:
# codegrade: login and api interfacing
import codegrade

from extract_student_data_from_API import API_Data

# dotenv: import the dotenv vars for codegrade login
from dotenv import load_dotenv

# os: for loading the dotenv variables
import os

def main():
    """Login and populate the class attributes."""
    load_dotenv()
    client = codegrade.login(
        username=os.getenv("CG_USER"),
        password=os.getenv("CG_PASS"),
        tenant="University of Nevada, Las Vegas",
    )

    cg_data = API_Data(client)