import os
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import black, lightgrey
from reportlab.platypus import Table, TableStyle
from typing import Dict, Any, List

# Use Helvetica which is built-in
DEFAULT_FONT = 'Helvetica'
BOLD_FONT = 'Helvetica-Bold'

def wrap_text(text: str, canvas_obj: canvas.Canvas, max_width: float, font: str, font_size: int) -> List[str]:
    """Wrap text to fit within max_width"""
    if not text:
        return []
    
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if canvas_obj.stringWidth(test_line, font, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def generate_laufkarte_direct(data: Dict[str, Any]) -> str:
    """Generate Laufkarte PDF directly using ReportLab"""
    
    # Create temporary file
    output_path = tempfile.mktemp(suffix='_laufkarte.pdf')
    
    # Create canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Get date
    datum = data.get('datum', datetime.now().strftime('%d.%m.%Y'))
    
    # Header - matching HTML exactly
    c.setFont(BOLD_FONT, 14)
    c.setFillColor(black)
    c.drawString(20*mm, height - 20*mm, "DZ Metall")
    
    c.setFont(DEFAULT_FONT, 14)
    c.drawRightString(width - 20*mm, height - 20*mm, datum)
    
    # Title - centered and underlined (moved up from 60mm to 40mm)
    c.setFont(DEFAULT_FONT, 24)
    title = "Laufkarte"
    title_width = c.stringWidth(title, DEFAULT_FONT, 24)
    title_x = (width - title_width) / 2
    c.drawString(title_x, height - 40*mm, title)
    
    # Underline the title
    c.setLineWidth(1)
    c.line(title_x, height - 42*mm, title_x + title_width, height - 42*mm)
    
    # Table setup (moved up from 90mm to 60mm)
    table_top = height - 60*mm
    table_left = 20*mm
    table_right = width - 20*mm
    table_width = table_right - table_left
    
    # Column widths (matching HTML percentages)
    col_widths = {
        'auftrag': table_width * 0.15,      # 15%
        'bezeichnung': table_width * 0.35,   # 35%
        'fv': table_width * 0.05,            # 5%
        'stk': table_width * 0.10,           # 10%
        'werkstoff': table_width * 0.15,     # 15%
        'modell': table_width * 0.20         # 20%
    }
    
    # Column positions
    col_x = {
        'auftrag': table_left,
        'bezeichnung': table_left + col_widths['auftrag'],
        'fv': table_left + col_widths['auftrag'] + col_widths['bezeichnung'],
        'stk': table_left + col_widths['auftrag'] + col_widths['bezeichnung'] + col_widths['fv'],
        'werkstoff': table_left + col_widths['auftrag'] + col_widths['bezeichnung'] + col_widths['fv'] + col_widths['stk'],
        'modell': table_left + col_widths['auftrag'] + col_widths['bezeichnung'] + col_widths['fv'] + col_widths['stk'] + col_widths['werkstoff']
    }
    
    # Header row
    header_height = 8*mm
    header_top = table_top
    header_bottom = table_top - header_height
    
    # Draw header background
    c.setFillColor(lightgrey)
    c.rect(table_left, header_bottom, table_width, header_height, fill=1, stroke=0)
    
    # Draw header borders
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(table_left, header_bottom, table_width, header_height, fill=0, stroke=1)
    
    # Draw header vertical lines
    c.line(col_x['bezeichnung'], header_top, col_x['bezeichnung'], header_bottom)
    c.line(col_x['fv'], header_top, col_x['fv'], header_bottom)
    c.line(col_x['stk'], header_top, col_x['stk'], header_bottom)
    c.line(col_x['werkstoff'], header_top, col_x['werkstoff'], header_bottom)
    c.line(col_x['modell'], header_top, col_x['modell'], header_bottom)
    
    # Header text
    c.setFillColor(black)
    c.setFont(BOLD_FONT, 11)
    text_y = header_bottom + 3*mm
    
    c.drawString(col_x['auftrag'] + 2*mm, text_y, "Auftrag")
    c.drawString(col_x['bezeichnung'] + 2*mm, text_y, "Bezeichnung")
    
    # Center-aligned headers
    fv_text = "FV"
    fv_width = c.stringWidth(fv_text, BOLD_FONT, 11)
    c.drawString(col_x['fv'] + (col_widths['fv'] - fv_width) / 2, text_y, fv_text)
    
    stk_text = "Stk"
    stk_width = c.stringWidth(stk_text, BOLD_FONT, 11)
    c.drawString(col_x['stk'] + (col_widths['stk'] - stk_width) / 2, text_y, stk_text)
    
    c.drawString(col_x['werkstoff'] + 2*mm, text_y, "Werkstoff")
    c.drawString(col_x['modell'] + 2*mm, text_y, "Modellnummer")
    
    # Data rows
    c.setFont(DEFAULT_FONT, 10)
    positions = data.get('positionen', [])
    min_row_height = 15*mm
    current_y = header_bottom
    
    for i, pos in enumerate(positions):
        # Calculate row height based on content
        pos_number = i + 1
        auftrag = f"{pos_number}){pos.get('auftrag', '')}"
        beschreibung = pos.get('beschreibung', '')
        vorgang = pos.get('vorgang', '')
        modellnummer = pos.get('modellnummer', '')
        werkstoff = pos.get('werkstoff', '')
        
        # Calculate lines needed for each field
        auftrag_lines = wrap_text(auftrag, c, col_widths['auftrag'] - 4*mm, DEFAULT_FONT, 10)
        
        all_beschreibung_lines = []
        beschreibung_parts = beschreibung.split('\n') if beschreibung else []
        for part in beschreibung_parts:
            wrapped = wrap_text(part, c, col_widths['bezeichnung'] - 4*mm, DEFAULT_FONT, 10)
            all_beschreibung_lines.extend(wrapped)
        
        vorgang_lines = wrap_text(vorgang, c, col_widths['bezeichnung'] - 4*mm, DEFAULT_FONT, 9) if vorgang else []
        werkstoff_lines = wrap_text(werkstoff, c, col_widths['werkstoff'] - 4*mm, DEFAULT_FONT, 10)
        modell_lines = wrap_text(modellnummer, c, col_widths['modell'] - 4*mm, DEFAULT_FONT, 10)
        
        # Calculate max lines needed
        max_lines = max(
            len(auftrag_lines),
            len(all_beschreibung_lines) + (len(vorgang_lines) if vorgang_lines else 0),
            len(werkstoff_lines),
            len(modell_lines),
            1  # minimum 1 line
        )
        
        # Calculate actual row height with more padding
        row_height = max(min_row_height, 10*mm + max_lines * 4*mm)
        
        row_top = current_y
        row_bottom = current_y - row_height
        
        # Draw row borders
        c.rect(table_left, row_bottom, table_width, row_height, fill=0, stroke=1)
        
        # Draw vertical lines
        c.line(col_x['bezeichnung'], row_top, col_x['bezeichnung'], row_bottom)
        c.line(col_x['fv'], row_top, col_x['fv'], row_bottom)
        c.line(col_x['stk'], row_top, col_x['stk'], row_bottom)
        c.line(col_x['werkstoff'], row_top, col_x['werkstoff'], row_bottom)
        c.line(col_x['modell'], row_top, col_x['modell'], row_bottom)
        
        # Get remaining data
        fv = str(pos.get('fv', ''))
        menge = str(pos.get('menge', '')).replace('.', ',') if pos.get('menge') else ''
        
        # Draw text with wrapping
        text_y = row_top - 5*mm  # Start from top with padding
        c.setFont(DEFAULT_FONT, 10)
        
        # Auftrag - use pre-calculated lines
        for j, line in enumerate(auftrag_lines):
            if text_y - j*3.5*mm > row_bottom + 2*mm:  # Check bottom boundary
                c.drawString(col_x['auftrag'] + 2*mm, text_y - j*3.5*mm, line)
        
        # Beschreibung - use pre-calculated lines
        for j, line in enumerate(all_beschreibung_lines):
            if text_y - j*3.5*mm > row_bottom + 2*mm:  # Check bottom boundary
                c.drawString(col_x['bezeichnung'] + 2*mm, text_y - j*3.5*mm, line)
        
        # Vorgang unter Beschreibung
        if vorgang_lines:
            c.setFont(DEFAULT_FONT, 9)
            vorgang_y = text_y - len(all_beschreibung_lines) * 3.5*mm if all_beschreibung_lines else text_y - 3.5*mm
            for j, line in enumerate(vorgang_lines):
                if vorgang_y - j*3*mm > row_bottom + 2*mm:  # Check bottom boundary
                    c.drawString(col_x['bezeichnung'] + 2*mm, vorgang_y - j*3*mm, line)
            c.setFont(DEFAULT_FONT, 10)
        
        # Center-aligned FV and Stk
        if fv and text_y > row_bottom + 2*mm:
            fv_width = c.stringWidth(fv, DEFAULT_FONT, 10)
            c.drawString(col_x['fv'] + (col_widths['fv'] - fv_width) / 2, text_y, fv)
        
        if menge and text_y > row_bottom + 2*mm:
            menge_width = c.stringWidth(menge, DEFAULT_FONT, 10)
            c.drawString(col_x['stk'] + (col_widths['stk'] - menge_width) / 2, text_y, menge)
        
        # Werkstoff - use pre-calculated lines
        for j, line in enumerate(werkstoff_lines):
            if text_y - j*3.5*mm > row_bottom + 2*mm:  # Check bottom boundary
                c.drawString(col_x['werkstoff'] + 2*mm, text_y - j*3.5*mm, line)
        
        # Modellnummer - use pre-calculated lines
        for j, line in enumerate(modell_lines):
            if text_y - j*3.5*mm > row_bottom + 2*mm:  # Check bottom boundary
                c.drawString(col_x['modell'] + 2*mm, text_y - j*3.5*mm, line)
        
        current_y = row_bottom
        
        # Check if we need a new page
        if current_y < 40*mm and i < len(positions) - 1:
            c.showPage()
            # Redraw header on new page
            c.setFont(BOLD_FONT, 14)
            c.drawString(20*mm, height - 20*mm, "DZ Metall")
            c.setFont(DEFAULT_FONT, 14)
            c.drawRightString(width - 20*mm, height - 20*mm, datum)
            c.setFont(DEFAULT_FONT, 24)
            c.drawString(title_x, height - 40*mm, title)
            c.line(title_x, height - 42*mm, title_x + title_width, height - 42*mm)
            
            # Reset table position
            current_y = table_top
            
            # Redraw table header
            c.setFillColor(lightgrey)
            c.rect(table_left, header_bottom, table_width, header_height, fill=1, stroke=0)
            c.setStrokeColor(black)
            c.rect(table_left, header_bottom, table_width, header_height, fill=0, stroke=1)
            
            c.line(col_x['bezeichnung'], header_top, col_x['bezeichnung'], header_bottom)
            c.line(col_x['fv'], header_top, col_x['fv'], header_bottom)
            c.line(col_x['stk'], header_top, col_x['stk'], header_bottom)
            c.line(col_x['werkstoff'], header_top, col_x['werkstoff'], header_bottom)
            c.line(col_x['modell'], header_top, col_x['modell'], header_bottom)
            
            c.setFillColor(black)
            c.setFont(BOLD_FONT, 11)
            header_text_y = header_bottom + 3*mm
            c.drawString(col_x['auftrag'] + 2*mm, header_text_y, "Auftrag")
            c.drawString(col_x['bezeichnung'] + 2*mm, header_text_y, "Bezeichnung")
            
            # Recalculate centered text widths for FV and Stk
            fv_header_width = c.stringWidth("FV", BOLD_FONT, 11)
            stk_header_width = c.stringWidth("Stk", BOLD_FONT, 11)
            c.drawString(col_x['fv'] + (col_widths['fv'] - fv_header_width) / 2, header_text_y, "FV")
            c.drawString(col_x['stk'] + (col_widths['stk'] - stk_header_width) / 2, header_text_y, "Stk")
            
            c.drawString(col_x['werkstoff'] + 2*mm, header_text_y, "Werkstoff")
            c.drawString(col_x['modell'] + 2*mm, header_text_y, "Modellnummer")
            
            c.setFont(DEFAULT_FONT, 10)
            current_y = header_bottom
    
    # Save the PDF
    c.save()
    
    return output_path