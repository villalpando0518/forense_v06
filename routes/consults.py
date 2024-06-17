from flask import session, render_template, send_file  # Para descargar archivos
import pandas as pd
import io
import openpyxl
import json

from db import get_db_connection

def consults():
    if 'username' in session:
        username = session['username']
        user_id = session.get('user_id')
        with get_db_connection() as conn:
            consultas = conn.execute(
                'SELECT id, date, algorithm, filename FROM consultas WHERE user_id = ? AND temporal=0 ORDER BY date DESC', 
                (user_id,)
            ).fetchall()

        return render_template('consults.html', username=username, consultas=consultas)
    else:
        flash('No has accedido a tu cuenta')
        return redirect(url_for('login'))


def download_consulta(consulta_id):
    if 'username' in session:
        with get_db_connection() as conn:
            consulta = conn.execute(
                'SELECT content FROM consultas WHERE id = ?', (consulta_id,)
            ).fetchone()

            if consulta:
                data = json.loads(consulta['content'])

                # Convert the data back into a DataFrame
                df = pd.DataFrame(data)

                # Create an Excel workbook and add a worksheet
                output = io.BytesIO()
                writer = pd.ExcelWriter(output, engine='openpyxl')
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.close()

                # Set the position of the stream to the beginning
                output.seek(0)

                # Return the Excel file for download
                return send_file(
                    output, 
                    as_attachment=True, 
                    download_name='consulta_results.xlsx',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    
    flash('Error downloading consultation.')
    return redirect(url_for('consults'))
