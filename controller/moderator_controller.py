from flask import jsonify, session
from model.models import User, Feedback, ChatSession, University, Gender, AcademicLevel
from model.db import db
from sqlalchemy import func
from datetime import datetime, timedelta

def get_statistics():
    # Datos para las tarjetas de estadísticas
    total_users = User.query.count()
    
    # Obtener nombres de universidades con usuarios
    universities_query = db.session.query(University.name).join(User).distinct().all()
    universities = [u[0] for u in universities_query if u[0]]
    universities_count = len(universities)
    
    feedback_list = Feedback.query.all()
    total_feedback = len(feedback_list)
    
    if total_feedback > 0:
        avg_clarity = sum(f.clarity_rating for f in feedback_list) / total_feedback
        avg_accessibility = sum(f.accessibility_rating for f in feedback_list) / total_feedback
        avg_reliability = sum(f.reliability_rating for f in feedback_list) / total_feedback
        general_avg = (avg_clarity + avg_accessibility + avg_reliability) / 3
    else:
        avg_clarity = avg_accessibility = avg_reliability = general_avg = 0

    # Datos para los gráficos
    avg_ratings_data = {
        'labels': ['Claridad', 'Accesibilidad', 'Confianza'],
        'datasets': [{'label': 'Puntuación promedio', 'data': [avg_clarity, avg_accessibility, avg_reliability]}]
    }

    ratings_distribution = db.session.query(
        func.round((Feedback.clarity_rating + Feedback.accessibility_rating + Feedback.reliability_rating) / 3),
        func.count()
    ).group_by(func.round((Feedback.clarity_rating + Feedback.accessibility_rating + Feedback.reliability_rating) / 3)).all()
    
    distribution_data = {
        'labels': [f'{int(stars)} Estrella(s)' for stars, count in ratings_distribution],
        'datasets': [{'data': [count for stars, count in ratings_distribution]}]
    }

    # Usuarios por universidad (unida por nombre)
    users_by_university = db.session.query(University.name, func.count(User.id))\
        .join(User)\
        .group_by(University.name)\
        .order_by(func.count(User.id).desc())\
        .limit(7).all()
        
    university_data = {
        'labels': [uni[0] for uni in users_by_university],
        'datasets': [{'label': 'Usuarios', 'data': [uni[1] for uni in users_by_university]}]
    }

    # Distribución por género
    gender_distribution = db.session.query(Gender.name, func.count(User.id))\
        .join(User)\
        .group_by(Gender.name).all()
        
    gender_data = {
        'labels': [g[0] for g in gender_distribution if g[0]],
        'datasets': [{'data': [g[1] for g in gender_distribution if g[0]]}]
    }

    # Distribución por nivel académico
    academic_level_distribution = db.session.query(AcademicLevel.name, func.count(User.id))\
        .join(User)\
        .group_by(AcademicLevel.name).all()
        
    academic_data = {
        'labels': [al[0] for al in academic_level_distribution if al[0]],
        'datasets': [{'label': 'Usuarios', 'data': [al[1] for al in academic_level_distribution if al[0]]}]
    }

    age_bins = [(18, 24), (25, 34), (35, 44), (45, 54), (55, 100)]
    age_distribution = [User.query.filter(User.age.between(min_age, max_age)).count() for min_age, max_age in age_bins]
    
    age_data = {
        'labels': [f'{min_age}-{max_age}' for min_age, max_age in age_bins],
        'datasets': [{'label': 'Usuarios', 'data': age_distribution}]
    }
    
    return {
        'feedback_list': feedback_list,
        'total_users': total_users,
        'general_avg': f'{general_avg:.2f}',
        'universities_count': universities_count,
        'satisfaction': f'{(general_avg / 5 * 100):.0f}%' if general_avg > 0 else '0%',
        'universities': universities,
        'genders': [g[0] for g in db.session.query(Gender.name).distinct().all() if g[0]],
        'academic_levels': [a[0] for a in db.session.query(AcademicLevel.name).distinct().all() if a[0]],
        'avg_ratings_data': avg_ratings_data,
        'distribution_data': distribution_data,
        'university_data': university_data,
        'gender_data': gender_data,
        'academic_data': academic_data,
        'age_data': age_data,
    }

