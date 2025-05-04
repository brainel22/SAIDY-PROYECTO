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
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle,TA_LEFT,TA_RIGHT
import pdfkit

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

#    Para los errores
from werkzeug.exceptions import BadRequestKeyError
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

search_map = {
    "inicio": "menu/menu.html",
    "nosotros": "menu/about.html",
    "contacto": "menu/contact.html",
    "servicios": "menu/services.html",
    "perfil": "menu/perfil_usuario.html",
    "reservas": "eventos/evento.html",
}

#    Inicio de la pagina
@app.route('/')
def inicio():
    if 'username' in session:
        return render_template('login/login.html', username=session['username'])
    return render_template('login/register.html')

# --- Tema Oscuro ---
@app.route('/toggle_tema', methods=['POST'])
def toggle_tema():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE user SET tema_oscuro = NOT tema_oscuro WHERE id = %s", 
            (session['id'],))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

# --- Notificaciones ---
@app.route('/actualizar_notificaciones', methods=['POST'])
def actualizar_notificaciones():
    if 'loggedin' in session:
        data = request.get_json()
        cursor = mysql.connection.cursor()
        cursor.execute(
            """UPDATE user SET 
                notif_email = %s, 
                notif_app = %s 
            WHERE id = %s""",
            (data.get('notif_email', True), 
             data.get('notif_app', True), 
             session['id']))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

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


# Ruta para solicitar el restablecimiento de la contraseña
@app.route('/reset', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Enviar correo de restablecimiento de contraseña
            subject = 'Solicitud de restablecimiento de contraseña'  # Texto en español con 'ñ'
            sender_email = 'boolingsr@gmail.com'  # Cambia esto por tu dirección de correo
            password = 'z r s g s v l q d c n g l b e u'  # Usa la contraseña de aplicación generada
            recipients = [email]
            reset_link = url_for("reset_password", email=email, _external=True)
            body = f'Haz clic en el siguiente enlace para restablecer tu contraseña: {reset_link}'  # Texto en español con 'ñ'

            # Crear mensaje de correo
            msg = MIMEMultipart()
            msg['From'] = Header(sender_email, 'utf-8')  # Codificar el campo 'From' en UTF-8
            msg['To'] = Header(email, 'utf-8')  # Codificar el campo 'To' en UTF-8
            msg['Subject'] = Header(subject, 'utf-8')  # Codificar el campo 'Subject' en UTF-8

            # Adjuntar el cuerpo del mensaje con codificación UTF-8
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            try:
                # Conexión SMTP para enviar el correo
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, recipients, msg.as_string())
                flash("Se ha enviado un correo con instrucciones para restablecer tu contraseña.")
            except smtplib.SMTPAuthenticationError:
                flash("Error de autenticación: Verifica tu correo y contraseña.")
            except Exception as e:
                flash(f"Error al enviar el correo electrónico: {str(e)}")
            
            return render_template('login/reset.html')
        else:
            flash("El correo no está registrado.")
            return render_template('login/reset.html')
    
    return render_template('login/reset.html')

# Ruta para restablecer la contraseña
@app.route('/reset/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        new_password = request.form['password']
        
        # Cifrar la nueva contraseña con bcrypt
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE user SET password = %s WHERE email = %s", (hashed_password, email))
        mysql.connection.commit()
        cursor.close()
        
        flash("Contraseña restablecida correctamente. Ahora puedes iniciar sesión.")
        return redirect(url_for('access_login'))
    
    return render_template('login/change_password.html', email=email)

@app.route('/perfil')
def perfil():
    if 'username' not in session:
        return redirect(url_for('access_login'))
    
    username = session['username']
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return redirect(url_for('access_login'))

    # Obtener reservas
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
    """, (user['id'],))
    reservations = cursor.fetchall()

    # Obtener favoritos CORREGIDO
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
    """, (user['id'],))
    favorites = cursor.fetchall()
    
    cursor.close()
    
    return render_template('menu/perfil_usuario.html', 
                         user=user, 
                         reservations=reservations,
                         favorites=favorites)

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
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        if not email:
            subject = 'Gracias Por contactarnos'
            sender_email = 'boolingsr@gmail.com'
            password = 'z r s g s v l q d c n g l b e u​'  # Update with your app password
            recipients = [email]
            body = message
            
            # Codificar el cuerpo del mensaje en UTF-8
            body_utf8 = body.encode('utf-8')
            
            # Configurar el mensaje MIME
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = subject
            
            # Adjuntar el cuerpo del mensaje codificado en UTF-8
            msg.attach(MIMEText(body_utf8, 'plain', 'utf-8'))

            # Configuración del servidor SMTP
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, recipients, msg.as_string())
                flash("Mensaje enviado correctamente.")
            except Exception as e:
                flash(f"Error al enviar el correo electrónico: {str(e)}")
        else:
            flash("Por favor, proporcione una dirección de correo electrónico válida.")
    return render_template('menu/contact.html')

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
                    dato['place']   # Lugar del evento (nuevo parámetro)
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

