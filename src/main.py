import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src import create_app, db
from src.models.user import User
from src.models.customer import Customer
from src.models.report import Report
from src.routes.user import user_bp
from src.routes.customer import customer_bp
from src.routes.report import report_bp

# Create app using factory pattern
app = create_app()

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(report_bp, url_prefix='/api')

@app.route('/')
def serve_index():
    """Serve the main application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_or_spa(path):
    """Serve static files or SPA routes"""
    try:
        # Try to serve static file first
        return send_from_directory(app.static_folder, path)
    except:
        # If file doesn't exist, serve index.html for SPA routing
        return send_from_directory(app.static_folder, 'index.html')

def create_default_users():
    """Create default users if they don't exist"""
    try:
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                first_name='Admin',
                last_name='User',
                email='admin@haral.com',
                phone='',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Check if auditor user exists
        auditor = User.query.filter_by(username='ralf.hartmann').first()
        if not auditor:
            auditor = User(
                username='ralf.hartmann',
                first_name='Ralf',
                last_name='Hartmann',
                email='ralf.hartmann@haral.com',
                phone='+49 123 456789',
                role='auditor'
            )
            auditor.set_password('auditor123')
            db.session.add(auditor)
        
        db.session.commit()
        print("Default users created:")
        print("Admin: admin / admin123")
        print("Auditor: ralf.hartmann / auditor123")
        
    except Exception as e:
        print(f"Error creating default users: {e}")
        db.session.rollback()

def create_sample_customer():
    """Create sample customer if none exist"""
    try:
        if Customer.query.count() == 0:
            sample_customer = Customer(
                company_name='IGM GmbH & Co. KG Fenster und Fassaden',
                contact_person='Marius Veith',
                email='info@igm-fenster.de',
                phone='+49 6221 123456',
                address='Hinter Inghell\n67744 Medard',
                notes='Spezialist für Fenster und Fassadensysteme'
            )
            db.session.add(sample_customer)
            db.session.commit()
            print("Sample customer created: IGM GmbH & Co. KG")
    except Exception as e:
        print(f"Error creating sample customer: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create default users and sample data
        create_default_users()
        create_sample_customer()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

