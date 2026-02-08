from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import numpy as np
from chatbot import InvestmentDataChatbot
import json

app = Flask(__name__)

# Initialize chatbot
chatbot = InvestmentDataChatbot()

@app.route('/')
def index():
    """
    Main page with chat interface
    """
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    API endpoint to handle questions
    """
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get response from chatbot
        response = chatbot.ask_question(question)
        
        # Convert DataFrame to JSON if results exist
        if response['success'] and not response['results'].empty:
            # Replace NaN values with None (which becomes null in JSON)
            clean_df = response['results'].replace({np.nan: None})
            results_json = clean_df.to_dict('records')
            response['results_json'] = results_json
            response['results_html'] = response['results'].to_html(classes='table table-striped', index=False)
        else:
            response['results_json'] = []
            response['results_html'] = '<p>No results found.</p>'
        
        # Remove the DataFrame object for JSON serialization
        del response['results']
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/columns')
def get_columns():
    """
    Get available columns
    """
    try:
        return jsonify({'columns': list(chatbot.schema.keys())})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """
    Get database statistics
    """
    try:
        conn = sqlite3.connect(chatbot.db_path)
        
        # Get row count
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {chatbot.table_name}")
        row_count = cursor.fetchone()[0]
        
        # Get unique companies
        cursor.execute(f"SELECT COUNT(DISTINCT company) FROM {chatbot.table_name} WHERE company IS NOT NULL AND company != '0' AND company != ''")
        company_count = cursor.fetchone()[0]
        
        # Get unique regions
        cursor.execute(f"SELECT COUNT(DISTINCT region) FROM {chatbot.table_name} WHERE region IS NOT NULL AND region != '0' AND region != ''")
        region_count = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            'total_projects': row_count,
            'unique_companies': company_count,
            'unique_regions': region_count,
            'total_columns': len(chatbot.schema)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample_questions')
def get_sample_questions():
    """
    Get sample questions for the UI
    """
    sample_questions = [
        "How many projects are there?",
        "Count projects by company",
        "Show all companies",
        "List all regions",
        "What is the total budget?",
        "Show projects by region",
        "Count projects by customer",
        "What is the average budget by company?",
        "Show the project with maximum budget",
        "List all customers",
        "Show all plants",
        "Count projects by investment category"
    ]
    
    return jsonify({'questions': sample_questions})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)