"""
Created by Daniel Levy, 3/17/2025

This is a factory class to generate a new Error object. This will be
used for the Error builder in case we have multiple errors while
performing data ingestion (which is unlikely).
"""

import data_ingestion.errors.DataIngestionError as error


class DataIngestionErrorFactory:

    def createError(self):
        return error.DataIngestionError()
