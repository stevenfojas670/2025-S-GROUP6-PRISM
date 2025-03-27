"use client";
import react, { useEffect } from "react";
import { useState } from "react";
import Dropdown from "../components/Dropdown";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import FileDrop, { File } from "../components/Filedrop";

export default function StudentSubmissions() {
  // Dummy Data for Testing
  const classList = [
    { Label: "CS 301", id: 0 },
    { Label: "CS 405", id: 1 },
    { Label: "CS 477", id: 2 },
  ];
  const assignmentList = [
    { Label: "CS 301 AS 1", id: 0, classId: 0 },
    { Label: "CS 301 AS 2", id: 1, classId: 0 },
    { Label: "CS 301 AS 3", id: 2, classId: 0 },
    { Label: "CS 301 AS 4", id: 3, classId: 0 },
    { Label: "CS 405 AS 1", id: 0, classId: 1 },
    { Label: "CS 405 AS 2", id: 1, classId: 1 },
    { Label: "CS 405 AS 3", id: 2, classId: 1 },
    { Label: "CS 477 AS 1", id: 0, classId: 2 },
    { Label: "CS 477 AS 2", id: 1, classId: 2 },
    { Label: "CS 477 AS 3", id: 2, classId: 2 },
    { Label: "CS 477 AS 4", id: 3, classId: 2 },
    { Label: "CS 477 AS 5", id: 4, classId: 2 },
  ];

  // States so Hold Data Inputted by User
  const [submissionFile, setSubmissionFile] = useState<File[]>([]);
  const [selectedClass, setSelectedClass] = useState(-1);
  const [assignmentName, setAssignmentName] = useState("");

  // Functions to Save the Inputted Data
  const handleClassSelect = (item: number | -1) => {
    setSelectedClass(item);
  };
  const handleAssignmentSelect = (item: number | -1) => {
    setAssignmentName(
      assignmentList.filter(
        (assignment) =>
          assignment.classId == selectedClass && assignment.id == item
      )[0].Label
    );
  };

  // Function to Submit data to backend (Currently just outputs to the Console)
  const handleButtonClick = () => {
    console.log(selectedClass);
    console.log(assignmentName);
    console.log("Submission Files: ");
    submissionFile.forEach((file) => console.log(file.name));
  };

  useEffect(() => {
    document.title = "Student Submissions Portal";
  }, []);

  return (
    <Stack
      spacing={1}
      sx={{ justifyContent: "center", alignItems: "center", paddingTop: 2 }}
    >
      <Typography variant="h3" gutterBottom>
        Student Submissions Portal
      </Typography>
      {/* Class Selection Component */}
      <Typography variant="h6" gutterBottom>
        Please Select The Class For The Submissions.
      </Typography>
      <Dropdown
        isDisabled={false}
        items={classList}
        onSelectItem={handleClassSelect}
        dropdownLabel="Classes"
      />
      {/* Assignment Selection Component */}
      <Typography variant="h6" gutterBottom>
        Please Select The Assignment For The Submissions.
      </Typography>
      <Dropdown
        isDisabled={selectedClass == -1 ? true : false}
        items={assignmentList.filter(
          (assignment) => assignment.classId == selectedClass
        )}
        onSelectItem={handleAssignmentSelect}
        dropdownLabel="Assignment"
      />
      {/* Submission File Upload Component */}
      <Typography variant="h6" gutterBottom>
        Submit ZIP File of all the Submissions
      </Typography>
      <FileDrop files={submissionFile} setFileUploads={setSubmissionFile} />
      <Button
        variant="outlined"
        onClick={() => {
          handleButtonClick();
        }}
      >
        Upload Submissions
      </Button>
    </Stack>
  );
}
