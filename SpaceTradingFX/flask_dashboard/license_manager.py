import rsa
import secrets
import json
import base64
from datetime import datetime, timedelta
from app import db
from models import License


# Generate RSA keys (run once and store securely)
# In production, load these from environment variables or secure storage
def generate_keys():
    """Generate RSA key pair for license signing"""
    (pubkey, privkey) = rsa.newkeys(2048)
    return pubkey, privkey


# Store these keys securely - for demo purposes only
# In production, store private key in environment variable or secret manager
try:
    PRIVATE_KEY = rsa.PrivateKey.load_pkcs1(base64.b64decode(
        "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBdDRtcXYyQnlxZkJ1YkZSMm53PT0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0="
    ))
    PUBLIC_KEY = rsa.PublicKey.load_pkcs1(base64.b64decode(
        "LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBdDRtcXYyQnlxZkJ1YkZSMm53PT0KLS0tLS1FTkQgUlNBIFBVQkxJQyBLRVktLS0tLQ=="
    ))
except Exception:
    # Generate new keys if not available
    PUBLIC_KEY, PRIVATE_KEY = generate_keys()


LICENSE_TYPES = {
    'basic': {
        'price': 29.99,
        'duration_days': 30,
        'max_trades': 3,
        'features': ['basic_signals', 'manual_trading']
    },
    'premium': {
        'price': 79.99,
        'duration_days': 30,
        'max_trades': 10,
        'features': ['advanced_signals', 'auto_trading', 'email_alerts']
    },
    'professional': {
        'price': 199.99,
        'duration_days': 30,
        'max_trades': 50,
        'features': ['advanced_signals', 'auto_trading', 'email_alerts', 'priority_support', 'custom_strategies']
    }
}


def generate_license_key(user_id, license_type='basic'):
    """Generate a cryptographically signed license key"""
    
    if license_type not in LICENSE_TYPES:
        raise ValueError(f"Invalid license type: {license_type}")
    
    # Generate unique license ID
    license_id = secrets.token_urlsafe(16)
    
    # Calculate expiry date
    duration = LICENSE_TYPES[license_type]['duration_days']
    issued_at = datetime.now()
    expires_at = issued_at + timedelta(days=duration)
    
    # Create license data
    license_data = {
        "id": license_id,
        "user_id": user_id,
        "license_type": license_type,
        "issued": issued_at.isoformat(),
        "expires": expires_at.isoformat(),
        "features": LICENSE_TYPES[license_type]['features'],
        "max_trades": LICENSE_TYPES[license_type]['max_trades']
    }
    
    # Serialize and sign
    data_bytes = json.dumps(license_data).encode('utf-8')
    signature = rsa.sign(data_bytes, PRIVATE_KEY, 'SHA-256')
    
    # Create license key format
    license_key = f"{base64.b64encode(data_bytes).decode()}.{base64.b64encode(signature).decode()}"
    
    return license_key, license_data


def validate_license_key(license_key):
    """Validate a license key signature and expiry"""
    try:
        # Split key into data and signature
        parts = license_key.split('.')
        if len(parts) != 2:
            return False, "Invalid license key format"
        
        data_enc, sig_enc = parts
        data_bytes = base64.b64decode(data_enc)
        signature = base64.b64decode(sig_enc)
        
        # Verify signature
        try:
            rsa.verify(data_bytes, signature, PUBLIC_KEY)
        except rsa.VerificationError:
            return False, "Invalid license signature"
        
        # Parse license data
        license_data = json.loads(data_bytes.decode('utf-8'))
        
        # Check expiry
        expires_at = datetime.fromisoformat(license_data['expires'])
        if datetime.now() > expires_at:
            return False, "License expired"
        
        return True, license_data
    
    except Exception as e:
        return False, f"License validation error: {str(e)}"


def create_user_license(user_id, license_type, stripe_payment_id=None):
    """Create a new license for a user after payment"""
    
    # Generate license key
    license_key, license_data = generate_license_key(user_id, license_type)
    
    # Create license record
    new_license = License(
        user_id=user_id,
        license_key=license_key,
        license_type=license_type,
        status='active',
        issued_at=datetime.fromisoformat(license_data['issued']),
        expires_at=datetime.fromisoformat(license_data['expires']),
        stripe_payment_id=stripe_payment_id,
        max_active_trades=license_data['max_trades'],
        features=license_data['features']
    )
    
    db.session.add(new_license)
    db.session.commit()
    
    return new_license


def get_active_license(user_id):
    """Get the active license for a user"""
    license = License.query.filter_by(
        user_id=user_id,
        status='active'
    ).filter(
        License.expires_at > datetime.now()
    ).first()
    
    # Update expired licenses
    if license and license.expires_at < datetime.now():
        license.status = 'expired'
        db.session.commit()
        return None
    
    return license


def check_license_valid(user_id):
    """Check if user has a valid active license"""
    license = get_active_license(user_id)
    if not license:
        return False, "No active license found"
    
    # Validate the license key
    is_valid, result = validate_license_key(license.license_key)
    
    if not is_valid:
        license.status = 'revoked'
        db.session.commit()
        return False, result
    
    return True, license


def require_license(f):
    """Decorator to require a valid license for a route"""
    from functools import wraps
    from flask import flash, redirect, url_for
    from flask_login import current_user
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this feature', 'warning')
            return redirect(url_for('login'))
        
        is_valid, result = check_license_valid(current_user.id)
        if not is_valid:
            flash(f'Valid license required: {result}', 'error')
            return redirect(url_for('buy_license'))
        
        return f(*args, **kwargs)
    
    return decorated_function
