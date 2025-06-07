import os
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import black, HexColor
from typing import Dict, Any, List

# Use Helvetica which is built-in
DEFAULT_FONT = 'Helvetica'
BOLD_FONT = 'Helvetica-Bold'

def generate_laufkarte_direct(data: Dict[str, Any]) -> str:
    """Generate Laufkarte PDF with specified layout"""
    print("=== LAUFKARTE_PDF_GENERATOR v3.0 FINAL ===")
    print("This is the NEW generator with correct header styling")
    
    # Create temporary file
    output_path = tempfile.mktemp(suffix='_laufkarte.pdf')
    
    # Create canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Header: DZMetall links, LAUFKARTE zentriert groß, Datum rechts
    # DZMetall logo/text
    c.setFont(BOLD_FONT, 14)
    c.drawString(50, height - 50, "DZMetall")
    
    # LAUFKARTE centered and large
    c.setFont(BOLD_FONT, 24)
    laufkarte_text = "LAUFKARTE"
    text_width = c.stringWidth(laufkarte_text, BOLD_FONT, 24)
    c.drawString((width - text_width) / 2, height - 55, laufkarte_text)
    
    # Date on the right
    c.setFont(DEFAULT_FONT, 12)
    datum = data.get('datum', datetime.now().strftime('%d.%m.%Y'))
    c.drawRightString(width - 50, height - 50, datum)
    
    # Order number below header
    bestellnummer = data.get('bestellnummer', '')
    c.setFont(DEFAULT_FONT, 14)
    c.drawString(50, height - 90, f"Bestellnummer: {bestellnummer}")
    
    # Table headers starting position
    y_start = height - 130
    x_margins = 50
    
    # Column definitions with positions
    columns = [
        {'name': 'Pos/Auftrag', 'x': x_margins, 'width': 80},
        {'name': 'Bezeichnung', 'x': x_margins + 80, 'width': 180},
        {'name': 'F/V', 'x': x_margins + 260, 'width': 30},
        {'name': 'Stk', 'x': x_margins + 290, 'width': 30},
        {'name': 'Werkstoff', 'x': x_margins + 320, 'width': 90},
        {'name': 'Modellnummer', 'x': x_margins + 410, 'width': 80}
    ]
    
    # Draw table headers
    c.setFont(BOLD_FONT, 10)
    
    # Header background
    c.setFillColor(HexColor('#f0f0f0'))
    c.setStrokeColor(black)
    header_height = 25
    # Calculate total width based on last column
    total_width = columns[-1]['x'] + columns[-1]['width'] - x_margins + 10
    c.rect(x_margins - 5, y_start - 5, total_width, header_height, fill=1, stroke=1)
    
    # Header text (positioned in the middle of the header box)
    c.setFillColor(black)
    text_y = y_start + (header_height / 2) - 4  # Center text vertically
    for col in columns:
        c.drawString(col['x'], text_y, col['name'])
    
    # Table content (start below the header box)
    y = y_start - 35  # Adjusted to start below header
    c.setFont(DEFAULT_FONT, 10)
    
    positions = data.get('positionen', [])
    
    for pos in positions:
        # Check if we need a new page
        if y < 100:
            c.showPage()
            # Redraw headers on new page
            y = height - 100
            c.setFont(BOLD_FONT, 10)
            
            # Header background
            c.setFillColor(HexColor('#f0f0f0'))
            c.setStrokeColor(black)
            c.rect(x_margins - 5, y - 5, total_width, header_height, fill=1, stroke=1)
            
            # Header text (positioned in the middle of the header box)
            c.setFillColor(black)
            text_y = y + (header_height / 2) - 4  # Center text vertically
            for col in columns:
                c.drawString(col['x'], text_y, col['name'])
            
            c.setFont(DEFAULT_FONT, 10)
            y = y - 35  # Start content below header
        
        # Pos/Auftrag column (Pos number and Auftrag on same column)
        pos_nr = str(pos.get('pos_nr', ''))
        auftrag = str(pos.get('auftrag', ''))
        c.drawString(columns[0]['x'], y, f"{pos_nr}) {auftrag}")
        
        # Bezeichnung (with Vorgang below)
        beschreibung = pos.get('beschreibung', '')
        vorgang = pos.get('vorgang', '')
        
        # Draw Bezeichnung
        c.drawString(columns[1]['x'], y, beschreibung[:50] + ('...' if len(beschreibung) > 50 else ''))
        
        # Draw Vorgang below Bezeichnung in smaller font
        if vorgang:
            c.setFont(DEFAULT_FONT, 8)
            c.drawString(columns[1]['x'], y - 12, f"({vorgang})")
            c.setFont(DEFAULT_FONT, 10)
        
        # F/V
        fv = str(pos.get('fv', ''))
        c.drawString(columns[2]['x'], y, fv)
        
        # Stk (Menge)
        menge = pos.get('menge', '')
        if menge:
            c.drawString(columns[3]['x'], y, str(int(float(menge))))
        
        # Werkstoff
        werkstoff = str(pos.get('werkstoff', ''))
        c.drawString(columns[4]['x'], y, werkstoff[:20] + ('...' if len(werkstoff) > 20 else ''))
        
        # Modellnummer
        modell = str(pos.get('modellnummer', ''))
        c.drawString(columns[5]['x'], y, modell[:15] + ('...' if len(modell) > 15 else ''))
        
        # Draw horizontal line between rows
        c.setStrokeColor(HexColor('#e0e0e0'))
        c.line(x_margins - 5, y - 5, x_margins - 5 + total_width, y - 5)
        c.setStrokeColor(black)
        
        # Move to next row (extra space if Vorgang exists)
        y -= 30 if vorgang else 25
    
    # Save the PDF
    c.save()
    
    return output_path