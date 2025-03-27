"use client";
import Image from "next/image";
import styles from "./page.module.css";
import react from "react";
import { useState } from "react";
import Dropdown from "../components/Dropdown";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

//todo: Just implement the text fields and button on page
export default function Home() {
  const [selectedClass, setSelectedClass] = useState(-1);
  const [assignmentName, setAssignmentName] = useState("");
  const list = [
    { Label: "CS 301", id: 0 },
    { Label: "CS 405", id: 1 },
    { Label: "CS 477", id: 2 },
  ];
  const handleItemSelect = (item: number | -1) => {
    setSelectedClass(item);
  };
  const handleButtonClick = () => {
    console.log(selectedClass);
    console.log(assignmentName);
  };
  return (
    //The TextField accepts and returns a string written by the user, The dropdown returns an id correlating to a specific
    // class, and the button will handle submitting the data to the database
    <Stack spacing={1} sx={{ justifyContent: "center", alignItems: "center" }}>
      <Typography variant="h6" gutterBottom>
        Please insert Assignment Name below.
      </Typography>
      <TextField
        required
        id="Assignment_Name"
        label="Assignment Name"
        variant="outlined"
        onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
          setAssignmentName(event.target.value);
        }}
      />
      <Typography variant="h6" gutterBottom>
        Please select which class the assignment is for below.
      </Typography>
      <Dropdown
        isDisabled={false}
        items={list}
        onSelectItem={handleItemSelect}
        dropdownLabel="Classes"
      />
      <Button
        variant="outlined"
        onClick={() => {
          handleButtonClick();
        }}
      >
        Create assignment
      </Button>
    </Stack>
  );
}
