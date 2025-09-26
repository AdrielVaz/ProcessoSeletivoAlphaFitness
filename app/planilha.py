from flask import Flask, jsonify, send_file, request
from flask_cors import CORS 
import pandas as pd
import time

app = Flask(__name__)
CORS(app)

# Cache em memória
CACHE_DURATION = 300
cache_data = None
cache_timestamp = 0

@app.route("/")
def serve_frontend():
    return send_file('Template/index.html')

@app.route("/styles/<path:filename>")
def serve_css(filename):
    return send_file(f'styles/{filename}')

@app.route("/api/dados")
def get_dados():
    global cache_data, cache_timestamp
    
    current_time = time.time()
    if cache_data is None or (current_time - cache_timestamp) > CACHE_DURATION:
        print("Atualizando cache...")
        try:
            url = "https://docs.google.com/spreadsheets/d/1OO7gDKXv4YJiDfpfrIHaXIa_XUgDhl3rG2FQImQ-ixY/export?format=xlsx"
            df = pd.read_excel(url)
            cache_data = df.to_dict(orient="records")
            cache_timestamp = current_time
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Parâmetros de filtro
    filtro_nome = request.args.get('filtro_nome', '').lower()
    filtro_email = request.args.get('filtro_email', '').lower()
    filtro_cpf = request.args.get('filtro_cpf', '').replace('.', '').replace('-', '')
    filtro_numero = request.args.get('filtro_numero', '')
    filtro_id = request.args.get('filtro_id', '')
    ordenar = request.args.get('ordenar', 'mais-recentes')
    
    # Aplica filtros em TODOS os dados
    dados_filtrados = cache_data.copy()
    
    # FILTROS (mostram apenas dados específicos)
    if filtro_nome:
        dados_filtrados = [item for item in dados_filtrados 
                          if filtro_nome in str(item.get('nome', '')).lower()]
    
    if filtro_email:
        dados_filtrados = [item for item in dados_filtrados 
                          if filtro_email in str(item.get('email', '')).lower()]
    
    if filtro_cpf:
        dados_filtrados = [item for item in dados_filtrados 
                          if filtro_cpf in str(item.get('cpf', '')).replace('.', '').replace('-', '')]
    
    if filtro_numero:
        dados_filtrados = [item for item in dados_filtrados 
                          if filtro_numero in str(item.get('numero', ''))]
    
    if filtro_id:
        dados_filtrados = [item for item in dados_filtrados 
                          if filtro_id in str(item.get('id', ''))]
    
    # ORDENAÇÃO (organiza os dados filtrados)
    if ordenar == "mais-recentes":
        dados_filtrados.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    elif ordenar == "mais-antigos":
        dados_filtrados.sort(key=lambda x: x.get('timestamp', ''))
    elif ordenar == "a-z":
        dados_filtrados.sort(key=lambda x: str(x.get('nome', '')).lower())
    elif ordenar == "z-a":
        dados_filtrados.sort(key=lambda x: str(x.get('nome', '')).lower(), reverse=True)
    
    # Paginação (após filtros E ordenação)
    try:
        page = int(request.args.get('page', 1))
    except (ValueError, TypeError):
        page = 1
    
    try:
        per_page = int(request.args.get('per_page', 100))
    except (ValueError, TypeError):
        per_page = 100
    
    page = max(1, page)
    per_page = max(1, min(per_page, 1000))
    
    total_filtrados = len(dados_filtrados)
    total_pages = (total_filtrados + per_page - 1) // per_page
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    dados_paginados = dados_filtrados[start_idx:end_idx]
    
    return jsonify({
        "data": dados_paginados,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(cache_data),  # Total original
            "total_filtrados": total_filtrados,  # Total após filtros
            "total_pages": total_pages
        }
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)