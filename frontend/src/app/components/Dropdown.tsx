"use client";
// Using Autocomplete from Material UI
// Documentation here: https://mui.com/material-ui/react-autocomplete/

import React, { ReactNode } from "react";
import { useState } from "react";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";

interface Props {
  items: { Label: string; id: number }[];
  onSelectItem: (item: number | null) => void;
}

export default function Dropdown({ items, onSelectItem }: Props) {
  return (
    <Autocomplete
      disablePortal
      //input data stuff below
      options={items}
      getOptionLabel={(items) => items.Label}
      sx={{ width: 300 }}
      onChange={(a, b) => {
        onSelectItem(b!.id);
      }}
      renderInput={(params) => (
        <TextField {...params} label="Name" color="primary" />
      )}
    />
  );
}
