import os
import tempfile
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import black
from typing import Dict, List, Any
try:
    from .lieferschein_counter import get_next_lieferschein_number
except ImportError:
    from lieferschein_counter import get_next_lieferschein_number

# Register fonts if available
try:
    # Try to register Cambria
    pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttf'))
    DEFAULT_FONT = 'Cambria'
except:
    try:
        # Fallback to Arial
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        DEFAULT_FONT = 'Arial'
    except:
        # Final fallback to Helvetica
        DEFAULT_FONT = 'Helvetica'

# Field coordinates for Lieferschein (in points, 1 point = 1/72 inch)
LIEFERSCHEIN_FIELDS = {
    'lieferschein_nr': (85, 515),  # Fortlaufende Nummer DZ2025-XXXX
    'bestellnummer': (320, 515),
    'datum': (475, 515),
    'kunde_name': (100, 650),
    'kunde_adresse': (100, 630),
    'kunde_plz_ort': (100, 610),
    # Position table starts at
    'positions_start': (25, 475),  # Erste Position bei Y=475 (5 Punkte tiefer)
    'positions_row_height': 35,    # 35 Punkte Abstand zwischen Zeilen (mehr Platz für mehrzeilige Beschreibung + Vorgang)
    'positions_min_y': 100,        # Letzte Position bei Y=100, dann neue Seite
    # Column x-coordinates (neue Reihenfolge)
    'auftrag_x': 25,       # Auftrag (kombiniert mit Pos)
    'beschreibung_x': 120,  # Bezeichnung
    'fv_x': 260,           # F/V
    'menge_x': 285,        # Stk
    'werkstoff_x': 315,    # Werkstoff
    'modell_x': 420,       # Modellnummer
    'preis_x': 510,        # EUR/Stk
}

# Field coordinates for Laufkarte
LAUFKARTE_FIELDS = {
    'bestellnummer': (420, 710),
    'datum': (420, 690),
    'auftrag': (100, 650),
    'kunde': (100, 630),
    'positions_start': (80, 550),
    'positions_row_height': 25,
}

# Field coordinates for Rechnung
RECHNUNG_FIELDS = {
    'rechnungsnummer': (420, 710),
    'datum': (420, 690),
    'kunde_name': (100, 650),
    'kunde_adresse': (100, 630),
    'kunde_plz_ort': (100, 610),
    'positions_start': (80, 500),
    'positions_row_height': 20,
    'summe_netto': (440, 200),
    'mwst': (440, 180),
    'summe_brutto': (440, 160),
}

def create_overlay(data: Dict[str, Any], doc_type: str) -> str:
    """Create an overlay PDF with the data"""
    overlay_path = tempfile.mktemp(suffix='.pdf')
    c = canvas.Canvas(overlay_path, pagesize=A4)
    
    # Set font
    c.setFont(DEFAULT_FONT, 10)
    
    if doc_type == 'lieferschein':
        create_lieferschein_overlay(c, data)
    elif doc_type == 'laufkarte':
        create_laufkarte_overlay(c, data)
    elif doc_type == 'rechnung':
        create_rechnung_overlay(c, data)
    
    c.save()
    return overlay_path

