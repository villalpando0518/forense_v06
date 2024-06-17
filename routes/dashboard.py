#Dashboard file
from flask import render_template, request, flash, redirect, url_for, session
import openpyxl
from utils.General_SVM import main as mandar_procesar

import pandas as pd
import numpy as np 

from db import get_db_connection
from datetime import datetime
import json

def dashboard():
    
    if 'username' in session:
        username = session['username']
        user_id = None
    else:
        flash('You need to be logged in to access the dashboard.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    

    if request.method == 'POST':
        if 'spreadsheet_file' in request.files:
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
            with get_db_connection() as conn:
                conn.execute(
                    'DELETE FROM consultas WHERE user_id = ? AND temporal = 1',
                    (user_id,)
                )
                conn.execute(
                    'INSERT INTO consultas (user_id, date, algorithm, data_name, content, temporal, filename) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (user_id, datetime.now().strftime('%Y-%m-%d %H:%M'), 'Algoritmo SVM', 'Esternon', json.dumps(tabla_resultado), True, file.filename)
                )
                conn.commit()
            return render_template('dashboard.html', username=username, processed_results=tabla_resultado, table_length=len(tabla_resultado), min=min)
        elif 'save_results' in request.form:    
            with get_db_connection() as conn:
                conn.execute(
                        'UPDATE consultas SET temporal = 0 WHERE user_id = ? AND temporal = 1',(user_id,) 
                    )
                conn.commit()
            flash('Consulta saved successfully!')
            return render_template('dashboard.html', username=username)
    else:
        return render_template('dashboard.html', username=username)


