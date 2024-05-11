from flask import Flask, render_template, request
import openpyxl
from General_SVM import main as mandar_procesar

import pandas as pd
import numpy as np 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])  # Handle both GET and POST
def index():
    if request.method == 'POST':
        file = request.files['spreadsheet_file'] 
        # Cargar archivo de excel
        workbook = openpyxl.load_workbook(file)
        worksheet = workbook.active  # Get the active worksheet

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

if __name__ == '__main__':
    app.run(debug=True) 