def create_lieferschein_overlay(c: canvas.Canvas, data: Dict[str, Any]):
    """Create overlay for Lieferschein"""
    fields = LIEFERSCHEIN_FIELDS
    
    # Generate Lieferschein number if not provided
    lieferschein_nr = data.get('lieferschein_nr', '')
    if not lieferschein_nr:
        # Get next number from counter (DZ2025-0900 onwards)
        lieferschein_nr = get_next_lieferschein_number()
    
    # Header fields
    if 'lieferschein_nr' in fields:
        c.drawString(fields['lieferschein_nr'][0], fields['lieferschein_nr'][1], 
                    str(lieferschein_nr))
    if 'bestellnummer' in fields:
        c.drawString(fields['bestellnummer'][0], fields['bestellnummer'][1], 
                    str(data.get('bestellnummer', '')))
    
    # Date field
    datum_text = str(data.get('datum', datetime.now().strftime('%d.%m.%Y')))
    
    # Ensure we only have the date part, no time
    if ', ' in datum_text:
        # If there's a comma followed by time, remove it
        datum_text = datum_text.split(',')[0].strip()
    
    if 'datum' in fields:
        c.drawString(fields['datum'][0], fields['datum'][1], datum_text)
    
    # Customer info (if available)
    if data.get('kunde'):
        if 'kunde_name' in fields:
            c.drawString(fields['kunde_name'][0], fields['kunde_name'][1], 
                        str(data['kunde'].get('name', '')))
        if 'kunde_adresse' in fields:
            c.drawString(fields['kunde_adresse'][0], fields['kunde_adresse'][1], 
                        str(data['kunde'].get('adresse', '')))
        if 'kunde_plz_ort' in fields:
            c.drawString(fields['kunde_plz_ort'][0], fields['kunde_plz_ort'][1], 
                        f"{data['kunde'].get('plz', '')} {data['kunde'].get('ort', '')}")
    
    # Only draw table if table fields are defined
    if 'positions_start' in fields and 'auftrag_x' in fields:
        # Table headers
        y = fields['positions_start'][1] + 20  # Start slightly higher for headers
        c.setFont(DEFAULT_FONT, 10)
        c.setFillColor(black)
        
        # Draw table headers
        c.drawString(fields['auftrag_x'], y, "Auftrag")
        c.drawString(fields['beschreibung_x'], y, "Bezeichnung")
        c.drawString(fields['fv_x'], y, "F/V")
        c.drawString(fields['menge_x'], y, "Stk")
        c.drawString(fields['werkstoff_x'], y, "Werkstoff")
        c.drawString(fields['modell_x'], y, "Modellnummer")
        c.drawString(fields['preis_x'], y, "EUR/Stk")
        
        # Draw line under headers
        c.line(fields['auftrag_x'] - 5, y - 5, fields['preis_x'] + 45, y - 5)
        
        # Positions
        positions = data.get('positionen', [])
        y = fields['positions_start'][1]
        page_positions = 0
        
        for i, pos in enumerate(positions):
            # Check if we need a new page
            if y < fields['positions_min_y']:
                c.showPage()  # Create new page
                c.setFont(DEFAULT_FONT, 10)
                
                # Repeat header on new page
                if 'lieferschein_nr' in fields:
                    c.drawString(fields['lieferschein_nr'][0], fields['lieferschein_nr'][1], 
                                str(lieferschein_nr))
                if 'bestellnummer' in fields:
                    c.drawString(fields['bestellnummer'][0], fields['bestellnummer'][1], 
                                str(data.get('bestellnummer', '')))
                # Use the cleaned date text from above
                if 'datum' in fields:
                    c.drawString(fields['datum'][0], fields['datum'][1], datum_text)
                
                # Repeat table headers on new page (neue Reihenfolge)
                y_header = fields['positions_start'][1] + 20
                c.drawString(fields['auftrag_x'], y_header, "Auftrag")
                c.drawString(fields['beschreibung_x'], y_header, "Bezeichnung")
                c.drawString(fields['fv_x'], y_header, "F/V")
                c.drawString(fields['menge_x'], y_header, "Stk")
                c.drawString(fields['werkstoff_x'], y_header, "Werkstoff")
                c.drawString(fields['modell_x'], y_header, "Modellnummer")
                c.drawString(fields['preis_x'], y_header, "EUR/Stk")
                c.line(fields['auftrag_x'] - 5, y_header - 5, fields['preis_x'] + 45, y_header - 5)
                
                y = fields['positions_start'][1]  # Reset Y position
                page_positions = 0
            
            # Auftrag kombiniert mit Position (Format: 1)FL-10001)
            c.setFont(DEFAULT_FONT, 10)
            auftrag_text = f"{i + 1}){pos.get('auftrag', '')}"
            c.drawString(fields['auftrag_x'], y, auftrag_text)
            
            # Beschreibung mit automatischem Zeilenumbruch
            beschreibung = str(pos.get('beschreibung', ''))
            
            # Calculate available width for beschreibung (from beschreibung_x to menge_x with some margin)
            max_width = fields['menge_x'] - fields['beschreibung_x'] - 20
            
            # Split text into lines that fit the width
            from reportlab.pdfbase.pdfmetrics import stringWidth
            
            lines = []
            current_line = ""
            words = beschreibung.split()
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                line_width = stringWidth(test_line, DEFAULT_FONT, 10)
                
                if line_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw the first line at the normal position
            if lines:
                c.drawString(fields['beschreibung_x'], y, lines[0])
                
                # Draw additional lines below
                for i, line in enumerate(lines[1:], 1):
                    c.setFont(DEFAULT_FONT, 10)  # Einheitliche Schriftgröße
                    c.drawString(fields['beschreibung_x'], y - (i * 10), line)
            
            # Vorgang unter der Beschreibung
            vorgang = pos.get('vorgang', '')
            if vorgang:
                c.setFont(DEFAULT_FONT, 10)  # Einheitliche Schriftgröße
                # Position vorgang below all description lines
                vorgang_y = y - (len(lines) * 10) if lines else y - 10
                c.drawString(fields['beschreibung_x'], vorgang_y, vorgang)
            
            # F/V
            c.setFont(DEFAULT_FONT, 10)
            fv = pos.get('fv', '')
            if fv:
                c.drawString(fields['fv_x'], y, str(fv))
            
            # Stk (Menge)
            menge = pos.get('menge', '')
            if menge:
                c.drawString(fields['menge_x'], y, str(int(float(menge))))
            
            # Werkstoff
            werkstoff = pos.get('werkstoff', '')
            if werkstoff:
                # Kürze Werkstoff wenn zu lang
                if len(werkstoff) > 15:
                    werkstoff = werkstoff[:14] + '.'
                c.drawString(fields['werkstoff_x'], y, werkstoff)
            
            # Modellnummer
            modell = pos.get('modellnummer', '')
            if modell:
                # Kürze Modellnummer wenn zu lang
                if len(modell) > 12:
                    modell = modell[:11] + '.'
                c.drawString(fields['modell_x'], y, modell)
            
            # EUR/Stk (Preis)
            preis = pos.get('preis', '')
            if preis:
                c.drawString(fields['preis_x'], y, f"{float(preis):.2f}")
            
            # Calculate actual row height based on number of description lines
            actual_row_height = fields['positions_row_height']
            if lines and len(lines) > 1:
                # Add extra space for each additional line
                actual_row_height += (len(lines) - 1) * 10
            
            y -= actual_row_height
            page_positions += 1
    

