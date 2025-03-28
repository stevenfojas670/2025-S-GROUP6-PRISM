/* 
    Variables: Class_Name, Section_Name, Display_Name
    Buttons: Menu, Student Comparison, Alerts, n boxes with Class_Names and Section_Names
    Links: Student Comparison Tool, Alerts, Each box
    Header takes Display_Name
*/

import React from "react";

/*
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Switch } from "react-router-dom";

import alerts from "./alerts";
import compareStudents from "./compareStudents";
*/

// basic button layout -> need to acces how many sections a teacher has, their name and the class name -> create that many buttons/div containers to show
// need an additional 2 buttons that are alwasy set for compare students and alerts -> respective buttons must be linked to their respective pages
// an alert icon appears if a section has been detected of cheating

// come back to header and replace the teacher name with the actual name assigned to the profile

// one div for the creating the sections

// the other div for the two main buttons at the top

// waiting to see how the team is going to approach linking the pages

function Dashboard() {
  return (
    <div>
      <div>
        <h1>"Hello, teacher name"</h1>
      </div>
      <div>
        <button>Compare Students</button>
        <button>Alerts</button>
      </div>
      <div>createSections();</div>
    </div>
  );
}

export default Dashboard;

// future code for when we begin to link the pages
/*
    <div>
            <Link to="/studentComparison">
                <button>Compare Students</button>
            </Link>
            <Link to="/about">
                <button>Alerts</button>
            </Link>
        </div>
            <div>
                createSections();
            </div>
        </div>
*/
