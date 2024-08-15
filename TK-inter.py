import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import re  # For regular expression validation

# Database connection settings
DB_CONFIG = {
    'DRIVER': 'SQL Server',
    'SERVER': 'ICT_RB_LT41',
    'DATABASE': 'FMTALI Students',
    'Trusted_Connection': 'yes'
}

def connect_db():
    try:
        conn = pyodbc.connect(
            f'DRIVER={{{DB_CONFIG["DRIVER"]}}};'
            f'SERVER={DB_CONFIG["SERVER"]};'
            f'DATABASE={DB_CONFIG["DATABASE"]};'
            f'Trusted_Connection={DB_CONFIG["Trusted_Connection"]}'
        )
        return conn
    except pyodbc.Error as e:
        messagebox.showerror("Database Connection Error", str(e))
        return None

def calculate_statistics():
    try:
        conn = connect_db()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        # Calculate averages
        cursor.execute("""
            SELECT 
                AVG(Grade_Python) AS Avg_Python, 
                AVG(Grade_Azure_Fundamentals) AS Avg_Azure_Fundamentals, 
                AVG(Grade_Azure_AI) AS Avg_Azure_AI, 
                AVG(Grade_Power_BI) AS Avg_Power_BI
            FROM Students
        """)
        averages = cursor.fetchone()
        
        # Calculate pass rates (assuming pass is >= 50)
        cursor.execute("""
            SELECT 
                (SUM(CASE WHEN Grade_Python >= 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS PassRate_Python,
                (SUM(CASE WHEN Grade_Azure_Fundamentals >= 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS PassRate_Azure_Fundamentals,
                (SUM(CASE WHEN Grade_Azure_AI >= 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS PassRate_Azure_AI,
                (SUM(CASE WHEN Grade_Power_BI >= 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS PassRate_Power_BI
            FROM Students
        """)
        pass_rates = cursor.fetchone()
        
        conn.close()
        
        return averages, pass_rates
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", str(e))
        return None

def show_home():
    clear_window()
    tk.Label(root, text="Welcome to FMTALI", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20, padx=20, sticky="nsew")

    # Fetch and display statistics
    stats = calculate_statistics()
    if stats:
        averages, pass_rates = stats
        stats_text = (
            f"Python Average: {averages.Avg_Python:.2f}, Pass Rate: {pass_rates.PassRate_Python:.2f}%\n"
            f"Azure Fundamentals Average: {averages.Avg_Azure_Fundamentals:.2f}, Pass Rate: {pass_rates.PassRate_Azure_Fundamentals:.2f}%\n"
            f"Azure AI Average: {averages.Avg_Azure_AI:.2f}, Pass Rate: {pass_rates.PassRate_Azure_AI:.2f}%\n"
            f"Power BI Average: {averages.Avg_Power_BI:.2f}, Pass Rate: {pass_rates.PassRate_Power_BI:.2f}%"
        )
        tk.Label(root, text=stats_text, font=("Helvetica", 12)).grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    
    tk.Button(root, text="View All Students", command=view_all_students).grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Add Student", command=open_add_student_form).grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Look Up Student", command=open_lookup_student_form).grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Analyze Data", command=open_analysis_form).grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

    for i in range(6):
        root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def view_all_students():
    clear_window()
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    rows = cursor.fetchall()
    conn.close()
    display_table(rows)

def display_table(rows, columns=None):
    if not columns:
        columns = [
            "StudentID", "StudentNumber", "FirstName", "LastName", "Gender", "Address", "DateOfBirth",
            "Qualification", "Grade_Python", "Grade_Azure_Fundamentals", "Grade_Azure_AI",
            "Grade_Power_BI", "Average_Grade"
        ]

    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title(), anchor="center")
        tree.column(col, width=100, anchor="center")
    tree.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

    for row in rows:
        formatted_row = [str(item) for item in row]
        tree.insert('', 'end', values=formatted_row)

    tk.Button(root, text="Back to Home", command=show_home).grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

