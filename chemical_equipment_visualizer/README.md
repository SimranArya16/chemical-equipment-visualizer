# Chemical Equipment Parameter Visualizer
A hybrid application that runs as both Web Application and Desktop Application for visualizing and analyzing chemical equipment data. Users can upload CSV files containing equipment parameters, and the system provides real-time analysis with charts and summary statistics.

git 

# Start Backend (Django)
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Server runs at: http://127.0.0.1:8000


# Start Web App (React)
cd web_front
npm install
npm start
# App opens at: http://localhost:3000

# Start Desktop App (PyQt5)
cd desktop_app
pip install -r requirements.txt
python main.py