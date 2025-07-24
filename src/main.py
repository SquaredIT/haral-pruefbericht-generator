import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db, User
from src.models.customer import Customer
from src.models.report import Report
from src.routes.user import user_bp
from src.routes.customer import customer_bp
from src.routes.report import report_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration for Heroku
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'haral-pruefbericht-secret-key-2025')

# Enable CORS for all routes with credentials support
CORS(app, supports_credentials=True)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(report_bp, url_prefix='/api')

# Database configuration - Heroku PostgreSQL or local SQLite
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Heroku PostgreSQL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database tables might already exist: {e}")
    
    # Create default admin user if no users exist
    try:
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@haral.eu',
                first_name='Admin',
                last_name='User',
                phone='0173 / 135 90 00',
                role='Admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # Create default auditor
            auditor_user = User(
                username='ralf.hartmann',
                email='rh@haral.eu',
                first_name='Ralf',
                last_name='Hartmann',
                phone='0173 / 135 90 00',
                role='Auditor'
            )
            auditor_user.set_password('auditor123')
            db.session.add(auditor_user)
            
            db.session.commit()
            print("Default users created:")
            print("Admin: admin / admin123")
            print("Auditor: ralf.hartmann / auditor123")
    except Exception as e:
        print(f"Error creating default users: {e}")
        db.session.rollback()
    
    # Create sample customer if none exists
    try:
        if Customer.query.count() == 0:
            sample_customer = Customer(
                company_name='IGM GmbH & Co. KG Fenster und Fassaden',
                contact_person='Marius Veith',
                street='Hinter Inghell',
                postal_code='67744',
                city='Medard'
            )
            db.session.add(sample_customer)
            db.session.commit()
    except Exception as e:
        print(f"Error creating sample customer: {e}")
        db.session.rollback()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

