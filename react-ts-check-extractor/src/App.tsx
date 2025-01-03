import React from 'react';
import ImageUploader from './components/ImageUploader';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <div className="App">
        <h1>Check Image Uploader</h1>
        <ImageUploader />
      </div>
    </ErrorBoundary>
  );
};

export default App;