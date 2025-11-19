from http.server import BaseHTTPRequestHandler
import json
import re
from io import BytesIO

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_text_from_pdf(pdf_bytes):
    if not PyPDF2:
        raise Exception("PyPDF2 not available")
    
    pdf_file = BytesIO(pdf_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_caar_data(text):
    data = {"type": "CAAR", "nome": None, "cpf": None}
    
    name_patterns = [
        r'que\s+([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑa-záàâãéèêíïóôõöúçñ\s]+?),?\s+CPF',
        r'aprovado.*?([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑa-záàâãéèêíïóôõöúçñ\s]+?),?\s+CPF',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["nome"] = match.group(1).strip().upper()
            break
    
    cpf_match = re.search(r'CPF[\s:]+(\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2})', text, re.IGNORECASE)
    if cpf_match:
        data["cpf"] = re.sub(r'\D', '', cpf_match.group(1))
    
    return data

def extract_anac_data(text):
    data = {"type": "ANAC", "registro": None, "fabricante": None, "modelo": None}
    
    reg_match = re.search(r'(PS-\d{9})', text, re.IGNORECASE)
    if reg_match:
        data["registro"] = reg_match.group(1).upper()
    
    mfg_match = re.search(r'Fabricante[:\s]+([A-Z\s]+?)(?=Modelo|N[°º]|Peso|$)', text, re.IGNORECASE)
    if mfg_match:
        data["fabricante"] = mfg_match.group(1).strip().upper()
    
    model_match = re.search(r'Modelo[:\s]+([A-Z0-9\s-]+?)(?=N[°º]|Peso|Série|$)', text, re.IGNORECASE)
    if model_match:
        data["modelo"] = model_match.group(1).strip().upper()
    
    return data

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            pdf_bytes = self.rfile.read(content_length)
            
            text = extract_text_from_pdf(pdf_bytes)
            text_upper = text.upper()
            
            if 'CAAR' in text_upper or ('CPF' in text_upper and 'ANAC' not in text_upper):
                result = extract_caar_data(text)
            elif 'ANAC' in text_upper or 'PS-' in text:
                result = extract_anac_data(text)
            else:
                result = {"type": "unknown", "error": "Tipo não identificado"}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"type": "error", "error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
