#   Biblioteca Flask y Mysql
from flask import Flask, render_template,request,redirect,flash, url_for,session,jsonify,make_response,Response
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
app.config['MAIL_PASSWORD'] = 'u u n e i j q s a f h c y th o​'

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

# Definir una tarea para enviar notificaciones
def notify_job():    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        current_date = datetime.now().date()
        for event in events:
            event_date = datetime.strptime(event['event_date'], "%Y-%m-%d").date()
            if event_date >= current_date:
                cursor.execute("SELECT email FROM user")
                emails = cursor.fetchall()
                for user_email in emails:
                    send_notification(user_email['email'], event['name'], event['event_date'])
    except Exception as e:
        print("Error al procesar la notificación:", e)
    finally:
        cursor.close()

def send_notification(email, event_name, event_date):
    try:
        subject = f"Notificación de evento próximo: {event_name}"
        body = f"Te recordamos que el evento '{event_name}' se llevará a cabo el {event_date}. ¡No te lo pierdas!"
        # Crear el mensaje MIME
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'boolingsr@gmail.com'
        msg['To'] = email

        with smtplib.SMTP('localhost', 25) as smtp:
            # Enviar el mensaje    
            smtp.send_message(msg)
        print(f"Notificación enviada sobre el evento: {event_name} el {event_date} a {email}")
    except Exception as e:
        print("Error al enviar la notificación por correo electrónico:", e)

# Crear un programador de tareas
scheduler = BackgroundScheduler()
scheduler.start()
# Agendar la tarea de notificación para que se ejecute diariamente
scheduler.add_job(notify_job, 'cron', minute='*', second='5')



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
    password = 'u u n e i j q s a f h c y th o​'

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
            password = 'u u n e i j q s a f h c y th o'  # Usa la contraseña de aplicación generada
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
    # Verifica que el usuario está logueado
    if 'username' not in session:
        return redirect(url_for('access_login'))  # Redirige al login si no está logueado
    
    # Obtiene el nombre de usuario desde la sesión
    username = session['username']
    
    # Consulta la base de datos para obtener los detalles del usuario logueado
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
    dato = cursor.fetchone()

    # Consulta la base de datos para obtener las reservas del usuario
    cursor.execute("""
        SELECT r.id_event, r.number_of_reserved_tickets, r.date
        FROM bookings r
        WHERE r.id_user = %s
    """, (dato['id'],))  # Usamos el 'id' del usuario para obtener sus reservas
    reservations = cursor.fetchall()

    cursor.close()

    # Renderiza el template de perfil con los datos del usuario y las reservas
    return render_template('menu/perfil_usuario.html', user=dato, reservations=reservations)

#         Desloguearse
@app.route('/logout')
def logout():
    # Elimina el nombre de usuario de la sesión
    session.pop('username', None)
    session.pop('logueado', None)  # También puedes eliminar la variable 'logueado'
    session.pop('id', None)
    session.pop('id_role', None)
    return redirect(url_for('access_login'))  # Redirige al login

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
            password = 'u u n e i j q s a f h c y th o​'  # Update with your app password
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


@app.route('/guardar_evento/<int:id>', methods=['GET'])
def guardar_evento(id):
    global eventos_guardados
    # Verifica si el evento ya está guardado, si no lo está, agrégalo a la lista
    if id not in eventos_guardados:
        eventos_guardados.append(id)
        # Inserta el evento guardado en la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO eventos_guardados (evento_id) VALUES (%s)", (id,))
        mysql.connection.commit()
        cursor.close()
        flash("El evento a sido agregado a favoritos")
    return redirect(url_for('eventos_disponibles'))


@app.route('/safe')
def safe():
    # Consulta para obtener los eventos guardados desde la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT e.* FROM events e INNER JOIN eventos_guardados eg ON e.id = eg.evento_id")
    eventos_guardados_datos = cursor.fetchall()
    cursor.close()
    return render_template('eventos/safe.html', eventos_guardados=eventos_guardados_datos)


@app.route('/eliminar_evento/<int:evento_id>', methods=['POST'])
def eliminar_evento(evento_id):
    global eventos_guardados
    if evento_id in eventos_guardados:
        eventos_guardados.remove(evento_id)
        # Elimina el evento guardado de la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM eventos_guardados WHERE evento_id = %s", (evento_id,))
        mysql.connection.commit()
        cursor.close()
        flash("El evento ha sido eliminado de favoritos")
    return redirect(url_for('safe'))

