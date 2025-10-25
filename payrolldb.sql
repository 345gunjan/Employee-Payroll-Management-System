CREATE DATABASE IF NOT EXISTS payrolldb;
USE payrolldb;

CREATE TABLE IF NOT EXISTS employees (
  id INT AUTO_INCREMENT PRIMARY KEY,
  emp_code VARCHAR(30) UNIQUE,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100),
  dob DATE,
  department VARCHAR(100),
  designation VARCHAR(100),
  joining_date DATE,
  basic_salary DECIMAL(12,2) NOT NULL,
  bank_account VARCHAR(100),
  tax_id VARCHAR(100),
  is_active TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payslips (
  id INT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  payroll_year INT NOT NULL,
  payroll_month TINYINT NOT NULL, -- 1-12
  basic_salary DECIMAL(12,2) NOT NULL,
  total_allowances DECIMAL(12,2) DEFAULT 0,
  total_deductions DECIMAL(12,2) DEFAULT 0,
  gross_salary DECIMAL(12,2) NOT NULL,
  net_salary DECIMAL(12,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_emp_month (employee_id, payroll_year, payroll_month),
  FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payroll_components (
  id INT AUTO_INCREMENT PRIMARY KEY,
  payslip_id INT NOT NULL,
  name VARCHAR(100),
  amount DECIMAL(12,2) NOT NULL,
  type ENUM('ALLOWANCE','DEDUCTION') NOT NULL,
  FOREIGN KEY (payslip_id) REFERENCES payslips(id) ON DELETE CASCADE
);
