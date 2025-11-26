import os
import stripe
import uuid
import hashlib
from flask import Blueprint, request, jsonify, current_app
from app import db, app
from models import License, User

bp = Blueprint('payments', __name__, url_prefix='/payments')

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')


@bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json() or request.form
    price_id = data.get('price_id') or os.environ.get('STRIPE_PRICE_ID')
    success_url = data.get('success_url') or os.environ.get('STRIPE_SUCCESS_URL', request.url_root)
    cancel_url = data.get('cancel_url') or os.environ.get('STRIPE_CANCEL_URL', request.url_root)
    customer_email = data.get('customer_email')
    if not price_id:
        return jsonify({'error': 'price_id required'}), 400

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=customer_email,
    )
    return jsonify({'id': session.id, 'url': session.url})


@bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret) if webhook_secret else stripe.Event.construct_from(request.json, stripe.api_key)
    except Exception as e:
        current_app.logger.exception('Webhook signature verification failed')
        return jsonify({'error': str(e)}), 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')
        # Create a license for the user if they exist
        if customer_email:
            with app.app_context():
                user = User.query.filter_by(email=customer_email).first()
                if user:
                    lic = License()
                    lic.user_id = user.id
                    # Generate a short 13-character license key from Stripe session ID
                    session_id = session.get('id', '')
                    short_id = uuid.uuid4().hex[:8].upper()
                    hash_suffix = hashlib.md5(session_id.encode()).hexdigest()[:5].upper()
                    lic.license_key = f"{short_id}{hash_suffix}"
                    lic.license_type = os.environ.get('DEFAULT_PURCHASE_LICENSE_TYPE', 'basic')
                    lic.status = 'active'
                    db.session.add(lic)
                    db.session.commit()
    return jsonify({'status': 'received'})


def register_payments_blueprint():
    app.register_blueprint(bp)


register_payments_blueprint()
