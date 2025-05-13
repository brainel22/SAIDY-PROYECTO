#   Biblioteca Flask y Mysql
from flask import Flask, render_template,request,redirect,flash, url_for,session,jsonify,make_response,Response,send_from_directory
from flask_mysqldb import MySQL
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
from itsdangerous import URLSafeTimedSerializer
import bcrypt

#   Matplotlib
import matplotlib.pyplot as plt
import pandas as pd

#   Para hacer la factura
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor  # Añade esta importación
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle,SimpleDocTemplate,Spacer, Table, TableStyle,Paragraph,Image,PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle,TA_LEFT,TA_RIGHT,TA_CENTER
import qrcode
from PIL import Image
from reportlab.lib.utils import ImageReader
import pdfkit
from reportlab.lib.pagesizes import letter
from datetime import datetime
from reportlab.lib.units import inch

import unicodedata
import base64
import json
#   Para las notificaciones al email
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
from flask_mail import Mail
from email.header import Header
from email import encoders
from email.mime.base import MIMEBase
from email.utils import formataddr

#    Para los errores
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.utils import secure_filename

import os
import io
from io import BytesIO
import time


app = Flask(__name__,template_folder='templates')
mail = Mail(app)
s = URLSafeTimedSerializer('Tu_Secret_Key')

application = app
usuarios_registrados = []
eventos_guardados = []

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'boolingsr@gmail.com'
app.config['MAIL_PASSWORD'] = 'z r s g s v l q d c n g l b e u'

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'boolings'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
app.config['SESSION_TYPE'] = 'filesystem'

wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

# Configura pdfkit para usar la ruta del ejecutable
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
Session(app)
mysql = MySQL(app)

app.secret_key = 'mysecretkey'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#    Inicio de la pagina
@app.route('/')
def inicio():
    if 'username' in session:
        return render_template('login/login.html', username=session['username'])
    return render_template('login/register.html')


@app.route('/register', methods = ['GET','POST']) 
def register():
    if request.method == 'POST':
        _username = request.form['username']
        _email = request.form['email']
        _password = request.form['password']
        usuarios_registrados.append({'username': _username, 'password': _password})

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username = %s', (_username,))
        existing_username = cur.fetchone()
        
        # Validar si el correo electrónico ya existe
        cur.execute('SELECT * FROM user WHERE email = %s', (_email,))
        existing_email = cur.fetchone()

        if existing_username:
            flash('El nombre de usuario ya está en uso. Por favor, elige otro.')
            return render_template('login/register.html')
        elif existing_email:
            flash('El correo electrónico ya está registrado. Por favor, utiliza otro.')
            return render_template('login/register.html')
        else:
            # Insertar datos en la tabla
            cur.execute('INSERT INTO user (username, email, password, id_role) VALUES (%s, %s, %s,%s)', (_username, _email, _password,'2'))
            mysql.connection.commit()
            # Lógica de autenticación
            authentication_success = True  # Aquí debes implementar la autenticación

            if authentication_success:
                flash('¡Registro exitoso! Por favor inicia sesión.')
                send_notification_email(_email)
                return render_template('login/login.html')
            
            else:
                flash("Credenciales inválidas")
                return render_template ('login/register.html')
            
    return render_template('login/register.html')


def send_notification_email(_email):
    sender_email = 'boolingsr@gmail.com'  # Cambia esto por tu dirección de correo electrónico
    receiver_email = _email  # La dirección de correo electrónico del usuario registrado
    password = 'z r s g s v l q d c n g l b e u'

    # Crear el mensaje de correo electrónico
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = '¡Bienvenido!'

    # Cuerpo del mensaje en HTML con estilos básicos
    body = "Tu cuenta se a creado correctamente"

    # Adjuntar el cuerpo del mensaje como parte HTML
    message.attach(MIMEText(body, 'html'))

    # Iniciar sesión en el servidor SMTP y enviar el correo electrónico
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)


    # Adjuntar el cuerpo del mensaje como parte HTML
    message.attach(MIMEText(body, 'html'))

    # Iniciar sesión en el servidor SMTP y enviar el correo electrónico
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)


# Login con validación de roles
@app.route('/access_login', methods=['GET', 'POST'])
def access_login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        _email = request.form['email']
        _password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE email = %s AND password = %s', (_email, _password,))
        account = cur.fetchone()
        if account:
            # Guarda en la sesión la información del usuario
            session['logueado'] = True
            session['id'] = account['id']
            session['id_role'] = account.get('id_role')  # Acceder al valor de 'id_role' usando get()
            session['username'] = account['username']  # Guarda el nombre de usuario en la sesión

            # Redirige según el rol del usuario
            if session['id_role'] == 1:
                return render_template('admin/menuadmin.html')
            elif session['id_role'] == 2:
                return redirect(url_for('perfil'))  # Redirige al perfil si el rol es 2
            elif session['id_role'] == 3:
                return render_template('admin/listas/eventos.html')
            else:
                flash('Credenciales Invalidas')
                return render_template('login/login.html')
        else:
            flash("Usuario o Contraseña Incorrectas")
            return render_template('login/login.html')
    
    return render_template('login/login.html')


