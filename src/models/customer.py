from datetime import datetime
from src.models.user import db

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    contact_person = db.Column(db.String(255))
    street = db.Column(db.String(255))
    postal_code = db.Column(db.String(20))
    city = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    notes = db.Column(db.Text)
    logo_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'street': self.street,
            'postal_code': self.postal_code,
            'city': self.city,
            'phone': self.phone,
            'email': self.email,
            'notes': self.notes,
            'logo_path': self.logo_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            company_name=data.get('company_name'),
            contact_person=data.get('contact_person'),
            street=data.get('street'),
            postal_code=data.get('postal_code'),
            city=data.get('city'),
            phone=data.get('phone'),
            email=data.get('email'),
            notes=data.get('notes'),
            logo_path=data.get('logo_path')
        )

