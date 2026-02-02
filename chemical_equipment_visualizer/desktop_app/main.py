import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class CSVUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_url = "http://localhost:8000/api"
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Chemical Equipment Visualizer')
        self.setGeometry(100, 100, 1200, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Title
        title = QLabel('Chemical Equipment Parameter Visualizer')
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Upload Section
        upload_group = QGroupBox("Upload CSV File")
        upload_layout = QHBoxLayout()
        
        # PDF Button (Left)
        pdf_layout = QVBoxLayout()
        pdf_btn = QPushButton("Generate PDF Report")
        pdf_btn.clicked.connect(self.generate_pdf)
        pdf_btn.setFixedHeight(45)
        pdf_btn.setStyleSheet("background: #dc3545; color: white; font-weight: bold;")
        pdf_layout.addWidget(pdf_btn)
        pdf_layout.addStretch()
        
        # Upload Controls (Right)
        controls_layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 8px; border: 1px solid #ccc;")
        browse_btn = QPushButton("Browse CSV")
        browse_btn.clicked.connect(self.browse_file)
        browse_btn.setStyleSheet("background: #007bff; color: white;")
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(browse_btn)
        controls_layout.addLayout(file_layout)
        
        # Upload button
        upload_btn = QPushButton("UPLOAD & ANALYZE")
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setFixedHeight(45)
        upload_btn.setStyleSheet("background: #28a745; color: white; font-weight: bold;")
        controls_layout.addWidget(upload_btn)
        
        # CSV requirements
        req_label = QLabel("CSV must contain: Equipment Name, Type, Flowrate, Pressure, Temperature")
        req_label.setStyleSheet("color: #666; font-size: 12px;")
        controls_layout.addWidget(req_label)
        
        # Combine layouts
        upload_layout.addLayout(pdf_layout, 1)
        upload_layout.addLayout(controls_layout, 3)
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Summary Section
        self.summary_group = QGroupBox("Data Summary")
        self.summary_layout = QHBoxLayout()
        self.summary_group.setLayout(self.summary_layout)
        layout.addWidget(self.summary_group)
        self.summary_group.hide()
        
        # Charts Section
        self.chart_group = QGroupBox("Visualizations")
        chart_layout = QHBoxLayout()
        self.figure = plt.figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        self.chart_group.setLayout(chart_layout)
        layout.addWidget(self.chart_group)
        self.chart_group.hide()
        
        # History Section
        history_group = QGroupBox("Recent Uploads")
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(120)
        history_layout.addWidget(self.history_list)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Status
        self.statusBar().showMessage('Ready')
        self.load_history()
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV (*.csv)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Selected: {file_path.split('/')[-1]}")
    
    def upload_file(self):
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, "Warning", "Please select a CSV file")
            return
            
        try:
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/upload/", files=files)
                
            if response.status_code == 200:
                data = response.json()
                self.display_summary(data['summary'])
                self.plot_charts(data['summary'])
                self.load_history()
                self.statusBar().showMessage('Upload successful')
            else:
                QMessageBox.critical(self, "Error", "Upload failed")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def display_summary(self, summary):
        for i in reversed(range(self.summary_layout.count())): 
            widget = self.summary_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        stats = [
            ("Total Equipment", str(summary['total_count']), "#007bff"),
            ("Avg Flowrate", f"{summary['avg_flowrate']:.1f}", "#28a745"),
            ("Avg Pressure", f"{summary['avg_pressure']:.1f}", "#ffc107"),
            ("Avg Temperature", f"{summary['avg_temperature']:.1f}", "#dc3545"),
        ]
        
        for title, value, color in stats:
            card = QFrame()
            card.setStyleSheet(f"background: {color}; border-radius: 4px; padding: 15px; margin: 5px;")
            card_layout = QVBoxLayout()
            
            title_label = QLabel(title)
            title_label.setStyleSheet("color: white; font-size: 12px;")
            title_label.setAlignment(Qt.AlignCenter)
            
            value_label = QLabel(value)
            value_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignCenter)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            card.setLayout(card_layout)
            self.summary_layout.addWidget(card)
        
        self.summary_group.show()
    
    def plot_charts(self, summary):
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        types = list(summary['type_distribution'].keys())
        counts = list(summary['type_distribution'].values())
        ax1.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Equipment Type Distribution')
        
        metrics = ['Flowrate', 'Pressure', 'Temperature']
        values = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]
        bars = ax2.bar(metrics, values, color=['#007bff', '#28a745', '#ffc107'])
        ax2.set_title('Average Values')
        ax2.set_ylabel('Value')
        
        self.figure.tight_layout()
        self.canvas.draw()
        self.chart_group.show()
    
    def load_history(self):
        try:
            response = requests.get(f"{self.base_url}/history/")
            if response.status_code == 200:
                history = response.json()
                self.history_list.clear()
                for item in history:
                    self.history_list.addItem(f"{item['file_name']} - {item['uploaded_at']}")
        except:
            pass
    
    def generate_pdf(self):
        try:
            response = requests.get(f"{self.base_url}/pdf/")
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF (*.pdf)")
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    self.statusBar().showMessage('PDF saved')
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = CSVUploader()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()