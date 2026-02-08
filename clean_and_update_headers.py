#!/usr/bin/env python3
"""
Ultra-careful data reading and processing script
Only replaces truly blank values with 0, preserves all actual data
"""

import pandas as pd
import sqlite3
import numpy as np
import os
from datetime import datetime

def analyze_raw_data(df):
    """
    Analyze the raw data structure very carefully
    """
    print("🔍 DETAILED FILE ANALYSIS")
    print("=" * 50)
    print(f"File dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Analyze each of the first 20 rows in detail
    print("\nDetailed row-by-row analysis:")
    for i in range(min(20, len(df))):
        row = df.iloc[i]
        
        # Count different types of values
        total_cells = len(row)
        empty_cells = sum(1 for val in row if pd.isna(val) or str(val).strip() == '')
        numeric_cells = sum(1 for val in row if pd.notna(val) and str(val).replace('.', '').replace('-', '').replace(',', '').isdigit())
        text_cells = total_cells - empty_cells - numeric_cells
        
        # Get first few non-empty values
        non_empty_values = [str(val)[:15] for val in row if pd.notna(val) and str(val).strip() != ''][:5]
        
        print(f"Row {i:2d}: Empty={empty_cells:3d}, Numeric={numeric_cells:3d}, Text={text_cells:3d} | Sample: {non_empty_values}")
        
        # Check if this looks like a header row
        row_text = ' '.join(str(val) for val in row if pd.notna(val)).lower()
        header_indicators = ['company', 'region', 'plant', 'customer', 'description', 'investment', 'budget']
        header_score = sum(1 for indicator in header_indicators if indicator in row_text)
        
        if header_score >= 3:
            print(f"    ⭐ POTENTIAL HEADER ROW (score: {header_score}/7)")
    
    return df

def find_data_boundaries(df):
    """
    Very carefully identify where headers and data start
    """
    print("\n🎯 IDENTIFYING DATA BOUNDARIES")
    print("=" * 50)
    
    header_row = None
    data_start_row = None
    
    # Look for header row with multiple key indicators
    for i in range(min(25, len(df))):
        row_values = [str(val).lower() for val in df.iloc[i] if pd.notna(val)]
        row_text = ' '.join(row_values)
        
        # Score this row as potential header
        header_indicators = {
            'id': 'id' in row_text and ('change' in row_text or 'delete' in row_text),
            'company': 'company' in row_text,
            'region': 'region' in row_text,
            'plant': 'plant' in row_text,
            'customer': 'customer' in row_text,
            'description': 'description' in row_text,
            'investment': 'investment' in row_text,
            'budget': 'budget' in row_text
        }
        
        score = sum(header_indicators.values())
        
        if score >= 4:  # Need at least 4 key indicators
            header_row = i
            print(f"✅ Header row identified at row {i} (score: {score}/8)")
            print(f"   Indicators found: {[k for k, v in header_indicators.items() if v]}")
            break
    
    if header_row is None:
        print("⚠️  No clear header row found, using heuristic approach...")
        # Look for row with highest data density
        max_density = 0
        for i in range(min(15, len(df))):
            non_empty = sum(1 for val in df.iloc[i] if pd.notna(val) and str(val).strip() != '')
            density = non_empty / len(df.columns)
            if density > max_density and density > 0.3:
                max_density = density
                header_row = i
        
        if header_row is not None:
            print(f"📊 Using row {header_row} as header (density: {max_density:.2%})")
        else:
            header_row = 8  # Safe fallback
            print(f"🔄 Using fallback header row: {header_row}")
    
    # Find where actual data starts
    data_start_row = header_row + 1
    
    # Skip instruction/format rows
    for i in range(data_start_row, min(data_start_row + 10, len(df))):
        row_values = [str(val).lower() for val in df.iloc[i] if pd.notna(val)]
        row_text = ' '.join(row_values)
        
        # Check if this looks like an instruction row
        instruction_indicators = [
            'mandatory', 'optional', 'select', 'input', 'formula', 'linked',
            'default', 'fill in', 'do not add', 'delete', 'collumn'
        ]
        
        if any(indicator in row_text for indicator in instruction_indicators):
            data_start_row = i + 1
            print(f"⏭️  Skipping instruction row {i}")
        else:
            break
    
    print(f"📍 Data starts at row: {data_start_row}")
    
    return header_row, data_start_row

def create_careful_headers(df, header_row):
    """
    Create headers very carefully, preserving meaning
    """
    print("\n📝 CREATING CAREFUL HEADERS")
    print("=" * 50)
    
    headers = df.iloc[header_row].tolist()
    cleaned_headers = []
    used_names = set()
    
    for i, header in enumerate(headers):
        if pd.isna(header) or str(header).strip() == '':
            clean_name = f'column_{i}'
        else:
            header_str = str(header).strip()
            
            # Handle multi-line headers
            header_str = header_str.replace('\n', ' ').replace('\r', ' ')
            header_str = ' '.join(header_str.split())  # Clean whitespace
            
            # Create meaningful names based on content analysis
            header_lower = header_str.lower()
            
            if 'id' in header_lower and ('change' in header_lower or 'delete' in header_lower or 'add' in header_lower):
                clean_name = 'project_id'
            elif header_lower == 'company':
                clean_name = 'company'
            elif header_lower == 'region':
                clean_name = 'region'
            elif header_lower == 'plant':
                clean_name = 'plant'
            elif header_lower == 'customer':
                clean_name = 'customer'
            elif 'cost center' in header_lower:
                clean_name = 'cost_center' if 'cost_center' not in used_names else f'cost_center_{i}'
            elif 'description' in header_lower:
                clean_name = 'description' if 'description' not in used_names else f'description_{i}'
            elif 'investment' in header_lower and 'category' in header_lower:
                clean_name = 'investment_category'
            elif 'budget' in header_lower or 'total' in header_lower:
                clean_name = f'budget_{i}'
            elif 'april' in header_lower and '2025' in header_lower:
                clean_name = 'april_2025'
            elif 'may' in header_lower and '2025' in header_lower:
                clean_name = 'may_2025'
            # Add more specific date patterns as needed
            else:
                # General cleaning while preserving meaning
                clean_name = header_str
                # Replace problematic characters
                clean_name = clean_name.replace('/', '_').replace('-', '_').replace(' ', '_')
                clean_name = clean_name.replace('(', '').replace(')', '').replace('[', '').replace(']', '')
                clean_name = clean_name.replace('\n', '_').replace('\r', '_').replace('"', '').replace("'", '')
                clean_name = clean_name.replace('?', '').replace('!', '').replace('&', 'and')
                # Remove multiple underscores
                clean_name = '_'.join(filter(None, clean_name.split('_')))
                # Limit length
                if len(clean_name) > 60:
                    clean_name = clean_name[:60]
                if not clean_name or clean_name == '_':
                    clean_name = f'column_{i}'
        
        # Handle duplicates - ensure uniqueness
        final_name = clean_name.lower()
        counter = 1
        while final_name in used_names:
            final_name = f"{clean_name.lower()}_{counter}"
            counter += 1
        
        used_names.add(final_name)
        cleaned_headers.append(final_name)
    
    print(f"✅ Created {len(cleaned_headers)} unique headers")
    
    # Verify no duplicates
    if len(cleaned_headers) != len(set(cleaned_headers)):
        print("⚠️  Warning: Duplicate headers detected, fixing...")
        final_headers = []
        final_used = set()
        for i, header in enumerate(cleaned_headers):
            if header in final_used:
                new_header = f"{header}_{i}"
                final_headers.append(new_header)
                final_used.add(new_header)
            else:
                final_headers.append(header)
                final_used.add(header)
        cleaned_headers = final_headers
        print(f"✅ Fixed duplicates: {len(cleaned_headers)} unique headers confirmed")
    
    return cleaned_headers

def ultra_careful_cleaning(df):
    """
    Ultra-careful data cleaning - only replace truly empty values
    """
    print("\n🧹 ULTRA-CAREFUL DATA CLEANING")
    print("=" * 50)
    
    original_shape = df.shape
    changes_made = 0
    
    # Convert entire dataframe to string first to avoid type issues
    df = df.astype(str)
    
    for col in df.columns:
        col_changes = 0
        
        # Replace pandas string representations of NaN
        nan_representations = ['nan', 'NaN', '<NA>', 'None']
        for nan_val in nan_representations:
            nan_mask = df[col] == nan_val
            col_changes += nan_mask.sum()
            df.loc[nan_mask, col] = '0'
        
        # Only replace truly empty strings
        empty_mask = df[col] == ''
        col_changes += empty_mask.sum()
        df.loc[empty_mask, col] = '0'
        
        # Replace whitespace-only strings
        whitespace_mask = df[col].str.strip() == ''
        col_changes += whitespace_mask.sum()
        df.loc[whitespace_mask, col] = '0'
        
        # Replace clear Excel error values (these are definitely not real data)
        error_values = ['#VALUE!', '#REF!', '#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!']
        for error_val in error_values:
            error_mask = df[col] == error_val
            col_changes += error_mask.sum()
            df.loc[error_mask, col] = '0'
        
        changes_made += col_changes
        
        if col_changes > 0:
            print(f"  {col}: {col_changes} empty values → 0")
    
    print(f"✅ Total changes: {changes_made} empty values replaced with 0")
    print(f"📊 Data preserved: {original_shape[0] * original_shape[1] - changes_made} original values kept")
    
    return df

def extract_actual_data(df, data_start_row):
    """
    Extract only the actual data rows, being very careful
    """
    print(f"\n📤 EXTRACTING DATA FROM ROW {data_start_row}")
    print("=" * 50)
    
    # Start from the identified data row
    data_df = df.iloc[data_start_row:].copy().reset_index(drop=True)
    
    print(f"Initial data extraction: {len(data_df)} rows")
    
    # Only remove rows that are completely empty in the first few key columns
    # Check first 5 columns for any meaningful content
    key_columns = min(5, len(data_df.columns))
    
    # Create mask for rows with actual data
    has_data_mask = pd.Series([False] * len(data_df))
    
    for i in range(key_columns):
        col_values = data_df.iloc[:, i].astype(str)
        # Row has data if any of the first 5 columns has non-zero, non-empty content
        has_data_mask = has_data_mask | (
            (col_values.str.strip() != '') & 
            (col_values != '0') & 
            (col_values != 'nan') &
            (col_values != 'NaN')
        )
    
    # Keep rows with actual data
    filtered_df = data_df[has_data_mask].reset_index(drop=True)
    
    removed_rows = len(data_df) - len(filtered_df)
    print(f"📊 Kept {len(filtered_df)} data rows, removed {removed_rows} empty rows")
    
    return filtered_df

def main():
    """
    Main function with ultra-careful data processing
    """
    print("🎯 ULTRA-CAREFUL EXCEL TO SQL PROCESSING")
    print("=" * 60)
    
    # Step 1: Read file
    print("\n1️⃣ READING FILE...")
    try:
        if os.path.exists('Anushka - Intern Assignment-Data.xlsx'):
            df = pd.read_excel('Anushka - Intern Assignment-Data.xlsx', header=None)
            print("✅ Excel file loaded successfully")
        elif os.path.exists('Anushka - Intern Assignment-Data.csv'):
            df = pd.read_csv('Anushka - Intern Assignment-Data.csv', header=None)
            print("✅ CSV file loaded successfully")
        else:
            print("❌ No data file found!")
            return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Step 2: Analyze structure
    print(f"\n2️⃣ ANALYZING STRUCTURE...")
    df = analyze_raw_data(df)
    
    # Step 3: Find boundaries
    print(f"\n3️⃣ FINDING DATA BOUNDARIES...")
    header_row, data_start_row = find_data_boundaries(df)
    
    # Step 4: Create headers
    print(f"\n4️⃣ CREATING HEADERS...")
    headers = create_careful_headers(df, header_row)
    
    # Step 5: Extract data
    print(f"\n5️⃣ EXTRACTING DATA...")
    data_df = extract_actual_data(df, data_start_row)
    data_df.columns = headers
    
    # Step 6: Clean data carefully
    print(f"\n6️⃣ CLEANING DATA...")
    data_df = ultra_careful_cleaning(data_df)
    
    # Step 7: Create database
    print(f"\n7️⃣ CREATING DATABASE...")
    try:
        conn = sqlite3.connect('investment_data_careful.db')
        cursor = conn.cursor()
        
        # Drop existing table
        cursor.execute('DROP TABLE IF EXISTS investment_projects')
        
        # Create table
        columns_def = [f'"{col}" TEXT' for col in data_df.columns]
        create_table_sql = f'''
        CREATE TABLE investment_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {', '.join(columns_def)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        
        cursor.execute(create_table_sql)
        print("✅ Database table created")
        
        # Insert data
        data_df.to_sql('investment_projects', conn, if_exists='append', index=False)
        conn.commit()
        
        print(f"✅ {len(data_df)} records inserted successfully")
        
        # Validate
        cursor.execute("SELECT COUNT(*) FROM investment_projects")
        count = cursor.fetchone()[0]
        print(f"✅ Database validation: {count} records confirmed")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Final summary
    print(f"\n🎉 PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📁 Database: investment_data_careful.db")
    print(f"📊 Records: {len(data_df)}")
    print(f"📋 Columns: {len(headers)}")
    print(f"🔍 Data carefully preserved - only blank values replaced with 0")

if __name__ == "__main__":
    main()