def open_add_student_form():
    clear_window()
    tk.Label(root, text="Add New Student", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    
    fields = ["Student Number", "First Name", "Last Name", "Gender", "Address",
              "Date of Birth (YYYY-MM-DD)", "Grade Python", "Grade Azure Fundamentals",
              "Grade Azure AI", "Grade Power BI", "Qualification"]
    
    entries = []
    for i, field in enumerate(fields):
        tk.Label(root, text=field).grid(row=i+1, column=0, sticky="e", padx=5, pady=5)
        entry = tk.Entry(root)
        entry.grid(row=i+1, column=1, padx=5, pady=5)
        entries.append(entry)

    tk.Button(root, text="Save", command=lambda: add_student(*[e.get() for e in entries])).grid(row=12, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Back to Home", command=show_home).grid(row=13, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

def validate_student_data(student_number, first_name, last_name, gender, address, dob, grade_python, grade_azure_fundamentals,
                          grade_azure_ai, grade_power_bi, qualification):
    # Validation patterns
    num_pattern = re.compile(r'^\d+(\.\d+)?$')  # Matches numbers and decimals
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # Matches YYYY-MM-DD format

    # Validate student number (should be 5 digits)
    if not student_number.isdigit() or len(student_number) != 5:
        return "Student Number must be a 5-digit number."
    
    # Validate grades (should be numbers)
    if not num_pattern.match(grade_python) or not num_pattern.match(grade_azure_fundamentals) or \
       not num_pattern.match(grade_azure_ai) or not num_pattern.match(grade_power_bi):
        return "Grades must be numbers."
    if not date_pattern.match(dob):
        return "Date of Birth must be in YYYY-MM-DD format."
    
    # Validate name fields
    if not all(char.isalpha() or char.isspace() for char in first_name):
        return "First Name must contain only letters and spaces."
    if not all(char.isalpha() or char.isspace() for char in last_name):
        return "Last Name must contain only letters and spaces."
    
    return None

def add_student(student_number, first_name, last_name, gender, address, dob, grade_python, grade_azure_fundamentals,
                grade_azure_ai, grade_power_bi, qualification):
    validation_error = validate_student_data(student_number, first_name, last_name, gender, address, dob,
                                              grade_python, grade_azure_fundamentals, grade_azure_ai, grade_power_bi, qualification)
    if validation_error:
        messagebox.showerror("Validation Error", validation_error)
        return

    try:
        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        # Insert new student
        cursor.execute("""
            INSERT INTO Students (StudentNumber, FirstName, LastName, Gender, Address, DateOfBirth, 
                                  Grade_Python, Grade_Azure_Fundamentals, Grade_Azure_AI, Grade_Power_BI, Qualification)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_number, first_name, last_name, gender, address, dob, grade_python, grade_azure_fundamentals,
              grade_azure_ai, grade_power_bi, qualification))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Student added successfully.")
        show_home()
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", str(e))

def open_lookup_student_form():
    clear_window()
    tk.Label(root, text="Look Up Student", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

    tk.Label(root, text="Student Number").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    student_number_entry = tk.Entry(root)
    student_number_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="First Name").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    first_name_entry = tk.Entry(root)
    first_name_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(root, text="Last Name").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    last_name_entry = tk.Entry(root)
    last_name_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Button(root, text="Search", command=lambda: lookup_student(student_number_entry.get(), first_name_entry.get(), last_name_entry.get())).grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Back to Home", command=show_home).grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

def lookup_student(student_number, first_name, last_name):
    try:
        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        query = "SELECT * FROM Students WHERE StudentNumber = ? OR FirstName = ? OR LastName = ?"
        cursor.execute(query, (student_number, first_name, last_name))
        student = cursor.fetchall()
        conn.close()
        
        if student:
            display_table(student)
            for row in student:
                create_update_delete_buttons(row[0])
        else:
            messagebox.showinfo("Not Found", "No student found with that information.")
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", str(e))

def create_update_delete_buttons(student_id):
    tk.Button(root, text="Update Student", command=lambda: open_update_student_form(student_id)).grid(row=6, column=0, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Delete Student", command=lambda: delete_student(student_id)).grid(row=6, column=1, pady=10, padx=20, sticky="nsew")

def open_update_student_form(student_id):
    clear_window()
    tk.Label(root, text="Update Student", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students WHERE StudentID = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()

    if not student:
        messagebox.showerror("Error", "Student not found.")
        return

    fields = ["Student Number", "First Name", "Last Name", "Gender", "Address",
              "Date of Birth", "Grade Python", "Grade Azure Fundamentals",
              "Grade Azure AI", "Grade Power BI", "Qualification"]
    
    entries = []
    for i, field in enumerate(fields):
        tk.Label(root, text=field).grid(row=i+1, column=0, sticky="e", padx=5, pady=5)
        entry = tk.Entry(root)
        entry.insert(0, student[i+1])
        entry.grid(row=i+1, column=1, padx=5, pady=5)
        entries.append(entry)

    tk.Button(root, text="Save Changes", command=lambda: update_student(student_id, *[e.get() for e in entries])).grid(row=12, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Back to Home", command=show_home).grid(row=13, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

def update_student(student_id, student_number, first_name, last_name, gender, address, dob, grade_python, grade_azure_fundamentals,
                   grade_azure_ai, grade_power_bi, qualification):
    validation_error = validate_student_data(student_number, first_name, last_name, gender, address, dob,
                                              grade_python, grade_azure_fundamentals, grade_azure_ai, grade_power_bi, qualification)
    if validation_error:
        messagebox.showerror("Validation Error", validation_error)
        return

    try:
        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        # Update student data
        cursor.execute("""
            UPDATE Students
            SET StudentNumber = ?, FirstName = ?, LastName = ?, Gender = ?, Address = ?, DateOfBirth = ?, 
                Grade_Python = ?, Grade_Azure_Fundamentals = ?, Grade_Azure_AI = ?, Grade_Power_BI = ?, Qualification = ?
            WHERE StudentID = ?
        """, (student_number, first_name, last_name, gender, address, dob, grade_python, grade_azure_fundamentals,
              grade_azure_ai, grade_power_bi, qualification, student_id))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Student updated successfully.")
        show_home()
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", str(e))

def delete_student(student_id):
    try:
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            conn = connect_db()
            if not conn:
                return
            cursor = conn.cursor()

            # Delete student
            cursor.execute("DELETE FROM Students WHERE StudentID = ?", (student_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Student deleted successfully.")
            show_home()
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", str(e))

def open_analysis_form():
    clear_window()
    tk.Label(root, text="Analyze Data", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

    tk.Label(root, text="Enter SQL Query").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    query_entry = tk.Entry(root, width=50)
    query_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(root, text="Execute", command=lambda: analyze_data(query_entry.get())).grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")
    tk.Button(root, text="Back to Home", command=show_home).grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

def analyze_data(query):
    try:
        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Get column names from cursor description
        columns = [column[0] for column in cursor.description]
        
        conn.close()
        display_table(rows, columns)
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", str(e))
    except Exception as e:
        messagebox.showerror("Query Error", str(e))

root = tk.Tk()
root.title("Student Management System")
root.geometry("800x600")
show_home()
root.mainloop()