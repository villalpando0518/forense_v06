from flask import Flask, render_template, request, flash, redirect, url_for
import openpyxl
from General_SVM import main as mandar_procesar

import pandas as pd
import numpy as np 

import sqlite3



app = Flask(__name__)
app.secret_key = 'bcd884cedd2df109285ee5b83d42e336'  # Para usar flask flash supongo


def get_db_connection(): #Para conectar a la base de datos
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # This allows fetching results as dictionaries
    return conn

# Create Users Table (Only if it doesn't exist)
def create_users_table():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')

# Inicializa la base de datos
create_users_table() 

@app.route('/', methods=['GET', 'POST'])  # Maneja GET y POST
def index():
    if request.method == 'POST':
        file = request.files['spreadsheet_file'] 
        # Cargar archivo de excel
        workbook = openpyxl.load_workbook(file)
        worksheet = workbook.active  # Extrae la página necesaria

        # Extract data 
        data = []
        for row in worksheet.iter_rows():
            row_data = [cell.value for cell in row]
            data.append(row_data)

        datanp = np.array(data)
        predicciones= mandar_procesar(datanp)
        tabla_resultado = np.column_stack((datanp, predicciones))
        tabla_resultado = tabla_resultado.tolist()

        
        print("Sample data:", tabla_resultado[:4])  #Prueba imprimir algunas lineas en consola
        return render_template('index.html', processed_results=tabla_resultado, table_length=len(tabla_resultado), min=min)
    else:
        return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']

        if not username or not password or not name:
            flash('All fields are required!')
            return render_template('register.html')

        # Hash the password (VERY IMPORTANT for security)
        #hashed_password = generate_password_hash(password) 
        hashed_password = password 

        with get_db_connection() as conn:
            try:
                conn.execute(
                    'INSERT INTO users (username, password, name) VALUES (?, ?, ?)',
                    (username, hashed_password, name)
                )
                conn.commit()
                flash('Registration successful!')
                return redirect(url_for('index'))  
            except sqlite3.IntegrityError:
                flash('Username already exists!')
                return render_template('register.html')
    else:
        return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True) 