def generate_ticket(reservation_id, event_name, client_name, num_tickets, event_date, event_time, event_place):
    """Genera un PDF con el ticket de reserva con diseño moderno y validación de datos"""
    try:
        # Validación de datos numéricos
        if not isinstance(num_tickets, int) or num_tickets <= 0:
            raise ValueError("Número de tickets inválido")
        
        if not reservation_id or not isinstance(reservation_id, (int, str)):
            raise ValueError("ID de reserva inválido")

        # Configuración del documento
        ticket_filename = f"ticket_{reservation_id}.pdf"
        ticket_path = os.path.join(app.root_path, 'static', 'tickets', ticket_filename)
        logo_path = os.path.join(app.root_path, 'static', 'img', 'Boolings Reserves.png')
        
        os.makedirs(os.path.dirname(ticket_path), exist_ok=True)

        # --- Paleta de colores mejorada ---
        primary_color = "#22333b"   # Azul oscuro elegante
        secondary_color = "#eae0d5" # Beige claro
        accent_color = "#c6ac8f"    # Dorado suave
        text_color = "#5e503f"      # Marrón oscuro

        # --- Crear PDF ---
        c = canvas.Canvas(ticket_path, pagesize=(3.5*inch, 6*inch))
        width, height = 3.5*inch, 6*inch

        # --- Fondo con diseño moderno ---
        c.setFillColor(secondary_color)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        # Elementos decorativos
        c.setFillColor(accent_color)
        c.rect(0, height-0.5*inch, width, 0.5*inch, fill=1, stroke=0)

        # --- Cabecera ---
        try:
            c.drawImage(logo_path, width/2-1.0*inch, height-1.2*inch, 
                       width=2.0*inch, height=0.7*inch, 
                       preserveAspectRatio=True, mask='auto')
        except:
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(primary_color)
            c.drawCentredString(width/2, height-1.0*inch, "BOOLINGS RESERVES")

        # --- Información principal ---
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(primary_color)
        c.drawCentredString(width/2, height-1.6*inch, "ENTRADA CONFIRMADA")
        
        # Validar y formatear fecha
        formatted_date = event_date.strftime('%d/%m/%Y') if hasattr(event_date, 'strftime') else str(event_date)
        formatted_time = str(event_time) if event_time else "Por confirmar"

        # --- Detalles en formato de tabla ---
        details = [
            ("Evento:", event_name.upper(), 0.3*inch, height-2.2*inch),
            ("Cliente:", client_name, 0.3*inch, height-2.6*inch),
            ("Fecha:", formatted_date, 0.3*inch, height-3.0*inch),
            ("Hora:", formatted_time, width/2, height-2.6*inch),
            ("Lugar:", event_place, width/2, height-3.0*inch),
            ("Entradas:", str(num_tickets), 0.3*inch, height-3.4*inch)
        ]

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(text_color)
        for label, value, x, y in details:
            c.drawString(x, y, label)
            c.setFont("Helvetica", 10)
            c.drawString(x + 0.8*inch if x < width/2 else x + 0.6*inch, y, str(value))
            c.setFont("Helvetica-Bold", 10)

        # --- Código QR con ID de reserva ---
        qr_size = 1.2*inch
        qr_y = height-4.8*inch
        c.setFillColor(secondary_color)
        c.roundRect(width/2-qr_size/2, qr_y, qr_size, qr_size, 8, fill=1, stroke=1)
        
        c.setFont("Helvetica", 8)
        c.setFillColor(primary_color)
        c.drawCentredString(width/2, qr_y+qr_size+0.2*inch, f"ID RESERVA: {reservation_id}")

        # --- Footer ---
        c.setFillColor(accent_color)
        c.rect(0, 0, width, 0.3*inch, fill=1, stroke=0)
        c.setFont("Helvetica", 7)
        c.setFillColor(primary_color)
        c.drawCentredString(width/2, 0.1*inch, "Reserva completada • Factura enviada por correo")

        c.save()
        
        return ticket_filename, ticket_path

    except Exception as e:
        print(f"Error generando ticket: {str(e)}")
        # Generar ticket de error como respaldo
        error_filename = f"error_ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        error_path = os.path.join(app.root_path, 'static', 'tickets', error_filename)
        
        c = canvas.Canvas(error_path, pagesize=(3.5*inch, 6*inch))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.5*inch, 5*inch, "ERROR EN LA RESERVA")
        c.setFont("Helvetica", 10)
        c.drawString(0.5*inch, 4.5*inch, "Los datos de reserva no son válidos")
        c.drawString(0.5*inch, 4*inch, f"Error: {str(e)}")
        c.drawString(0.5*inch, 3*inch, "Por favor contacta al soporte técnico")
        c.save()
        
        return error_filename, error_path

