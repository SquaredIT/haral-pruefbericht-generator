from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line
from reportlab.graphics import renderPDF
import os
import json
from datetime import datetime

# HARAL Brand Colors (based on visual analysis)
HARAL_YELLOW = colors.Color(1, 0.8, 0)  # Yellow from logo
HARAL_GRAY = colors.Color(0.4, 0.4, 0.4)  # Dark gray
HARAL_LIGHT_GRAY = colors.Color(0.9, 0.9, 0.9)  # Light gray for backgrounds
HARAL_BLUE = colors.Color(0.2, 0.4, 0.6)  # Professional blue

def create_header_footer(canvas, doc):
    """Create consistent header and footer for all pages"""
    canvas.saveState()
    
    # Header - HARAL Logo area (simplified)
    canvas.setFillColor(HARAL_GRAY)
    canvas.rect(2*cm, A4[1] - 3*cm, A4[0] - 4*cm, 1*cm, fill=1, stroke=0)
    
    # HARAL text in header
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(3*cm, A4[1] - 2.5*cm, "HARAL")
    canvas.setFont("Helvetica", 8)
    canvas.drawString(5*cm, A4[1] - 2.5*cm, "VERPACKUNGSLÖSUNGEN")
    canvas.drawString(5*cm, A4[1] - 2.8*cm, "NACHHALTIG BEEINDRUCKEN")
    
    # Yellow accent
    canvas.setFillColor(HARAL_YELLOW)
    canvas.rect(2*cm, A4[1] - 3*cm, 1*cm, 1*cm, fill=1, stroke=0)
    
    # Footer
    canvas.setFillColor(HARAL_GRAY)
    canvas.setFont("Helvetica", 8)
    footer_text = "HARAL Verpackungslösungen e.K. | Obere Langgasse 9 | D- 67346 Speyer"
    canvas.drawCentredText(A4[0]/2, 1.5*cm, footer_text)
    footer_contact = "☎ 06232 - 695 95 85 ✉ info@haral.eu 🌐 www.haral.eu"
    canvas.drawCentredText(A4[0]/2, 1.2*cm, footer_contact)
    
    # Page number
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawRightString(A4[0] - 2*cm, 1*cm, str(doc.page))
    
    canvas.restoreState()

def create_process_icons():
    """Create process visualization icons (simplified)"""
    drawing = Drawing(16*cm, 2*cm)
    
    # Process steps
    steps = ["ANALYSE", "SITUATIONSBERICHT", "EVALUIERUNG", "ZERTIFIZIERUNG", "IMPLEMENTIERUNG", "MONITORING"]
    step_width = 16*cm / len(steps)
    
    for i, step in enumerate(steps):
        x = i * step_width + step_width/2
        
        # Hexagon shape (simplified as circle)
        circle = Circle(x, 1.5*cm, 0.4*cm)
        circle.fillColor = HARAL_LIGHT_GRAY
        circle.strokeColor = HARAL_GRAY
        circle.strokeWidth = 2
        drawing.add(circle)
        
        # Step text
        from reportlab.graphics.shapes import String
        text = String(x, 0.5*cm, step, textAnchor='middle')
        text.fontSize = 6
        text.fillColor = HARAL_GRAY
        drawing.add(text)
    
    return drawing

