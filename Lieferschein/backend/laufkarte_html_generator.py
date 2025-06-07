import os
import tempfile
from datetime import datetime
from typing import Dict, List, Any

def generate_laufkarte_html(data: Dict[str, Any]) -> str:
    """Generate Laufkarte HTML with dynamic data"""
    
    # Get current date
    datum = data.get('datum', datetime.now().strftime('%d.%m.%Y'))
    
    # Start building HTML
    html = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laufkarte - DZ Metall</title>
    <style>
        @page {
            size: A4;
            margin: 0;
        }
        
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #e0e0e0;
        }
        
        .page {
            width: 210mm;
            min-height: 297mm;
            padding: 20mm;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 5mm rgba(0,0,0,0.1);
            box-sizing: border-box;
        }
        
        @media print {
            body {
                background-color: white;
            }
            .page {
                margin: 0;
                box-shadow: none;
                page-break-after: always;
            }
        }
        
        .header {
            margin-bottom: 30px;
        }
        
        .company {
            float: left;
            font-weight: bold;
            font-size: 14pt;
        }
        
        .date {
            float: right;
            font-size: 14pt;
        }
        
        .clearfix::after {
            content: "";
            display: table;
            clear: both;
        }
        
        h1 {
            text-align: center;
            margin: 40px 0 30px 0;
            text-decoration: underline;
            font-size: 24pt;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            font-size: 11pt;
        }
        
        th, td {
            border: 1px solid #333;
            padding: 6px 8px;
            text-align: left;
        }
        
        th {
            background-color: #e0e0e0;
            font-weight: bold;
        }
        
        .center {
            text-align: center;
        }
        
        .main-table {
            margin-bottom: 40px;
        }
        
        
        @media screen and (max-width: 800px) {
            .page {
                width: 100%;
                min-height: auto;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="page">
        <div class="header clearfix">
            <div class="company">DZ Metall</div>
            <div class="date">''' + datum + '''</div>
        </div>
        
        <h1>Laufkarte</h1>
        
        <table class="main-table">
            <thead>
                <tr>
                    <th style="width: 15%;">Auftrag</th>
                    <th style="width: 35%;">Bezeichnung</th>
                    <th style="width: 5%;" class="center">FV</th>
                    <th style="width: 10%;" class="center">Stk</th>
                    <th style="width: 15%;">Werkstoff</th>
                    <th style="width: 20%;">Modellnummer</th>
                </tr>
            </thead>
            <tbody>'''
    
    # Add positions
    positions = data.get('positionen', [])
    for i, pos in enumerate(positions):
        pos_number = i + 1
        auftrag = pos.get('auftrag', '')
        beschreibung = pos.get('beschreibung', '')
        vorgang = pos.get('vorgang', '')
        fv = pos.get('fv', '')
        menge = pos.get('menge', '')
        werkstoff = pos.get('werkstoff', '')
        modellnummer = pos.get('modellnummer', '')
        
        # Format menge as string with comma
        if menge:
            menge_str = str(menge).replace('.', ',')
        else:
            menge_str = ''
        
        # Combine beschreibung with vorgang if available
        if vorgang:
            full_beschreibung = f"{beschreibung}<br>{vorgang}"
        else:
            full_beschreibung = beschreibung
        
        html += f'''
                <tr>
                    <td>{pos_number}){auftrag}</td>
                    <td>{full_beschreibung}</td>
                    <td class="center">{fv}</td>
                    <td class="center">{menge_str}</td>
                    <td>{werkstoff}</td>
                    <td>{modellnummer}</td>
                </tr>'''
    
    html += '''
            </tbody>
        </table>
    </div>
</body>
</html>'''
    
    return html

def generate_laufkarte_pdf_from_html(data: Dict[str, Any]) -> str:
    """Generate Laufkarte PDF from HTML"""
    # Generate HTML
    html_content = generate_laufkarte_html(data)
    
    # Save to temporary HTML file
    html_path = tempfile.mktemp(suffix='.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # For now, just return the HTML file
    # PDF conversion libraries (pdfkit, weasyprint) can be added later if needed
    return html_path