@app.route('/reset', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            try:
                # Configuración del correo
                subject = 'Restablecimiento de contraseña - Booling SR'
                sender_email = 'boolingsr@gmail.com'
                password = 'z r s g s v l q d c n g l b e u'  # Usar contraseña de aplicación
                
                # Crear enlace de restablecimiento
                reset_link = url_for("reset_password", email=email, _external=True)
                
                # Cuerpo del mensaje en HTML (con caracteres especiales)
                html_content = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Restablecer Contraseña</title>
                </head>
                <body>
                    <p>Hola,</p>
                    <p>Has solicitado restablecer tu contraseña en Booling SR.</p>
                    <p>Por favor, haz clic en el siguiente enlace para continuar:</p>
                    <p><a href="{reset_link}">Restablecer contraseña</a></p>
                    <p>Si no solicitaste este cambio, ignora este mensaje.</p>
                    <p>Atentamente,<br>El equipo de Booling SR</p>
                </body>
                </html>
                """
                
                # Versión alternativa en texto plano
                text_content = f"""
                Hola,

                Has solicitado restablecer tu contraseña en Booling SR.
                Por favor, visita el siguiente enlace para continuar:
                {reset_link}

                Si no solicitaste este cambio, ignora este mensaje.

                Atentamente,
                El equipo de Booling SR
                """

                # Crear mensaje MIME
                msg = MIMEMultipart('alternative')
                msg['From'] = formataddr(('Booling SR', sender_email))
                msg['To'] = email
                msg['Subject'] = Header(subject, 'utf-8')
                
                # Adjuntar ambas versiones (texto y HTML)
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                part2 = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(part1)
                msg.attach(part2)

                # Enviar correo
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, password)
                    server.send_message(msg)  # Usar send_message en lugar de sendmail
                
                flash("Se ha enviado un correo con instrucciones para restablecer tu contraseña.", 'success')
                return redirect(url_for('reset_request'))
            
            except Exception as e:
                flash(f"Error al enviar el correo: {str(e)}", 'error')
                app.logger.error(f"Error enviando correo: {str(e)}")
                return redirect(url_for('reset_request'))
        
        flash("El correo no está registrado.", 'error')
    
    return render_template('login/reset.html')

# Ruta para restablecer la contraseña
@app.route('/reset/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        try:
            new_password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not new_password or not confirm_password:
                flash("Todos los campos son requeridos", 'error')
                return render_template('login/change_password.html', email=email)
            
            if len(new_password) < 8:
                flash("La contraseña debe tener al menos 8 caracteres", 'error')
                return render_template('login/change_password.html', email=email)
                
            if new_password != confirm_password:
                flash("Las contraseñas no coinciden", 'error')
                return render_template('login/change_password.html', email=email)
            
            # Resto de la lógica...
            
        except Exception as e:
            flash("Ocurrió un error al procesar tu solicitud", 'error')
            app.logger.error(f"Error en reset_password: {str(e)}")
            return render_template('login/change_password.html', email=email)
    
    return render_template('login/change_password.html', email=email)

# Añade esta función para generar recomendaciones
def generate_recommendations(user_id):
    cursor = mysql.connection.cursor()
    
    try:
        # Paso 1: Obtener los intereses del usuario (categorías de eventos reservados/favoritos)
        cursor.execute("""
            SELECT e.category, COUNT(*) as count 
            FROM (
                SELECT id_event FROM bookings WHERE id_user = %s
                UNION ALL
                SELECT id_event FROM favorites WHERE id_user = %s
            ) as user_events
            JOIN events e ON user_events.id_event = e.id
            GROUP BY e.category
            ORDER BY count DESC
            LIMIT 3
        """, (user_id, user_id))
        
        top_categories = [row['category'] for row in cursor.fetchall()]
        
        if not top_categories:
            return []  # No hay datos para generar recomendaciones
        
        # Paso 2: Obtener eventos similares que el usuario no ha reservado ni marcado como favorito
        cursor.execute("""
            SELECT e.*, 
                   CASE WHEN e.category IN %s THEN 1 ELSE 0 END as match_score
            FROM events e
            WHERE e.id NOT IN (
                SELECT id_event FROM bookings WHERE id_user = %s
                UNION
                SELECT id_event FROM favorites WHERE id_user = %s
            )
            ORDER BY match_score DESC, e.event_date ASC
            LIMIT 6
        """, (tuple(top_categories), user_id, user_id))
        
        recommended_events = cursor.fetchall()
        
        # Paso 3: Guardar las recomendaciones en la base de datos
        # Primero borrar recomendaciones antiguas
        cursor.execute("DELETE FROM recommendations WHERE id_user = %s", (user_id,))
        
        # Insertar nuevas recomendaciones
        for event in recommended_events:
            score = 1.0 if event['match_score'] else 0.5  # Puntuación más alta para coincidencias exactas
            cursor.execute("""
                INSERT INTO recommendations (id_user, id_event, score)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE score = VALUES(score)
            """, (user_id, event['id'], score))
        
        mysql.connection.commit()
        
        return recommended_events
    
    except Exception as e:
        print(f"Error generando recomendaciones: {str(e)}")
        mysql.connection.rollback()
        return []
    finally:
        cursor.close()

@app.route('/perfil')
def perfil():
    if 'username' not in session:
        return redirect(url_for('access_login'))
    
    user_id = session.get('id')
    cursor = mysql.connection.cursor()
    
    try:
        # 1. Datos básicos del usuario
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return redirect(url_for('access_login'))

        # 2. Reservas recientes (últimas 5)
        cursor.execute("""
            SELECT 
                e.id AS event_id,
                e.name AS event_name,
                e.image_url AS event_image,
                b.number_of_reserved_tickets,
                b.date AS reservation_date,
                e.event_date AS date,
                e.event_hour AS time,
                e.category AS category_name
            FROM bookings b
            JOIN events e ON b.id_event = e.id
            WHERE b.id_user = %s
            ORDER BY b.date DESC
            LIMIT 5
        """, (user_id,))
        reservations = cursor.fetchall()

        # 3. Favoritos recientes (últimos 5)
        cursor.execute("""
            SELECT 
                e.id AS event_id, 
                e.name AS event_name, 
                e.image_url AS event_image,
                e.event_date AS date, 
                e.event_hour AS time,
                e.category AS category_name,
                f.created_at AS favorite_date
            FROM favorites f
            JOIN events e ON f.id_event = e.id
            WHERE f.id_user = %s
            ORDER BY f.created_at DESC
            LIMIT 5
        """, (user_id,))
        favorites = cursor.fetchall()
        
        # 4. Actividades diarias (reservas y favoritos de hoy)
        cursor.execute("""
            (
                SELECT 
                    'reserva' as type,
                    b.date as activity_date,
                    CONCAT('Reservaste ', b.number_of_reserved_tickets, ' entradas para ', e.name) as activity_text,
                    e.name as event_name,
                    e.id as event_id,
                    e.image_url as event_image
                FROM bookings b
                JOIN events e ON b.id_event = e.id
                WHERE b.id_user = %s 
                AND DATE(b.date) = CURDATE()
            )
            UNION ALL
            (
                SELECT 
                    'favorito' as type,
                    f.created_at as activity_date,
                    CONCAT('Agregaste "', e.name, '" a favoritos') as activity_text,
                    e.name as event_name,
                    e.id as event_id,
                    e.image_url as event_image
                FROM favorites f
                JOIN events e ON f.id_event = e.id
                WHERE f.id_user = %s
                AND DATE(f.created_at) = CURDATE()
            )
            ORDER BY activity_date DESC
            LIMIT 10
        """, (user_id, user_id))
        daily_activities = cursor.fetchall()
        
        # 5. Recomendaciones
        cursor.execute("""
            SELECT e.* 
            FROM recommendations r
            JOIN events e ON r.id_event = e.id
            WHERE r.id_user = %s
            ORDER BY r.score DESC, r.recommendation_date DESC
            LIMIT 6
        """, (user_id,))
        recommendations = cursor.fetchall()
        
        if not recommendations:
            recommendations = generate_recommendations(user_id)
        
        # 6. Calcular estadísticas
        stats = {
            'total_reservations': len(reservations),
            'total_favorites': len(favorites),
            'today_reservations': sum(1 for activity in daily_activities if activity['type'] == 'reserva'),
            'total_events': len(reservations) + len(favorites)
        }
        
        return render_template('menu/perfil_usuario.html', 
                           user=user, 
                           reservations=reservations,
                           favorites=favorites,
                           daily_activities=daily_activities,
                           recommendations=recommendations,
                           stats=stats)
    
    except Exception as e:
        print(f"Error en /perfil: {str(e)}")
        # Asegurarse de pasar stats vacío en caso de error
        return render_template('menu/perfil_usuario.html', 
                           user={},
                           reservations=[],
                           favorites=[],
                           daily_activities=[],
                           recommendations=[],
                           stats={
                               'total_reservations': 0,
                               'total_favorites': 0,
                               'today_reservations': 0,
                               'total_events': 0
                           },
                           error="Error al cargar datos del perfil")
    finally:
        cursor.close()

# Añade esta ruta para actualizar recomendaciones manualmente
@app.route('/update_recommendations')
def update_recommendations():
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    recommendations = generate_recommendations(session['id'])
    return jsonify({
        'success': True,
        'message': 'Recomendaciones actualizadas',
        'count': len(recommendations)
    })

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('access_login'))  # Redirige si no hay sesión

    username = session['username']
    new_email = request.form['email']  # Obtiene el nuevo correo

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE user SET email = %s WHERE username = %s", (new_email, username))
        mysql.connection.commit()
        cursor.close()

        flash('Perfil actualizado con éxito.', 'success')
        return redirect(url_for('perfil'))  # Redirige al perfil

    except Exception as e:
        flash(f'Error al actualizar el perfil: {str(e)}', 'danger')
        return redirect(url_for('perfil'))
    

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    event_id = request.form.get('event_id')
    user_id = session.get('id')
    
    cursor = mysql.connection.cursor()
    
    try:
        # Verificar si ya es favorito primero
        cursor.execute("SELECT * FROM favorites WHERE id_user = %s AND id_event = %s", 
                      (user_id, event_id))
        existing = cursor.fetchone()
        
        if existing:
            # Si ya existe, eliminarlo (toggle)
            cursor.execute("DELETE FROM favorites WHERE id_user = %s AND id_event = %s", 
                         (user_id, event_id))
            action = 'removed'
            message = 'Eliminado de favoritos'
        else:
            # Si no existe, agregarlo
            cursor.execute("INSERT INTO favorites (id_user, id_event) VALUES (%s, %s)", 
                         (user_id, event_id))
            action = 'added'
            message = 'Añadido a favoritos'
        
        mysql.connection.commit()
        
        # Obtener datos actualizados del evento
        cursor.execute("""
            SELECT e.name, e.image_url, e.event_date, e.event_hour, e.category 
            FROM events e WHERE e.id = %s
        """, (event_id,))
        event_data = cursor.fetchone()
        
        return jsonify({
            'success': True,
            'action': action,
            'message': message,
            'event': {
                'id': event_id,
                'name': event_data['name'],
                'image': event_data['image_url'],
                'date': event_data['event_date'].strftime('%Y-%m-%d') if event_data['event_date'] else None,
                'time': str(event_data['event_hour']) if event_data['event_hour'] else None,
                'category': event_data['category']
            }
        })
        
    except Exception as e:
        mysql.connection.rollback()
        # Manejar específicamente el error de duplicado
        if "Duplicate entry" in str(e):
            return jsonify({
                'success': False,
                'message': 'Este evento ya está en tus favoritos'
            }), 400
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
        
    finally:
        cursor.close()


@app.route('/check_favorites')
def check_favorites():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    event_ids = request.args.get('ids', '').split(',')
    if not event_ids or event_ids[0] == '':
        return jsonify({'favorites': []})
    
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute("SELECT id FROM user WHERE username = %s", (session['username'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Obtener los favoritos del usuario entre los eventos mostrados
        cursor.execute("""
            SELECT id_event FROM favorites 
            WHERE id_user = %s AND id_event IN (%s)
        """ % (user['id'], ','.join(['%s']*len(event_ids))), tuple(event_ids))
        
        favorites = [str(row['id_event']) for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'favorites': favorites
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al verificar favoritos: {str(e)}'
        }), 500
        
    finally:
        cursor.close()

# Eliminar de favoritos (ya lo tienes, pero aquí está la versión corregida)
@app.route('/eliminar_favorito', methods=['POST'])
def eliminar_favorito():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    event_id = request.form.get('event_id')
    username = session['username']
    
    cursor = mysql.connection.cursor()
    
    try:
        # Obtener ID del usuario
        cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Eliminar de favoritos
        cursor.execute("DELETE FROM favorites WHERE id_user = %s AND id_event = %s", 
                      (user['id'], event_id))
        mysql.connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evento eliminado de favoritos'
        })
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar de favoritos: {str(e)}'
        }), 500
        
    finally:
        cursor.close()

@app.route('/historial')
def historial():
    if 'username' not in session:
        return redirect(url_for('access_login'))
    
    user_id = session.get('id')
    
    try:
        with mysql.connection.cursor() as cursor:
            # Consulta unificada que obtiene todos los tipos de historial
            query = """
            (SELECT 
                e.id AS event_id,
                e.name AS event_name,
                IFNULL(e.image_url, 'default.jpg') AS event_image,
                b.number_of_reserved_tickets,
                b.date AS action_date,
                e.event_date,
                e.event_hour,
                e.category,
                'reserva' AS type,
                NULL AS amount_paid,
                NULL AS card_number
            FROM bookings b
            JOIN events e ON b.id_event = e.id
            WHERE b.id_user = %s)
            
            UNION ALL
            
            (SELECT 
                e.id AS event_id,
                e.name AS event_name,
                IFNULL(e.image_url, 'default.jpg') AS event_image,
                NULL AS number_of_reserved_tickets,
                f.created_at AS action_date,
                e.event_date,
                e.event_hour,
                e.category,
                'favorito' AS type,
                NULL AS amount_paid,
                NULL AS card_number
            FROM favorites f
            JOIN events e ON f.id_event = e.id
            WHERE f.id_user = %s)
            
            UNION ALL
            
            (SELECT 
                e.id AS event_id,
                e.name AS event_name,
                IFNULL(e.image_url, 'default.jpg') AS event_image,
                NULL AS number_of_reserved_tickets,
                p.payment_date AS action_date,
                e.event_date,
                e.event_hour,
                e.category,
                'pago' AS type,
                p.amount_paid,
                p.card_number
            FROM payment p
            JOIN events e ON p.evento_id = e.id
            WHERE p.id_user = %s)
            
            ORDER BY action_date DESC
            LIMIT 50
            """
            
            cursor.execute(query, (user_id, user_id, user_id))
            historial_data = cursor.fetchall()
            
            if not historial_data:
                return render_template('menu/historial.html', 
                                   historial=[],
                                   user=session,
                                   mensaje="No hay actividades recientes")
            
            # Procesar los datos para el template
            processed_data = []
            for item in historial_data:
                entry = {
                    'type': item['type'],
                    'event_name': item['event_name'],
                    'event_image': item['event_image'],
                    'reservation_date': item['action_date'],
                    'event_date': item['event_date'],
                    'event_time': str(item['event_hour']) if item['event_hour'] else '',
                    'category': item['category'] or 'General'
                }
                
                # Campos específicos por tipo
                if item['type'] == 'reserva':
                    entry['number_of_reserved_tickets'] = item['number_of_reserved_tickets']
                elif item['type'] == 'pago':
                    entry['amount_paid'] = float(item['amount_paid']) if item['amount_paid'] else 0.0
                    entry['card_number'] = item['card_number'][-4:] if item['card_number'] else '****'
                
                processed_data.append(entry)
            
            return render_template('menu/historial.html', 
                               historial=processed_data,
                               user=session)
    
    except Exception as e:
        print(f"Error en /historial: {str(e)}")
        return render_template('menu/historial.html', 
                           historial=[],
                           user=session,
                           error="Error temporal al cargar el historial")
#         Desloguearse
@app.route('/logout')
def logout():
    # Elimina el nombre de usuario de la sesión
    session.pop('username', None)
    session.pop('logueado', None)  # También puedes eliminar la variable 'logueado'
    session.pop('id', None)
    session.pop('id_role', None)
    return redirect(url_for('access_login'))  # Redirige al login


#  Pagina del menu
@app.route('/menu')
def menu():
    return render_template('menu/menu.html')



#      Pagina sobre nosotros
@app.route('/about')
def about():
    # Lógica para renderizar la página "Acerca de"
    return render_template('menu/about.html')

#      Paginas de contactos
@app.route('/contact')
def contact():
    return render_template("menu/contact.html")

#        Sistema de reservas
@app.route('/concierto')
def concierto():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events WHERE category = 'Música y Conciertos'")
    datos = cursor.fetchall()
    cursor.close()
    return render_template('eventos/concierto.html', datos=datos)

@app.route('/arte_cultura')
def arte_cultura():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events WHERE category = 'Arte y Cultura'")
    datos = cursor.fetchall()
    cursor.close()
    return render_template('eventos/arte.html', datos=datos)

@app.route('/festivales')
def festivales():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events WHERE category = 'Eventos Comunitarios y Festivales'")
    datos = cursor.fetchall()
    cursor.close()
    return render_template('eventos/festivales.html', datos=datos)

@app.route('/conferencia')
def conferencia():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events WHERE category = 'Conferencia'")
    datos = cursor.fetchall()
    cursor.close()
    return render_template('eventos/conferencia.html', datos=datos)

@app.route('/talleres')
def talleres():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events WHERE category = 'Educación y Talleres'")
    datos = cursor.fetchall()
    cursor.close()
    return render_template('eventos/talleres.html', datos=datos)

#       Carrito de los Eventos
@app.route('/events', methods=['GET', 'POST'])
def eventos_disponibles():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM events")
        datos = cursor.fetchall()
        return render_template('eventos/evento.html', datos=datos)
    except Exception as e:
        return str(e)

@app.route('/reservar_evento/<int:id>', methods=['GET', 'POST'])
def reservar_evento(id):
    if 'id' not in session:  # Asegúrate que el usuario está logueado
        flash("Debes iniciar sesión para reservar", "error")
        return redirect(url_for('access_login'))

    cursor = mysql.connection.cursor()
    
    try:
        # Verificar que el evento existe
        cursor.execute("SELECT * FROM events WHERE id = %s", (id,))
        dato = cursor.fetchone()

        if not dato:
            flash("Evento no encontrado.", "error")
            return redirect(url_for('eventos_disponibles'))

        if request.method == 'POST':
            # Validación básica
            required_fields = ['nombre', 'email', 'tickets', 'date',
                             'amount_paid', 'payment_date', 'card_number',
                             'card_holder', 'card_expiry', 'card_cvv']
            
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    flash(f"Falta el campo: {field}", "error")
                    return render_template('eventos/reservations.html', dato=dato)

            try:
                # Procesar datos
                nombre = request.form['nombre']
                email = request.form['email']
                tickets = int(request.form['tickets'])
                date = request.form['date']
                price = request.form['amount_paid']
                payment_date = request.form['payment_date']
                user_id = session['id']  # ID del usuario logueado
                
                if tickets <= 0:
                    flash("Número de tickets inválido", "error")
                    return render_template('eventos/reservations.html', dato=dato)

                # VERIFICAR QUE EL USUARIO EXISTE
                cursor.execute("SELECT id FROM user WHERE id = %s", (user_id,))
                if not cursor.fetchone():
                    flash("Usuario no válido", "error")
                    return redirect(url_for('access_login'))

                # Insertar reserva
                cursor.execute(
                    """INSERT INTO bookings 
                    (name_client, email_client, id_event, id_user, date, number_of_reserved_tickets) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (nombre, email, id, user_id, date, tickets)
                )
                reservation_id = cursor.lastrowid

                # Insertar pago (asegurando que id_user es válido)
                cursor.execute(
                    """INSERT INTO payment 
                    (evento_id, id_user, amount_paid, payment_date, card_number, card_holder, card_expiry_date, card_cvv) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (id, user_id, price, payment_date, 
                     request.form['card_number'], 
                     request.form['card_holder'],
                     request.form['card_expiry'],
                     request.form['card_cvv'])
                )

                mysql.connection.commit()

                # Generar factura
                factura_filename = f"factura_{id}_{int(time.time())}.pdf"
                factura_path = os.path.join(app.root_path, 'static', 'factura', factura_filename)
                os.makedirs(os.path.dirname(factura_path), exist_ok=True)
                create_invoice(factura_path, nombre, tickets, dato)
                
                # Generar ticket
                ticket_filename, ticket_path = generate_ticket(
                    reservation_id, 
                    dato['name'],  # Nombre del evento
                    nombre,        # Nombre del cliente
                    tickets,       # Número de tickets
                    dato['event_date'],  # Fecha del evento
                    dato['event_hour'],  # Hora del evento
                    dato['place'],
                    dato['image_url']   # Lugar del evento (nuevo parámetro)
                )
                
                # Guardar en sesión para descarga
                session['pdf_filename'] = factura_filename
                session['pdf_path'] = factura_path
                session['ticket_filename'] = ticket_filename
                session['ticket_path'] = ticket_path
                session['email_cliente'] = email

                # Enviar factura y ticket por correo
                success, message = enviar_factura_y_ticket(email, factura_path, ticket_path)
                
                if success:
                    flash("Reserva completada. Factura y ticket enviados a tu correo", "success")
                else:
                    flash(f"Reserva completada pero error al enviar documentos: {message}", "warning")

                return redirect(url_for('confirmacion'))
                
            except ValueError:
                mysql.connection.rollback()
                flash("Datos numéricos inválidos", "error")
                return render_template('eventos/reservations.html', dato=dato)
                
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error: {str(e)}", "error")
                return render_template('eventos/reservations.html', dato=dato)

        return render_template('eventos/reservations.html', dato=dato)

    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for('eventos_disponibles'))
    finally:
        cursor.close()


@app.route('/confirmacion')
def confirmacion():
    if 'pdf_filename' not in session or 'ticket_filename' not in session:
        flash("No hay documentos disponibles", "error")
        return redirect(url_for('eventos_disponibles'))
        
    # Construir las rutas para los templates
    factura_url = url_for('static', filename='factura/' + session['pdf_filename'])
    ticket_url = url_for('static', filename='tickets/' + session['ticket_filename'])
    
    return render_template('eventos/confirmacion.html', 
                         factura_file_path=factura_url,
                         ticket_file_path=ticket_url)


def enviar_factura_y_ticket(destinatario, factura_path, ticket_path):
    """
    Envía factura y ticket por email de forma segura
    
    Args:
        destinatario (str): Email del destinatario
        factura_path (str): Ruta al archivo PDF de factura
        ticket_path (str): Ruta al archivo PDF de ticket
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Configuración desde variables de entorno
    email_user = os.getenv('EMAIL_USER', 'boolingsr@gmail.com')
    email_password = os.getenv('EMAIL_APP_PASSWORD', 'z r s g s v l q d c n g l b e u')
    
    if not email_user or not email_password:
        return False, "Configuración de email no encontrada"
    
    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = destinatario
    msg['Subject'] = Header('Reserva Confirmada - Factura y Ticket', 'utf-8')
    
    # Cuerpo del mensaje
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #2c3e50;">¡Reserva Confirmada!</h2>
                <p>Estimado cliente,</p>
                <p>Adjunto encontrarás:</p>
                <ul>
                    <li>La factura de tu reserva</li>
                    <li>Tu ticket de entrada (imprímelo o guárdalo en tu móvil)</li>
                </ul>
                <p>Fecha de envío: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <br>
                <p>Gracias por confiar en nosotros,</p>
                <p><strong>Equipo Boolings Reserves</strong></p>
                <p style="font-size: 12px; color: #7f8c8d;">
                    Este es un mensaje automático, por favor no respondas directamente.
                </p>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))
    
    # Adjuntar factura
    try:
        with open(factura_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(factura_path))
        part['Content-Disposition'] = f'attachment; filename="Factura_{os.path.basename(factura_path)}"'
        msg.attach(part)
    except FileNotFoundError:
        return False, "Archivo de factura no encontrado"
    
    # Adjuntar ticket
    try:
        with open(ticket_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(ticket_path))
        part['Content-Disposition'] = f'attachment; filename="Ticket_{os.path.basename(ticket_path)}"'
        msg.attach(part)
    except FileNotFoundError:
        return False, "Archivo de ticket no encontrado"
    
    # Enviar email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_password)
            server.send_message(msg)
        return True, f"Documentos enviados a {destinatario}"
    except smtplib.SMTPAuthenticationError:
        return False, "Error de autenticación con Gmail"
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"


