from flask import Blueprint, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import db, app
from models import User, License
from flask import render_template
import uuid
import hashlib

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'authentication required'}), 401
        if not getattr(current_user, 'is_admin', False):
            return jsonify({'error': 'admin privileges required'}), 403
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


@bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json() or request.form
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid credentials'}), 401
    if not user.is_admin:
        return jsonify({'error': 'not an admin user'}), 403
    login_user(user)
    return jsonify({'status': 'ok', 'message': 'logged in'})


@bp.route('/logout', methods=['POST'])
@login_required
@admin_required
def admin_logout():
    logout_user()
    return jsonify({'status': 'ok', 'message': 'logged out'})


@bp.route('/licenses', methods=['GET'])
@login_required
@admin_required
def list_licenses():
    licenses = License.query.all()
    out = []
    for lic in licenses:
        out.append({
            'id': lic.id,
            'user_id': lic.user_id,
            'license_key': lic.license_key,
            'license_type': lic.license_type,
            'status': lic.status,
            'issued_at': lic.issued_at.isoformat() if lic.issued_at else None,
            'expires_at': lic.expires_at.isoformat() if lic.expires_at else None,
        })
    return jsonify(out)


@bp.route('/licenses/create', methods=['POST'])
@login_required
@admin_required
def create_license():
    data = request.get_json() or request.form
    user_id = data.get('user_id')
    license_type = data.get('license_type', 'basic')
    max_active_trades = int(data.get('max_active_trades', 3))
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    lic = License()
    lic.user_id = user_id
    # Generate a short 13-character license key if not provided
    if data.get('license_key'):
        lic.license_key = data.get('license_key')[:13]
    else:
        # Create a short key: 8 random hex chars + 5 from hash
        short_id = uuid.uuid4().hex[:8].upper()
        hash_suffix = hashlib.md5(f"{user_id}-{uuid.uuid4().hex}".encode()).hexdigest()[:5].upper()
        lic.license_key = f"{short_id}{hash_suffix}"
    lic.license_type = license_type
    lic.status = data.get('status', 'active')
    lic.max_active_trades = max_active_trades
    db.session.add(lic)
    db.session.commit()
    return jsonify({'status': 'ok', 'license_id': lic.id, 'license_key': lic.license_key})


@bp.route('/licenses/<int:license_id>/status', methods=['POST'])
@login_required
@admin_required
def set_license_status(license_id):
    data = request.get_json() or request.form
    status = data.get('status')
    if not status:
        return jsonify({'error': 'status required'}), 400
    lic = License.query.get(license_id)
    if not lic:
        return jsonify({'error': 'license not found'}), 404
    lic.status = status
    db.session.commit()
    return jsonify({'status': 'ok', 'license_id': lic.id, 'new_status': status})


@bp.route('/ui')
def admin_ui():
    return render_template('admin.html')


def register_admin_blueprint():
    app.register_blueprint(bp)


# Register when imported
register_admin_blueprint()
