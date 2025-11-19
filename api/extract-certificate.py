from http.server import BaseHTTPRequestHandler
importar json
importar re
from io import BytesIO
importar PyPDF2

def extrair_texto_de_pdf(pdf_bytes):
    """Extrai texto do PDF usando PyPDF2"""
    tentar:
        arquivo_pdf = BytesIO(bytes_pdf)
        leitor_pdf = PyPDF2.PdfReader(arquivo_pdf)
        texto = ""
        para página em pdf_reader.pages:
            texto += página.extrair_texto()
        texto de retorno
    exceto Exception como e:
        raise Exception(f"Erro ao ler PDF: {str(e)}")

def extract_caar_data(text):
    """Dados extras do Certificado CAAR (Piloto)"""
    dados = {
        "tipo": "CAAR",
        "nome": Nenhum,
        "cpf": Nenhum
    }
    
    # Padrões para extrair nome
    padrões_de_nome = [
        r'que\s+([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑa-záàâãéèêíïóôõöúçñ\s]+?),?\s+CPF',
        r'aprovado.*?([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑa-záàâãéèêíïóôõöúçñ\s]+?),?\s+CPF',
        r'certificado.*?([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑa-záàâãéèêíïóôõöúçñ\s]+?),?\s+CPF',
        r'piloto.*?([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑa-záàâãéèêíïóôõöúçñ\s]+?),?\s+CPF'
    ]
    
    para padrão em name_patterns:
        correspondência = re.pesquisar(padrão, texto, re.IGNORECASE)
        se houver correspondência:
            nome = match.group(1).strip()
            # Limpar espaços extras e capitalizar corretamente
            nome = ' '.join(nome.split())
            dados["nome"] = nome.upper()
            quebrar
    
    # Extrair CPF (com ou sem formatação)
    cpf_match = re.search(r'CPF[\s:]+(\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2})', text, re.IGNORECASE)
    se cpf_match:
        cpf = re.sub(r'\D', '', cpf_match.group(1))
        dados["cpf"] = cpf
    
    retornar dados

def extract_anac_data(text):
    """Dados extras da Certidão ANAC (Drone/Aeronave)"""
    dados = {
        "tipo": "ANAC",
        "registro": Nenhum,
        "fabricante": Nenhum,
        "modelo": Nenhum
    }
    
    # Extrair Registro ANAC (formato PS-XXXXXXXXX)
    reg_match = re.search(r'(PS-\d{9})', text, re.IGNORECASE)
    se reg_match:
        dados["registro"] = reg_match.group(1).upper()
    
    # Extrair Fabricante
    padrões_mfg = [
        r'Fabricante[:\s]+([AZ\s]+?)(?=Modelo|N[°º]|Peso|$)',
        r'Fabricante[:\s]+([AZ]+)',
    ]
    para padrão em mfg_patterns:
        correspondência = re.search(padrão, texto, re.IGNORECASE | re.MULTILINE)
        se houver correspondência:
            fabricante = match.group(1).strip()
            fabricante = ' '.join(fabricante.split())
            dados["fabricante"] = fabricante.upper()
            quebrar
    
    # Extrair Modelo
    padrões_do_modelo = [
        r'Modelo[:\s]+([A-Z0-9\s-]+?)(?=N[°º]|Peso|Série|Fabricante|$)',
        r'Modelo[:\s]+([A-Z0-9\s-]+)',
    ]
    para cada padrão em model_patterns:
        correspondência = re.search(padrão, texto, re.IGNORECASE | re.MULTILINE)
        se houver correspondência:
            modelo = match.group(1).strip()
            modelo = ' '.join(modelo.split())
            data["modelo"] = modelo.upper()
            quebrar
    
    retornar dados

manipulador de classe (BaseHTTPRequestHandler):
    def do_POST(self):
        tentar:
            # Ler o conteúdo do arquivo PDF
            content_length = int(self.headers['Content-Length'])
            pdf_bytes = self.rfile.read(content_length)
            
            # Extrair texto do PDF
            texto = extrair_texto_do_pdf(bytes_pdf)
            
            # Detectar tipo de certificado baseado no conteúdo
            texto_maiúsculo = texto.maiúsculo()
            
            se 'CAAR' estiver em text_upper ou 'PILOTO' estiver em text_upper ou ('CPF' estiver em text_upper e 'ANAC' não estiver em text_upper):
                resultado = extrair_dados_caar(texto)
            elif 'ANAC' in text_upper or 'AERONAVE' in text_upper or 'PS-' in text:
                resultado = extrair_dados_anac(texto)
            outro:
                # Tentar ambos e retornar o que tiver mais dados
                caar = extract_caar_data(texto)
                anac = extrair_dados_anac(texto)
                
                if caar["nome"] ou caar["cpf"]:
                    resultado = carro
                elif anac["registro"] ou anac["fabricante"]:
                    resultado = anac
                outro:
                    resultado = {
                        "tipo": "desconhecido",
                        "error": "Não foi possível identificar o tipo de certificado"
                    }
            
            # Adicione o texto completo para depuração (opcional)
            resultado["_debug_text_length"] = len(texto)
            
            #orgr resposta JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        exceto Exception como e:
            #erro
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            resposta_de_erro = {
                "tipo": "erro",
                "erro": str(e),
                "message": "Erro ao processar certificado. Preencha os dados manualmente."
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """OPÇÕES de resposta a requisições (preflight CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