def get_time_evolution_data():
    if session.get('user_role') not in ['administrator', 'moderator']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Define the time range (e.g., last 30 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    # Query for user creation data
    user_data = db.session.query(func.date(User.created_at), func.count(User.id)) \
        .filter(User.created_at >= start_date) \
        .group_by(func.date(User.created_at)) \
        .order_by(func.date(User.created_at)) \
        .all()

    # Query for feedback submission data
    feedback_data = db.session.query(func.date(Feedback.submitted_at), func.count(Feedback.id)) \
        .filter(Feedback.submitted_at >= start_date) \
        .group_by(func.date(Feedback.submitted_at)) \
        .order_by(func.date(Feedback.submitted_at)) \
        .all()

    # Query for chat session creation data
    chatsession_data = db.session.query(func.date(ChatSession.created_at), func.count(ChatSession.id)) \
        .filter(ChatSession.created_at >= start_date) \
        .group_by(func.date(ChatSession.created_at)) \
        .order_by(func.date(ChatSession.created_at)) \
        .all()

    # Process data for Chart.js
    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
    users = [0] * 31
    feedbacks = [0] * 31
    chatsessions = [0] * 31

    for date, count in user_data:
        if date:
            day_index = (date - start_date.date()).days
            if 0 <= day_index < 31:
                users[day_index] = count
    
    for date, count in feedback_data:
        if date:
            day_index = (date - start_date.date()).days
            if 0 <= day_index < 31:
                feedbacks[day_index] = count

    for date, count in chatsession_data:
        if date:
            day_index = (date - start_date.date()).days
            if 0 <= day_index < 31:
                chatsessions[day_index] = count

    return jsonify({
        'labels': labels,
        'users': users,
        'feedbacks': feedbacks,
        'chatsessions': chatsessions
    })

def upload_pdf(file):
    """
    Maneja la subida de un nuevo PDF para el chatbot.
    Reemplaza el PDF existente en la carpeta tesis.
    """
    import os
    from werkzeug.utils import secure_filename
    
    try:
        # Validar que sea un archivo PDF
        if not file or not file.filename:
            return {'success': False, 'error': 'No se proporcionó ningún archivo'}
        
        if not file.filename.lower().endswith('.pdf'):
            return {'success': False, 'error': 'El archivo debe ser un PDF'}
        
        # Definir la carpeta de destino
        tesis_folder = os.path.join(os.getcwd(), 'tesis')
        
        # Crear carpeta si no existe
        if not os.path.exists(tesis_folder):
            os.makedirs(tesis_folder)
        
        # Crear carpeta si no existe
        if not os.path.exists(tesis_folder):
            os.makedirs(tesis_folder)
        
        # Guardar el archivo con su nombre original (sanitizado)
        original_filename = secure_filename(file.filename)
        original_path = os.path.join(tesis_folder, original_filename)
        file.save(original_path)
        print(f"✅ PDF guardado: {original_filename}")
        
        # Establecer como activo automáticamente (copiar a tesis1234.pdf)
        import shutil
        target_path = os.path.join(tesis_folder, 'tesis1234.pdf')
        
        # Si existe tesis1234.pdf y no es el mismo archivo que acabamos de subir
        # if os.path.exists(target_path) and original_filename != 'tesis1234.pdf':
            # Hacer backup del anterior activo
            # backup_name = f'tesis1234_backup_{int(os.path.getmtime(target_path))}.pdf'
            # backup_path = os.path.join(tesis_folder, backup_name)
            # try:
            #     shutil.copy2(target_path, backup_path)
            #     print(f"📦 Backup creado: {backup_name}")
            # except Exception as e:
            #     print(f"⚠️ No se pudo crear backup: {e}")
        
        # Copiar el nuevo archivo como activo
        if original_filename != 'tesis1234.pdf':
            shutil.copy2(original_path, target_path)
        
        return {
            'success': True, 
            'message': f'PDF "{original_filename}" subido y activado correctamente',
            'filename': original_filename
        }
        
    except Exception as e:
        print(f"❌ Error al subir PDF: {e}")
        return {'success': False, 'error': str(e)}

def get_all_pdfs_info():
    """
    Obtiene información de todos los PDFs en la carpeta tesis.
    """
    import os
    from datetime import datetime
    
    try:
        tesis_folder = os.path.join(os.getcwd(), 'tesis')
        
        if not os.path.exists(tesis_folder):
            os.makedirs(tesis_folder)
            return {'pdfs': []}
        
        # Buscar todos los archivos PDF
        pdf_files = [f for f in os.listdir(tesis_folder) if f.lower().endswith('.pdf')]
        
        pdfs_info = []
        for pdf_filename in pdf_files:
            pdf_path = os.path.join(tesis_folder, pdf_filename)
            
            # Obtener información del archivo
            file_stats = os.stat(pdf_path)
            file_size = file_stats.st_size
            modified_time = datetime.fromtimestamp(file_stats.st_mtime)
            
            # Convertir tamaño a formato legible
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.2f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            
            # Calcular hash MD5 para identificar archivos idénticos
            import hashlib
            file_hash = ''
            try:
                with open(pdf_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            except Exception:
                pass

            pdfs_info.append({
                'filename': pdf_filename,
                'size': size_str,
                'size_bytes': file_size,
                'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': pdf_filename == 'tesis1234.pdf',  # Marcar el PDF activo por nombre
                'hash': file_hash # Hash para identificar contenido idéntico
            })
        
        # Ordenar por fecha de modificación (más reciente primero)
        pdfs_info.sort(key=lambda x: x['modified'], reverse=True)
        
        return {'pdfs': pdfs_info}
        
    except Exception as e:
        print(f"❌ Error al obtener info de PDFs: {e}")
        return {'pdfs': [], 'error': str(e)}

def delete_pdf(filename):
    """
    Elimina un PDF específico de la carpeta tesis.
    """
    import os
    
    try:
        # Validar nombre de archivo
        if not filename or not filename.lower().endswith('.pdf'):
            return {'success': False, 'error': 'Nombre de archivo inválido'}
        
        # Prevenir eliminación del PDF activo si es el único
        tesis_folder = os.path.join(os.getcwd(), 'tesis')
        pdf_files = [f for f in os.listdir(tesis_folder) if f.lower().endswith('.pdf')]
        
        if filename == 'tesis1234.pdf' and len(pdf_files) == 1:
            return {'success': False, 'error': 'No puedes eliminar el único PDF activo. Sube otro primero.'}
        
        # Construir ruta completa
        file_path = os.path.join(tesis_folder, filename)
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            return {'success': False, 'error': 'El archivo no existe'}
        
        # Eliminar el archivo
        os.remove(file_path)
        print(f"🗑️ PDF eliminado: {filename}")
        
        return {
            'success': True,
            'message': f'PDF "{filename}" eliminado correctamente'
        }
        
    except Exception as e:
        print(f"❌ Error al eliminar PDF: {e}")
        return {'success': False, 'error': str(e)}

def set_active_pdf(filename):
    """
    Establece un PDF como activo para el chatbot.
    Renombra el archivo seleccionado a tesis1234.pdf
    """
    import os
    import shutil
    
    try:
        tesis_folder = os.path.join(os.getcwd(), 'tesis')
        
        # Validar que el archivo existe
        source_path = os.path.join(tesis_folder, filename)
        if not os.path.exists(source_path):
            return {'success': False, 'error': 'El archivo no existe'}
        
        # Si ya es el archivo activo, no hacer nada
        if filename == 'tesis1234.pdf':
            return {'success': True, 'message': 'Este PDF ya es el activo'}
        
        target_path = os.path.join(tesis_folder, 'tesis1234.pdf')
        
        # Si existe tesis1234.pdf, eliminarlo primero para asegurar reemplazo limpio
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
                print(f"🗑️ Archivo anterior eliminado: {target_path}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar el archivo anterior: {e}")
                # Intentar continuar de todos modos, shutil.copy2 podría funcionar o fallar
        
        # Copiar el archivo seleccionado como tesis1234.pdf
        shutil.copy2(source_path, target_path)
        print(f"✅ PDF activo cambiado a: {filename}")
        
        return {
            'success': True,
            'message': f'PDF "{filename}" establecido como activo. El chatbot se recargará automáticamente.'
        }
        
    except Exception as e:
        print(f"❌ Error al establecer PDF activo: {e}")
        return {'success': False, 'error': str(e)}