def create_laufkarte_overlay(c: canvas.Canvas, data: Dict[str, Any]):
    """Create overlay for Laufkarte"""
    fields = LAUFKARTE_FIELDS
    
    # Header fields
    c.drawString(fields['bestellnummer'][0], fields['bestellnummer'][1], 
                str(data.get('bestellnummer', '')))
    c.drawString(fields['datum'][0], fields['datum'][1], 
                str(data.get('datum', datetime.now().strftime('%d.%m.%Y'))))
    
    # Positions with process information
    positions = data.get('positionen', [])
    y = fields['positions_start'][1]
    
    c.setFont(DEFAULT_FONT, 12)  # Larger font for Laufkarte
    
    for pos in positions[:10]:  # Max 10 positions on Laufkarte
        # Create a box for each position
        c.rect(70, y - 20, 450, 40)
        
        # Position info
        text = f"Pos {pos.get('pos_nr', '')}: {pos.get('auftrag', '')} - {pos.get('beschreibung', '')}"
        c.drawString(80, y, text)
        
        # Process info
        y -= 15
        process_text = f"Vorgang: {pos.get('vorgang', '')} | Werkstoff: {pos.get('werkstoff', '')} | F/V: {pos.get('fv', '')}"
        c.setFont(DEFAULT_FONT, 10)
        c.drawString(80, y, process_text)
        c.setFont(DEFAULT_FONT, 12)
        
        y -= fields['positions_row_height'] + 10

def create_rechnung_overlay(c: canvas.Canvas, data: Dict[str, Any]):
    """Create overlay for Rechnung"""
    fields = RECHNUNG_FIELDS
    
    # Header fields
    c.drawString(fields['rechnungsnummer'][0], fields['rechnungsnummer'][1], 
                f"RE-{data.get('bestellnummer', '')}")
    c.drawString(fields['datum'][0], fields['datum'][1], 
                str(data.get('datum', datetime.now().strftime('%d.%m.%Y'))))
    
    # Customer info
    if data.get('kunde'):
        c.drawString(fields['kunde_name'][0], fields['kunde_name'][1], 
                    str(data['kunde'].get('name', '')))
        c.drawString(fields['kunde_adresse'][0], fields['kunde_adresse'][1], 
                    str(data['kunde'].get('adresse', '')))
        c.drawString(fields['kunde_plz_ort'][0], fields['kunde_plz_ort'][1], 
                    f"{data['kunde'].get('plz', '')} {data['kunde'].get('ort', '')}")
    
    # Positions
    positions = data.get('positionen', [])
    y = fields['positions_start'][1]
    total_netto = 0.0
    
    for pos in positions[:15]:
        # Position number
        c.drawString(80, y, str(pos.get('pos_nr', '')))
        
        # Beschreibung
        c.drawString(120, y, str(pos.get('beschreibung', '')))
        
        # Menge
        menge = pos.get('menge', 0)
        if menge:
            c.drawRightString(380, y, f"{float(menge):.2f}")
        
        # Einzelpreis
        preis = pos.get('preis', 0)
        if preis:
            c.drawRightString(440, y, f"{float(preis):.2f} €")
        
        # Gesamtpreis
        if menge and preis:
            gesamt = float(menge) * float(preis)
            total_netto += gesamt
            c.drawRightString(500, y, f"{gesamt:.2f} €")
        
        y -= fields['positions_row_height']
    
    # Totals
    c.setFont(DEFAULT_FONT, 10)
    c.drawRightString(fields['summe_netto'][0], fields['summe_netto'][1], 
                     f"Netto: {total_netto:.2f} €")
    
    mwst = total_netto * 0.19
    c.drawRightString(fields['mwst'][0], fields['mwst'][1], 
                     f"MwSt 19%: {mwst:.2f} €")
    
    c.setFont(DEFAULT_FONT, 12)
    c.drawRightString(fields['summe_brutto'][0], fields['summe_brutto'][1], 
                     f"Gesamt: {(total_netto + mwst):.2f} €")