@app.route('/enviar_factura')
def enviar_factura():
    if 'email_cliente' not in session or 'pdf_path' not in session:
        flash("No se puede enviar la factura", "error")
        return redirect(url_for('eventos_disponibles'))
    
    # Verificar si el archivo existe
    if not os.path.exists(session['pdf_path']):
        flash("El archivo de factura no existe", "error")
        return redirect(url_for('eventos_disponibles'))
    
    # Enviar email
    success, message = enviar_factura_y_ticket(session['email_cliente'], session['pdf_path'])
    
    if success:
        flash(message, "success")
    else:
        flash(f"Error: {message}", "error")
    
    return redirect(url_for('eventos_disponibles'))


def create_invoice(file_path, nombre, tickets, dato, descuento=0.1):
    # Configuración inicial
    current_date = datetime.now().strftime("%d/%m/%Y")
    width, height = letter
    margin = 0.5 * inch
    content_width = width - 2 * margin

    # Colores modernos
    primary_color = HexColor("#3498db")  # Azul brillante
    secondary_color = HexColor("#2ecc71")  # Verde esmeralda
    dark_color = HexColor("#2c3e50")     # Azul oscuro
    light_color = HexColor("#ecf0f1")    # Gris claro
    accent_color = HexColor("#e74c3c")    # Rojo

    # Validar datos
    event_name = dato.get('name', 'Evento Desconocido')
    event_date = dato.get('date', 'Fecha no especificada')
    event_price = float(dato.get('price', 0))
    event_total = tickets * event_price
    total_descuento = event_total * descuento
    sub_total = event_total - total_descuento

    # Crear PDF
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # --- Fondo degradado ---
    c.setFillColor(light_color)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(primary_color)
    c.rect(0, height - inch, width, inch, fill=1, stroke=0)

    # --- Encabezado moderno ---
    logo_path = os.path.join(app.root_path, 'static', 'img', 'Boolings Reserves.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, margin, height - margin - 0.8*inch, 
                   width=1.5*inch, height=0.8*inch, 
                   preserveAspectRatio=True, mask='auto')

    # Información de la empresa
    c.setFont('Helvetica-Bold', 16)
    c.setFillColor(colors.white)
    c.drawString(margin + 1.6*inch, height - margin - 0.3*inch, "BOOLINGS RESERVES")
    
    c.setFont('Helvetica', 9)
    c.setFillColor(dark_color)
    c.drawString(margin, height - margin - 1.1*inch, "173 Calle Pedernales, Ensanche Espallait")
    c.drawString(margin, height - margin - 1.3*inch, "+1 234 567 8900 | boolingsr@empresa.com")
    c.drawString(margin, height - margin - 1.5*inch, "www.boolingsreserves.com")

    # Número de factura y fecha
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(dark_color)
    c.drawRightString(width - margin, height - margin - 0.3*inch, f"FACTURA #{invoice_number}")
    c.setFont('Helvetica', 10)
    c.drawRightString(width - margin, height - margin - 0.6*inch, f"Fecha: {current_date}")

    # --- Información del cliente ---
    c.setFillColor(primary_color)
    c.rect(margin, height - margin - 2*inch, content_width, 0.25*inch, fill=1, stroke=0)
    
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(colors.white)
    c.drawString(margin + 0.1*inch, height - margin - 1.9*inch, "INFORMACIÓN DEL CLIENTE")
    
    c.setFont('Helvetica', 10)
    c.setFillColor(dark_color)
    c.drawString(margin, height - margin - 2.3*inch, f"Nombre: {nombre}")
    c.drawString(margin, height - margin - 2.5*inch, f"Evento: {event_name}")
    c.drawString(margin, height - margin - 2.7*inch, f"Fecha del evento: {event_date}")
    c.drawString(margin, height - margin - 2.9*inch, f"N° de tickets: {tickets}")

    # --- Tabla de items ---
    table_start = height - margin - 3.4*inch
    
    # Encabezado de la tabla
    c.setFillColor(secondary_color)
    c.rect(margin, table_start - 0.25*inch, content_width, 0.25*inch, fill=1, stroke=0)
    
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(colors.white)
    c.drawString(margin + 0.1*inch, table_start - 0.2*inch, "DESCRIPCIÓN")
    c.drawString(margin + content_width*0.6, table_start - 0.2*inch, "CANTIDAD")
    c.drawString(margin + content_width*0.75, table_start - 0.2*inch, "PRECIO")
    c.drawString(margin + content_width*0.9, table_start - 0.2*inch, "TOTAL")

    # Contenido de la tabla
    c.setFont('Helvetica', 9)
    c.setFillColor(dark_color)
    
    # Item 1
    c.drawString(margin + 0.1*inch, table_start - 0.5*inch, f"Entrada general - {event_name}")
    c.drawString(margin + content_width*0.6, table_start - 0.5*inch, str(tickets))
    c.drawString(margin + content_width*0.75, table_start - 0.5*inch, f"${event_price:.2f}")
    c.drawString(margin + content_width*0.9, table_start - 0.5*inch, f"${event_total:.2f}")
    
    # Descuento
    c.setFillColor(accent_color)
    c.drawString(margin + 0.1*inch, table_start - 0.8*inch, f"Descuento ({descuento*100}%)")
    c.drawString(margin + content_width*0.9, table_start - 0.8*inch, f"-${total_descuento:.2f}")

    # Línea divisoria
    c.setStrokeColor(HexColor("#bdc3c7"))
    c.setLineWidth(0.5)
    c.line(margin, table_start - inch, width - margin, table_start - inch)

    # --- Totales ---
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(dark_color)
    
    c.drawRightString(width - margin - 1.5*inch, table_start - 1.3*inch, "SUBTOTAL:")
    c.drawRightString(width - margin - 1.5*inch, table_start - 1.6*inch, "DESCUENTO:")
    c.drawRightString(width - margin - 1.5*inch, table_start - 1.9*inch, "TOTAL:")
    
    c.drawRightString(width - margin, table_start - 1.3*inch, f"${event_total:.2f}")
    c.drawRightString(width - margin, table_start - 1.6*inch, f"-${total_descuento:.2f}")
    
    c.setFillColor(secondary_color)
    c.drawRightString(width - margin, table_start - 1.9*inch, f"${sub_total:.2f}")

    # Línea decorativa
    c.setStrokeColor(primary_color)
    c.setLineWidth(2)
    c.line(width - margin - 3*inch, table_start - 2.1*inch, width - margin, table_start - 2.1*inch)

    # --- Notas ---
    c.setFont('Helvetica', 8)
    c.setFillColor(dark_color)
    notes_start = table_start - 2.5*inch
    c.drawString(margin, notes_start, "NOTAS:")
    c.drawString(margin, notes_start - 0.2*inch, "- Esta factura es válida como comprobante de pago.")
    c.drawString(margin, notes_start - 0.4*inch, "- Presentar este documento al ingresar al evento.")
    c.drawString(margin, notes_start - 0.6*inch, "- No se aceptan devoluciones ni cambios.")
    c.drawString(margin, notes_start - 0.8*inch, "- Para consultas contacte a boolingsr@empresa.com")

    # --- Pie de página ---
    c.setFillColor(primary_color)
    c.rect(0, 0, width, 0.8*inch, fill=1, stroke=0)
    
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.white)
    c.drawCentredString(width/2, 0.5*inch, "Gracias por su preferencia!")
    c.drawCentredString(width/2, 0.3*inch, "© 2024 Boolings Reserves. Todos los derechos reservados.")

    # Finalizar PDF
    c.save()

