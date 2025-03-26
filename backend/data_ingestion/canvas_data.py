import os
import pandas as pd

# Dummy manager to allow patching of get_or_create
class DummyManager:
    def get_or_create(self, **kwargs):
        # This dummy method returns a tuple like (instance, created)
        return None, True

# Dummy model classes to be used by CanvasDataIngestion
class Semester:
    objects = DummyManager()

class Class:
    objects = DummyManager()

class CanvasDataIngestion:
    def __init__(self, directory):
        self.directory = directory
        self.errors = []

    def extractData(self):
        # Reset errors on each extraction run
        self.errors = []
        # Iterate over each file in the given directory
        for filename in os.listdir(self.directory):
            # Check if file has a .csv extension
            if not filename.endswith(".csv"):
                self.errors.append(f"File {filename} is not a valid CSV file.")
                continue

            file_path = os.path.join(self.directory, filename)
            try:
                # Read the CSV file using pandas
                df = pd.read_csv(file_path)
                # Simulate data extraction logic
                # For example, call get_or_create on Semester and Class
                Semester.objects.get_or_create(name="Dummy Semester")
                Class.objects.get_or_create(name="Dummy Class")
                # (Optionally, add further processing logic here)
            except Exception as e:
                self.errors.append(str(e))