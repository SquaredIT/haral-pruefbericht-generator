from flask import Blueprint, request, jsonify, send_file
from src.models.report import Report
from src.models.customer import Customer
from src.models.user import db
from src.utils.enhanced_pdf_generator import generate_enhanced_report_pdf
import os
from datetime import datetime

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports', methods=['GET'])
def get_reports():
    """Get all reports"""
    try:
        reports = Report.query.all()
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Get a specific report"""
    try:
        report = Report.query.get_or_404(report_id)
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports', methods=['POST'])
def create_report():
    """Create a new report"""
    try:
        data = request.get_json()
        
        if not data or not data.get('customer_id'):
            return jsonify({'error': 'Customer ID is required'}), 400
        
        # Verify customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        report = Report.from_dict(data)
        db.session.add(report)
        db.session.commit()
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Update a report"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update basic fields
        for field in ['title', 'author', 'author_phone', 'author_email', 'status']:
            if field in data:
                setattr(report, field, data[field])
        
        # Update audit_date
        if 'audit_date' in data:
            try:
                report.audit_date = datetime.strptime(data['audit_date'], '%Y-%m-%d').date()
            except:
                pass
        
        # Update content
        content_fields = [
            'focus_goals', 'machine_manufacturer', 'machine_type', 'machine_model',
            'machine_number', 'machine_year', 'machine_quantity', 'machine_features',
            'palette_type', 'palette_length', 'palette_width', 'palette_weight',
            'packaging_types', 'foil_supplier', 'foil_manufacturer', 'foil_article_number',
            'foil_thickness', 'foil_height', 'foil_roll_weight', 'foil_work_area'
        ]
        
        import json
        content_data = {}
        if report.content:
            try:
                content_data = json.loads(report.content)
            except:
                content_data = {}
        
        for field in content_fields:
            if field in data:
                content_data[field] = data[field]
        
        report.content = json.dumps(content_data)
        
        db.session.commit()
        return jsonify(report.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a report"""
    try:
        report = Report.query.get_or_404(report_id)
        
        # Delete PDF file if exists
        if report.pdf_path and os.path.exists(report.pdf_path):
            os.remove(report.pdf_path)
        
        db.session.delete(report)
        db.session.commit()
        return jsonify({'message': 'Report deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/<int:report_id>/pdf', methods=['GET'])
def download_report_pdf(report_id):
    """Generate and download report PDF"""
    try:
        report = Report.query.get_or_404(report_id)
        customer = Customer.query.get_or_404(report.customer_id)
        
        # Generate PDF
        pdf_path = generate_enhanced_report_pdf(report, customer)
        
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        # Update report with PDF path
        report.pdf_path = pdf_path
        db.session.commit()
        
        # Send file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Prüfbericht_{customer.company_name}_{report.audit_date}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/<int:report_id>/status', methods=['PUT'])
def update_report_status(report_id):
    """Update report status"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['draft', 'in_progress', 'completed', 'archived']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        report.status = data['status']
        
        # If status is completed, try to generate PDF
        if data['status'] == 'completed':
            try:
                customer = Customer.query.get_or_404(report.customer_id)
                pdf_path = generate_enhanced_report_pdf(report, customer)
                if pdf_path:
                    report.pdf_path = pdf_path
            except Exception as e:
                print(f"PDF generation failed: {e}")
        
        db.session.commit()
        return jsonify(report.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@report_bp.route('/reports/<int:report_id>/generate-pdf', methods=['POST'])
def generate_pdf(report_id):
    """Generate PDF for a report"""
    try:
        report = Report.query.get_or_404(report_id)
        customer = Customer.query.get_or_404(report.customer_id)
        
        # Generate PDF
        pdf_path = generate_enhanced_report_pdf(report, customer)
        
        if not pdf_path:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        # Update report with PDF path
        report.pdf_path = pdf_path
        report.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'message': 'PDF generated successfully',
            'pdf_path': pdf_path
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