black = HexColor("#000000")
white = HexColor("#FFFFFF")

def generate_ticket(reservation_id, event_name, client_name, num_tickets, event_date, event_time, event_place, event_image_path=None):
    """Genera un PDF con el ticket de reserva con diseño ultra compacto"""
    try:
        # Validación de datos
        if not isinstance(num_tickets, int) or num_tickets <= 0:
            raise ValueError("Número de tickets inválido")
        
        if not reservation_id or not isinstance(reservation_id, (int, str)):
            raise ValueError("ID de reserva inválido")

        # Configuración del documento
        ticket_filename = f"ticket_{reservation_id}.pdf"
        ticket_path = os.path.join('static', 'tickets', ticket_filename)
        logo_path = os.path.join('static', 'img', 'Boolings Reserves.png')
        
        os.makedirs(os.path.dirname(ticket_path), exist_ok=True)

        # Tamaño del ticket (3.5 x 7 pulgadas)
        ticket_width, ticket_height = 3.5 * inch, 7 * inch
        c = canvas.Canvas(ticket_path, pagesize=(ticket_width, ticket_height))
        
        # Margenes y áreas
        margin = 0.15 * inch
        content_width = ticket_width - (2 * margin)
        current_y = ticket_height - margin  # Comenzamos desde arriba

        ## DISEÑO COMPACTO ##

        # 1. Encabezado negro (compacto)
        header_height = 0.7 * inch
        c.setFillColor(black)
        c.rect(0, current_y - header_height, ticket_width, header_height, fill=1, stroke=0)
        
        # Logo centrado en el encabezado
        try:
            logo_img = ImageReader(logo_path)
            logo_height = 0.5 * inch
            logo_width = 1.8 * inch
            c.drawImage(logo_img, 
                       (ticket_width - logo_width)/2, 
                       current_y - header_height + (header_height - logo_height)/2,
                       width=logo_width, 
                       height=logo_height,
                       preserveAspectRatio=True, 
                       mask='auto')
        except:
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(white)
            c.drawCentredString(ticket_width/2, current_y - header_height/2 - 0.1*inch, "BOOLINGS RESERVES")
        
        current_y -= header_height + 0.1 * inch

        # 2. Imagen del evento (si existe)
        if event_image_path and os.path.exists(event_image_path):
            try:
                img_height = 1.1 * inch  # Altura fija compacta
                img = ImageReader(event_image_path)
                c.drawImage(img, margin, current_y - img_height,
                          width=content_width, height=img_height,
                          preserveAspectRatio=True, anchor='c', mask='auto')
                current_y -= img_height + 0.1 * inch
            except Exception as e:
                print(f"Error cargando imagen: {str(e)}")

        # 3. Título compacto
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(black)
        c.drawCentredString(ticket_width/2, current_y - 0.25*inch, "ENTRADA CONFIRMADA")
        current_y -= 0.4 * inch

        # 4. Línea divisoria fina
        c.setStrokeColor(HexColor("#2ecc71"))
        c.setLineWidth(0.5)
        c.line(margin, current_y, ticket_width - margin, current_y)
        current_y -= 0.15 * inch

        # 5. Detalles ultra compactos
        formatted_date = event_date.strftime('%d/%m/%Y') if hasattr(event_date, 'strftime') else str(event_date)
        formatted_time = str(event_time) if event_time else "Por confirmar"

        details = [
            ("Evento:", event_name[:25].upper() + ("..." if len(event_name) > 25 else "")),
            ("Cliente:", client_name[:20] + ("..." if len(client_name) > 20 else "")),
            ("Fecha:", formatted_date),
            ("Hora:", formatted_time),
            ("Lugar:", event_place[:20] + ("..." if len(event_place) > 20 else "")),
            ("Entradas:", str(num_tickets))
        ]
        
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(black)
        c.drawString(margin, current_y, "DETALLES:")
        current_y -= 0.2 * inch

        c.setFont("Helvetica", 7)
        for label, value in details:
            c.drawString(margin + 0.1*inch, current_y, label)
            c.setFont("Helvetica-Bold", 7)
            c.drawString(margin + 0.8*inch, current_y, value)
            c.setFont("Helvetica", 7)
            current_y -= 0.18 * inch  # Espaciado mínimo

        # 6. Código QR compacto
        # Generar la URL de la factura
        factura_filename = f"factura_{reservation_id}_{int(time.time())}.pdf"
        qr_data = f"http://127.0.0.1:5000/static/factura/{factura_filename}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,  # Más compacto
            border=1,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_array = BytesIO()
        qr_img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        
        # Tamaño reducido del QR
        qr_size = 0.9 * inch
        c.drawImage(ImageReader(img_byte_array), 
                   (ticket_width - qr_size)/2, 
                   current_y - qr_size - 0.1*inch,
                   width=qr_size, 
                   height=qr_size)
        
        # Texto QR compacto
        c.setFont("Helvetica-Bold", 6)
        c.setFillColor(HexColor("#2ecc71"))
        c.drawCentredString(ticket_width/2, current_y - qr_size - 0.2*inch, "ESCANEAR PARA VER FACTURA")
        
        # 7. ID de reserva compacto
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HexColor("#e74c3c"))
        c.drawCentredString(ticket_width/2, current_y - qr_size - 0.4*inch, f"RESERVA: {reservation_id}")

        # 8. Footer mínimo
        footer_height = 0.25 * inch
        c.setFillColor(black)
        c.rect(0, 0, ticket_width, footer_height, fill=1, stroke=0)
        c.setFont("Helvetica", 6)
        c.setFillColor(white)
        c.drawCentredString(ticket_width/2, 0.08*inch, "www.boolingsreserves.com")

        c.save()
        return ticket_filename, ticket_path

    except Exception as e:
        print(f"Error generando ticket: {str(e)}")
        error_filename = f"error_ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        error_path = os.path.join('static', 'tickets', error_filename)
        
        c = canvas.Canvas(error_path, pagesize=(3.5*inch, 1.5*inch))
        c.setFillColor(HexColor("#e74c3c"))
        c.rect(0, 1.3*inch, 3.5*inch, 0.2*inch, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(white)
        c.drawString(0.2*inch, 1.35*inch, "ERROR EN TICKET")
        c.setFont("Helvetica", 7)
        c.setFillColor(black)
        c.drawString(0.2*inch, 1.0*inch, f"Motivo: {str(e)[:50]}")
        c.save()
        
        return error_filename, error_path

#        Pagina para el Admin
@app.route('/menu_admin')
def menu_admin():
    return render_template('admin/menuadmin.html')


# CRUD de Eventos
@app.route('/eventos')
def evento():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM events")
    eventos = cur.fetchall()
    cur.close()
    if eventos:    
        return render_template('admin/eventos.html', eventos=eventos)
    else:
        return "No se encontraron eventos", 404

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM events WHERE id = %s", (id,))
    evento = cur.fetchone()
    cur.close()
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            name = request.form.get('name', '').strip()
            event_date = request.form.get('event_date', '').strip()
            event_hour = request.form.get('event_hour', '').strip()
            place = request.form.get('place', '').strip()
            category = request.form.get('category', '').strip()
            price = request.form.get('price', '0').strip()
            reservation_status = request.form.get('reservation_status', 'available').strip()
            
            # Validación básica
            if not name:
                flash("El nombre del evento es requerido", "error")
                return redirect(url_for('edit', id=id))
            
            # Manejar la carga de archivos
            image_path = None
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    if allowed_file(image.filename):
                        filename = secure_filename(f"event_{id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}")
                        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        image.save(image_path)
                        
                        # Eliminar la imagen anterior si existe
                        if evento and evento.get('image_url'):
                            try:
                                old_image_path = evento['image_url']
                                if os.path.exists(old_image_path):
                                    os.remove(old_image_path)
                            except Exception as e:
                                print(f"Error eliminando imagen anterior: {str(e)}")
                    else:
                        flash("Tipo de archivo no permitido. Use .png, .jpg, .jpeg o .gif", "error")
            
            # Actualizar la base de datos
            cur = mysql.connection.cursor()
            
            if image_path:
                cur.execute("""
                    UPDATE events 
                    SET name = %s, event_date = %s, event_hour = %s, 
                        place = %s, price = %s, category = %s, 
                        reservation_status = %s, image_url = %s
                    WHERE id = %s
                    """, 
                    (name, event_date, event_hour, place, price, category, reservation_status, image_path, id))
            else:
                cur.execute("""
                    UPDATE events 
                    SET name = %s, event_date = %s, event_hour = %s, 
                        place = %s, price = %s, category = %s, 
                        reservation_status = %s
                    WHERE id = %s
                    """, 
                    (name, event_date, event_hour, place, price, category, reservation_status, id))
            
            mysql.connection.commit()
            cur.close()
            
            flash("Evento actualizado correctamente", "success")
            return redirect(url_for('evento'))
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al actualizar el evento: {str(e)}", "error")
            return redirect(url_for('edit', id=id))
    
    return render_template('admin/eventos.html', dato=evento)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = mysql.connection.cursor()
    # Eliminar pagos asociados a este evento
    cur.execute("DELETE FROM payment WHERE evento_id = %s", (id,))
    # Ahora se puede eliminar el evento
    cur.execute("DELETE FROM events WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('evento'))


@app.route('/add_events', methods=['GET', 'POST'])
def add_events():
    if request.method == 'POST':
        _nombre = request.form['name']
        _fecha = request.form['event_date']
        _hora = request.form['event_hour']
        _lugar = request.form['place']
        _precio = request.form['price']
        _categoria = request.form['category']
        _reserva_status = request.form['reservation_status']
        
        # Valor por defecto si no se sube imagen
        image_url = "default.jpg"  # o "" si prefieres una cadena vacía
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_url = filename  # Guardar el nombre del archivo
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO events 
            (name, event_date, event_hour, place, price, category, reservation_status, image_url) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (_nombre, _fecha, _hora, _lugar, _precio, _categoria, _reserva_status, image_url))
        
        mysql.connection.commit()
        cursor.close()
        
        flash("Evento agregado correctamente")
        return redirect(url_for('evento'))
    
    return render_template('admin/eventos.html')


#Crud reservas
@app.route('/reservas')
def reservas():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM bookings")
        datos = cursor.fetchall()
        return render_template('admin/reservas.html', datos=datos)
    except Exception as e:
        return str(e)

@app.route('/editar_reserva/<int:id>', methods=['GET', 'POST'])
def editar_reserva(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        tickets = int(request.form['tickets'])
        date = request.form['date']
        # Ejecutar una consulta SQL para actualizar el registro en la tabla
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE bookings SET name_client = %s, date = %s, number_of_reserved_tickets = %s WHERE id = %s", (nombre,date,tickets, id))

        mysql.connection.commit()
        flash("Reserva actualizado correctamente")
        return redirect(url_for('reservas'))
    else:
        cursor = mysql.connection.cursor()
        # Obtener los datos del registro a editar
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (id,))
        dato = cursor.fetchone()
        return render_template('admin/reservas', dato=dato)


@app.route('/eliminar_reserva/<int:id>', methods=['POST'])
def eliminar_reserva(id):
    cursor = mysql.connection.cursor()
    # Ejecutar una consulta SQL para eliminar el registro de la tabla]
    cursor.execute("DELETE FROM bookings WHERE id = %s", (id,))
    mysql.connection.commit()
    flash("Usuario eliminado correctamente")
    return redirect(url_for('reservas'))

# Ruta principal para mostrar todos los usuarios
@app.route('/user')
def index():
    # Ejecutar una consulta SQL para obtener los datos de la tabla
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user")
    datos = cursor.fetchall()
    return render_template('admin/user.html', datos=datos)

# Ruta para agregar un nuevo usuario
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        _username = request.form['username']
        _email = request.form['email']
        _password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (username, email, password, id_role) VALUES (%s, %s, %s, %s)",
                       (_username, _email, _password, '2'))
        mysql.connection.commit()
        flash("Usuario agregado correctamente")
        return redirect(url_for('index'))
    return render_template('admin/lista/user.html')