@app.route('/cotizacion')
def cotizacion():
    return render_template('cotizacion.html')


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
        name = request.form['name']
        event_date = request.form['event_date']
        event_hour = request.form['event_hour']
        place = request.form['place']
        category = request.form['category']
        price = request.form['price']
        reservation_status = request.form['reservation_status']
        # Manejar la carga de archivos
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Guardar la imagen en el directorio de carga
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(image_path)
                # Actualizar la ruta de la imagen en la base de datos
                cur = mysql.connection.cursor()
                cur.execute("UPDATE events SET image_url = %s WHERE id = %s", (image_path, id))
                mysql.connection.commit()
                cur.close()
        # Actualizar los otros campos del evento en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("UPDATE events SET name = %s, event_date = %s, event_hour = %s, place = %s, price = %s, category = %s, reservation_status = %s WHERE id = %s", (name, event_date, event_hour, place, price,category, reservation_status, id))
        mysql.connection.commit()
        cur.close()
        notify_users(name)
        flash("Evento actualizado correctamente")
        return redirect(url_for('evento'))
    return render_template('admin/eventos.html', dato=evento)

def notify_users(name):
    try:
        # 1. Obtener emails de la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM user")
        emails = [email[0] for email in cursor.fetchall()]
        cursor.close()

        if not emails:
            return

        # 2. Configurar mensaje
        msg = MIMEMultipart()
        msg['From'] = "boolingsr@gmail.com"
        msg['To'] = ", ".join(emails)
        msg['Subject'] = "Evento Actualizado"
        msg.attach(MIMEText(f"El evento '{name}' ha sido actualizado.", 'plain'))

        # 3. Configurar SMTP (con contraseña de aplicación)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login("boolingsr@gmail.com", "z r s g s v l q d c n g l b e u")
            server.send_message(msg)
            
    except Exception as e:
        print(f"Error de notificación: {str(e)}")

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


@app.route('/add_events',methods=['GET','POST'])
def add_events():
    if request.method == 'POST':
        _nombre = request.form['name']
        _fecha = request.form['event_date']
        _hora = request.form['event_hour']
        _lugar = request.form['place']
        _precio = request.form['price']
        _categoria = request.form['category']
        _reserva_status = request.form['reservation_status']
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Guardar la imagen en el directorio de carga
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(image_path)
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO events (name,event_date,event_hour,place,price,category,reservation_status,image_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (_nombre,_fecha,_hora,_lugar,_precio,_categoria,_reserva_status,image_path if image.filename != '' else None))
        mysql.connection.commit()
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



#      Buscador de las paginas
@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('query', '').lower()  # Asumimos que la búsqueda se hace por GET
    if query in search_map:
        return render_template(search_map[query])
    else:
        return "No se encontraron resultados para la búsqueda: {}".format(query), 404
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
    return render_template('admin/listas/user.html', datos=datos)

# Función para obtener los datos de los usuarios desde la base de datos MySQL
def obtener_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user")
    usuarios = cursor.fetchall()
    cursor.close()
    return usuarios

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from reportlab.lib.units import inch

