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
        self.setWindowTitle('Chemical Equipment Visualizer - Desktop App')
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('Chemical Equipment Parameter Visualizer')
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Tab 1: Upload & Analyze
        upload_tab = QWidget()
        upload_layout = QVBoxLayout()
        upload_tab.setLayout(upload_layout)
        
        # Upload section
        upload_group = QGroupBox("Upload CSV File")
        upload_group_layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 3px;")
        btn_browse = QPushButton("Browse CSV")
        btn_browse.clicked.connect(self.browse_file)
        btn_browse.setStyleSheet("padding: 8px 16px; background-color: #007bff; color: white; border-radius: 4px;")
        
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(btn_browse)
        upload_group_layout.addLayout(file_layout)
        
        # Upload button
        btn_upload = QPushButton("Upload & Analyze")
        btn_upload.clicked.connect(self.upload_file)
        btn_upload.setStyleSheet("padding: 10px; background-color: #28a745; color: white; font-weight: bold; border-radius: 4px;")
        upload_group_layout.addWidget(btn_upload)
        
        # PDF Button
        btn_pdf = QPushButton("📄 Generate PDF Report")
        btn_pdf.clicked.connect(self.generate_pdf)
        btn_pdf.setStyleSheet("padding: 10px; background-color: #dc3545; color: white; font-weight: bold; border-radius: 4px;")
        upload_group_layout.addWidget(btn_pdf)
        
        upload_group.setLayout(upload_group_layout)
        upload_layout.addWidget(upload_group)
        
        # Summary section
        self.summary_group = QGroupBox("Data Summary")
        self.summary_layout = QVBoxLayout()
        self.summary_group.setLayout(self.summary_layout)
        upload_layout.addWidget(self.summary_group)
        
        # Chart section
        self.chart_group = QGroupBox("Visualizations")
        chart_layout = QHBoxLayout()
        
        # Matplotlib figure for charts
        self.figure = plt.figure(figsize=(12, 5))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        self.chart_group.setLayout(chart_layout)
        upload_layout.addWidget(self.chart_group)
        
        # Tab 2: History
        history_tab = QWidget()
        history_layout = QVBoxLayout()
        history_tab.setLayout(history_layout)
        
        history_group = QGroupBox("Upload History (Last 5 Files)")
        history_group_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(['ID', 'File Name', 'Uploaded At'])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_group_layout.addWidget(self.history_table)
        
        btn_refresh = QPushButton("Refresh History")
        btn_refresh.clicked.connect(self.load_history)
        btn_refresh.setStyleSheet("padding: 8px; background-color: #17a2b8; color: white; border-radius: 4px;")
        history_group_layout.addWidget(btn_refresh)
        
        history_group.setLayout(history_group_layout)
        history_layout.addWidget(history_group)
        
        # Add tabs
        tabs.addTab(upload_tab, "Upload & Analyze")
        tabs.addTab(history_tab, "History")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        # Load initial history
        self.load_history()
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Selected: {file_path.split('/')[-1]}")
            self.statusBar().showMessage(f'File selected: {file_path}')
    
    def upload_file(self):
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, "Warning", "Please select a CSV file first")
            return
            
        try:
            # Upload file to backend
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/upload/", files=files)
                
            if response.status_code == 200:
                data = response.json()
                self.display_summary(data['summary'])
                self.plot_charts(data['summary'])
                self.load_history()
                QMessageBox.information(self, "Success", "File uploaded and analyzed successfully!")
                self.statusBar().showMessage('Upload successful')
            else:
                error_msg = response.json().get('error', 'Unknown error')
                QMessageBox.critical(self, "Error", f"Upload failed: {error_msg}")
                self.statusBar().showMessage('Upload failed')
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.statusBar().showMessage(f'Error: {str(e)}')
    
    def display_summary(self, summary):
        # Clear previous summary
        for i in reversed(range(self.summary_layout.count())): 
            widget = self.summary_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Create grid for summary stats
        grid = QGridLayout()
        
        stats = [
            ("Total Equipment", str(summary['total_count'])),
            ("Avg Flowrate", f"{summary['avg_flowrate']:.2f}"),
            ("Avg Pressure", f"{summary['avg_pressure']:.2f}"),
            ("Avg Temperature", f"{summary['avg_temperature']:.2f}"),
        ]
        
        for i, (label, value) in enumerate(stats):
            label_widget = QLabel(f"<b>{label}:</b>")
            label_widget.setStyleSheet("font-size: 14px; padding: 5px;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px; color: #007bff;")
            grid.addWidget(label_widget, i, 0)
            grid.addWidget(value_widget, i, 1)
        
        # Add type distribution
        type_label = QLabel("<b>Type Distribution:</b>")
        type_label.setStyleSheet("font-size: 14px; padding: 5px;")
        
        type_text = QTextEdit()
        type_text.setReadOnly(True)
        type_text.setMaximumHeight(100)
        distribution_text = "\n".join([f"{k}: {v}" for k, v in summary['type_distribution'].items()])
        type_text.setText(distribution_text)
        
        grid.addWidget(type_label, len(stats), 0)
        grid.addWidget(type_text, len(stats), 1)
        
        self.summary_layout.addLayout(grid)
        self.summary_group.show()
    
    def plot_charts(self, summary):
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        # Pie chart for type distribution
        types = list(summary['type_distribution'].keys())
        counts = list(summary['type_distribution'].values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
        ax1.pie(counts, labels=types, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.set_title('Equipment Type Distribution', fontweight='bold')
        
        # Bar chart for averages
        metrics = ['Flowrate', 'Pressure', 'Temperature']
        values = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]
        bars = ax2.bar(metrics, values, color=['#36A2EB', '#FF6384', '#FFCE56'])
        ax2.set_title('Average Values', fontweight='bold')
        ax2.set_ylabel('Value')
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        self.figure.tight_layout()
        self.canvas.draw()
        self.chart_group.show()
    
    def load_history(self):
        try:
            response = requests.get(f"{self.base_url}/history/")
            if response.status_code == 200:
                history = response.json()
                self.history_table.setRowCount(len(history))
                
                for row, item in enumerate(history):
                    # ID
                    id_item = QTableWidgetItem(str(item['id']))
                    id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                    self.history_table.setItem(row, 0, id_item)
                    
                    # File Name
                    name_item = QTableWidgetItem(item['file_name'])
                    name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                    self.history_table.setItem(row, 1, name_item)
                    
                    # Uploaded At
                    date_item = QTableWidgetItem(item['uploaded_at'])
                    date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                    self.history_table.setItem(row, 2, date_item)
                
                self.history_table.resizeColumnsToContents()
                self.statusBar().showMessage(f'Loaded {len(history)} history items')
            else:
                self.statusBar().showMessage('Failed to load history')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load history: {str(e)}")
            self.statusBar().showMessage('Error loading history')
    
    def generate_pdf(self):
        try:
            response = requests.get(f"{self.base_url}/pdf/")
            if response.status_code == 200:
                # Save PDF file
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save PDF Report", "", "PDF Files (*.pdf)"
                )
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, "Success", f"PDF saved to:\n{file_path}")
                    self.statusBar().showMessage('PDF generated successfully')
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF")
                self.statusBar().showMessage('PDF generation failed')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"PDF Error: {str(e)}")
            self.statusBar().showMessage(f'Error: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = CSVUploader()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()