def create_palette_diagram():
    """Create 3D palette visualization (simplified)"""
    drawing = Drawing(8*cm, 6*cm)
    
    # Palette base (isometric view)
    # Front face
    front_points = [1*cm, 1*cm, 6*cm, 1*cm, 6*cm, 4*cm, 1*cm, 4*cm]
    from reportlab.graphics.shapes import Polygon
    front = Polygon(front_points)
    front.fillColor = HARAL_LIGHT_GRAY
    front.strokeColor = HARAL_GRAY
    drawing.add(front)
    
    # Top face (isometric)
    top_points = [1*cm, 4*cm, 6*cm, 4*cm, 7*cm, 5*cm, 2*cm, 5*cm]
    top = Polygon(top_points)
    top.fillColor = colors.white
    top.strokeColor = HARAL_GRAY
    drawing.add(top)
    
    # Right face
    right_points = [6*cm, 1*cm, 7*cm, 2*cm, 7*cm, 5*cm, 6*cm, 4*cm]
    right = Polygon(right_points)
    right.fillColor = HARAL_LIGHT_GRAY
    right.strokeColor = HARAL_GRAY
    drawing.add(right)
    
    # Wrapping lines
    for i in range(3):
        y = 1.5*cm + i * 0.8*cm
        line = Line(0.5*cm, y, 7.5*cm, y + 1*cm)
        line.strokeColor = colors.blue
        line.strokeWidth = 2
        drawing.add(line)
    
    # Dimensions
    from reportlab.graphics.shapes import String
    drawing.add(String(3.5*cm, 0.5*cm, "120 cm", textAnchor='middle', fontSize=8))
    drawing.add(String(7.5*cm, 3*cm, "80 cm", textAnchor='middle', fontSize=8))
    drawing.add(String(0.2*cm, 2.5*cm, "250 cm", textAnchor='middle', fontSize=8))
    
    return drawing