# Ruta para la página de edición de datos
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        nombre = request.form['username']
        correo = request.form['email']
        contrasena = request.form['password']
        # Ejecutar una consulta SQL para actualizar el registro en la tabla
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE user SET username = %s, email = %s, password = %s WHERE id = %s",
                       (nombre, correo, contrasena, id))
        mysql.connection.commit()
        flash("Usuario actualizado correctamente")
        return redirect(url_for('index'))
    else:
        cursor = mysql.connection.cursor()
        # Obtener los datos del registro a editar
        cursor.execute("SELECT * FROM user WHERE id = %s", (id,))
        dato = cursor.fetchone()
        return render_template('admin/user.html', dato=dato)

# Ruta para la eliminación de datos
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    cursor = mysql.connection.cursor()
    # Ejecutar una consulta SQL para eliminar el registro de la tabla]
    cursor.execute("DELETE FROM user WHERE id = %s", (id,))
    mysql.connection.commit()
    flash("Usuario eliminado correctamente")
    return redirect(url_for('index'))

@app.route('/search_admin', methods=['GET'])
def search_admin():
    try:
        search = request.args['search']
    except BadRequestKeyError:
        return jsonify({'error': 'Parámetro "search" faltante'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events WHERE name LIKE %s", ("%" + search + "%",))
    datos = cursor.fetchall()
    return render_template('admin/eventos.html', datos=datos)

#       Buscador para buscar los usuarios
@app.route('/search_user', methods=['GET'])
def search_user():
    try:
        search = request.args['search']
    except BadRequestKeyError:
        return jsonify({'error': 'Parámetro "search" faltante'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user WHERE username LIKE %s", ("%" + search + "%",))
    datos = cursor.fetchall()
    return render_template('admin/user.html', datos=datos)

# Función para obtener los datos de los usuarios desde la base de datos MySQL
def obtener_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user")
    usuarios = cursor.fetchall()
    cursor.close()
    return usuarios



def generar_reporte_usuarios():
    # Obtener los datos de los usuarios desde la base de datos MySQL
    usuarios = obtener_usuarios()

    # Configuración del documento
    pdf_filename = "reporte_usuarios_premium.pdf"
    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter, 
                          rightMargin=30, leftMargin=30,
                          topMargin=50, bottomMargin=30)

    # Estilos premium
    styles = getSampleStyleSheet()
    
    # Paleta de colores moderna
    COLOR_PRIMARIO = "#3498db"
    COLOR_SECUNDARIO = "#2ecc71"
    COLOR_TERCIARIO = "#e74c3c"
    COLOR_FONDO = "#f8f9fa"
    COLOR_TEXTO = "#2c3e50"
    COLOR_ENCABEZADO = "#1a237e"
    
    # Estilo para el título
    estilo_titulo = ParagraphStyle(
        name="TituloPremium",
        fontSize=28,
        leading=36,
        textColor=colors.HexColor(COLOR_ENCABEZADO),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=10,
        underlineWidth=1,
        underlineColor=colors.HexColor(COLOR_SECUNDARIO),
        underlineOffset=-6
    )
    
    # Estilo para subtítulos
    estilo_subtitulo = ParagraphStyle(
        name="SubtituloPremium",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.HexColor(COLOR_PRIMARIO),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName="Helvetica-BoldOblique"
    )
    
    # Estilo para contenido
    estilo_contenido = ParagraphStyle(
        name="ContenidoPremium",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor(COLOR_TEXTO),
        leading=16,
        spaceAfter=12,
        fontName="Helvetica"
    )
    
    # Estilo para el pie de página
    estilo_pie = ParagraphStyle(
        name="PiePremium",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#7f8c8d"),
        alignment=TA_CENTER,
        fontName="Helvetica-Oblique"
    )

    # Encabezado con diseño premium
    logo = "static/img/Boolings Reserves.png"
    imagen_logo = Image(logo, width=2.2*inch, height=0.9*inch)  # Tamaño ajustado
    imagen_logo.hAlign = 'CENTER'

    # Fondo decorativo para el encabezado
    encabezado_fondo = Table([[imagen_logo]], colWidths=[7*inch], rowHeights=[1.5*inch])
    encabezado_fondo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_FONDO)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(COLOR_PRIMARIO)),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    
    titulo = Paragraph("REPORTE DE USUARIOS PREMIUM", estilo_titulo)
    subtitulo = Paragraph("Información detallada de usuarios registrados en Boolings Reserves", estilo_subtitulo)
    
    # Fecha de generación con diseño especial
    fecha_actual = datetime.now().strftime("%d de %B de %Y - %H:%M")
    fecha_texto = Table([[Paragraph(f"<b>Generado el:</b> {fecha_actual}", estilo_subtitulo)]], 
                       colWidths=[7*inch])
    fecha_texto.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_FONDO)),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor(COLOR_TERCIARIO)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(COLOR_SECUNDARIO)),
    ]))
    
    # Descripción con fondo destacado
    descripcion = Table([[Paragraph("""
    <b>Este documento contiene la lista completa de usuarios registrados en el sistema Boolings Reserves.</b><br/>
    Se muestra información detallada incluyendo identificador único, nombre de usuario y dirección de correo electrónico.
    """, estilo_contenido)]], colWidths=[7*inch])
    
    descripcion.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f8e9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#c8e6c9")),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Tabla de datos con diseño premium
    data = [["ID", "NOMBRE DE USUARIO", "CORREO ELECTRÓNICO"]]
    for usuario in usuarios:
        data.append([usuario["id"], usuario["username"], usuario["email"]])
    
    tabla = Table(data, colWidths=[0.8*inch, 2.2*inch, 3.5*inch], repeatRows=1)
    
    # Estilo de tabla premium
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_ENCABEZADO)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ffffff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor(COLOR_SECUNDARIO)),
    ])
    
    # Efecto zebra para las filas
    for i in range(1, len(data)):
        if i % 2 == 0:
            estilo_tabla.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f5f5f5"))
    
    # Resaltar la primera columna
    estilo_tabla.add('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor(COLOR_TERCIARIO))
    estilo_tabla.add('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold')
    
    tabla.setStyle(estilo_tabla)
    
    # Pie de página con diseño moderno
    pie_texto = f"Boolings Reserves | Reporte generado automáticamente | Página 1 | {datetime.now().strftime('%d/%m/%Y')}"
    pie_pagina = Table([[Paragraph(pie_texto, estilo_pie)]], colWidths=[7*inch])
    pie_pagina.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_FONDO)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Construcción del documento con elementos premium
    elementos = [
        Spacer(1, 0.5*inch),
        encabezado_fondo,
        Spacer(1, 0.3*inch),
        titulo,
        subtitulo,
        Spacer(1, 0.2*inch),
        fecha_texto,
        Spacer(1, 0.4*inch),
        descripcion,
        Spacer(1, 0.5*inch),
        tabla,
        Spacer(1, 0.3*inch),
        pie_pagina
    ]
    
    # Generar PDF con estilo premium
    pdf.build(elementos)
    
    return pdf_filename


