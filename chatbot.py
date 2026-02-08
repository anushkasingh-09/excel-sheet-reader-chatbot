import sqlite3
import pandas as pd
import re
from typing import List, Dict, Any

class InvestmentDataChatbot:
    def __init__(self, db_path: str = 'investment_data_careful.db'):
        """
        Initialize the chatbot with database connection
        """
        self.db_path = db_path
        self.table_name = 'investment_projects'
        self.schema = self._get_table_schema()
        
    def _get_table_schema(self) -> Dict[str, str]:
        """
        Get the table schema for better query generation
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()
            
            schema = {}
            for col in columns:
                schema[col[1].lower()] = col[2]  # column_name: data_type
            
            conn.close()
            return schema
            
        except Exception as e:
            print(f"Error getting schema: {e}")
            return {}
    
    def _natural_language_to_sql(self, question: str) -> str:
        """
        Convert natural language question to SQL query
        This is a simplified NLP to SQL converter
        """
        question = question.lower().strip()
        
        # Common query patterns
        if any(word in question for word in ['count', 'how many', 'number of']):
            return self._generate_count_query(question)
        elif any(word in question for word in ['total', 'sum', 'amount']):
            return self._generate_sum_query(question)
        elif any(word in question for word in ['average', 'avg', 'mean']):
            return self._generate_avg_query(question)
        elif any(word in question for word in ['list', 'show', 'display', 'get']):
            return self._generate_select_query(question)
        elif any(word in question for word in ['maximum', 'max', 'highest', 'largest']):
            return self._generate_max_query(question)
        elif any(word in question for word in ['minimum', 'min', 'lowest', 'smallest']):
            return self._generate_min_query(question)
        else:
            return self._generate_general_query(question)
    
    def _generate_count_query(self, question: str) -> str:
        """Generate COUNT queries"""
        base_query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        
        if 'company' in question:
            if 'by company' in question or 'per company' in question:
                return f"SELECT company, COUNT(*) as count FROM {self.table_name} WHERE company IS NOT NULL AND company != '0' AND company != '' GROUP BY company ORDER BY count DESC"
            else:
                return f"{base_query} WHERE company IS NOT NULL AND company != '0' AND company != ''"
        
        elif 'region' in question:
            if 'by region' in question or 'per region' in question:
                return f"SELECT region, COUNT(*) as count FROM {self.table_name} WHERE region IS NOT NULL AND region != '0' AND region != '' GROUP BY region ORDER BY count DESC"
            else:
                return f"{base_query} WHERE region IS NOT NULL AND region != '0' AND region != ''"
        
        elif 'project' in question:
            return base_query
        
        elif 'customer' in question:
            if 'by customer' in question:
                return f"SELECT customer, COUNT(*) as count FROM {self.table_name} WHERE customer IS NOT NULL AND customer != '0' AND customer != '' GROUP BY customer ORDER BY count DESC"
            else:
                return f"{base_query} WHERE customer IS NOT NULL AND customer != '0' AND customer != ''"
        
        return base_query
    
    def _generate_sum_query(self, question: str) -> str:
        """Generate SUM queries"""
        # Look for budget-related columns
        budget_columns = [col for col in self.schema.keys() if 'budget' in col or 'total' in col or 'value' in col]
        
        if budget_columns:
            main_budget_col = budget_columns[0]  # Use first budget column found
            
            if 'by company' in question:
                return f"SELECT company, SUM(CAST({main_budget_col} AS REAL)) as total FROM {self.table_name} WHERE company IS NOT NULL AND company != '0' AND company != '' GROUP BY company ORDER BY total DESC"
            elif 'by region' in question:
                return f"SELECT region, SUM(CAST({main_budget_col} AS REAL)) as total FROM {self.table_name} WHERE region IS NOT NULL AND region != '0' AND region != '' GROUP BY region ORDER BY total DESC"
            else:
                return f"SELECT SUM(CAST({main_budget_col} AS REAL)) as total FROM {self.table_name}"
        
        return f"SELECT COUNT(*) as count FROM {self.table_name}"
    
    def _generate_avg_query(self, question: str) -> str:
        """Generate AVG queries"""
        budget_columns = [col for col in self.schema.keys() if 'budget' in col or 'total' in col or 'value' in col]
        
        if budget_columns:
            main_budget_col = budget_columns[0]
            
            if 'by company' in question:
                return f"SELECT Company, AVG(CAST({main_budget_col} AS REAL)) as average FROM {self.table_name} WHERE Company IS NOT NULL AND Company != '0' GROUP BY Company ORDER BY average DESC"
            elif 'by region' in question:
                return f"SELECT Region, AVG(CAST({main_budget_col} AS REAL)) as average FROM {self.table_name} WHERE Region IS NOT NULL AND Region != '0' GROUP BY Region ORDER BY average DESC"
            else:
                return f"SELECT AVG(CAST({main_budget_col} AS REAL)) as average FROM {self.table_name}"
        
        return f"SELECT COUNT(*) as count FROM {self.table_name}"
    
    def _generate_select_query(self, question: str) -> str:
        """Generate SELECT queries"""
        if 'company' in question:
            return f"SELECT DISTINCT company FROM {self.table_name} WHERE company IS NOT NULL AND company != '0' AND company != '' ORDER BY company"
        elif 'region' in question:
            return f"SELECT DISTINCT region FROM {self.table_name} WHERE region IS NOT NULL AND region != '0' AND region != '' ORDER BY region"
        elif 'customer' in question:
            return f"SELECT DISTINCT customer FROM {self.table_name} WHERE customer IS NOT NULL AND customer != '0' AND customer != '' ORDER BY customer"
        elif 'plant' in question:
            return f"SELECT DISTINCT plant FROM {self.table_name} WHERE plant IS NOT NULL AND plant != '0' AND plant != '' ORDER BY plant"
        else:
            return f"SELECT * FROM {self.table_name} LIMIT 10"
    
    def _generate_max_query(self, question: str) -> str:
        """Generate MAX queries"""
        budget_columns = [col for col in self.schema.keys() if 'budget' in col or 'total' in col or 'value' in col]
        
        if budget_columns:
            main_budget_col = budget_columns[0]
            return f"SELECT *, MAX(CAST({main_budget_col} AS REAL)) as max_value FROM {self.table_name}"
        
        return f"SELECT * FROM {self.table_name} LIMIT 1"
    
    def _generate_min_query(self, question: str) -> str:
        """Generate MIN queries"""
        budget_columns = [col for col in self.schema.keys() if 'budget' in col or 'total' in col or 'value' in col]
        
        if budget_columns:
            main_budget_col = budget_columns[0]
            return f"SELECT *, MIN(CAST({main_budget_col} AS REAL)) as min_value FROM {self.table_name} WHERE CAST({main_budget_col} AS REAL) > 0"
        
        return f"SELECT * FROM {self.table_name} LIMIT 1"
    
    def _generate_general_query(self, question: str) -> str:
        """Generate general queries for unmatched patterns"""
        return f"SELECT * FROM {self.table_name} LIMIT 10"
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame
        """
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Main method to ask questions in natural language
        """
        print(f"\nQuestion: {question}")
        print("-" * 50)
        
        # Convert to SQL
        sql_query = self._natural_language_to_sql(question)
        print(f"Generated SQL: {sql_query}")
        print("-" * 50)
        
        # Execute query
        result_df = self.execute_query(sql_query)
        
        if not result_df.empty:
            print("Results:")
            print(result_df.to_string(index=False))
            
            return {
                'question': question,
                'sql_query': sql_query,
                'results': result_df,
                'success': True
            }
        else:
            print("No results found or query failed.")
            return {
                'question': question,
                'sql_query': sql_query,
                'results': pd.DataFrame(),
                'success': False
            }
    
    def show_available_columns(self):
        """
        Show available columns for reference
        """
        print("\nAvailable columns in the database:")
        print("-" * 50)
        for i, col in enumerate(self.schema.keys(), 1):
            print(f"{i:2d}. {col}")
    
    def interactive_mode(self):
        """
        Start interactive chatbot mode
        """
        print("Investment Data Chatbot")
        print("=" * 50)
        print("Ask questions about the investment data in natural language!")
        print("Type 'help' for sample questions, 'columns' to see available data, or 'quit' to exit.")
        print()
        
        while True:
            question = input("Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            elif question.lower() == 'help':
                self._show_help()
            elif question.lower() == 'columns':
                self.show_available_columns()
            elif question:
                self.ask_question(question)
            else:
                print("Please enter a question or type 'help' for examples.")
    
    def _show_help(self):
        """
        Show sample questions
        """
        print("\nSample questions you can ask:")
        print("-" * 30)
        print("• How many projects are there?")
        print("• Count projects by company")
        print("• Show all companies")
        print("• List all regions")
        print("• What is the total budget?")
        print("• Show projects by region")
        print("• Count projects by customer")
        print("• What is the average budget by company?")
        print("• Show the project with maximum budget")
        print("• List all customers")
        print("• Show all plants")

def main():
    """
    Main function to run the chatbot
    """
    try:
        chatbot = InvestmentDataChatbot()
        
        # Test with some sample questions
        sample_questions = [
            "How many projects are there?",
            "Count projects by company",
            "Show all companies",
            "What is the total budget?",
            "List all regions"
        ]
        
        print("Testing chatbot with sample questions:")
        print("=" * 50)
        
        for question in sample_questions:
            chatbot.ask_question(question)
            print("\n")
        
        # Start interactive mode
        print("\nStarting interactive mode...")
        chatbot.interactive_mode()
        
    except Exception as e:
        print(f"Error starting chatbot: {e}")
        print("Make sure the database file exists. Run 'python read_excel_and_load_sql.py' first.")

if __name__ == "__main__":
    main()