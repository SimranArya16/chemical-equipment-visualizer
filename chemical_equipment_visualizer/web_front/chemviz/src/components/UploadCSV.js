import { useState, useEffect } from "react";
import axios from "axios";
import { Pie, Bar } from "react-chartjs-2";
import { 
  Chart as ChartJS, 
  ArcElement, 
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip, 
  Legend
} from "chart.js";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function UploadCSV() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/history/");
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const uploadFile = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/upload/", 
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          }
        }
      );

      setSummary(res.data.summary);
      loadHistory();
      setFile(null);
      document.querySelector('input[type="file"]').value = "";
      
    } catch (err) {
      setError(err.response?.data?.error || "Upload failed. Check CSV format.");
    } finally {
      setLoading(false);
    }
  };

  // Create pie chart data
  const pieChartData = summary ? {
    labels: Object.keys(summary.type_distribution),
    datasets: [{
      data: Object.values(summary.type_distribution),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
      borderWidth: 1
    }]
  } : null;

  // Create bar chart data
  const barChartData = summary ? {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [{
      label: 'Average Values',
      data: [
        summary.avg_flowrate || 0,
        summary.avg_pressure || 0,
        summary.avg_temperature || 0
      ],
      backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56'],
      borderWidth: 1
    }]
  } : null;

  return (
    <div className="upload-container">
      <h2>Upload CSV File</h2>
      
      <div className="upload-section">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
          disabled={loading}
        />
        <button onClick={uploadFile} disabled={!file || loading}>
          {loading ? "Uploading..." : "Upload & Analyze"}
        </button>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="file-requirements">
          <p><strong>CSV Requirements:</strong></p>
          <ul>
            <li>Columns: Equipment Name, Type, Flowrate, Pressure, Temperature</li>
            <li>First row should be headers</li>
            <li>Numeric values for Flowrate, Pressure, Temperature</li>
          </ul>
        </div>
      </div>

      {summary && (
        <div className="summary-section">
          <h2>Analysis Summary</h2>
          
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Equipment</h3>
              <p className="stat-value">{summary.total_count}</p>
            </div>
            <div className="stat-card">
              <h3>Avg Flowrate</h3>
              <p className="stat-value">{summary.avg_flowrate.toFixed(2)}</p>
            </div>
            <div className="stat-card">
              <h3>Avg Pressure</h3>
              <p className="stat-value">{summary.avg_pressure.toFixed(2)}</p>
            </div>
            <div className="stat-card">
              <h3>Avg Temperature</h3>
              <p className="stat-value">{summary.avg_temperature.toFixed(2)}</p>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-container">
              <h3>Type Distribution</h3>
              {pieChartData && (
                <Pie 
                  data={pieChartData} 
                  options={{
                    plugins: {
                      legend: {
                        position: 'bottom'
                      }
                    }
                  }}
                />
              )}
            </div>
            <div className="chart-container">
              <h3>Average Values</h3>
              {barChartData && (
                <Bar 
                  data={barChartData} 
                  options={{
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }}
                />
              )}
            </div>
          </div>
        </div>
      )}

      <div className="history-section">
        <h2>Recent Uploads (Last 5)</h2>
        
        {history.length === 0 ? (
          <p className="no-history">No uploads yet. Upload a CSV to see history.</p>
        ) : (
          <div className="history-list">
            {history.map((item) => (
              <div key={item.id} className="history-item">
                <div>
                  <strong>{item.file_name}</strong>
                  <div style={{fontSize: '12px', color: '#666'}}>
                    {new Date(item.uploaded_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}