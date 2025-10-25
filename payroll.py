# full_employee_payroll_gui.py
import os
import mysql.connector
from mysql.connector import Error
from decimal import Decimal, ROUND_HALF_UP
from dotenv import load_dotenv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ---------------- Environment & DB ---------------- #
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'Gunjan@123'),
    'database': os.getenv('DB_NAME', 'payrolldb'),
    'auth_plugin': 'mysql_native_password'
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("Database Error", f"Cannot connect to MySQL: {e}")
        return None

def decimal(v):
    return Decimal(v).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# ---------------- Database Setup ---------------- #
def create_tables():
    ddl = [
        f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']};",
        f"USE {DB_CONFIG['database']};",
        """CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            emp_code VARCHAR(30) UNIQUE,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            dob DATE,
            department VARCHAR(100),
            designation VARCHAR(100),
            joining_date DATE,
            basic_salary DECIMAL(12,2),
            bank_account VARCHAR(100),
            tax_id VARCHAR(100),
            is_active TINYINT(1) DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS payslips (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            payroll_year INT NOT NULL,
            payroll_month TINYINT NOT NULL,
            basic_salary DECIMAL(12,2) NOT NULL,
            total_allowances DECIMAL(12,2) DEFAULT 0,
            total_deductions DECIMAL(12,2) DEFAULT 0,
            gross_salary DECIMAL(12,2) NOT NULL,
            net_salary DECIMAL(12,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );"""
    ]
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        for s in ddl:
            cur.execute(s)
        conn.commit()
    except Error as e:
        messagebox.showerror("Database Error", f"Error creating tables: {e}")
    finally:
        conn.close()

