from flask import Flask, jsonify, send_file
from flask_cors import CORS 
import pandas as pd
app = Flask(__name__)

CORS(app)  # Habilita CORS para todas as rotas

# Servir o frontend
@app.route("/")
def serve_frontend():
    return send_file('Template/index.html')

# Servir arquivos CSS
@app.route("/styles/<path:filename>")
def serve_css(filename):
    return send_file(f'styles/{filename}')

@app.route("/api/dados") # api para obter os dados (caso real, necessita de autenticação, isso deve ser implementado ass. Adriel)
def get_dados():
 
    url = "https://docs.google.com/spreadsheets/d/1OO7gDKXv4YJiDfpfrIHaXIa_XUgDhl3rG2FQImQ-ixY/export?format=xlsx" 
    df = pd.read_excel(url)
    return jsonify(df.to_dict(orient="records"))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