def merge_with_template(template_path: str, overlay_path: str, output_path: str):
    """Merge overlay with template PDF"""
    # Read template
    template_pdf = PdfReader(template_path)
    overlay_pdf = PdfReader(overlay_path)
    output_pdf = PdfWriter()
    
    # Always use fresh template pages
    num_pages_needed = len(overlay_pdf.pages)
    
    for i in range(num_pages_needed):
        # Always use the first template page as base
        # Open template fresh each time to avoid accumulation
        with open(template_path, 'rb') as f:
            fresh_template = PdfReader(f)
            template_page = fresh_template.pages[0]
            overlay_page = overlay_pdf.pages[i]
            template_page.merge_page(overlay_page)
            output_pdf.add_page(template_page)
    
    # Write output
    with open(output_path, 'wb') as f:
        output_pdf.write(f)
    
    # Clean up
    os.remove(overlay_path)

def generate_lieferschein(data: Dict[str, Any]) -> str:
    """Generate Lieferschein PDF"""
    template_path = os.path.join(os.path.dirname(__file__), 'ls_vorlage.pdf')
    if not os.path.exists(template_path):
        # Try alternative path
        template_path = os.path.join(os.path.dirname(__file__), 'ls2.pdf')
        if not os.path.exists(template_path):
            create_blank_template(template_path, "LIEFERSCHEIN")
    
    output_path = tempfile.mktemp(suffix='_lieferschein.pdf')
    overlay_path = create_overlay(data, 'lieferschein')
    merge_with_template(template_path, overlay_path, output_path)
    
    return output_path

def generate_laufkarte(data: Dict[str, Any]) -> str:
    """Generate Laufkarte PDF using direct generation only"""
    try:
        # First try relative import (for local development)
        from .laufkarte_pdf_generator import generate_laufkarte_direct
    except ImportError:
        # Then try absolute import (for Render deployment)
        from laufkarte_pdf_generator import generate_laufkarte_direct
    
    print("Using direct PDF generation for Laufkarte")
    return generate_laufkarte_direct(data)

def generate_rechnung(data: Dict[str, Any]) -> str:
    """Generate Rechnung PDF"""
    template_path = os.path.join(os.path.dirname(__file__), 'rechnung_template.pdf')
    output_path = tempfile.mktemp(suffix='_rechnung.pdf')
    
    # Create template if it doesn't exist
    if not os.path.exists(template_path):
        create_blank_template(template_path, "RECHNUNG")
    
    overlay_path = create_overlay(data, 'rechnung')
    merge_with_template(template_path, overlay_path, output_path)
    
    return output_path

def create_blank_template(path: str, title: str):
    """Create a blank template PDF if none exists"""
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    
    # Draw header
    c.setFont(DEFAULT_FONT, 24)
    c.drawCentredString(width/2, height - 50, f"DZMetall {title}")
    
    # Draw logo placeholder
    c.setFont(DEFAULT_FONT, 10)
    c.rect(50, height - 100, 100, 50)
    c.drawString(75, height - 80, "LOGO")
    
    # Draw company info
    c.drawRightString(width - 50, height - 50, "DZMetall GmbH")
    c.drawRightString(width - 50, height - 65, "Industriestraße 123")
    c.drawRightString(width - 50, height - 80, "12345 Metallstadt")
    
    # Draw fields labels
    c.setFont(DEFAULT_FONT, 10)
    c.drawString(350, 710, "Bestellnummer:")
    c.drawString(350, 690, "Datum:")
    
    # Draw table header for positions
    if title == "LIEFERSCHEIN":
        y = 520
        c.drawString(80, y, "Pos")
        c.drawString(120, y, "Auftrag")
        c.drawString(200, y, "Beschreibung")
        c.drawString(380, y, "Menge")
        c.drawString(440, y, "Preis")
        c.drawString(500, y, "Gesamt")
        c.line(70, y - 5, width - 70, y - 5)
    
    # Footer
    c.setFont(DEFAULT_FONT, 8)
    c.drawCentredString(width/2, 30, "DZMetall GmbH | Geschäftsführer: Max Mustermann | HRB 12345")
    
    c.save()