# ---------------- Employee Functions ---------------- #
def add_employee_to_db(data):
    sql = """INSERT INTO employees 
             (emp_code, first_name, last_name, dob, department, designation, joining_date, basic_salary, bank_account, tax_id)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        messagebox.showerror("Database Error", f"Error adding employee: {e}")
        return None
    finally:
        conn.close()

def update_employee(emp_id, data):
    sql = """UPDATE employees SET emp_code=%s, first_name=%s, last_name=%s, dob=%s, department=%s,
             designation=%s, joining_date=%s, basic_salary=%s, bank_account=%s, tax_id=%s
             WHERE id=%s"""
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(sql, data + (emp_id,))
        conn.commit()
    except Error as e:
        messagebox.showerror("Database Error", f"Error updating employee: {e}")
    finally:
        conn.close()

def delete_employee(emp_id):
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
        conn.commit()
    except Error as e:
        messagebox.showerror("Database Error", f"Cannot delete employee: {e}")
    finally:
        conn.close()

def fetch_employees():
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        query = """
        SELECT e.id, e.emp_code, e.first_name, e.last_name, e.dob, e.department, e.designation,
               e.joining_date, e.basic_salary, e.bank_account, e.tax_id,
               IFNULL(SUM(p.total_allowances),0) AS bonus
        FROM employees e
        LEFT JOIN payslips p ON e.id = p.employee_id
        GROUP BY e.id
        ORDER BY e.id
        """
        cur.execute(query)
        return cur.fetchall()
    except Error as e:
        messagebox.showerror("Error", f"Cannot fetch employees: {e}")
        return []
    finally:
        conn.close()

# ---------------- GUI ---------------- #
class PayrollGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Payroll Management System")
        self.root.geometry("1200x600")
        self.root.configure(bg="#f0f4f7")

        title = tk.Label(root, text="Employee Payroll Management System", font=("Helvetica", 20, "bold"), bg="#f0f4f7", fg="#1a1a2e")
        title.pack(pady=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), foreground="#1a1a2e")
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25)

        columns = ("ID","Code","First Name","Last Name","DOB","Department","Designation","Joining Date","Salary","Bank Account","Tax ID","Bonus")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(root, bg="#f0f4f7")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Employee", font=("Helvetica", 12, "bold"), bg="#1a73e8", fg="white", command=self.add_employee_gui, width=15).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Edit Employee", font=("Helvetica", 12, "bold"), bg="#ffa500", fg="white", command=self.edit_employee_gui, width=15).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Delete Employee", font=("Helvetica", 12, "bold"), bg="#e84118", fg="white", command=self.delete_employee_gui, width=15).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="Refresh", font=("Helvetica", 12, "bold"), bg="#00a8ff", fg="white", command=self.load_data, width=15).grid(row=0, column=3, padx=10)

        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        employees = fetch_employees()
        for emp in employees:
            self.tree.insert("", "end", values=(
                emp['id'], emp['emp_code'], emp['first_name'], emp['last_name'], emp['dob'], emp['department'],
                emp['designation'], emp['joining_date'], f"{emp['basic_salary']:.2f}", emp['bank_account'], emp['tax_id'], f"{emp['bonus']:.2f}"
            ))

    def get_employee_input(self, prefill=None):
        # prefill is a dict for editing
        emp_code = simpledialog.askstring("Employee Code", "Enter Employee Code:", initialvalue=(prefill['emp_code'] if prefill else ""))
        if not emp_code: return None
        first_name = simpledialog.askstring("First Name", "Enter First Name:", initialvalue=(prefill['first_name'] if prefill else ""))
        last_name = simpledialog.askstring("Last Name", "Enter Last Name:", initialvalue=(prefill['last_name'] if prefill else ""))
        dob = simpledialog.askstring("DOB", "Enter DOB (YYYY-MM-DD):", initialvalue=(prefill['dob'] if prefill else ""))
        department = simpledialog.askstring("Department", "Enter Department:", initialvalue=(prefill['department'] if prefill else ""))
        designation = simpledialog.askstring("Designation", "Enter Designation:", initialvalue=(prefill['designation'] if prefill else ""))
        joining_date = simpledialog.askstring("Joining Date", "Enter Joining Date (YYYY-MM-DD):", initialvalue=(prefill['joining_date'] if prefill else ""))
        basic_salary = simpledialog.askfloat("Basic Salary", "Enter Basic Salary:", initialvalue=(prefill['basic_salary'] if prefill else 0))
        bank_account = simpledialog.askstring("Bank Account", "Enter Bank Account:", initialvalue=(prefill['bank_account'] if prefill else ""))
        tax_id = simpledialog.askstring("Tax ID", "Enter Tax ID:", initialvalue=(prefill['tax_id'] if prefill else ""))
        return (emp_code, first_name, last_name, dob, department, designation, joining_date, decimal(basic_salary), bank_account, tax_id)

    def add_employee_gui(self):
        data = self.get_employee_input()
        if data:
            add_employee_to_db(data)
            self.load_data()

    def edit_employee_gui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Employee", "Please select an employee to edit")
            return
        emp_id = self.tree.item(selected[0])['values'][0]
        prefill = {
            'emp_code': self.tree.item(selected[0])['values'][1],
            'first_name': self.tree.item(selected[0])['values'][2],
            'last_name': self.tree.item(selected[0])['values'][3],
            'dob': self.tree.item(selected[0])['values'][4],
            'department': self.tree.item(selected[0])['values'][5],
            'designation': self.tree.item(selected[0])['values'][6],
            'joining_date': self.tree.item(selected[0])['values'][7],
            'basic_salary': float(self.tree.item(selected[0])['values'][8]),
            'bank_account': self.tree.item(selected[0])['values'][9],
            'tax_id': self.tree.item(selected[0])['values'][10]
        }
        data = self.get_employee_input(prefill)
        if data:
            update_employee(emp_id, data)
            self.load_data()

    def delete_employee_gui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Employee", "Please select an employee to delete")
            return
        emp_id = self.tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Employee ID {emp_id}?")
        if confirm:
            delete_employee(emp_id)
            self.load_data()

# ---------------- Main ---------------- #
if __name__ == "__main__":
    create_tables()
    root = tk.Tk()
    gui = PayrollGUI(root)
    root.mainloop()
