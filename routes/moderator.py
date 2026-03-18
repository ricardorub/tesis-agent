from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from functools import wraps
import json
from controller import moderator_controller

moderator_bp = Blueprint('moderator', __name__)

def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') not in ['moderator', 'administrator']:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@moderator_bp.route('/moderator')
@moderator_required
def moderator_dashboard():
    stats = moderator_controller.get_statistics()
    # Convert data to JSON format for Chart.js
    stats['avg_ratings_data'] = json.dumps(stats.get('avg_ratings_data', {}))
    stats['distribution_data'] = json.dumps(stats.get('distribution_data', {}))
    stats['university_data'] = json.dumps(stats.get('university_data', {}))
    stats['gender_data'] = json.dumps(stats.get('gender_data', {}))
    stats['academic_data'] = json.dumps(stats.get('academic_data', {}))
    stats['age_data'] = json.dumps(stats.get('age_data', {}))
    
    return render_template('moderator.html', **stats)

@moderator_bp.route('/moderator/time_evolution', methods=['GET'])
@moderator_required
def get_time_evolution_data():
    return moderator_controller.get_time_evolution_data()

@moderator_bp.route('/moderator/upload_pdf', methods=['POST'])
@moderator_required
def upload_pdf():
    """Ruta para subir un nuevo PDF"""
    from flask import request, jsonify
    
    if 'pdf_file' not in request.files:
        return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['pdf_file']
    result = moderator_controller.upload_pdf(file)
    
    if result['success']:
        # Recargar el procesador de PDF en el chatbot
        try:
            from routes.chat import reload_pdf_processor
            reload_pdf_processor()
        except Exception as e:
            print(f"⚠️ Advertencia: No se pudo recargar el procesador: {e}")
        
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@moderator_bp.route('/moderator/pdf_info', methods=['GET'])
@moderator_required
def get_pdf_info():
    """Ruta para obtener información de todos los PDFs"""
    from flask import jsonify
    info = moderator_controller.get_all_pdfs_info()
    return jsonify(info), 200

@moderator_bp.route('/moderator/delete_pdf/<filename>', methods=['DELETE'])
@moderator_required
def delete_pdf_route(filename):
    """Ruta para eliminar un PDF específico"""
    from flask import jsonify
    result = moderator_controller.delete_pdf(filename)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@moderator_bp.route('/moderator/set_active_pdf/<filename>', methods=['POST'])
@moderator_required
def set_active_pdf_route(filename):
    """Ruta para establecer un PDF como activo"""
    from flask import jsonify
    result = moderator_controller.set_active_pdf(filename)
    
    if result['success']:
        # Recargar el procesador de PDF en el chatbot
        try:
            from routes.chat import reload_pdf_processor
            reload_pdf_processor()
        except Exception as e:
            print(f"⚠️ Advertencia: No se pudo recargar el procesador: {e}")
        
        return jsonify(result), 200
    else:
        return jsonify(result), 400
