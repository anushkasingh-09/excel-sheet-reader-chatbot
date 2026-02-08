# Investment Data Analysis System

A comprehensive system for processing Excel investment data and providing natural language query capabilities through a chatbot interface.

## 🎯 Features

- **Intelligent data processing** - Analyzes file structure to find the correct header row
- **Preserves all actual data** - Only replaces truly blank/empty cells with 0
- **Conservative cleaning approach** - Protects unusual but valid data
- **Natural language chatbot** - Ask questions in plain English
- **Web interface** - User-friendly browser-based access

## 📊 System Components

- `clean_and_update_headers.py` - Data processing script
- `chatbot.py` - Natural language to SQL chatbot
- `webapp.py` - Flask web application
- `templates/index.html` - Web interface template
- `investment_data_careful.db` - Processed database (5,251 records)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Process Data (if database doesn't exist)
```bash
python clean_and_update_headers.py
```

### 3. Run the Web Application
```bash
python webapp.py
```

Then open your browser to `http://localhost:5000`

### 4. Or Use the Chatbot Directly
```bash
python chatbot.py
```

## 📈 Data Statistics

- **Records**: 5,251 investment projects
- **Columns**: 125 data fields
- **Total Budget**: €33,603,532
- **Companies**: 7 (SMP: 3,286, Other: 653, SMRC: 645, MDRSC: 587, etc.)
- **Regions**: 7 (Germany & EE, Iberica, China, LATAM, Mexico, USA, France & North Africa)
- **Customers**: 84 unique customers

## 🤖 Chatbot Usage

The chatbot supports natural language queries:

```python
from chatbot import InvestmentDataChatbot

# Initialize chatbot
chatbot = InvestmentDataChatbot('investment_data_careful.db')

# Ask questions in natural language
chatbot.ask_question("How many projects are there?")
chatbot.ask_question("Count projects by company")
chatbot.ask_question("What is the total budget?")
chatbot.ask_question("List all regions")
```

### Sample Questions
- "How many projects are there?"
- "Count projects by company"
- "Show all companies"
- "List all regions"
- "What is the total budget?"
- "Show projects by region"
- "Count projects by customer"
- "What is the average budget by company?"
- "Show the project with maximum budget"

## 📋 Requirements

Required packages:
- pandas==2.0.3
- numpy==1.24.3
- flask==2.3.2
- openpyxl==3.1.2

Install with:
```bash
pip install -r requirements.txt
```

## 🛠️ File Structure

```
├── Anushka - Intern Assignment-Data.xlsx  # Input data file
├── Anushka - Intern Assignment-Data.csv   # Input data file (CSV)
├── clean_and_update_headers.py            # Data processing script
├── chatbot.py                             # Chatbot engine
├── webapp.py                              # Web application
├── templates/
│   └── index.html                         # Web interface
├── investment_data_careful.db             # Processed database
├── requirements.txt                       # Python dependencies
└── README.md                              # Documentation
```

## 🎯 How It Works

1. **Data Processing** - `clean_and_update_headers.py` reads the Excel file, intelligently detects headers, cleans data, and creates a SQLite database
2. **Chatbot Engine** - `chatbot.py` converts natural language questions to SQL queries
3. **Web Interface** - `webapp.py` provides a Flask-based web UI for easy interaction

## 📄 License

This project is created for educational/internship purposes.

## 📧 Contact

For questions or issues, please refer to the project documentation or contact the development team.