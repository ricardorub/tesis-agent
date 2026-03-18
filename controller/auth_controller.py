from flask import request, jsonify, session, redirect, url_for
from model.models import User, University, AcademicLevel, Gender
from model.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_first_name'] = user.first_name or ''
        session['user_last_name'] = user.last_name or ''
        session['user_role'] = user.role
        
        if user.role == 'administrator':
            redirect_url = '/admin'
        elif user.role == 'moderator':
            redirect_url = '/moderator'
        else:
            redirect_url = '/chat'

        return jsonify({
            'message': 'Login exitoso',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'role': user.role
            },
            'redirect': redirect_url
        }), 200
    else:
        return jsonify({'error': 'Credenciales inválidas'}), 401

def logout():
    session.clear()
    return redirect(url_for('index'))

def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    university_name = data.get('university')
    gender_name = data.get('gender')
    academic_level_name = data.get('academic_level')
    age = data.get('age')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    # Validar formato de email
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Formato de email inválido'}), 400

    # Verificar si el usuario ya existe
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'El usuario ya existe'}), 400

    try:
        # Buscar o crear universidad
        university = None
        if university_name:
            university = University.query.filter_by(name=university_name).first()
            if not university:
                university = University(name=university_name)
                db.session.add(university)
                db.session.flush()

        # Buscar o crear nivel académico
        academic_level = None
        if academic_level_name:
            academic_level = AcademicLevel.query.filter_by(name=academic_level_name).first()
            if not academic_level:
                academic_level = AcademicLevel(name=academic_level_name)
                db.session.add(academic_level)
                db.session.flush()

        # Buscar o crear género
        gender = None
        if gender_name:
            gender = Gender.query.filter_by(name=gender_name).first()
            if not gender:
                gender = Gender(name=gender_name)
                db.session.add(gender)
                db.session.flush()

        # Crear nuevo usuario con los objetos encontrados o creados
        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_password,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None,
            university=university,
            gender=gender,
            academic_level=academic_level,
            age=age
        )

        db.session.add(new_user)
        db.session.commit()
        
        # Iniciar sesión automáticamente después del registro
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        session['user_first_name'] = new_user.first_name or ''
        session['user_last_name'] = new_user.last_name or ''
        session['user_role'] = new_user.role
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'role': new_user.role
            },
            'redirect': '/chat'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear el usuario: ' + str(e)}), 500

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'administrator':
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        return f(*args, **kwargs)
    return decorated_function