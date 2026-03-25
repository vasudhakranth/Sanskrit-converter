**Sanskrit USR & JSON NLG Converter**
A full-stack web application designed to convert Sanskrit Universal Semantic Representation (USR) and JSON graph data into coherent, natural language paragraphs using the Google Gemini API.

This project features a modern, responsive React frontend and a lightweight Flask Python backend that processes semantic text natively in memory.

**Project Structure**
sanskrit-converter-project/
├── backend/                  # Python/Flask server and NLP scripts
│   ├── server.py             # Main Flask API gateway
│   ├── json_formatter.py     # USR to JSON parsing logic
│   ├── sanskrit_nlg.py       # JSON to Paragraph NLG generation
│   ├── sanskrit_usr_paragraph_nlg_inference.py # USR to Paragraph NLG
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React + Vite web interface
│   ├── src/
│   │   ├── App.jsx           # Main UI logic and API fetching
│   │   └── App.css           # Glassmorphic responsive styling
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js
├── .gitignore                # Git exclusion rules
└── README.md
Features
Three Conversion Modes: * USR-JSON: Parses raw USR semantic text into structured JSON.

JSON-NLG: Generates flowing paragraphs from structured JSON graph data.

USR-NLG: Direct end-to-end generation from USR text to natural language.

Multi-Language Support: Generates output in both English and Hindi.

In-Memory Processing: The web API processes all string data in memory for fast, zero-disk-I/O responses.

Batch Processing CLI: The Python scripts can also be run directly from the terminal to process entire folders of .usr or .json files.

Prerequisites
Before you begin, ensure you have the following installed:

Node.js (v20 or higher)

Python (v3.8 or higher)

Google Gemini API Key

Important API Key Setup: > Before running the backend, you must add your active Google Gemini API key. Open backend/sanskrit_nlg.py and backend/sanskrit_usr_paragraph_nlg_inference.py and replace the placeholder API_KEY string with your actual key.

Installation & Setup
You will need to set up the backend and frontend separately.

1. Backend Setup (Flask & Python)
Open a terminal, navigate to the backend folder, and set up your virtual environment:

Bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
2. Frontend Setup (React & Vite)
Open a new, separate terminal, navigate to the frontend folder, and install the Node packages:

**Bash**
cd frontend
npm install
Running the Application
To run the full-stack application, you must keep both servers running simultaneously in two separate terminal windows.

Terminal 1 (Backend):

**Bash**
cd backend
# Ensure venv is activated
python server.py
# Server will start on http://localhost:5000
Terminal 2 (Frontend):

**Bash**
cd frontend
npm run dev
# App will start on http://localhost:5173
Open your browser and navigate to http://localhost:5173 to use the interface.

CLI Usage (Terminal Batch Processing)
The Python scripts are designed to be flexible. If you want to process hundreds of files without using the web UI, you can run them directly via the command line.

Example: Converting a folder of USR files to JSON

**Bash**
cd backend
python json_formatter.py
Example: Generating paragraphs from a folder of JSON files

**Bash**
cd backend
python sanskrit_nlg.py ./test_input -o ./output -l hindi
