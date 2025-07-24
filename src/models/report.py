from datetime import datetime
import json
from src import db

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    audit_date = db.Column(db.Date, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    author_phone = db.Column(db.String(50))
    author_email = db.Column(db.String(100))
    
    # Report content as JSON
    content = db.Column(db.Text)  # JSON string
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, completed, archived
    
    # PDF path
    pdf_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        content_data = {}
        if self.content:
            try:
                content_data = json.loads(self.content)
            except:
                content_data = {}
        
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'title': self.title,
            'audit_date': self.audit_date.isoformat() if self.audit_date else None,
            'author': self.author,
            'author_phone': self.author_phone,
            'author_email': self.author_email,
            'content': content_data,
            'status': self.status,
            'pdf_path': self.pdf_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            **content_data  # Flatten content data for easier access
        }
    
    @classmethod
    def from_dict(cls, data):
        # Extract content fields
        content_fields = [
            'focus_goals', 'machine_manufacturer', 'machine_type', 'machine_model',
            'machine_number', 'machine_year', 'machine_quantity', 'machine_features',
            'palette_type', 'palette_length', 'palette_width', 'palette_weight',
            'packaging_types', 'foil_supplier', 'foil_manufacturer', 'foil_article_number',
            'foil_thickness', 'foil_height', 'foil_roll_weight', 'foil_work_area'
        ]
        
        content_data = {}
        for field in content_fields:
            if field in data:
                content_data[field] = data[field]
        
        # Parse audit_date
        audit_date = None
        if data.get('audit_date'):
            try:
                audit_date = datetime.strptime(data['audit_date'], '%Y-%m-%d').date()
            except:
                audit_date = datetime.utcnow().date()
        
        return cls(
            customer_id=data.get('customer_id'),
            title=data.get('title'),
            audit_date=audit_date,
            author=data.get('author'),
            author_phone=data.get('author_phone'),
            author_email=data.get('author_email'),
            content=json.dumps(content_data),
            status=data.get('status', 'draft')
        )

