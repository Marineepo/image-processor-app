// import React, { useCallback, useState } from 'react';
import React from 'react';
import { useDropzone } from 'react-dropzone';
import { StyledDropzone } from './Dropzone.styled';

interface DropzoneProps {
  onDrop: (acceptedFiles: File[]) => void;
  preview: string | null;
}

const Dropzone: React.FC<DropzoneProps> = ({ onDrop, preview }) => {
  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  return (
    <StyledDropzone {...getRootProps()}>
      <input {...getInputProps()} />
      {preview ? (
        <img src={preview} alt="Preview" style={{ maxWidth: '100%', maxHeight: '200px' }} />
      ) : (
        <p>Drag or Click to select files</p>
      )}
    </StyledDropzone>
  );
};

export default Dropzone;
// IF ABOVE ISN"T WORKING UNCOMMENT BELOW FOR TESTING -- NOTE
// const Dropzone: React.FC<{ onDrop: (files: File[]) => void }> = ({ onDrop }) => {
//     const [dragging, setDragging] = useState(false);

//     const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
//         event.preventDefault();
//         setDragging(true);
//     };

//     const handleDragLeave = () => {
//         setDragging(false);
//     };

//     const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
//         event.preventDefault();
//         setDragging(false);
//         const files = Array.from(event.dataTransfer.files);
//         onDrop(files);
//     };

//     return (
//         <div
//             onDragOver={handleDragOver}
//             onDragLeave={handleDragLeave}
//             onDrop={handleDrop}
//             style={{
//                 border: dragging ? '2px dashed #007bff' : '2px dashed #ccc',
//                 borderRadius: '5px',
//                 padding: '20px',
//                 textAlign: 'center',
//                 transition: 'border-color 0.3s',
//             }}
//         >
//             <p>Drag and drop your check image here, or click to select files.</p>
//         </div>
//     );
// };

// export default Dropzone;