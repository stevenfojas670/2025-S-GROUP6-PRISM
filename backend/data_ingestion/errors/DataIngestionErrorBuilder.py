"""Created by Daniel Levy, 3/17/2025.

This is a simple error builder class that can be used for PRISM's data
ingestion. Every builder will create a new error, and we can add the
error information we need based on what we're checking.
"""

import data_ingestion.errors.DataIngestionErrorFactory as ef


class DataIngestionErrorBuilder:
    """DataIngestionErrorBuilder is a builder class for constructing instances
    of DataIngestionError with a fluent interface. It allows setting various
    attributes of the error object step by step.

    Methods:
        __init__():
            Initializes the builder and creates a new instance of DataIngestionError
            using the DataIngestionErrorFactory.

        createError():
            Returns the constructed DataIngestionError object.

        addFileName(fileName):
            Sets the file name associated with the error.
            Args:
                fileName (str): The name of the file where the error occurred.
            Returns:
                DataIngestionErrorBuilder: The builder instance for method chaining.

        addLine(line):
            Sets the line number associated with the error.
            Args:
                line (int): The line number where the error occurred.
            Returns:
                DataIngestionErrorBuilder: The builder instance for method chaining.

        addMsg(msg):
            Sets the error message.
            Args:
                msg (str): The error message describing the issue.
            Returns:
                DataIngestionErrorBuilder: The builder instance for method chaining.
    """

    __error = None  # Copy of Error object

    def __init__(self):
        """Initializes the DataIngestionErrorBuilder instance by creating a new
        DataIngestionError object using the DataIngestionErrorFactory."""
        self.__error = ef.DataIngestionErrorFactory().createError()

    def createError(self):
        """Creates and returns the error object.

        Returns:
            object: The error object that has been built.
        """
        return self.__error

    def addFileName(self, fileName):
        """Sets the file name for the error being built.

        Args:
            fileName (str): The name of the file associated with the error.

        Returns:
            DataIngestionErrorBuilder: The current instance of the builder to allow method chaining.
        """
        self.__error.setFileName(fileName)
        return self

    def addLine(self, line):
        """Sets the line number for the error being built and returns the
        builder instance.

        Args:
            line (int): The line number associated with the error.

        Returns:
            DataIngestionErrorBuilder: The current instance of the builder to allow method chaining.
        """
        self.__error.setLine(line)
        return self

    def addMsg(self, msg):
        """Adds a message to the error object being built.

        Args:
            msg (str): The message to be set for the error.

        Returns:
            DataIngestionErrorBuilder: The current instance of the builder to allow method chaining.
        """
        self.__error.setMsg(msg)
        return self
