from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os
import json
from datetime import datetime

def generate_report_pdf(report, customer):
    """Generate PDF report based on report and customer data"""
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    safe_customer_name = "".join(c for c in customer.company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"Prüfbericht_{safe_customer_name}_{report.audit_date}_{report.id}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.spaceAfter = 6
    
    # Parse content
    content_data = {}
    if report.content:
        try:
            content_data = json.loads(report.content)
        except:
            content_data = {}
    
    # Build PDF content
    story = []
    
    # Header with customer info
    story.append(Paragraph(customer.company_name, title_style))
    if customer.contact_person:
        story.append(Paragraph(customer.contact_person, normal_style))
    
    address_parts = []
    if customer.street:
        address_parts.append(customer.street)
    if customer.postal_code and customer.city:
        address_parts.append(f"{customer.postal_code} {customer.city}")
    
    if address_parts:
        story.append(Paragraph(" · ".join(address_parts), normal_style))
    
    story.append(Spacer(1, 20))
    
    # Report title
    audit_number = f"AUDIT {report.id:05d}"
    story.append(Paragraph(f"PRÜFBERICHT {audit_number}", title_style))
    
    # Author info
    author_info = [
        f"Verfasser {report.author}"
    ]
    if report.author_phone:
        author_info.append(f"Telefon {report.author_phone}")
    if report.author_email:
        author_info.append(f"E-Mail: {report.author_email}")
    
    story.append(Paragraph(" · ".join(author_info), normal_style))
    story.append(Spacer(1, 30))
    
    # Table of Contents
    story.append(Paragraph("Inhaltsverzeichnis", heading_style))
    toc_data = [
        ["1. Ausgangssituation", "2"],
        ["2. Palettenstabilität - Wickelschema und Haltekräfte", "3"],
        ["3. Gesamtübersicht", "4"],
        ["4. Einsparpotentiale", "5"],
        ["5. Fazit und nächste Schritte", "6"],
        ["6. Bilddokumentation", "8"]
    ]
    
    toc_table = Table(toc_data, colWidths=[14*cm, 2*cm])
    toc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 30))
    
    # Quintessenz (Summary)
    story.append(Paragraph("Quintessenz:", heading_style))
    quintessenz_text = """
    Durch eine ganzheitliche Optimierung der eingesetzten Stretchfolie in Verbindung mit der 
    Maschinentechnik, können Materialeinsparungen von bis zu 37% und damit eine Kostenreduzierung von 
    circa 14% realisiert werden. Zugleich können die CO2-Emissionen um 37% gesenkt werden. Die 
    Palettenstabilität und damit die Ladungssicherung der Packstücke kann dabei im Mittelwert um 8,2 kg 
    gesteigert werden.
    """
    story.append(Paragraph(quintessenz_text, normal_style))
    
    story.append(PageBreak())
    
    # 1. Ausgangssituation
    story.append(Paragraph("1. Ausgangssituation:", heading_style))
    
    # Machine information
    machine_info = []
    if content_data.get('machine_manufacturer'):
        machine_info.append(f"Hersteller {content_data['machine_manufacturer']}")
    if content_data.get('machine_model'):
        machine_info.append(f"Modell: {content_data['machine_model']}")
    
    ausgangssituation_text = f"""
    An Ihrem Produktionstandort in {customer.city or '[Ort]'} wird ein {content_data.get('machine_type', 'Roboter')} des 
    Herstellers {content_data.get('machine_manufacturer', '[Hersteller]')} 
    (Modell: {content_data.get('machine_model', '[Modell]')}) betrieben. 
    
    Zum Einsatz kommt aktuell eine transparente {content_data.get('foil_thickness', '23')} μm Maschinenstretchfolie von 
    {content_data.get('foil_manufacturer', 'unbekannt')}, diese wird aktuell von der Firma 
    {content_data.get('foil_supplier', '[Lieferant]')} geliefert. 
    
    Innerhalb des Arbeitsbereichs, ist eine Vordehnung auf bis zu {content_data.get('foil_work_area', '250')} % möglich.
    """
    
    story.append(Paragraph(ausgangssituation_text, normal_style))
    
    # Palette information
    if content_data.get('palette_type'):
        palette_text = f"""
        Getestet wurde eine {content_data.get('palette_type', 'Euro')}palette, 
        {content_data.get('palette_length', '120')} x {content_data.get('palette_width', '80')} x 250 cm (l x b x h), 
        mit {', '.join(content_data.get('packaging_types', ['Fassadenfenster']))}.
        """
        story.append(Paragraph(palette_text, normal_style))
    
    story.append(PageBreak())
    
    # 2. Palettenstabilität
    story.append(Paragraph("2. Palettenstabilität - Wickelschema und Haltekräfte", heading_style))
    
    # Machine details table
    if content_data.get('machine_manufacturer'):
        story.append(Paragraph(f"2.1 {content_data['machine_manufacturer']} {content_data.get('machine_type', 'Roboter')}", subheading_style))
    
    # Wickelschema visualization (simplified)
    wickel_data = [
        ["Wicklungsschema", ""],
        ["5 Wicklungen - Vordehnung 39%", "Oben"],
        ["5 Wicklungen - Vordehnung 39%", "Mitte"],
        ["4 Wicklungen - Vordehnung 39%", "Unten"]
    ]
    
    wickel_table = Table(wickel_data, colWidths=[10*cm, 6*cm])
    wickel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(wickel_table)
    story.append(Spacer(1, 20))
    
    # Palette description
    palette_desc = f"""
    {content_data.get('palette_type', 'Euro')}palette mit {', '.join(content_data.get('packaging_types', ['Packgut']))}, 
    Bruttogewicht: {content_data.get('palette_weight', '1200')} kg
    """
    story.append(Paragraph(palette_desc, normal_style))
    story.append(Spacer(1, 15))
    
    # Haltekräfte table
    haltekraft_data = [
        ["Haltekräfte (ASTM)", "Messwert \"SOLL\"", "Messwert \"IST\"", "Abweichung in Prozent"],
        ["Lange Seite oben:", "25 kg", "3 kg", "-88%"],
        ["Lange Seite unten:", "25 kg", "3 kg", "-88%"],
        ["Kurze Seite oben:", "40 kg", "4 kg", "-91%"],
        ["Kurze Seite unten:", "40 kg", "4 kg", "-91%"]
    ]
    
    haltekraft_table = Table(haltekraft_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
    haltekraft_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(haltekraft_table)
    story.append(Spacer(1, 15))
    
    # Assessment
    assessment_text = """
    Die Haltekräfte sind mit ungenügend zu bewerten. Eine Bewertung bzgl. der Erfüllung der 
    Anforderungen gem. EU-Richtlinie 2014/47 in Verbindung mit EUMOS 40509 ist nicht ohne 
    Validierungsversuch im Prüflabor abschließend möglich. Aktuell kann aber nicht davon ausgegangen 
    werden, dass diese vollumfänglich erfüllt werden.
    """
    story.append(Paragraph(assessment_text, normal_style))
    story.append(Spacer(1, 15))
    
    # Technical details
    tech_details = f"""
    Folien Dicke: {content_data.get('foil_thickness', '23')} μm | 
    Vordehnung: 38% | 
    Folienverbrauch: 428 g | 
    Gewicht Rollenkern: {content_data.get('foil_roll_weight', '1045')} g
    """
    story.append(Paragraph(tech_details, normal_style))
    
    # Additional sections would be added here for a complete report
    # For now, we'll add placeholders
    
    story.append(PageBreak())
    story.append(Paragraph("3. Gesamtübersicht", heading_style))
    story.append(Paragraph("Detaillierte Übersicht der Testergebnisse...", normal_style))
    
    story.append(PageBreak())
    story.append(Paragraph("4. Einsparpotentiale", heading_style))
    story.append(Paragraph("Analyse der möglichen Einsparungen...", normal_style))
    
    story.append(PageBreak())
    story.append(Paragraph("5. Fazit und nächste Schritte", heading_style))
    story.append(Paragraph("Zusammenfassung und Empfehlungen...", normal_style))
    
    story.append(PageBreak())
    story.append(Paragraph("6. Bilddokumentation", heading_style))
    story.append(Paragraph("Fotodokumentation des Audits...", normal_style))
    
    # Build PDF
    try:
        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

