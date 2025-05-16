from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask import request

import os

db = SQLAlchemy()
migrate = Migrate() 

def formatar_real(valor):
    try:
        valor = float(valor)
        return f"{valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except Exception:
        return "0,00"


def create_app():
    app = Flask(__name__)

    # Configurações básicas
    app.config['SECRET_KEY'] = 'chave-secreta-supersegura'  # Usada para sessões e formulários
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/pdv.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa extensões
    db.init_app(app)
    Bootstrap(app)
    migrate.init_app(app, db)

    # Importa e registra rotas
    from .routes import main
    app.register_blueprint(main)
    
    #Adiciona filtro customizado ao Jinja2
    app.jinja_env.filters['real'] = formatar_real

    return app