@app.route('/get_reservations', methods=['GET'])
def get_reservations():
    if 'logueado' in session:
        user_id = session['id']
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT r.id_event, r.number_of_reserved_tickets, r.date
                FROM reservations r
                WHERE r.user_id = %s
            """, (user_id,))
            reservations = cursor.fetchall()
            cursor.close()

            # Preparar los datos para devolver
            reservation_data = []
            for reservation in reservations:
                reservation_data.append({
                    'id_event': reservation[0],
                    'number_of_reserved_tickets': reservation[1],
                    'date': reservation[2]
                })

            return jsonify(reservation_data)
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'An error occurred while fetching reservations'}), 500
    else:
        return jsonify({'error': 'User not logged in'}), 401



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
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events WHERE id = %s", (id,))
    dato = cursor.fetchone()

    if not dato:
        flash("Evento no encontrado.", "error")
        return redirect(url_for('eventos_disponibles'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        tickets = int(request.form['tickets'])
        date = request.form['date']
        price = request.form['amount_paid']
        payment_date = request.form['payment_date']
        card_number = request.form['card_number']
        card_holder = request.form['card_holder']
        card_expiry = request.form['card_expiry']
        card_cvv = request.form['card_cvv']

        if tickets <= 0:
            flash("Número de tickets debe ser mayor a cero.", "error")
            return render_template('eventos/reservations.html', dato=dato)

        try:
            # Obtener el id_user de la sesión
            id_user = session['id']

            # Después de que el usuario inicia sesión con éxito
            cursor.execute(
                "INSERT INTO bookings (name_client, email_client, id_event, id_user, date, number_of_reserved_tickets) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, email, id, id_user, date, tickets)
            )

            cursor.execute(
                "INSERT INTO payment (evento_id, amount_paid, payment_date, card_number, card_holder, card_expiry_date, card_cvv) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (id, price, payment_date, card_number, card_holder, card_expiry, card_cvv)
            )

            mysql.connection.commit()

            # Remueve caracteres especiales del nombre del evento y lo normaliza
            normalized_name = unicodedata.normalize('NFKD', dato['event_date']).encode('ascii', 'ignore').decode('utf-8')

            # Reemplaza los caracteres no ASCII con un guion bajo
            normalized_name = normalized_name.replace('/', '_')

            file_path = 'static/factura/factura_{}_{}.pdf'.format(id, normalized_name)
            session['pdf_path'] = file_path
            session['email'] = email
            create_invoice(file_path, nombre, tickets, dato, descuento=0.1)
            return redirect(url_for('confirmacion'))
        except Exception as e:
            mysql.connection.rollback()
            flash(str(e), "error")
            return render_template('eventos/reservations.html', dato=dato)

    return render_template('eventos/reservations.html', dato=dato)

@app.route('/confirmacion',methods=['GET','POST'])
def confirmacion():
    # Suponiendo que la ruta del archivo PDF se guarda en la sesión
    pdf_file_path = session.get('pdf_path')
    return render_template('eventos/confirmacion.html', pdf_file_path=pdf_file_path)

@app.route('/enviar_factura')
def enviar_factura():
    email = session.get('email')
    file_path = session.get('pdf_path')
    enviar_email(email, file_path)
    flash("Factura enviada con éxito.", "success")
    return redirect(url_for('eventos_disponibles'))


def enviar_email(email, file_path):
    sender_email = 'boolingsr@gmail.com'
    password = 'u u n e i j q s a f h c y th o​'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Reserva exitosa"

    try:
        # Adjuntar el PDF
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file_path)
        msg.attach(part)

        # Mensaje en el cuerpo del email
        msg.attach(MIMEText("Aquí está su factura.", 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        print("Correo electrónico enviado con éxito.")
    except FileNotFoundError:
        print(f"El archivo PDF no se encontró en la ruta especificada: {file_path}")
        # Manejar el error de manera apropiada, por ejemplo, mostrar un mensaje al usuario o registrar el error
    except Exception as e:
        print(f"Error al enviar el correo electrónico: {e}")
        # Manejar otros errores de manera apropiada


# Definir el color para ;a factura
dark_gold = colors.HexColor("#B08B12")
elegantblue = colors.HexColor("#1B365D")


def create_invoice(file_path, nombre, tickets, dato, descuento=0.1):
     # Obtener la fecha actual
    current_date = datetime.now().strftime("%d/%m/%Y")

    # Crear el lienzo del PDF
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter  # Dimensiones de la página

    # Definir márgenes
    overall_margin = 0.5 * inch
    content_margin = 0.75 * inch  
    footer_margin = 1.25 * inch  

    # Dibujar un borde en color dark gold
    c.setStrokeColor(dark_gold)
    c.setLineWidth(1)
    c.rect(overall_margin, overall_margin, width - 2 * overall_margin, height - 2 * overall_margin)

    # Título de la factura y logo
    title_position = height - overall_margin - 1.0 * inch
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(width / 2.0, title_position, "Boolings Reserves")
    logo_path = 'static/img/Boolings Reserves.png'
    logo_size = 1.5 * inch  
    logo_height_position = title_position - logo_size - 0.25 * inch
    c.drawImage(logo_path, (width - logo_size) / 2, logo_height_position, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto')

    # Fecha actual en la parte superior derecha
    c.setFont('Helvetica', 10)
    c.drawRightString(width - content_margin, height - content_margin, f"Fecha: {current_date}")

    # Información del cliente
    client_info_position = logo_height_position - 0.75 * inch
    c.setFont('Helvetica-Bold', 12)
    c.drawString(content_margin, client_info_position, "Facturado a:")
    c.setFont('Helvetica', 10)
    client_name_position = client_info_position - 0.15 * inch
    client_date_position = client_name_position - 0.15 * inch
    c.drawString(content_margin, client_name_position, f"Nombre: {nombre}")
    c.drawString(content_margin, client_date_position, f"Fecha del evento: {dato['price']}")

    # Tabla de elementos de factura
    table_width = width - 2 * content_margin
    colWidths = [0.5 * table_width, 0.15 * table_width, 0.175 * table_width, 0.175 * table_width]
    event_total = tickets * dato['price']
    data = [
        ["Descripción", "Cantidad", "Precio Unitario", "Total"],
        ["Entrada al evento: " + dato['name'], tickets, f"${dato['price']:.2f}", f"${event_total:.2f}"]
    ]
    table = Table(data, colWidths=colWidths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('GRID', (0, 0), (-1, -1), 2, colors.black)
    ])
    table.setStyle(style)
    table_start = client_date_position - 0.75 * inch
    table.wrapOn(c, content_margin, table_start)
    table.drawOn(c, content_margin, table_start)

    # Calculando los totales
    total_descuento = event_total * descuento
    sub_total = event_total - total_descuento
    total_final = sub_total

    # Tabla de totales, alineada a la derecha bajo la tabla principal
    data_totals = [
        ["Descuento", f"${total_descuento:.2f}"],
        ["Subtotal", f"${sub_total:.2f}"],
        ["Total", f"${total_final:.2f}"]
    ]
    totals_table = Table(data_totals, colWidths=[1.0*inch, 1.0*inch])
    totals_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('GRID', (0, 0), (-1, -1), 2, colors.black)
    ])
    totals_table.setStyle(totals_style)
    totals_table_position_x = content_margin + table_width - 2*inch  # Align right to the main table
    totals_table_position_y = table_start + table._height + 0.1 * inch  # Below the main table
    totals_table.wrapOn(c, totals_table_position_x, totals_table_position_y)
    totals_table.drawOn(c, totals_table_position_x, totals_table_position_y)

    # Información de la empresa en el pie de página
    footer_line_position = footer_margin - 0.25 * inch
    c.setStrokeColor(colors.grey)
    c.line(content_margin, footer_line_position, width - content_margin, footer_line_position) 
    c.setFont("Helvetica", 9)
    footer_text = "Empresa Boolings Reserves - 173 Calle Pedernales Ensanche Espallait - +1 234 567 8900 - boolingsr@empresa.com"
    c.drawCentredString(width / 2.0, footer_margin - 0.5 * inch, footer_text)  
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2.0, footer_margin - 0.65 * inch, "© 2024 Boolings Reserves. Todos los derechos reservados.") 

    # Finalizar PDF
    c.showPage()
    c.save()

    # Verificar y crear el directorio si no existe
    output_dir = os.path.dirname(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT email FROM user")
    email = cursor.fetchall()
    # Configura los detalles del correo electrónico
    sender_email = "boolingsr@gmail.com"
    recipient_email = email
    subject = "Evento Actualizado"
    body = f"El evento '{name}' ha sido actualizado."

    # Crea un mensaje multipart
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Agrega el cuerpo del mensaje
    msg.attach(MIMEText(body, 'plain'))

    # Configura el servidor SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "boolingsr@gmail.com"
    smtp_password = 'u u n e i j q s a f h c y th o​'  # Asegúrate de usar una contraseña segura o token de aplicación

    # Inicia una conexión SMTP segura
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        # Codifica el mensaje como UTF-8
        text = msg.as_string().encode('utf-8')
        server.sendmail(sender_email, recipient_email, text)

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

def generar_reporte_usuarios():
    # Obtener los datos de los usuarios desde la base de datos MySQL
    usuarios = obtener_usuarios()

    # Crear el documento PDF
    pdf_filename = "reporte_usuarios.pdf"
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
    pie_pagina = Paragraph(f"Generado por Boolings Reserves {fecha_actual}", estilo_contenido)

    # Tabla de datos
    data = [["ID", "Nombre", "Email"]]
    for usuario in usuarios:
        data.append([usuario["id"], usuario["username"], usuario["email"]])
    tabla = Table(data)

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
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

    elements = [
    imagen_logo,
    titulo,
    Spacer(0, 10),
    Paragraph(descripcion, estilo_contenido),  # Aplicar estilo aquí
    Spacer(0, 10),
    tabla,
    Spacer(0, 20),
    pie_pagina
    ]


    # Ajustar márgenes
    pdf.topMargin = 50
    pdf.bottomMargin = 50

    # Generar el PDF
    pdf.build(elements)

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