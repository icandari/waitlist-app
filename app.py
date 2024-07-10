from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import sqlite3
import logging

app = Flask(__name__, static_folder='static')

# Set logging to show only errors
logging.basicConfig(level=logging.ERROR)

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

def update_database():
    # Read the Excel file
    df = pd.read_excel('students.xlsx')

    # Ensure column names are correctly set
    df.columns = ['Name', 'StudentID', 'Registered', 'GettingMarried', 'ApplicationDate']

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
            return jsonify({'error': 'Student not found'}), 404
        
        # Determine position in Excel file
        excel_data = pd.read_excel('students.xlsx')
        excel_data.columns = ['Name', 'StudentID', 'Registered', 'GettingMarried', 'ApplicationDate']
        student_index = int(excel_data.index[excel_data['StudentID'] == int(student_id)][0]) + 1  # +1 to convert zero-indexed to 1-indexed position
        
        # Determine registration and marriage status
        registered = student['Registered']
        getting_married = student['GettingMarried']
        application_date = student['ApplicationDate']
        registration_status = "Active" if registered == 1 and getting_married == 1 else "Inactive"
        
        general_position = student_index
        
        if registration_status == "Active":
            # Filter active students and determine position among them
            active_students = excel_data[(excel_data['Registered'] == 1) & (excel_data['GettingMarried'] == 1)]
            active_student_ids = active_students['StudentID'].tolist()
            active_position = int(active_student_ids.index(int(student_id))) + 1  # +1 to convert zero-indexed to 1-indexed position
            
            # Determine the number of inactive students ahead of the active student
            inactive_students_ahead = general_position - active_position
            
            message = "Well done! Our records indicate you are on the active waitlist for next semester because you are registered for classes and getting married in the next semester."
            response = {
                "application_date": application_date,
                "general_position": general_position,
                "position_label": "Upcoming Semester Position",
                "active_position": active_position,
                "inactive_ahead": inactive_students_ahead,
                "active_status": registration_status,
                "message": message
            }
        else:
            message = ("Our records indicate that you are not registered for classes, or not getting married in the upcoming semester. "
                       "In order to be on the active waitlist for next semester, you must be registered for classes and be getting married next semester. <br><br>"
                       "You will continue to be on the general waitlist until both requirements are fulfilled. "
                       "Please ensure you are registered for classes and have submitted a TVA application with a wedding date in the upcoming semester. "
                       "Contact housing@byuh.edu if our records are incorrect.")
            response = {
                "application_date": application_date,
                "general_position": general_position,
                "active_status": registration_status,
                "message": message
            }
        
        return jsonify(response)
    finally:
        conn.close()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    update_database()  # Update the database with the latest data from Excel
    app.run(debug=True)