# Utiliza esta función en tu ruta de Flask para mostrar el reporte en PDF
@app.route('/ver_pdf_usuarios')
def ver_pdf_usuarios():
    pdf_filename = generar_reporte_usuarios()
    with open(pdf_filename, 'rb') as f:
        pdf_contents = f.read()
    response = make_response(pdf_contents)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_usuarios.pdf'
    return response

# Función para obtener los datos de los usuarios desde la base de datos MySQL
def obtener_eventos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events")
    usuarios = cursor.fetchall()
    cursor.close()
    return usuarios

def generar_reporte_eventos():
    # Obtener los datos de los eventos desde la base de datos
    eventos = obtener_eventos()

    # Configuración del documento con márgenes optimizados
    pdf_filename = "reporte_eventos_premium.pdf"
    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter,
                          rightMargin=40, leftMargin=40,
                          topMargin=60, bottomMargin=40)

    # Paleta de colores moderna
    COLOR_PRIMARIO = "#2c3e50"
    COLOR_SECUNDARIO = "#e74c3c"
    COLOR_TERCIARIO = "#3498db"
    COLOR_FONDO = "#f8f9fa"
    COLOR_TEXTO = "#34495e"
    COLOR_ENCABEZADO = "#1a5276"

    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    # Estilo para el título principal
    estilo_titulo = ParagraphStyle(
        name="TituloEvento",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor(COLOR_PRIMARIO),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=15,
        underlineWidth=1,
        underlineColor=colors.HexColor(COLOR_SECUNDARIO),
        underlineOffset=-8
    )
    
    # Estilo para subtítulos
    estilo_subtitulo = ParagraphStyle(
        name="SubtituloEvento",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.HexColor(COLOR_SECUNDARIO),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName="Helvetica-Bold"
    )
    
    # Estilo para contenido
    estilo_contenido = ParagraphStyle(
        name="ContenidoEvento",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor(COLOR_TEXTO),
        leading=14,
        spaceAfter=10,
        fontName="Helvetica"
    )
    
    # Estilo para el pie de página
    estilo_pie = ParagraphStyle(
        name="PieEvento",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#7f8c8d"),
        alignment=TA_CENTER,
        fontName="Helvetica-Oblique"
    )

    # Encabezado con logo y título
    # Logo ajustado (mismo tamaño que en usuarios para consistencia)
    logo = "static/img/Boolings Reserves.png"
    imagen_logo = Image(logo, width=2.2*inch, height=0.9*inch)  # Tamaño igual al anterior
    imagen_logo.hAlign = 'CENTER'
    
    # Marco decorativo para el encabezado
    encabezado = Table([[imagen_logo]], colWidths=[7*inch])
    encabezado.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_FONDO)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(COLOR_PRIMARIO)),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    
    titulo = Paragraph("REPORTE DE EVENTOS DISPONIBLES", estilo_titulo)
    
    # Fecha de generación con diseño especial
    fecha_actual = datetime.now().strftime("%d de %B de %Y - %H:%M")
    fecha_texto = Table([[Paragraph(f"<b>Generado el:</b> {fecha_actual}", estilo_subtitulo)]], 
                       colWidths=[7*inch])
    fecha_texto.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_FONDO)),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor(COLOR_TERCIARIO)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(COLOR_SECUNDARIO)),
    ]))
    
    # Descripción con fondo destacado
    descripcion = Table([[Paragraph("""
    <b>Información detallada de eventos disponibles en Boolings Reserves</b><br/>
    Este reporte muestra todos los eventos registrados en el sistema con sus fechas y precios correspondientes.
    """, estilo_contenido)]], colWidths=[7*inch])
    
    descripcion.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eaf2f8")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#aed6f1")),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    # Tabla de datos con diseño mejorado
    data = [["ID", "NOMBRE DEL EVENTO", "FECHA", "PRECIO (USD)"]]
    for evento in eventos:
        # Formatear precio con símbolo de dólar y 2 decimales
        precio_formateado = f"${evento['price']:.2f}"
        # Formatear fecha si es necesario
        fecha_formateada = evento["event_date"].strftime("%d/%m/%Y") if hasattr(evento["event_date"], 'strftime') else evento["event_date"]
        data.append([evento["id"], evento["name"], fecha_formateada, precio_formateado])
    
    tabla = Table(data, colWidths=[0.7*inch, 3*inch, 1.5*inch, 1*inch], repeatRows=1)
    
    # Estilo de tabla premium
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_ENCABEZADO)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ffffff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor(COLOR_SECUNDARIO)),
    ])
    
    # Efecto zebra para mejor legibilidad
    for i in range(1, len(data)):
        if i % 2 == 0:
            estilo_tabla.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f5f5f5"))
    
    # Resaltar columna de precios
    estilo_tabla.add('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor(COLOR_SECUNDARIO))
    estilo_tabla.add('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold')
    
    tabla.setStyle(estilo_tabla)
    
    # Pie de página con diseño moderno
    pie_texto = f"Boolings Reserves | Reporte generado automáticamente | Página 1 | {datetime.now().strftime('%d/%m/%Y')}"
    pie_pagina = Table([[Paragraph(pie_texto, estilo_pie)]], colWidths=[7*inch])
    pie_pagina.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(COLOR_FONDO)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Estadísticas resumen (opcional)
    total_eventos = len(eventos) - 1  # Restamos el encabezado
    precio_promedio = sum(float(evento['price']) for evento in eventos) / total_eventos if total_eventos > 0 else 0
    
    resumen = Table([
        [Paragraph("<b>ESTADÍSTICAS</b>", estilo_contenido)],
        [Paragraph(f"Total de eventos: {total_eventos}", estilo_contenido)],
        [Paragraph(f"Precio promedio: ${precio_promedio:.2f}", estilo_contenido)]
    ], colWidths=[2*inch])
    
    resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_PRIMARIO)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#e8f4f8")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(COLOR_TERCIARIO)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    
    # Construcción del documento
    elementos = [
        Spacer(1, 0.3*inch),
        encabezado,
        Spacer(1, 0.3*inch),
        titulo,
        fecha_texto,
        Spacer(1, 0.3*inch),
        descripcion,
        Spacer(1, 0.4*inch),
        tabla,
        Spacer(1, 0.4*inch),
        resumen,
        Spacer(1, 0.3*inch),
        pie_pagina
    ]
    
    # Generar PDF
    pdf.build(elementos)
    
    return pdf_filename
