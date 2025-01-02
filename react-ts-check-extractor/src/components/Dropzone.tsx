// import React, { useCallback, useState } from 'react';
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface DropzoneProps {
  onDrop: (acceptedFiles: File[]) => void;
}

const Dropzone: React.FC<DropzoneProps> = ({ onDrop }) => {
  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  return (
    <div {...getRootProps({ className: 'dropzone' })}>
      <input {...getInputProps()} />
      <p>Drag 'n' drop some files here, or click to select files</p>
    </div>
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