import React, { useState } from 'react';
import axios from 'axios';
import Dropzone from './Dropzone';

const ImageUploader: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [totalAmount, setTotalAmount] = useState<number | null>(null);
  const [senderNames, setSenderNames] = useState<string[]>([]);
  const [preview, setPreview] = useState<string | null>(null);

  const handleDrop = (acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
    if (acceptedFiles.length > 0) {
      setPreview(URL.createObjectURL(acceptedFiles[0]));
    } else {
      setPreview(null);
    }
  };

  const handleSubmit = () => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('images', file);
    });

    axios.post('http://127.0.0.1:5000/upload_check', formData)
      .then(response => {
        setTotalAmount(response.data.total_amount);
        setSenderNames(response.data.sender_names);
      })
      .catch(error => {
        console.error('Error uploading images:', error);
      });
  };

  const handleClear = () => {
    setFiles([]);
    setTotalAmount(null);
    setSenderNames([]);
    setPreview(null);
  };

  return (
    <div>
      <Dropzone onDrop={handleDrop} preview={preview} />
      <div>
        <button onClick={handleSubmit} disabled={files.length === 0}>Submit</button>
        <button onClick={handleClear} disabled={files.length === 0}>Clear</button>
      </div>
      {totalAmount !== null && (
        <div>
          <p>Total Amount: ${totalAmount.toFixed(2)}</p>
          <div>
            <p>Sender Names:</p>
            {senderNames.map((name, index) => (
              <p key={index}>{name}</p>
            ))}
          </div>
        </div>
      )}
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