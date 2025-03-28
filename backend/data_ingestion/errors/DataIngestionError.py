"""Created by Daniel Levy, 3/17/2025.

This is an Error class to handle any errors from PRISM's data ingestion.
The likelihood of errors is low, especially since we are trying to
automate it. However, it doesn't mean we should have a safety net in
case something unexpected happens.
"""

import json


class DataIngestionError:
    """DataIngestionError is a class designed to handle and represent errors
    encountered during the data ingestion process. It provides functionality to
    store error details and generate a JSON file containing all the errors for
    further processing or display.

    Attributes:
        __fileName (str): The name of the input file where the error was found.
        __line (str): The specific line in the file where the issue occurred.
        __msg (str): The error message to be output.

    Methods:
        __init__():
            Initializes a new instance of the DataIngestionError class with default values.

        createErrorJSON(fileName, errors):
            Static method that creates a JSON file containing all the errors provided.
            Args:
                fileName (str): The name of the output JSON file (without extension).
                errors (list): A list of DataIngestionError objects representing the errors.

        setFileName(fileName):
            Sets the name of the file where the error occurred.
            Args:
                fileName (str): The name of the file.

        setLine(line):
            Sets the specific line in the file where the error occurred.
            Args:
                line (str): The line number or description.

        setMsg(msg):
            Sets the error message.
            Args:
                msg (str): The error message.

        getFileName():
            Retrieves the name of the file where the error occurred.
            Returns:
                str: The name of the file.

        getLine():
            Retrieves the specific line in the file where the error occurred.
            Returns:
                str: The line number or description.

        getMsg():
            Retrieves the error message.
            Returns:
                str: The error message.
    """

    __fileName = None  # Input file error was found in
    __line = None  # Specific line in file with issue
    __msg = None  # Error message we should output"""

    def __init__(self):
        """Initializes a new instance of the DataIngestionError class.

        Attributes:
            __fileName (str): The name of the file where the error occurred.
            __line (str): The line number in the file where the error occurred.
            __msg (str): The error message describing the issue.
        """
        self.__fileName = ""
        self.__line = ""
        self.__msg = ""

    """
        If we encounter any errors, then this method will create a JSON
        file containing all the errors that can then be parsed/displayed
        to the user however we want.
    """

    @staticmethod
    def createErrorJSON(fileName, errors):
        """Creates a JSON file containing a list of error objects.

        Args:
            fileName (str): The name of the file (without extension) where the JSON data will be saved.
            errors (list): A list of error objects. Each object should have a `__dict__` attribute
                           that can be serialized into JSON format.

        Writes:
            A JSON file named `<fileName>.json` with the following structure:
            {
                "errors": [
                    { ... },  # Serialized representation of each error object
                    ...
                ]
            }
        """
        errorCount = len(errors)
        with open(f"{fileName}.json", "w") as oFile:
            oFile.write('{\n\t"errors": [\n')
            for i, e in enumerate(errors):
                json.dump(e.__dict__, oFile, indent=4)
                if i != errorCount - 1:
                    oFile.write(",\n")
            oFile.write("\t]\n")
            oFile.write("}\n")

    def setFileName(self, fileName):
        """Sets the name of the file associated with the data ingestion error.

        Args:
            fileName (str): The name of the file to be set.
        """
        self.__fileName = fileName

    def setLine(self, line):
        """Sets the line number associated with the error.

        Args:
            line (int): The line number to associate with the error.
        """
        self.__line = line

    def setMsg(self, msg):
        """Sets the error message for the DataIngestionError instance.

        Args:
            msg (str): The error message to be set.
        """
        self.__msg = msg

    def getFileName(self):
        """Retrieves the name of the file associated with the data ingestion
        error.

        Returns:
            str: The name of the file.
        """
        return self.__fileName

    def getLine(self):
        """Retrieves the line number associated with the error.

        Returns:
            int: The line number where the error occurred.
        """
        return self.__line

    def getMsg(self):
        """Retrieves the error message associated with the DataIngestionError.

        Returns:
            str: The error message stored in the private attribute __msg.
        """
        return self.__msg
