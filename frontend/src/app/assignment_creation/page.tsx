"use client";
import Image from "next/image";
import styles from "./page.module.css";
import react from "react";
import { useState } from "react";
import Dropdown from "../components/Dropdown";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

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
    <div>
      <TextField
        required
        id="Assignment_Name"
        label="Assignment Name"
        variant="outlined"
        onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
          setAssignmentName(event.target.value);
        }}
      />
      <Dropdown
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
        Create assignmnet
      </Button>
    </div>
  );
}