# Utiliza esta función en tu ruta de Flask para mostrar el reporte en PDF
@app.route('/ver_pdf_eventos')
def ver_pdf_eventos():
    pdf_filename = generar_reporte_eventos()
    with open(pdf_filename, 'rb') as f:
        pdf_contents = f.read()
    response = make_response(pdf_contents)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_eventos.pdf'
    return response


@app.route('/balance')
def balance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT date, number_of_reserved_tickets FROM bookings")
    data = cur.fetchall()
    cur.close()

    # Procesamiento de los datos
    dates = []
    tickets_reserved = []
    for row in data:
        dates.append(row['date'])
        tickets_reserved.append(row['number_of_reserved_tickets'])

    # Creación del gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(dates, tickets_reserved, marker='o', linestyle='-')
    plt.title('Reservas de tickets a lo largo del tiempo')
    plt.xlabel('Fecha')
    plt.ylabel('Número de tickets reservados')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Crear un archivo PDF en memoria
    pdf_output = BytesIO()
    plt.savefig(pdf_output, format='pdf')
    pdf_output.seek(0)

    # Crear una respuesta Flask con el archivo PDF como contenido
    response = make_response(pdf_output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=reservas_tickets.pdf'
    response.headers['Content-Type'] = 'application/pdf'

    return response


@app.route('/facturas')
def facturas():
    return render_template('admin/facturas.html')

@app.route('/sales')
def sales():
    return render_template('reporte.html')


# Ruta para obtener los datos de las reservas en formato JSON
@app.route('/reservas_json')
def reservas_json():
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT e.name, e.price, b.date, SUM(b.number_of_reserved_tickets) 
                   AS total_tickets, SUM(e.price) AS total_price FROM 
                   events e JOIN bookings b ON e.id = b.id_event GROUP BY e.name""")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route('/descargar_balance')
def descargar_pdf():

    # URL del contenido a convertir en PDF
    url = 'http://127.0.0.1:5000/sales'
    
    # Genera el PDF desde la URL
    pdf = pdfkit.from_url(url, False, configuration=config)

    response = Response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=factura N. 001.pdf'
    
    return response

def parse_dato(dato):
    try:
        return json.loads(dato)
    except ValueError:
        return None

def generate_pdf(event_data):
    if not event_data:
        return None

    # Crear un buffer de bytes para almacenar el PDF
    pdf_buffer = io.BytesIO()

    # Crear el documento PDF
    document = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    Story = [Spacer(1, 2*inch)]

    # Crear la tabla con los datos del evento
    data = [
        ["Evento", "Fecha", "Ubicación", "Costo por Persona", "Mínimo de Asistentes", "Costo Total Estimado"],
        [event_data['name'], event_data['event_date'], event_data['place'], event_data['price'], event_data['maximum_quota'], event_data['price'] * event_data['maximum_quota']]
    ]

    table = Table(data)
    table.setStyle(TableStyle([
       ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
       ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
       ('ALIGN',(0,0),(-1,-1),'CENTER'),
       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
       ('BACKGROUND',(0,1),(-1,-1),colors.beige),
    ]))
    Story.append(table)

    # Construir el PDF y guardar en el buffer
    document.build(Story)

    # Colocar el puntero del buffer al inicio
    pdf_buffer.seek(0)

    return pdf_buffer
    
@app.route('/ver_cotizaciones')
def ver_cotizaciones():
    dato = request.args.get('dato')  # Obtener el dato de la solicitud
    event_data = parse_dato(dato)  # Parsear el dato a un diccionario con los datos del evento
    pdf_buffer = generate_pdf(event_data)  # Pasar el dato a generate_pdf()
    if pdf_buffer:
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=reporte_cotizacion.pdf'
        return response
    else:
        return "No se encontraron datos del evento."

if __name__ == "__main__":
    app.run(debug=True)