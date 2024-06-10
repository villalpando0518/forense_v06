from flask import Flask, render_template, request, flash, redirect, url_for, session
import openpyxl
from utils.General_SVM import main as mandar_procesar
from routes.dashboard import dashboard
from routes.auth import login, register
from db import get_db_connection

import pandas as pd
import numpy as np 


app = Flask(__name__)
app.secret_key = 'bcd884cedd2df109285ee5b83d42e336'  # Para usar flask flash supongo

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

#Para organizar en diferentes archivos
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', view_func=dashboard)

if __name__ == '__main__':
    app.run(debug=True) 
