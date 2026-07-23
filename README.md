*AI-Powered Business Intelligence System*

A full-stack BI web application built from scratch that lets users upload data files and get instant AI-powered insights.

## Features
- Upload CSV, DOCX, and SQL files via drag and drop
- Auto-generates bar, line, and pie charts
- Click any bar to drill down into raw data
- AI-written plain-English insights powered by Llama via Groq API
- Download chart + insights as a PDF report
- Clean dashboard UI with sidebar navigation

## Tech Stack
**Backend:** Python, FastAPI, SQLAlchemy, SQLite, pandas, python-docx, Groq API

**Frontend:** HTML, CSS, JavaScript, Chart.js, jsPDF

## How to Run
1. Clone the repository
2. Go into the backend folder:
   cd backend
3. Create a virtual environment:
   python -m venv venv
   venv\Scripts\activate
4. Install dependencies:
   pip install -r requirements.txt
5. Create a .env file with your Groq API key:
   GROQ_API_KEY=your-key-here
6. Start the server:
   uvicorn main:app --reload
7. Open frontend/index.html in your browser
| CSV | pandas DataFrame analysis |
| DOCX | Table extraction or word frequency |
| SQL | In-memory SQLite execution |
