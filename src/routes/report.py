from flask import Blueprint, request, jsonify, send_file
from src import db
from src.models.report import Report
from src.models.customer import Customer
from src.models.user import User
from src.utils.enhanced_pdf_generator import generate_enhanced_report_pdf
import os
from datetime import datetime
import json

report_bp = Blueprint('report', __name__)

@report_bp.route('/api/reports', methods=['GET'])
def get_reports():
    """Alle Berichte abrufen"""
    try:
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Einzelnen Bericht abrufen"""
    try:
        report = Report.query.get_or_404(report_id)
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports', methods=['POST'])
def create_report():
    """Neuen Bericht erstellen"""
    try:
        data = request.get_json()
        
        # Validierung der Pflichtfelder
        required_fields = ['customer_id', 'user_id', 'author']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Feld {field} ist erforderlich'}), 400
        
        # Prüfen ob Kunde und User existieren
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Kunde nicht gefunden'}), 404
            
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'Benutzer nicht gefunden'}), 404
        
        # Neuen Bericht erstellen
        report = Report(
            customer_id=data['customer_id'],
            user_id=data['user_id'],
            title=data.get('title', 'PRÜFBERICHT AUDIT'),
            audit_number=data.get('audit_number') or Report.generate_audit_number(),
            author=data['author'],
            phone=data.get('phone'),
            email=data.get('email'),
            
            # Ausgangssituation
            production_site=data.get('production_site'),
            robot_manufacturer=data.get('robot_manufacturer'),
            robot_model=data.get('robot_model'),
            film_type=data.get('film_type'),
            film_thickness=float(data['film_thickness']) if data.get('film_thickness') else None,
            film_supplier=data.get('film_supplier'),
            max_prestretch=float(data['max_prestretch']) if data.get('max_prestretch') else None,
            film_consumption_per_pallet=float(data['film_consumption_per_pallet']) if data.get('film_consumption_per_pallet') else None,
            pallets_per_year=int(data['pallets_per_year']) if data.get('pallets_per_year') else None,
            roll_core_weight=float(data['roll_core_weight']) if data.get('roll_core_weight') else None,
            
            # Testpalette
            pallet_type=data.get('pallet_type'),
            pallet_dimensions=data.get('pallet_dimensions'),
            pallet_content=data.get('pallet_content'),
            gross_weight=float(data['gross_weight']) if data.get('gross_weight') else None,
            
            # Wickelschema
            windings_top=int(data['windings_top']) if data.get('windings_top') else None,
            windings_middle=int(data['windings_middle']) if data.get('windings_middle') else None,
            windings_bottom=int(data['windings_bottom']) if data.get('windings_bottom') else None,
            prestretch_actual=float(data['prestretch_actual']) if data.get('prestretch_actual') else None,
            
            # Haltekräfte SOLL
            holding_force_long_top_target=float(data['holding_force_long_top_target']) if data.get('holding_force_long_top_target') else None,
            holding_force_long_bottom_target=float(data['holding_force_long_bottom_target']) if data.get('holding_force_long_bottom_target') else None,
            holding_force_short_top_target=float(data['holding_force_short_top_target']) if data.get('holding_force_short_top_target') else None,
            holding_force_short_bottom_target=float(data['holding_force_short_bottom_target']) if data.get('holding_force_short_bottom_target') else None,
            
            # Haltekräfte IST
            holding_force_long_top_actual=float(data['holding_force_long_top_actual']) if data.get('holding_force_long_top_actual') else None,
            holding_force_long_bottom_actual=float(data['holding_force_long_bottom_actual']) if data.get('holding_force_long_bottom_actual') else None,
            holding_force_short_top_actual=float(data['holding_force_short_top_actual']) if data.get('holding_force_short_top_actual') else None,
            holding_force_short_bottom_actual=float(data['holding_force_short_bottom_actual']) if data.get('holding_force_short_bottom_actual') else None,
            
            # Bewertung
            holding_force_rating=data.get('holding_force_rating'),
            eu_directive_compliant=bool(data.get('eu_directive_compliant', False)),
            certificate_required=bool(data.get('certificate_required', False)),
            
            # Empfehlung
            recommended_alternative=data.get('recommended_alternative'),
            quality_improvement=bool(data.get('quality_improvement', False)),
            holding_force_increase=bool(data.get('holding_force_increase', False)),
            
            # Fazit
            conclusion_text=data.get('conclusion_text'),
            recommendations_text=data.get('recommendations_text'),
            next_steps_text=data.get('next_steps_text'),
            implementation_timeframe=data.get('implementation_timeframe'),
            training_required=bool(data.get('training_required', False)),
            follow_up_required=bool(data.get('follow_up_required', False)),
            
            # Quintessenz
            material_savings=float(data['material_savings']) if data.get('material_savings') else 0,
            cost_reduction=float(data['cost_reduction']) if data.get('cost_reduction') else 0,
            co2_reduction=float(data['co2_reduction']) if data.get('co2_reduction') else 0,
            stability_increase=float(data['stability_increase']) if data.get('stability_increase') else 0,
            
            status=data.get('status', 'draft')
        )
        
        # Alternativen setzen
        if data.get('alternatives'):
            report.set_alternatives(data['alternatives'])
        
        # Bilder setzen
        if data.get('images'):
            report.set_images(data['images'])
        
        # Berechnungen durchführen
        report.update_calculations()
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify(report.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': f'Ungültiger Wert: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Bericht aktualisieren"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.get_json()
        
        # Aktualisierbare Felder
        updatable_fields = [
            'title', 'author', 'phone', 'email',
            'production_site', 'robot_manufacturer', 'robot_model',
            'film_type', 'film_thickness', 'film_supplier', 'max_prestretch',
            'film_consumption_per_pallet', 'pallets_per_year', 'roll_core_weight',
            'pallet_type', 'pallet_dimensions', 'pallet_content', 'gross_weight',
            'windings_top', 'windings_middle', 'windings_bottom', 'prestretch_actual',
            'holding_force_long_top_target', 'holding_force_long_bottom_target',
            'holding_force_short_top_target', 'holding_force_short_bottom_target',
            'holding_force_long_top_actual', 'holding_force_long_bottom_actual',
            'holding_force_short_top_actual', 'holding_force_short_bottom_actual',
            'holding_force_rating', 'eu_directive_compliant', 'certificate_required',
            'recommended_alternative', 'quality_improvement', 'holding_force_increase',
            'conclusion_text', 'recommendations_text', 'next_steps_text',
            'implementation_timeframe', 'training_required', 'follow_up_required',
            'material_savings', 'cost_reduction', 'co2_reduction', 'stability_increase',
            'status'
        ]
        
        # Felder aktualisieren
        for field in updatable_fields:
            if field in data:
                value = data[field]
                
                # Typkonvertierung für numerische Felder
                numeric_fields = [
                    'film_thickness', 'max_prestretch', 'film_consumption_per_pallet',
                    'pallets_per_year', 'roll_core_weight', 'gross_weight',
                    'prestretch_actual', 'holding_force_long_top_target',
                    'holding_force_long_bottom_target', 'holding_force_short_top_target',
                    'holding_force_short_bottom_target', 'holding_force_long_top_actual',
                    'holding_force_long_bottom_actual', 'holding_force_short_top_actual',
                    'holding_force_short_bottom_actual', 'material_savings',
                    'cost_reduction', 'co2_reduction', 'stability_increase'
                ]
                
                integer_fields = [
                    'pallets_per_year', 'windings_top', 'windings_middle', 'windings_bottom'
                ]
                
                boolean_fields = [
                    'eu_directive_compliant', 'certificate_required',
                    'quality_improvement', 'holding_force_increase',
                    'training_required', 'follow_up_required'
                ]
                
                if field in boolean_fields:
                    value = bool(value)
                elif field in integer_fields and value is not None:
                    value = int(value) if value != '' else None
                elif field in numeric_fields and value is not None:
                    value = float(value) if value != '' else None
                
                setattr(report, field, value)
        
        # Alternativen aktualisieren
        if 'alternatives' in data:
            report.set_alternatives(data['alternatives'])
        
        # Bilder aktualisieren
        if 'images' in data:
            report.set_images(data['images'])
        
        # Berechnungen aktualisieren
        report.update_calculations()
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(report.to_dict())
        
    except ValueError as e:
        return jsonify({'error': f'Ungültiger Wert: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/<int:report_id>/status', methods=['PUT'])
def update_report_status(report_id):
    """Berichtstatus aktualisieren"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if new_status not in ['draft', 'completed', 'archived']:
            return jsonify({'error': 'Ungültiger Status'}), 400
        
        report.status = new_status
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': f'Status auf {new_status} aktualisiert'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Bericht löschen"""
    try:
        report = Report.query.get_or_404(report_id)
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Bericht erfolgreich gelöscht'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/<int:report_id>/pdf', methods=['GET'])
def generate_report_pdf(report_id):
    """PDF-Bericht generieren"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # PDF generieren
        pdf_path = generate_enhanced_report_pdf(report)
        
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF konnte nicht generiert werden'}), 500
        
        # PDF-Datei senden
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'Pruefbericht_{report.audit_number}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/statistics', methods=['GET'])
def get_report_statistics():
    """Berichtsstatistiken abrufen"""
    try:
        total_reports = Report.query.count()
        draft_reports = Report.query.filter_by(status='draft').count()
        completed_reports = Report.query.filter_by(status='completed').count()
        archived_reports = Report.query.filter_by(status='archived').count()
        
        # Durchschnittliche Einsparungen
        avg_material_savings = db.session.query(db.func.avg(Report.material_savings)).filter(
            Report.material_savings > 0
        ).scalar() or 0
        
        avg_cost_reduction = db.session.query(db.func.avg(Report.cost_reduction)).filter(
            Report.cost_reduction > 0
        ).scalar() or 0
        
        avg_co2_reduction = db.session.query(db.func.avg(Report.co2_reduction)).filter(
            Report.co2_reduction > 0
        ).scalar() or 0
        
        return jsonify({
            'total_reports': total_reports,
            'draft_reports': draft_reports,
            'completed_reports': completed_reports,
            'archived_reports': archived_reports,
            'average_savings': {
                'material_savings': round(avg_material_savings, 1),
                'cost_reduction': round(avg_cost_reduction, 1),
                'co2_reduction': round(avg_co2_reduction, 1)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/search', methods=['GET'])
def search_reports():
    """Berichte suchen"""
    try:
        query = request.args.get('q', '')
        status = request.args.get('status')
        customer_id = request.args.get('customer_id')
        
        reports_query = Report.query
        
        if query:
            reports_query = reports_query.filter(
                db.or_(
                    Report.title.contains(query),
                    Report.audit_number.contains(query),
                    Report.author.contains(query)
                )
            )
        
        if status:
            reports_query = reports_query.filter_by(status=status)
        
        if customer_id:
            reports_query = reports_query.filter_by(customer_id=customer_id)
        
        reports = reports_query.order_by(Report.created_at.desc()).all()
        
        return jsonify([report.to_dict() for report in reports])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/api/reports/<int:report_id>/duplicate', methods=['POST'])
def duplicate_report(report_id):
    """Bericht duplizieren"""
    try:
        original_report = Report.query.get_or_404(report_id)
        
        # Neuen Bericht basierend auf dem Original erstellen
        new_report = Report(
            customer_id=original_report.customer_id,
            user_id=original_report.user_id,
            title=f"{original_report.title} (Kopie)",
            author=original_report.author,
            phone=original_report.phone,
            email=original_report.email,
            production_site=original_report.production_site,
            robot_manufacturer=original_report.robot_manufacturer,
            robot_model=original_report.robot_model,
            film_type=original_report.film_type,
            film_thickness=original_report.film_thickness,
            film_supplier=original_report.film_supplier,
            max_prestretch=original_report.max_prestretch,
            film_consumption_per_pallet=original_report.film_consumption_per_pallet,
            pallets_per_year=original_report.pallets_per_year,
            roll_core_weight=original_report.roll_core_weight,
            pallet_type=original_report.pallet_type,
            pallet_dimensions=original_report.pallet_dimensions,
            pallet_content=original_report.pallet_content,
            gross_weight=original_report.gross_weight,
            windings_top=original_report.windings_top,
            windings_middle=original_report.windings_middle,
            windings_bottom=original_report.windings_bottom,
            prestretch_actual=original_report.prestretch_actual,
            holding_force_long_top_target=original_report.holding_force_long_top_target,
            holding_force_long_bottom_target=original_report.holding_force_long_bottom_target,
            holding_force_short_top_target=original_report.holding_force_short_top_target,
            holding_force_short_bottom_target=original_report.holding_force_short_bottom_target,
            holding_force_long_top_actual=original_report.holding_force_long_top_actual,
            holding_force_long_bottom_actual=original_report.holding_force_long_bottom_actual,
            holding_force_short_top_actual=original_report.holding_force_short_top_actual,
            holding_force_short_bottom_actual=original_report.holding_force_short_bottom_actual,
            holding_force_rating=original_report.holding_force_rating,
            eu_directive_compliant=original_report.eu_directive_compliant,
            certificate_required=original_report.certificate_required,
            alternatives=original_report.alternatives,
            recommended_alternative=original_report.recommended_alternative,
            quality_improvement=original_report.quality_improvement,
            holding_force_increase=original_report.holding_force_increase,
            conclusion_text=original_report.conclusion_text,
            recommendations_text=original_report.recommendations_text,
            next_steps_text=original_report.next_steps_text,
            implementation_timeframe=original_report.implementation_timeframe,
            training_required=original_report.training_required,
            follow_up_required=original_report.follow_up_required,
            images=original_report.images,
            status='draft'  # Neue Berichte sind immer Entwürfe
        )
        
        # Berechnungen durchführen
        new_report.update_calculations()
        
        db.session.add(new_report)
        db.session.commit()
        
        return jsonify(new_report.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

