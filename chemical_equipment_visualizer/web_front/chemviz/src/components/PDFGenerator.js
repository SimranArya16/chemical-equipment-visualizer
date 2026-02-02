import React, { useState } from "react";
import axios from "axios";

export default function PDFGenerator() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generatePDF = async () => {
    setLoading(true);
    setError("");
    
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/pdf/", {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'equipment_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
    } catch (err) {
      setError("Failed to generate PDF");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      background: '#fff',
      borderRadius: '8px',
      padding: '20px',
      margin: '20px 0',
      borderLeft: '4px solid #dc3545'
    }}>
      <h3 style={{marginTop: '0', color: '#333'}}>PDF Report</h3>
      
      <button 
        onClick={generatePDF}
        disabled={loading}
        style={{
          width: '100%',
          padding: '12px',
          background: '#dc3545',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '16px'
        }}
      >
        {loading ? "Generating PDF..." : "Download PDF Report"}
      </button>
      
      {error && <div style={{color: '#dc3545', marginTop: '10px'}}>{error}</div>}
    </div>
  );
}