def generate_enhanced_report_pdf(report, customer):
    """Generate enhanced PDF report with professional styling"""
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    safe_customer_name = "".join(c for c in customer.company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"Prüfbericht_{safe_customer_name}_{report.audit_date}_{report.id}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    
    # Create PDF document with custom page template
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=3.5*cm,
        bottomMargin=3*cm
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Enhanced custom styles
    title_style = ParagraphStyle(
        'HARALTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HARAL_GRAY,
        fontName='Helvetica-Bold'
    )
    
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Heading1'],
        fontSize=36,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=HARAL_GRAY,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=HARAL_GRAY,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'HARALHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=HARAL_GRAY,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'HARALSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=HARAL_GRAY,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'HARALNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Parse content
    content_data = {}
    if report.content:
        try:
            content_data = json.loads(report.content)
        except:
            content_data = {}
    
    # Build PDF content
    story = []
    
    # TITLE PAGE
    story.append(Spacer(1, 2*cm))
    
    # Customer company name (large, styled like IGM logo)
    company_parts = customer.company_name.split()
    if len(company_parts) > 1:
        main_name = company_parts[0]
        sub_name = " ".join(company_parts[1:])
        story.append(Paragraph(main_name, company_style))
        story.append(Paragraph(sub_name, subtitle_style))
    else:
        story.append(Paragraph(customer.company_name, company_style))
    
    # Horizontal line
    story.append(Spacer(1, 10))
    line_table = Table([[""], [""]], colWidths=[16*cm], rowHeights=[2, 2])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 2, HARAL_GRAY),
        ('LINEABOVE', (0, 1), (-1, 1), 2, HARAL_GRAY),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 10))
    
    # Business description
    if "Fenster" in customer.company_name or "Fassaden" in customer.company_name:
        story.append(Paragraph("Fenster & Fassaden", subtitle_style))
    
    story.append(Spacer(1, 3*cm))
    
    # Customer details
    story.append(Paragraph(customer.company_name, normal_style))
    if customer.contact_person:
        story.append(Paragraph(customer.contact_person, normal_style))
    
    address_parts = []
    if customer.street:
        address_parts.append(customer.street)
    if customer.postal_code and customer.city:
        address_parts.append(f"{customer.postal_code} {customer.city}")
    
    if address_parts:
        story.append(Paragraph(" · ".join(address_parts), normal_style))
    
    story.append(Spacer(1, 2*cm))
    
    # Report title
    audit_number = f"AUDIT {report.id:05d}"
    story.append(Paragraph(f"PRÜFBERICHT {audit_number}", title_style))
    
    # Author info
    author_info = [f"Verfasser {report.author}"]
    if report.author_phone:
        author_info.append(f"Telefon {report.author_phone}")
    if report.author_email:
        author_info.append(f"E-Mail: {report.author_email}")
    
    story.append(Paragraph(" · ".join(author_info), normal_style))
    story.append(Spacer(1, 3*cm))
    
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
    story.append(Spacer(1, 2*cm))
    
    # Quintessenz (Summary box)
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
    
    # PAGE 2 - Process Icons and Ausgangssituation
    # Add process icons
    story.append(create_process_icons())
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("1. Ausgangssituation:", heading_style))
    
    ausgangssituation_text = f"""
    An Ihrem Produktionstandort in {customer.city or '[Ort]'} wird ein {content_data.get('machine_type', 'Roboter')} des 
    Herstellers {content_data.get('machine_manufacturer', '[Hersteller]')} 
    (Modell: {content_data.get('machine_model', '[Modell]')}) betrieben. 
    Zum Einsatz kommt aktuell eine transparente {content_data.get('foil_thickness', '23')} μm Maschinenstretchfolie von 
    {content_data.get('foil_manufacturer', 'unbekannt')}, diese wird aktuell von der Firma 
    {content_data.get('foil_supplier', '[Lieferant]')} geliefert. 
    Innerhalb des Arbeitsbereichs, ist eine Vordehnung auf bis zu {content_data.get('foil_work_area', '250')} % möglich. 
    Diese Folie wurde auch bewertet und bildet die Basis der IST-Situation. Der aktuelle Folienverbrauch für die 
    gemessene Musterpalette liegt bei 428 g pro Palette.* Aufgrund des eingesetzten Materials und des gemessenen 
    Folienverbrauches je Palette, ergibt sich bei einer Palettenanzahl von ca. 3000 Europaletten pro Jahr und ein 
    Gesamtmaterialbedarf von ca. 1284 kg im Jahr. Das Gewicht des verwendeten Rollenkerns liegt bei 1,045 kg und 
    daraus resultierend entstehen jährliche Kosten in Höhe von 176,- €. Bei einem Produktwechsel können die Kosten 
    um 14% gesenkt und somit auf 152,- € reduziert werden.
    """
    story.append(Paragraph(ausgangssituation_text, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # Palette test description
    palette_text = f"""
    Getestet wurde eine {content_data.get('palette_type', 'Euro')}palette, 
    {content_data.get('palette_length', '120')} x {content_data.get('palette_width', '80')} x 250 cm (l x b x h), 
    mit {', '.join(content_data.get('packaging_types', ['Fassadenfenster']))}. Hierbei wurde der aktuelle 
    Folienverbrauch, die Palettenstabilität sowie die Vordehnung der Stretchfolie überprüft.
    """
    story.append(Paragraph(palette_text, normal_style))
    story.append(Spacer(1, 1*cm))
    
    plug_play_text = """
    Neben der Aufnahme der Ist-Situation, wurde u. a. eine 23 μm Folie getestet. Bei diesem sogenannten 
    Plug- und Play-Test wurde lediglich die Folie ausgetauscht und keinerlei Änderungen an den 
    Einstellungen der vorgenommen. Dies machen wir um verlässliche, standardisierte Werte u. a. 
    bezüglich der Haltekräfte und der Vordehnung zu erhalten.
    """
    story.append(Paragraph(plug_play_text, normal_style))
    
    story.append(PageBreak())
    
    # PAGE 3 - Palettenstabilität with diagram
    story.append(Paragraph("2. Palettenstabilität - Wickelschema und Haltekräfte", heading_style))
    story.append(Paragraph(f"2.1 {content_data.get('machine_manufacturer', 'Motion')} {content_data.get('machine_type', 'Roboter')}", subheading_style))
    
    # Add palette diagram
    story.append(create_palette_diagram())
    story.append(Spacer(1, 1*cm))
    
    # Palette description
    palette_desc = f"""
    {content_data.get('palette_type', 'Euro')}palette mit {', '.join(content_data.get('packaging_types', ['Fassadenfenster']))}, 
    Bruttogewicht: {content_data.get('palette_weight', '1200')} kg
    """
    story.append(Paragraph(palette_desc, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # Enhanced Haltekräfte table
    haltekraft_data = [
        ["Haltekräfte (ASTM)", "Messwert \"SOLL\"", "Messwert \"IST\"", "Abweichung in Prozent"],
        ["Lange Seite oben:", "25 kg", "3 kg", "-88%"],
        ["Lange Seite unten:", "25 kg", "3 kg", "-88%"],
        ["Kurze Seite oben:", "40 kg", "4 kg", "-91%"],
        ["Kurze Seite unten:", "40 kg", "4 kg", "-91%"]
    ]
    
    haltekraft_table = Table(haltekraft_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
    haltekraft_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HARAL_GRAY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, HARAL_GRAY),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    story.append(haltekraft_table)
    story.append(Spacer(1, 1*cm))
    
    # Assessment
    assessment_text = """
    Die Haltekräfte sind mit ungenügend zu bewerten. Eine Bewertung bzgl. der Erfüllung der 
    Anforderungen gem. EU-Richtlinie 2014/47 in Verbindung mit EUMOS 40509 ist nicht ohne 
    Validierungsversuch im Prüflabor abschließend möglich. Aktuell kann aber nicht davon ausgegangen 
    werden, dass diese vollumfänglich erfüllt werden.
    """
    story.append(Paragraph(assessment_text, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # Partnership text with background
    partnership_text = """
    Im Zuge einer partnerschaftlichen Zusammenarbeit, können wir bei der Erfüllung dieser Anforderungen 
    behilflich sein. Hierzu erstellen wir für jedes Packschema entsprechende Zertifikate, welche vom 
    Spediteur mitgeführt werden und bei Kontrollen durch die Polizei oder das Bundesamt für Güterverkehr 
    (BAG) vorgelegt werden.
    """
    story.append(Paragraph(partnership_text, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # Technical details table
    tech_data = [
        ["Folien Dicke:", f"{content_data.get('foil_thickness', '23')} μm", "Vordehnung:", "38 %"],
        ["Folienverbrauch:", "428 g", "Gewicht Rollenkern:", f"{content_data.get('foil_roll_weight', '1045')} g"]
    ]
    
    tech_table = Table(tech_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
    tech_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    story.append(tech_table)
    
    story.append(PageBreak())
    
    # PAGE 4 - Gesamtübersicht with comparison table
    story.append(Paragraph("3. Gesamtübersicht", heading_style))
    story.append(Paragraph(f"3.1 {content_data.get('machine_manufacturer', 'Motion')} {content_data.get('machine_type', 'Roboter')}", subheading_style))
    
    # Enhanced comparison table
    comparison_data = [
        ["", "IST-Situation | 1", "Alternative | 1", "Alternative | 2", "Alternative | 3"],
        ["", "23 μm", "-", "-", "17 μm"],
        ["Vordehnung", "38 %", "-", "-", "38 %"],
        ["Folienverbrauch im Jahr", "1.284 kg", "-", "-", "815 kg"],
        ["Differenz", "", "-", "-", "-37 %"],
        ["Gesamtkosten im Jahr", "3.258 €", "-", "-", "2.809 €"],
        ["Differenz", "", "-", "-", "-14 %"],
        ["CO2-Emissionen im Jahr*", "3.876 kg", "-", "-", "2.461 kg"],
        ["Differenz", "", "-", "-", "-37 %"],
        ["Palettenstabilität", "ungenügend", "-", "-", "ungenügend"]
    ]
    
    comparison_table = Table(comparison_data, colWidths=[3.5*cm, 3*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HARAL_GRAY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), HARAL_LIGHT_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, HARAL_GRAY),
        ('BACKGROUND', (0, 2), (-1, -1), colors.white),
        # Highlight differences
        ('TEXTCOLOR', (4, 4), (4, 4), colors.red),
        ('TEXTCOLOR', (4, 6), (4, 6), colors.red),
        ('TEXTCOLOR', (4, 8), (4, 8), colors.red),
    ]))
    story.append(comparison_table)
    story.append(Spacer(1, 1*cm))
    
    # Footnote
    footnote = "*Die Werte können je nach Folientyp und Hersteller geringfügig abweichen."
    story.append(Paragraph(footnote, normal_style))
    
    # Build PDF with custom page template
    def add_page_decorations(canvas, doc):
        create_header_footer(canvas, doc)
    
    try:
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        return pdf_path
    except Exception as e:
        print(f"Error generating enhanced PDF: {e}")
        return None

