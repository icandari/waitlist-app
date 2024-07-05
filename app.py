from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import sqlite3

app = Flask(__name__, static_folder='static')

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

def update_database():
    # Read the Excel file
    df = pd.read_excel('students.xlsx')

    # Connect to SQLite database
    conn = sqlite3.connect('students.db')

    # Write the DataFrame to the SQLite table
    df.to_sql('students', conn, if_exists='replace', index=False)

    conn.close()

@app.route('/student/<student_id>', methods=['GET'])
def get_student(student_id):
    conn = get_db_connection()
    try:
        # Retrieve student details from database
        student = conn.execute('SELECT * FROM students WHERE StudentID = ?', (student_id,)).fetchone()
        
        if student is None:
            response = jsonify({'error': 'Student not found'})
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            return response, 404
        
        # Determine position in Excel file
        excel_data = pd.read_excel('students.xlsx')
        student_index = excel_data.index[excel_data['StudentID'] == int(student_id)][0] + 1  # +1 to convert zero-indexed to 1-indexed position
        
        # Determine registration status
        registration_status = "Active" if student['Registered'] == 1 else "Inactive"
        
        # Construct response with name, position, and registration status
        response = {
            "name": student['Name'],
            "position": f"Position {student_index}",
            "active_status": registration_status
        }
        
        # Set cache-control headers to prevent caching
        response = jsonify(response)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        
        return response
    finally:
        conn.close()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    update_database()  # Update the database with the latest data from Excel
    app.run(debug=True)
