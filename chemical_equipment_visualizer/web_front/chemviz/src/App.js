import React from 'react';
import './App.css';
import UploadCSV from './components/UploadCSV';
import PDFGenerator from './components/PDFGenerator';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
        <p className="subtitle">Hybrid Web + Desktop Application</p>
      </header>
      
      <main>
        <UploadCSV />
        <PDFGenerator />
      </main>
      
      <footer>
        <p>Intern Screening Task Project</p>
      </footer>
    </div>
  );
}

export default App;