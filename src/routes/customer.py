import os
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from ..models.customer import Customer
from .. import db

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    try:
        customers = Customer.query.all()
        return jsonify([customer.to_dict() for customer in customers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer by ID"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create new customer"""
    try:
        data = request.get_json()
        
        if not data or not data.get('company_name'):
            return jsonify({'error': 'Company name is required'}), 400
        
        customer = Customer(
            company_name=data['company_name'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            notes=data.get('notes')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'company_name' in data:
            customer.company_name = data['company_name']
        if 'contact_person' in data:
            customer.contact_person = data['contact_person']
        if 'email' in data:
            customer.email = data['email']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'address' in data:
            customer.address = data['address']
        if 'notes' in data:
            customer.notes = data['notes']
        
        db.session.commit()
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Delete logo file if exists
        if customer.logo_path:
            logo_path = os.path.join(current_app.root_path, 'static', customer.logo_path)
            if os.path.exists(logo_path):
                os.remove(logo_path)
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'Customer deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>/logo', methods=['POST'])
def upload_logo(customer_id):
    """Upload logo for customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        if 'logo' not in request.files:
            return jsonify({'error': 'No logo file provided'}), 400
        
        file = request.files['logo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Delete old logo if exists
            if customer.logo_path:
                old_logo_path = os.path.join(current_app.root_path, 'static', customer.logo_path)
                if os.path.exists(old_logo_path):
                    os.remove(old_logo_path)
            
            # Generate secure filename
            filename = secure_filename(f"customer_{customer_id}_{file.filename}")
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            file.save(file_path)
            
            # Update customer record
            customer.logo_path = f"uploads/logos/{filename}"
            db.session.commit()
            
            return jsonify({
                'message': 'Logo uploaded successfully',
                'logo_path': customer.logo_path
            })
        else:
            return jsonify({'error': 'Invalid file type. Only images are allowed.'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>/logo', methods=['GET'])
def get_logo(customer_id):
    """Get customer logo"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        if not customer.logo_path:
            return jsonify({'error': 'No logo found'}), 404
        
        logo_path = os.path.join(current_app.root_path, 'static', customer.logo_path)
        
        if not os.path.exists(logo_path):
            return jsonify({'error': 'Logo file not found'}), 404
        
        return send_file(logo_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

