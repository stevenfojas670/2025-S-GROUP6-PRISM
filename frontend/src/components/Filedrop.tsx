import { IconButton, List, ListItem, Tooltip, Typography } from "@mui/material";
import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import ClearIcon from '@mui/icons-material/Clear';

// File Type to use where this component is used to keep the type the same
export type File = {
  name:string
}

// Expected paramaters for this component
type Props = {
  files: File[];
  setFileUploads: (newFiles: React.SetStateAction<File[]>) => void;
}

const FileDrop = ({files, setFileUploads}: Props) => {

  // Function to handle dropped files
  const onDrop = useCallback((acceptedFiles:File[]) => {
    setFileUploads((prevFiles) => [...prevFiles, ...acceptedFiles]);
  }, []);

  // Function to remove a file
  const removeFile = (fileName:string) => {
    setFileUploads((prevFiles) => prevFiles.filter((file:File) => file.name !== fileName));
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    multiple: true, // Enables multiple file uploads
  });

  return (
    <div>
      <div
        {...getRootProps()}
        style={{
          border: "2px dashed #cccccc",
          padding: "20px",
          cursor: "pointer",
        }}
      >
        <input {...getInputProps()} />
        <Typography variant="body1">Drag & drop files here, or click to select files</Typography>
      </div>
      <List sx={{ alignItems:"center", justifyContent:"center" }}>
        {files.map((file) => (
          <ListItem key={file.name}>
            <Typography variant="body2">{file.name}</Typography>
            <Tooltip title="Remove">
              <IconButton onClick={() => removeFile(file.name)}>
                <ClearIcon/>
                </IconButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
    </div>
  );
};

export default FileDrop;
