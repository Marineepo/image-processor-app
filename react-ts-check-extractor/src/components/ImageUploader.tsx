import React, { useState } from 'react';
import axios from 'axios';
import Dropzone from './Dropzone';

interface CheckData {
  name_address: string;
  pay_to_order_of: string | null;
  typed_amounts: number[];
  handwritten_amounts: number[];
  total_amount: number;
  routing_number: string | null;
  account_number: string | null;
}

const ImageUploader: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [checkData, setCheckData] = useState<CheckData[] | null>(null);
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
        setCheckData(response.data.checks_data);
      })
      .catch(error => {
        console.error('Error uploading images:', error);
      });
  };

  const handleClear = () => {
    setFiles([]);
    setCheckData(null);
    setPreview(null);
  };

  return (
    <div>
      <Dropzone onDrop={handleDrop} preview={preview} />
      <div>
        <button onClick={handleSubmit} disabled={files.length === 0}>Submit</button>
        <button onClick={handleClear} disabled={files.length === 0}>Clear</button>
      </div>
      {checkData && checkData.map((check, index) => (
        <div key={index}>
          <p><strong>Name & Address:</strong> {check.name_address || 'N/A'}</p>
          <p><strong>Pay to the Order of:</strong> {check.pay_to_order_of || 'N/A'}</p>
          <p><strong>Typed Amounts:</strong> {check.typed_amounts?.length > 0 ? check.typed_amounts.join(', ') : 'N/A'}</p>
          <p><strong>Handwritten Amounts:</strong> {check.handwritten_amounts?.length > 0 ? check.handwritten_amounts.join(', ') : 'N/A'}</p>
          <p><strong>Total Amount:</strong> ${check.total_amount?.toFixed(2) || 'N/A'}</p>
          <p><strong>Routing Number:</strong> {check.routing_number || 'N/A'}</p>
          <p><strong>Account Number:</strong> {check.account_number || 'N/A'}</p>
        </div>
      ))}
    </div>
  );
};

export default ImageUploader;