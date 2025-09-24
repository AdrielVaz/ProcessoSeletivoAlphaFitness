from flask import Flask, jsonify
from flask_cors import CORS 
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

@app.route("/")
def home():
    return "<h1>Servidor rodando!</h1><p>Acesse <a href='/api/dados'>/api/dados</a> para ver os dados.</p>"

@app.route("/api/dados") # api para obter os dados (caso real, necessita de autenticação, isso deve ser implementado ass. Adriel)
def get_dados():
    import pandas as pd
    url = "https://docs.google.com/spreadsheets/d/1OO7gDKXv4YJiDfpfrIHaXIa_XUgDhl3rG2FQImQ-ixY/export?format=xlsx" 
    df = pd.read_excel(url)
    return jsonify(df.to_dict(orient="records"))



if __name__ == "__main__":
    app.run(debug=True)
