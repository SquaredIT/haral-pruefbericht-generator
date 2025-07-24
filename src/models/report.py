from datetime import datetime
import json
from src import db

class Report(db.Model):
    __tablename__ = 'reports'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Grundinformationen
    title = db.Column(db.String(200), nullable=False, default='PRÜFBERICHT AUDIT')
    audit_number = db.Column(db.String(50), unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    
    # Ausgangssituation
    production_site = db.Column(db.String(100))
    robot_manufacturer = db.Column(db.String(100))
    robot_model = db.Column(db.String(100))
    film_type = db.Column(db.String(100))
    film_thickness = db.Column(db.Float)  # in μm
    film_supplier = db.Column(db.String(100))
    max_prestretch = db.Column(db.Float)  # in %
    film_consumption_per_pallet = db.Column(db.Float)  # in g
    pallets_per_year = db.Column(db.Integer)
    roll_core_weight = db.Column(db.Float)  # in kg
    
    # Testpalette
    pallet_type = db.Column(db.String(100))
    pallet_dimensions = db.Column(db.String(100))
    pallet_content = db.Column(db.String(200))
    gross_weight = db.Column(db.Float)  # in kg
    
    # Wickelschema
    windings_top = db.Column(db.Integer)
    windings_middle = db.Column(db.Integer)
    windings_bottom = db.Column(db.Integer)
    prestretch_actual = db.Column(db.Float)  # in %
    
    # Haltekräfte SOLL-Werte (in kg)
    holding_force_long_top_target = db.Column(db.Float)
    holding_force_long_bottom_target = db.Column(db.Float)
    holding_force_short_top_target = db.Column(db.Float)
    holding_force_short_bottom_target = db.Column(db.Float)
    
    # Haltekräfte IST-Werte (in kg)
    holding_force_long_top_actual = db.Column(db.Float)
    holding_force_long_bottom_actual = db.Column(db.Float)
    holding_force_short_top_actual = db.Column(db.Float)
    holding_force_short_bottom_actual = db.Column(db.Float)
    
    # Bewertung
    holding_force_rating = db.Column(db.String(50))
    eu_directive_compliant = db.Column(db.Boolean, default=False)
    certificate_required = db.Column(db.Boolean, default=False)
    
    # Alternativen (JSON-Feld für bis zu 3 Alternativen)
    alternatives = db.Column(db.Text)  # JSON: [{"film_thickness": 17, "prestretch": 38, "pallet_stability": "Gut"}, ...]
    
    # Empfehlung
    recommended_alternative = db.Column(db.String(50))
    quality_improvement = db.Column(db.Boolean, default=False)
    holding_force_increase = db.Column(db.Boolean, default=False)
    
    # Fazit und nächste Schritte
    conclusion_text = db.Column(db.Text)
    recommendations_text = db.Column(db.Text)
    next_steps_text = db.Column(db.Text)
    implementation_timeframe = db.Column(db.String(50))
    training_required = db.Column(db.Boolean, default=False)
    follow_up_required = db.Column(db.Boolean, default=False)
    
    # Bilddokumentation (JSON-Feld)
    images = db.Column(db.Text)  # JSON: [{"filename": "img1.jpg", "description": "..."}, ...]
    
    # Quintessenz (automatisch berechnet)
    material_savings = db.Column(db.Float, default=0)  # in %
    cost_reduction = db.Column(db.Float, default=0)  # in %
    co2_reduction = db.Column(db.Float, default=0)  # in %
    stability_increase = db.Column(db.Float, default=0)  # in kg
    
    # Berechnete Werte
    total_material_consumption = db.Column(db.Float)  # in kg/Jahr
    annual_costs = db.Column(db.Float)  # in €
    co2_emissions = db.Column(db.Float)  # in kg/Jahr
    
    # Status und Metadaten
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, completed, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='reports')
    user = db.relationship('User', backref='reports')
    
    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)
        if not self.audit_number:
            self.audit_number = self.generate_audit_number()
    
    @staticmethod
    def generate_audit_number():
        """Generiert eine eindeutige Auftragsnummer"""
        import time
        import random
        timestamp = str(int(time.time()))[-5:]
        random_num = str(random.randint(100, 999))
        return timestamp + random_num
    
    def set_alternatives(self, alternatives_list):
        """Setzt die Alternativen als JSON"""
        self.alternatives = json.dumps(alternatives_list) if alternatives_list else None
    
    def get_alternatives(self):
        """Gibt die Alternativen als Python-Liste zurück"""
        if self.alternatives:
            try:
                return json.loads(self.alternatives)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_images(self, images_list):
        """Setzt die Bilder als JSON"""
        self.images = json.dumps(images_list) if images_list else None
    
    def get_images(self):
        """Gibt die Bilder als Python-Liste zurück"""
        if self.images:
            try:
                return json.loads(self.images)
            except json.JSONDecodeError:
                return []
        return []
    
    def calculate_holding_force_deviations(self):
        """Berechnet die Abweichungen der Haltekräfte"""
        deviations = {}
        
        # Lange Seite oben
        if self.holding_force_long_top_target and self.holding_force_long_top_target > 0:
            deviation = ((self.holding_force_long_top_actual or 0) - self.holding_force_long_top_target) / self.holding_force_long_top_target * 100
            deviations['long_top'] = round(deviation, 1)
        
        # Lange Seite unten
        if self.holding_force_long_bottom_target and self.holding_force_long_bottom_target > 0:
            deviation = ((self.holding_force_long_bottom_actual or 0) - self.holding_force_long_bottom_target) / self.holding_force_long_bottom_target * 100
            deviations['long_bottom'] = round(deviation, 1)
        
        # Kurze Seite oben
        if self.holding_force_short_top_target and self.holding_force_short_top_target > 0:
            deviation = ((self.holding_force_short_top_actual or 0) - self.holding_force_short_top_target) / self.holding_force_short_top_target * 100
            deviations['short_top'] = round(deviation, 1)
        
        # Kurze Seite unten
        if self.holding_force_short_bottom_target and self.holding_force_short_bottom_target > 0:
            deviation = ((self.holding_force_short_bottom_actual or 0) - self.holding_force_short_bottom_target) / self.holding_force_short_bottom_target * 100
            deviations['short_bottom'] = round(deviation, 1)
        
        return deviations
    
    def calculate_consumption_and_costs(self):
        """Berechnet Verbrauch und Kosten"""
        if self.film_consumption_per_pallet and self.pallets_per_year:
            # Gesamtmaterialverbrauch in kg/Jahr
            self.total_material_consumption = (self.film_consumption_per_pallet * self.pallets_per_year) / 1000
            
            # Vereinfachte Kostenberechnung (€2.50 pro kg Folie + Rollenkern-Kosten)
            foil_cost_per_kg = 2.50
            roll_core_cost_per_year = (self.roll_core_weight or 0) * 0.50 * (self.pallets_per_year or 0) / 1000
            self.annual_costs = (self.total_material_consumption * foil_cost_per_kg) + roll_core_cost_per_year
            
            # CO2-Emissionen (3.02 kg CO2 pro kg Folie)
            co2_factor = 3.02
            self.co2_emissions = self.total_material_consumption * co2_factor
    
    def calculate_quintessenz(self):
        """Berechnet die Quintessenz basierend auf der besten Alternative"""
        alternatives = self.get_alternatives()
        if not alternatives or not self.film_thickness:
            return
        
        # Finde die beste Alternative (niedrigste Foliendicke)
        best_alternative = min(alternatives, key=lambda x: float(x.get('film_thickness', 999)) if x.get('film_thickness') else 999)
        
        if best_alternative.get('film_thickness'):
            new_thickness = float(best_alternative['film_thickness'])
            current_thickness = float(self.film_thickness)
            
            if current_thickness > 0:
                # Materialeinsparung
                self.material_savings = round(((current_thickness - new_thickness) / current_thickness) * 100, 1)
                
                # Kostenreduzierung (vereinfacht: 40% der Materialeinsparung)
                self.cost_reduction = round(self.material_savings * 0.4, 1)
                
                # CO2-Reduktion (entspricht der Materialeinsparung)
                self.co2_reduction = self.material_savings
                
                # Stabilitätssteigerung (vereinfacht: 20% der Materialeinsparung in kg)
                self.stability_increase = round(self.material_savings * 0.2, 1)
    
    def update_calculations(self):
        """Aktualisiert alle Berechnungen"""
        self.calculate_consumption_and_costs()
        self.calculate_quintessenz()
    
    def to_dict(self):
        """Konvertiert das Report-Objekt zu einem Dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'title': self.title,
            'audit_number': self.audit_number,
            'author': self.author,
            'phone': self.phone,
            'email': self.email,
            'production_site': self.production_site,
            'robot_manufacturer': self.robot_manufacturer,
            'robot_model': self.robot_model,
            'film_type': self.film_type,
            'film_thickness': self.film_thickness,
            'film_supplier': self.film_supplier,
            'max_prestretch': self.max_prestretch,
            'film_consumption_per_pallet': self.film_consumption_per_pallet,
            'pallets_per_year': self.pallets_per_year,
            'roll_core_weight': self.roll_core_weight,
            'pallet_type': self.pallet_type,
            'pallet_dimensions': self.pallet_dimensions,
            'pallet_content': self.pallet_content,
            'gross_weight': self.gross_weight,
            'windings_top': self.windings_top,
            'windings_middle': self.windings_middle,
            'windings_bottom': self.windings_bottom,
            'prestretch_actual': self.prestretch_actual,
            'holding_force_long_top_target': self.holding_force_long_top_target,
            'holding_force_long_bottom_target': self.holding_force_long_bottom_target,
            'holding_force_short_top_target': self.holding_force_short_top_target,
            'holding_force_short_bottom_target': self.holding_force_short_bottom_target,
            'holding_force_long_top_actual': self.holding_force_long_top_actual,
            'holding_force_long_bottom_actual': self.holding_force_long_bottom_actual,
            'holding_force_short_top_actual': self.holding_force_short_top_actual,
            'holding_force_short_bottom_actual': self.holding_force_short_bottom_actual,
            'holding_force_rating': self.holding_force_rating,
            'eu_directive_compliant': self.eu_directive_compliant,
            'certificate_required': self.certificate_required,
            'alternatives': self.get_alternatives(),
            'recommended_alternative': self.recommended_alternative,
            'quality_improvement': self.quality_improvement,
            'holding_force_increase': self.holding_force_increase,
            'conclusion_text': self.conclusion_text,
            'recommendations_text': self.recommendations_text,
            'next_steps_text': self.next_steps_text,
            'implementation_timeframe': self.implementation_timeframe,
            'training_required': self.training_required,
            'follow_up_required': self.follow_up_required,
            'images': self.get_images(),
            'material_savings': self.material_savings,
            'cost_reduction': self.cost_reduction,
            'co2_reduction': self.co2_reduction,
            'stability_increase': self.stability_increase,
            'total_material_consumption': self.total_material_consumption,
            'annual_costs': self.annual_costs,
            'co2_emissions': self.co2_emissions,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'customer': self.customer.to_dict() if self.customer else None,
            'user': {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email
            } if self.user else None,
            'holding_force_deviations': self.calculate_holding_force_deviations()
        }
    
    def __repr__(self):
        return f'<Report {self.audit_number}: {self.title}>'

