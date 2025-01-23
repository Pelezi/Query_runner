import streamlit as st
import mysql.connector
import pandas as pd
import os
import re

config = {
    'user': 'phoenix',
    'password': 'comeia@10',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_'
}

# Function to connect to the MySQL database
def run_query(query, database):
    # Remove comments from the first 5 lines if they are present
    query_lines = query.split('\n')
    for i in range(min(5, len(query_lines))):
        if query_lines[i].strip().startswith('--'):
            query_lines[i] = query_lines[i].strip()[2:].strip()
    uncommented_query = '\n'.join(query_lines)
    
    config_ = config.copy()
    config_['database'] = config_['database'] + database
    conexao = mysql.connector.connect(**config_)
    cursor = conexao.cursor()
    
    try:
        cursor.execute(uncommented_query)
        conexao.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conexao.close()
        return f"{affected_rows} rows affected"
    except mysql.connector.Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

# Function to save the query to a SQL file
def save_query_to_file(query, database, path):
    # Extract the view name from the query
    match = re.search(r'VIEW\s+[\w\.]+\.(\w+)', query, re.IGNORECASE)
    if match:
        view_name = match.group(1)
    else:
        view_name = "unknown_view"
    
    # Comment the first 5 lines of the query if not already commented
    query_lines = query.split('\n')
    for i in range(min(5, len(query_lines))):
        if not query_lines[i].strip().startswith('--'):
            query_lines[i] = '-- ' + query_lines[i]
    commented_query = '\n'.join(query_lines)
    
    filename = f"{view_name}.sql"
    filepath = os.path.join(path + "\\" + database, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(commented_query)
    return filepath

# Streamlit app
def main():
    st.title("MySQL Query Modifier and Runner")
    
    query = st.text_area("Enter your MySQL query:")
    
    databases = ['aracaju', 'joao_pessoa', 'maceio', 'natal', 'noronha', 'recife', 'salvador']
    
    # Automatically detect the starter database from the query
    starter_database = None
    for db in databases:
        if db in query:
            starter_database = db
            break
    
    if starter_database is None:
        st.error("Could not detect the starter database from the query. Please include one of the database names in the query.")
        return
    
    st.write(f"Detected starter database: {starter_database}")
    
    save_path = r"C:\Users\Alessandro\Documents\Programming\Phonenix\Views" 
    
    # Add checkboxes for each database, all selected by default
    selected_databases = []
    for db in databases:
        if st.checkbox(f"{db}", value=True):
            selected_databases.append(db)
    
    if st.button("Run Queries"):
        if not query.strip():
            st.error("Please enter a query.")
            return
        
        try:
            st.subheader("Original Query Results")
            original_results = run_query(query, starter_database)
            filepath = save_query_to_file(query, starter_database, save_path)
            st.write(f"Query saved to: {filepath}")
            st.write(original_results)
            
            for db in selected_databases:
                if starter_database != db:
                    modified_query = query.replace(starter_database, db)
                    st.text_area(f"Modified Query for {db}", value=modified_query, height=500)
                    modified_results = run_query(modified_query, db)
                    st.write(modified_results)
                    
                    # Save the modified query to a file
                    filepath = save_query_to_file(modified_query, db, save_path)
                    st.write(f"Query saved to: {filepath}")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