def generar_reporte_usuarios():
    # Obtener los datos de los usuarios desde la base de datos MySQL
    usuarios = obtener_usuarios()

    # Configuración del documento
    pdf_filename = "reporte_usuarios_moderno.pdf"
    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter, 
                          rightMargin=40, leftMargin=40,
                          topMargin=80, bottomMargin=40)

    # Estilos modernos
    styles = getSampleStyleSheet()
    
    # Estilo para el título
    estilo_titulo = ParagraphStyle(
        name="TituloModerno",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#2c3e50"),
        fontName="Helvetica-Bold",
        alignment=TA_CENTER
    )
    
    # Estilo para subtítulos
    estilo_subtitulo = ParagraphStyle(
        name="SubtituloModerno",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#7f8c8d"),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Estilo para contenido
    estilo_contenido = ParagraphStyle(
        name="ContenidoModerno",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#34495e"),
        leading=14,
        spaceAfter=10
    )
    
    # Estilo para el pie de página
    estilo_pie = ParagraphStyle(
        name="PieModerno",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#95a5a6"),
        alignment=TA_CENTER
    )

    # Encabezado con logo y título
    logo = "static/img/Boolings Reserves.png"
    imagen_logo = Image(logo, width=2*inch, height=1*inch)
    imagen_logo.hAlign = 'CENTER'
    
    titulo = Paragraph("REPORTE DE USUARIOS", estilo_titulo)
    subtitulo = Paragraph("Información detallada de usuarios registrados", estilo_subtitulo)
    
    # Fecha de generación
    fecha_actual = datetime.now().strftime("%d de %B de %Y - %H:%M")
    fecha_texto = Paragraph(f"Generado el {fecha_actual}", estilo_subtitulo)
    
    # Descripción
    descripcion = Paragraph("""
    Este documento contiene la lista completa de usuarios registrados en el sistema Boolings Reserves, 
    mostrando información relevante como identificador, nombre de usuario y correo electrónico.
    """, estilo_contenido)
    
    # Tabla de datos con diseño moderno
    data = [["ID", "NOMBRE", "EMAIL"]]
    for usuario in usuarios:
        data.append([usuario["id"], usuario["username"], usuario["email"]])
    
    tabla = Table(data, colWidths=[0.8*inch, 2*inch, 3.5*inch], repeatRows=1)
    
    # Estilo de tabla moderno
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    
    # Alternar colores de filas para mejor legibilidad
    for i in range(1, len(data)):
        if i % 2 == 0:
            estilo_tabla.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#ffffff"))
    
    tabla.setStyle(estilo_tabla)
    
    # Pie de página
    pie_pagina = Paragraph(f"Boolings Reserves · Página 1 · {datetime.now().strftime('%d/%m/%Y')}", estilo_pie)
    
    # Construcción del documento
    elementos = [
        imagen_logo,
        Spacer(1, 0.2*inch),
        titulo,
        fecha_texto,
        Spacer(1, 0.3*inch),
        descripcion,
        Spacer(1, 0.4*inch),
        tabla,
        Spacer(1, 0.5*inch),
        pie_pagina
    ]
    
    # Generar PDF
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

# Función para generar el reporte PDF de los usuarios
def generar_reporte_eventos():
    # Obtener los datos de los usuarios desde la base de datos MySQL
    usuarios = obtener_eventos()

    # Crear el documento PDF
    pdf_filename = "reporte_eventos.pdf"
    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Estilos
    estilo_titulo = getSampleStyleSheet()["Title"]

    estilo_subtitulo = ParagraphStyle(name="Subtitulo", parent=estilo_titulo)
    estilo_subtitulo.fontSize = 12

    estilo_contenido = ParagraphStyle(name="Contenido")
    estilo_contenido.alignment = TA_LEFT

    # Encabezado
    titulo = Paragraph("Reporte de Usuarios", estilo_titulo)

    # Logo
    logo = "static/img/Boolings Reserves.png"  # Cambia esto por la ruta de tu logo
    imagen_logo = Image(logo, width=200, height=100)

    # Descripción
    descripcion = "Este reporte muestra información detallada de los usuarios registrados en el sistema."

    # Pie de página
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pie_pagina = Paragraph(f"Generado por Coder's Haven {fecha_actual}", estilo_contenido)

    # Tabla de datos
    data = [["ID", "Nombre", "Fecha","Precio"]]
    for usuario in usuarios:
        data.append([usuario["id"], usuario["name"], usuario["event_date"],usuario['price']])
    tabla = Table(data)

    # Estilo de la tabla
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                        ])
    tabla.setStyle(style)

    # Agregar elementos al PDF
    elementos = [imagen_logo, Spacer(0, 20), titulo, Spacer(0, 10), Paragraph(descripcion, estilo_contenido), Spacer(0, 20), tabla, Spacer(0, 20), pie_pagina]

    # Ajustar márgenes
    pdf.topMargin = 50
    pdf.bottomMargin = 50

    # Generar el PDF
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
    response.headers['Content-Disposition'] = 'inline; filename=reporte_usuarios.pdf'
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