import React, { useState } from 'react';
import axios from 'axios';
import Dropzone from './Dropzone';

const ImageUploader: React.FC = () => {
  const [totalAmount, setTotalAmount] = useState<number | null>(null);

  const handleDrop = (acceptedFiles: File[]) => {
    const formData = new FormData();
    acceptedFiles.forEach(file => {
      formData.append('images', file);
    });

    axios.post('http://localhost:5000/upload', formData)
      .then(response => {
        setTotalAmount(response.data.total_amount);
      })
      .catch(error => {
        console.error('Error uploading images:', error);
      });
  };

  return (
    <div>
      <Dropzone onDrop={handleDrop} />
      {totalAmount !== null && <p>Total Amount: ${totalAmount.toFixed(2)}</p>}
    </div>
  );
};

export default ImageUploader;
// IF ABOVE ISN"T WORKING UNCOMMENT BELOW FOR TESTING -- NOTE
// const ImageUploader: React.FC = () => {
//     const [files, setFiles] = useState<File[]>([]);

//     const handleDrop = (acceptedFiles: File[]) => {
//         setFiles(acceptedFiles);
//     };

//     const handleSubmit = async () => {
//         const formData = new FormData();
//         files.forEach(file => {
//             formData.append('images', file);
//         });

//         const response = await fetch('/upload', {
//             method: 'POST',
//             body: formData,
//         });

//         const data = await response.json();
//         console.log('Total Amount:', data.total_amount);
//     };

//     return (
//         <div>
//             <Dropzone onDrop={handleDrop} />
//             <button onClick={handleSubmit} disabled={files.length === 0}>
//                 Submit
//             </button>
//         </div>
//     );
// };

// export default ImageUploader;