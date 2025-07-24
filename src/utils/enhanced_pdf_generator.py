from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
import tempfile

class HARALReportTemplate:
    """Template für HARAL Prüfberichte basierend auf dem ursprünglichen Design"""
    
    def __init__(self, report):
        self.report = report
        self.customer = report.customer
        self.user = report.user
        
        # Seitenformat und Ränder
        self.pagesize = A4
        self.width, self.height = A4
        self.margin_left = 25*mm
        self.margin_right = 25*mm
        self.margin_top = 20*mm
        self.margin_bottom = 20*mm
        
        # HARAL Farben
        self.haral_yellow = colors.Color(1, 0.843, 0)  # #FFD700
        self.haral_gray = colors.Color(0.5, 0.5, 0.5)  # #808080
        self.dark_gray = colors.Color(0.25, 0.25, 0.25)  # #404040
        
        # Styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Benutzerdefinierte Styles einrichten"""
        
        # Hauptüberschrift
        self.styles.add(ParagraphStyle(
            name='HARALTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.dark_gray,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Kundenname
        self.styles.add(ParagraphStyle(
            name='CustomerName',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.dark_gray,
            spaceAfter=3,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Kontaktdaten
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.dark_gray,
            spaceAfter=2,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        # Berichtstitel
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.dark_gray,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Verfasser-Info
        self.styles.add(ParagraphStyle(
            name='AuthorInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.dark_gray,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Inhaltsverzeichnis
        self.styles.add(ParagraphStyle(
            name='TOCHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.dark_gray,
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # TOC Einträge
        self.styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.dark_gray,
            spaceAfter=3,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        # Quintessenz Box
        self.styles.add(ParagraphStyle(
            name='QuintessenzTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.dark_gray,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Quintessenz Text
        self.styles.add(ParagraphStyle(
            name='QuintessenzText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.dark_gray,
            spaceAfter=0,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Kapitelüberschriften
        self.styles.add(ParagraphStyle(
            name='ChapterHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.dark_gray,
            spaceAfter=12,
            spaceBefore=18,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Unterüberschriften
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.dark_gray,
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Normaler Text
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.dark_gray,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Tabellen-Header
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Tabellen-Zellen
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.dark_gray,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

class HARALPageTemplate:
    """Seitenvorlage mit Header und Footer"""
    
    def __init__(self, template):
        self.template = template
    
    def draw_header_footer(self, canvas, doc):
        """Header und Footer zeichnen"""
        canvas.saveState()
        
        # Header
        self.draw_header(canvas)
        
        # Footer
        self.draw_footer(canvas, doc)
        
        canvas.restoreState()
    
    def draw_header(self, canvas):
        """Header mit Logos zeichnen"""
        # HARAL Logo (links)
        haral_logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'HARAL-LOGO.png')
        if os.path.exists(haral_logo_path):
            try:
                canvas.drawImage(
                    haral_logo_path,
                    self.template.margin_left,
                    self.template.height - self.template.margin_top - 20*mm,
                    width=60*mm,
                    height=15*mm,
                    preserveAspectRatio=True
                )
            except:
                # Fallback wenn Logo nicht geladen werden kann
                canvas.setFont("Helvetica-Bold", 14)
                canvas.setFillColor(self.template.haral_yellow)
                canvas.drawString(
                    self.template.margin_left,
                    self.template.height - self.template.margin_top - 15*mm,
                    "HARAL"
                )
        
        # Kundenlogo (rechts)
        if self.template.customer and hasattr(self.template.customer, 'logo_path') and self.template.customer.logo_path:
            customer_logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', self.template.customer.logo_path)
            if os.path.exists(customer_logo_path):
                try:
                    canvas.drawImage(
                        customer_logo_path,
                        self.template.width - self.template.margin_right - 40*mm,
                        self.template.height - self.template.margin_top - 20*mm,
                        width=40*mm,
                        height=15*mm,
                        preserveAspectRatio=True
                    )
                except:
                    pass  # Ignoriere Fehler beim Laden des Kundenlogos
    
    def draw_footer(self, canvas, doc):
        """Footer mit Seitenzahl zeichnen"""
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(self.template.haral_gray)
        
        # Seitenzahl
        page_num = canvas.getPageNumber()
        canvas.drawRightString(
            self.template.width - self.template.margin_right,
            self.template.margin_bottom - 10*mm,
            f"{page_num}"
        )
        
        # Datum
        canvas.drawString(
            self.template.margin_left,
            self.template.margin_bottom - 10*mm,
            datetime.now().strftime("%d.%m.%Y")
        )

def generate_enhanced_report_pdf(report):
    """Generiert ein PDF basierend auf dem ursprünglichen HARAL Design"""
    
    # Temporäre PDF-Datei erstellen
    temp_dir = tempfile.gettempdir()
    pdf_filename = f"haral_report_{report.audit_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    # Template initialisieren
    template = HARALReportTemplate(report)
    page_template = HARALPageTemplate(template)
    
    # PDF-Dokument erstellen
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=template.pagesize,
        leftMargin=template.margin_left,
        rightMargin=template.margin_right,
        topMargin=template.margin_top + 25*mm,  # Platz für Header
        bottomMargin=template.margin_bottom + 15*mm  # Platz für Footer
    )
    
    # Story (Inhalt) aufbauen
    story = []
    
    # Titelseite
    story.extend(build_title_page(template))
    
    # Inhaltsverzeichnis
    story.append(PageBreak())
    story.extend(build_table_of_contents(template))
    
    # Hauptinhalt
    story.append(PageBreak())
    story.extend(build_main_content(template))
    
    # PDF generieren
    doc.build(
        story,
        onFirstPage=page_template.draw_header_footer,
        onLaterPages=page_template.draw_header_footer
    )
    
    return pdf_path

def build_title_page(template):
    """Titelseite erstellen"""
    story = []
    
    # Kundeninformationen
    if template.customer:
        story.append(Paragraph(template.customer.company_name, template.styles['CustomerName']))
        if template.customer.contact_person:
            story.append(Paragraph(template.customer.contact_person, template.styles['ContactInfo']))
        if template.customer.address:
            story.append(Paragraph(template.customer.address, template.styles['ContactInfo']))
    
    story.append(Spacer(1, 20*mm))
    
    # Berichtstitel
    title = f"{template.report.title} {template.report.audit_number}"
    story.append(Paragraph(title, template.styles['ReportTitle']))
    
    story.append(Spacer(1, 10*mm))
    
    # Verfasser-Informationen
    author_info = f"Verfasser {template.report.author}"
    if template.report.phone or template.report.email:
        contact_parts = []
        if template.report.phone:
            contact_parts.append(f"Telefon {template.report.phone}")
        if template.report.email:
            contact_parts.append(f"E-Mail: {template.report.email}")
        author_info += "<br/>" + " · ".join(contact_parts)
    
    story.append(Paragraph(author_info, template.styles['AuthorInfo']))
    
    story.append(Spacer(1, 30*mm))
    
    # Quintessenz-Box
    if template.report.material_savings or template.report.cost_reduction:
        story.extend(build_quintessenz_box(template))
    
    return story

def build_quintessenz_box(template):
    """Quintessenz-Box erstellen"""
    story = []
    
    story.append(Paragraph("Quintessenz:", template.styles['QuintessenzTitle']))
    
    quintessenz_text = f"""Durch eine ganzheitliche Optimierung der eingesetzten Stretchfolie in Verbindung mit der 
    Maschinentechnik, können Materialeinsparungen von bis zu {template.report.material_savings}% und damit eine Kostenreduzierung von 
    circa {template.report.cost_reduction}% realisiert werden. Zugleich können die CO2-Emmissionen um {template.report.co2_reduction}% gesenkt werden. Die 
    Palettenstabilität und damit die Ladungssicherung der Packstücke kann dabei im Mittelwert um {template.report.stability_increase} kg 
    gesteigert werden."""
    
    story.append(Paragraph(quintessenz_text, template.styles['QuintessenzText']))
    
    return story

def build_table_of_contents(template):
    """Inhaltsverzeichnis erstellen"""
    story = []
    
    story.append(Paragraph("Inhaltsverzeichnis", template.styles['TOCHeading']))
    story.append(Spacer(1, 6*mm))
    
    toc_entries = [
        "1. Ausgangssituation",
        "2. Palettenstabilität - Wickelschema und Haltekräfte",
        "3. Gesamtübersicht",
        "4. Einsparpotentiale",
        "5. Fazit und nächste Schritte"
    ]
    
    if template.report.get_images():
        toc_entries.append("6. Bilddokumentation")
    
    for entry in toc_entries:
        story.append(Paragraph(entry, template.styles['TOCEntry']))
    
    return story

def build_main_content(template):
    """Hauptinhalt erstellen"""
    story = []
    
    # 1. Ausgangssituation
    story.extend(build_ausgangssituation(template))
    
    # 2. Palettenstabilität
    story.append(PageBreak())
    story.extend(build_palettenstabilitaet(template))
    
    # 3. Gesamtübersicht
    story.append(PageBreak())
    story.extend(build_gesamtuebersicht(template))
    
    # 4. Einsparpotentiale
    story.append(PageBreak())
    story.extend(build_einsparpotentiale(template))
    
    # 5. Fazit
    story.append(PageBreak())
    story.extend(build_fazit(template))
    
    # 6. Bilddokumentation
    if template.report.get_images():
        story.append(PageBreak())
        story.extend(build_bilddokumentation(template))
    
    return story

def build_ausgangssituation(template):
    """Ausgangssituation-Kapitel erstellen"""
    story = []
    
    story.append(Paragraph("1. Ausgangssituation:", template.styles['ChapterHeading']))
    
    # Haupttext
    text_parts = []
    
    if template.report.production_site:
        text_parts.append(f"An Ihrem Produktionstandort in {template.report.production_site}")
    
    if template.report.robot_manufacturer and template.report.robot_model:
        text_parts.append(f"wird ein Roboter des Herstellers {template.report.robot_manufacturer} (Modell: {template.report.robot_model}) betrieben.")
    
    if template.report.film_type and template.report.film_thickness:
        text_parts.append(f"Zum Einsatz kommt aktuell eine {template.report.film_type.lower()} {template.report.film_thickness} μm Maschinenstretchfolie")
        
        if template.report.film_supplier:
            text_parts.append(f"von {template.report.film_supplier}")
    
    if template.report.max_prestretch:
        text_parts.append(f"Innerhalb des Arbeitsbereichs, ist eine Vordehnung auf bis zu {template.report.max_prestretch}% möglich.")
    
    if template.report.film_consumption_per_pallet:
        text_parts.append(f"Der aktuelle Folienverbrauch für die gemessene Musterpalette liegt bei {template.report.film_consumption_per_pallet} g pro Palette.*")
    
    if template.report.pallets_per_year and template.report.total_material_consumption:
        text_parts.append(f"Bei einer Palettenanzahl von ca. {template.report.pallets_per_year} Europaletten pro Jahr ergibt sich ein Gesamtmaterialbedarf von ca. {template.report.total_material_consumption:.0f} kg im Jahr.")
    
    if template.report.annual_costs:
        text_parts.append(f"Bei einem Produktwechsel können die Kosten um {template.report.cost_reduction}% gesenkt und somit auf {template.report.annual_costs * (1 - template.report.cost_reduction/100):.0f} € reduziert werden.")
    
    main_text = " ".join(text_parts)
    story.append(Paragraph(main_text, template.styles['BodyText']))
    
    story.append(Spacer(1, 6*mm))
    
    # Testpalette-Informationen
    if template.report.pallet_dimensions and template.report.pallet_content:
        test_text = f"Getestet wurde eine {template.report.pallet_type or 'Europalette'}, {template.report.pallet_dimensions}, mit {template.report.pallet_content}."
        
        if template.report.gross_weight:
            test_text += f" Das Bruttogewicht beträgt {template.report.gross_weight} kg."
        
        story.append(Paragraph(test_text, template.styles['BodyText']))
    
    # Fußnote
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("*Kann bei anderen Paletten aufgrund unterschiedlicher Packstücke und Packhöhen abweichen.", template.styles['BodyText']))
    
    return story

def build_palettenstabilitaet(template):
    """Palettenstabilität-Kapitel erstellen"""
    story = []
    
    story.append(Paragraph("2. Palettenstabilität - Wickelschema und Haltekräfte", template.styles['ChapterHeading']))
    
    # Wickelschema-Diagramm (vereinfacht als Text)
    if template.report.robot_manufacturer:
        story.append(Paragraph(f"2.1 {template.report.robot_manufacturer} Roboter", template.styles['SubHeading']))
    
    # Wickelschema-Tabelle
    if any([template.report.windings_top, template.report.windings_middle, template.report.windings_bottom]):
        wickel_data = [
            ['Position', 'Wicklungen', 'Vordehnung'],
            [f'Oben', f'{template.report.windings_top or 0}', f'{template.report.prestretch_actual or 0}%'],
            [f'Mitte', f'{template.report.windings_middle or 0}', f'{template.report.prestretch_actual or 0}%'],
            [f'Unten', f'{template.report.windings_bottom or 0}', f'{template.report.prestretch_actual or 0}%']
        ]
        
        wickel_table = Table(wickel_data, colWidths=[40*mm, 30*mm, 30*mm])
        wickel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), template.haral_gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(wickel_table)
        story.append(Spacer(1, 10*mm))
    
    # Haltekräfte-Tabelle
    if any([template.report.holding_force_long_top_target, template.report.holding_force_short_top_target]):
        story.append(Paragraph("Haltekräfte (ASTM)", template.styles['SubHeading']))
        
        haltekraft_data = [
            ['Haltekräfte (ASTM)', 'Messwert "SOLL"', 'Messwert "IST"', 'Abweichung in Prozent']
        ]
        
        deviations = template.report.calculate_holding_force_deviations()
        
        positions = [
            ('Lange Seite oben:', template.report.holding_force_long_top_target, template.report.holding_force_long_top_actual, deviations.get('long_top')),
            ('Lange Seite unten:', template.report.holding_force_long_bottom_target, template.report.holding_force_long_bottom_actual, deviations.get('long_bottom')),
            ('Kurze Seite oben:', template.report.holding_force_short_top_target, template.report.holding_force_short_top_actual, deviations.get('short_top')),
            ('Kurze Seite unten:', template.report.holding_force_short_bottom_target, template.report.holding_force_short_bottom_actual, deviations.get('short_bottom'))
        ]
        
        for pos_name, target, actual, deviation in positions:
            if target is not None:
                target_str = f"{target} kg" if target else "-"
                actual_str = f"{actual} kg" if actual else "-"
                deviation_str = f"{deviation}%" if deviation is not None else "-"
                haltekraft_data.append([pos_name, target_str, actual_str, deviation_str])
        
        haltekraft_table = Table(haltekraft_data, colWidths=[50*mm, 30*mm, 30*mm, 40*mm])
        haltekraft_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), template.haral_gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(haltekraft_table)
        story.append(Spacer(1, 10*mm))
    
    # Bewertung
    if template.report.holding_force_rating:
        bewertung_text = f"Die Haltekräfte sind mit {template.report.holding_force_rating.lower()} zu bewerten."
        
        if not template.report.eu_directive_compliant:
            bewertung_text += " Eine Bewertung bzgl. der Erfüllung der Anforderungen gem. EU-Richtlinie 2014/47 in Verbindung mit EUMOS 40509 ist nicht ohne Validierungsversuch im Prüflabor abschließend möglich."
        
        story.append(Paragraph(bewertung_text, template.styles['BodyText']))
    
    # Zusätzliche Informationen
    if template.report.film_thickness and template.report.prestretch_actual:
        info_text = f"Folien Dicke: {template.report.film_thickness} μm Vordehnung: {template.report.prestretch_actual}%"
        if template.report.film_consumption_per_pallet:
            info_text += f"<br/>Folienverbrauch: {template.report.film_consumption_per_pallet} g"
        if template.report.roll_core_weight:
            info_text += f" Gewicht Rollenkern: {template.report.roll_core_weight * 1000:.0f} g"
        
        story.append(Spacer(1, 6*mm))
        story.append(Paragraph(info_text, template.styles['BodyText']))
    
    return story

def build_gesamtuebersicht(template):
    """Gesamtübersicht-Kapitel erstellen"""
    story = []
    
    story.append(Paragraph("3. Gesamtübersicht", template.styles['ChapterHeading']))
    
    if template.report.robot_manufacturer:
        story.append(Paragraph(f"3.1 {template.report.robot_manufacturer} Roboter", template.styles['SubHeading']))
    
    # Vergleichstabelle
    alternatives = template.report.get_alternatives()
    if alternatives:
        # Tabellen-Header
        table_data = [
            ['', 'IST-Situation', 'Alternative 1', 'Alternative 2', 'Alternative 3']
        ]
        
        # Foliendicke
        row = ['Foliendicke', f"{template.report.film_thickness} μm" if template.report.film_thickness else "-"]
        for alt in alternatives[:3]:
            if alt.get('film_thickness'):
                row.append(f"{alt['film_thickness']} μm")
            else:
                row.append("-")
        while len(row) < 5:
            row.append("-")
        table_data.append(row)
        
        # Vordehnung
        row = ['Vordehnung', f"{template.report.prestretch_actual}%" if template.report.prestretch_actual else "-"]
        for alt in alternatives[:3]:
            if alt.get('prestretch'):
                row.append(f"{alt['prestretch']}%")
            else:
                row.append("-")
        while len(row) < 5:
            row.append("-")
        table_data.append(row)
        
        # Folienverbrauch im Jahr
        row = ['Folienverbrauch im Jahr', f"{template.report.total_material_consumption:.0f} kg" if template.report.total_material_consumption else "-"]
        for i, alt in enumerate(alternatives[:3]):
            if alt.get('film_thickness') and template.report.film_thickness:
                # Vereinfachte Berechnung
                reduction = (float(template.report.film_thickness) - float(alt['film_thickness'])) / float(template.report.film_thickness)
                new_consumption = template.report.total_material_consumption * (1 - reduction)
                row.append(f"{new_consumption:.0f} kg")
            else:
                row.append("-")
        while len(row) < 5:
            row.append("-")
        table_data.append(row)
        
        # Differenz
        row = ['Differenz', "-"]
        for i, alt in enumerate(alternatives[:3]):
            if alt.get('film_thickness') and template.report.film_thickness:
                reduction = (float(template.report.film_thickness) - float(alt['film_thickness'])) / float(template.report.film_thickness) * 100
                row.append(f"-{reduction:.0f}%")
            else:
                row.append("-")
        while len(row) < 5:
            row.append("-")
        table_data.append(row)
        
        # Gesamtkosten im Jahr
        row = ['Gesamtkosten im Jahr', f"{template.report.annual_costs:.0f} €" if template.report.annual_costs else "-"]
        for i, alt in enumerate(alternatives[:3]):
            if alt.get('film_thickness') and template.report.film_thickness and template.report.annual_costs:
                reduction = (float(template.report.film_thickness) - float(alt['film_thickness'])) / float(template.report.film_thickness)
                new_costs = template.report.annual_costs * (1 - reduction * 0.4)  # Vereinfacht
                row.append(f"{new_costs:.0f} €")
            else:
                row.append("-")
        while len(row) < 5:
            row.append("-")
        table_data.append(row)
        
        # CO2-Emissionen
        row = ['CO2-Emissionen im Jahr*', f"{template.report.co2_emissions:.0f} kg" if template.report.co2_emissions else "-"]
        for i, alt in enumerate(alternatives[:3]):
            if alt.get('film_thickness') and template.report.film_thickness and template.report.co2_emissions:
                reduction = (float(template.report.film_thickness) - float(alt['film_thickness'])) / float(template.report.film_thickness)
                new_emissions = template.report.co2_emissions * (1 - reduction)
                row.append(f"{new_emissions:.0f} kg")
            else:
                row.append("-")
        while len(row) < 5:
            row.append("-")
        table_data.append(row)
        
        # Palettenstabilität
        row = ['Palettenstabilität', template.report.holding_force_rating or "ungenügend"]
        for alt in alternatives[:3]:
            row.append(alt.get('pallet_stability', '-'))
        while len(row) < 5:
            row.append("-")
        table_data.append(row)
        
        # Tabelle erstellen
        overview_table = Table(table_data, colWidths=[40*mm, 30*mm, 30*mm, 30*mm, 30*mm])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), template.haral_gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 6*mm))
        story.append(Paragraph("*Die Werte können je nach Folientyp und Hersteller geringfügig abweichen.", template.styles['BodyText']))
    
    return story

def build_einsparpotentiale(template):
    """Einsparpotentiale-Kapitel erstellen"""
    story = []
    
    story.append(Paragraph("4. Einsparpotentiale", template.styles['ChapterHeading']))
    
    if template.report.recommended_alternative:
        empfehlung_text = f"Um die Einsparpotenziale vollumfänglich auszuschöpfen, empfehlen wir die Umsetzung der {template.report.recommended_alternative}."
        
        if template.report.material_savings:
            empfehlung_text += f" Hierbei würde sich eine Materialreduzierung von {template.report.material_savings}% ergeben."
        
        story.append(Paragraph(empfehlung_text, template.styles['BodyText']))
    
    # Einsparungen visualisieren
    if any([template.report.material_savings, template.report.cost_reduction, template.report.co2_reduction]):
        story.append(Spacer(1, 10*mm))
        
        savings_data = []
        if template.report.material_savings:
            savings_data.append(['FOLIE', f'-{template.report.material_savings}%'])
        if template.report.cost_reduction:
            savings_data.append(['KOSTEN', f'-{template.report.cost_reduction}%'])
        if template.report.co2_reduction:
            savings_data.append(['CO2', f'-{template.report.co2_reduction}%'])
        
        if savings_data:
            savings_table = Table(savings_data, colWidths=[30*mm, 30*mm])
            savings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), template.haral_yellow),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('GRID', (0, 0), (-1, -1), 2, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(savings_table)
    
    story.append(Spacer(1, 10*mm))
    
    zusatz_text = """Wobei sich eine Materialreduzierung, ohne Qualitätsabstriche, in der Praxis nur mittels Detailarbeit erzielen lässt.
    Die Haltekräfte zur aktuellen IST-Situation, mit mindestens vergleichbaren Werten, bleiben erhalten oder können 
    sogar gesteigert werden. Dieses erfolgt auf der Grundlage der Optimierung der Wickelschemen."""
    
    story.append(Paragraph(zusatz_text, template.styles['BodyText']))
    
    return story

def build_fazit(template):
    """Fazit-Kapitel erstellen"""
    story = []
    
    story.append(Paragraph("5. Fazit und nächste Schritte", template.styles['ChapterHeading']))
    
    if template.report.conclusion_text:
        story.append(Paragraph(template.report.conclusion_text, template.styles['BodyText']))
        story.append(Spacer(1, 6*mm))
    
    if template.report.recommendations_text:
        story.append(Paragraph("Empfehlungen:", template.styles['SubHeading']))
        story.append(Paragraph(template.report.recommendations_text, template.styles['BodyText']))
        story.append(Spacer(1, 6*mm))
    
    if template.report.next_steps_text:
        story.append(Paragraph("Nächste Schritte:", template.styles['SubHeading']))
        story.append(Paragraph(template.report.next_steps_text, template.styles['BodyText']))
    
    return story

def build_bilddokumentation(template):
    """Bilddokumentation-Kapitel erstellen"""
    story = []
    
    story.append(Paragraph("6. Bilddokumentation", template.styles['ChapterHeading']))
    
    images = template.report.get_images()
    for i, image_info in enumerate(images):
        if image_info.get('filename'):
            image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', image_info['filename'])
            
            if os.path.exists(image_path):
                try:
                    # Bild hinzufügen
                    story.append(Image(image_path, width=120*mm, height=80*mm))
                    
                    # Beschreibung
                    if image_info.get('description'):
                        story.append(Paragraph(f"Bild {i+1}: {image_info['description']}", template.styles['BodyText']))
                    
                    story.append(Spacer(1, 10*mm))
                    
                except Exception as e:
                    # Fallback wenn Bild nicht geladen werden kann
                    story.append(Paragraph(f"Bild {i+1}: {image_info.get('description', 'Bild konnte nicht geladen werden')}", template.styles['BodyText']))
    
    return story

