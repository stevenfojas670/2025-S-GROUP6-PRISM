"use client";
import Image from "next/image";
import styles from "./page.module.css";
import { useState, useEffect, useCallback } from "react";
import { FormControl, InputLabel, MenuItem, Select } from "@mui/material";
import Dropdown from "../components/Dropdown";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { easyFetch } from "@/utils/fetchWrapper";
import { RepeatOneSharp } from "@mui/icons-material";

//todo: Just implement the text fields and button on page
export default function StudentComparison() {
  //These are variables needed for work and their default values
  const [selectedClass, setSelectedClass] = useState<any[]>([]);
  const [assignmentName, setAssignmentName] = useState("");
  const [student, setStudents] = useState<any[]>([]);
  let studentList = [
    { Label: "null", id: -1 },
    { Label: "null2", id: -1 },
  ];
  let isDisabled = true;
  let rows = [
    { name: "Please select", similarity: 0 },
    { name: "Different students", similarity: 0 },
    { name: "From same class", similarity: 0 },
  ];
  let overall = 0;

  const fetchClasses = useCallback(async () => {
    const response = await fetch(`http://localhost:8000/api/course/classes`, {
      method: "get",
    });

    const data = await response.json();

    if (response.ok) {
      console.log("Fetched classes:", data);
      setSelectedClass(data);
    }
  }, []);

  const fetchStudents = useCallback(async (classInstanceId: string) => {
    const response = await fetch(
      `http://localhost:8000/api/course/enrollments?class_instance${classInstanceId}`,
      {
        method: "get",
      }
    );

    const data = await response.json();

    if (response.status === 200) {
      console.log("GOOD REQUEST");
      setStudents(data);
    }
  }, []);

  return (
    //The TextField accepts and returns a string written by the user, The dropdown returns an id correlating to a specific
    // class, and the button will handle submitting the data to the database
    <Stack spacing={1} sx={{ justifyContent: "center", alignItems: "center" }}>
      <FormControl fullWidth>
        <InputLabel id="demo-simple-select-label">Classes</InputLabel>
        <Select
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          label="Age"
          onOpen={fetchClasses}
        >
          {selectedClass?.map((value, index) => (
            <MenuItem key={index} value={value}>
              {value["name"]}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {/* <Dropdown isDisabled={false} items={list} dropdownLabel="Classes" /> */}
      <Stack direction="row">
        <Dropdown
          isDisabled={isDisabled}
          items={studentList}
          dropdownLabel="Select Student"
        />
        <Dropdown
          isDisabled={isDisabled}
          items={studentList}
          dropdownLabel="Select a different student"
        />
      </Stack>
      <Typography variant="h5" gutterBottom>
        {"Overall - " + overall}
      </Typography>
      <TableContainer component={Paper}>
        <Table
          sx={{ width: 650, justifyContent: "center" }}
          aria-label="simple table"
        >
          <TableHead>
            <TableRow>
              <TableCell>Student Name</TableCell>
              <TableCell>Relative</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow
                key={row.name}
                sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {row.name}
                </TableCell>
                <TableCell>{row.similarity}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  );
}
