from . import db
from datetime import datetime
from sqlalchemy import Column, Date, Numeric

# -----------------------------
# Produto
# -----------------------------
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    data_compra = Column(Date, nullable=True)
    valor_compra = Column(Numeric(10, 2), nullable=True)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    validade = db.Column(db.Date, nullable=False)
    fornecedor = db.Column(db.String(100), nullable=True) 
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    ativo = db.Column(db.Boolean, default=True)
    ciente_vencimento = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Produto {self.nome}>'


# -----------------------------
# Funcionário
# -----------------------------
class Funcionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    limite_mensal = db.Column(db.Float, nullable=True, default=100.0)

    # ✅ A venda já tem backref='funcionario', então aqui não precisa nada!
    # Evita conflito de nomes


# -----------------------------
# Venda
# -----------------------------
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    cliente_tipo = db.Column(db.String(20))  # Externo ou Funcionário
    forma_pagamento = db.Column(db.String(20))  # Pix, Dinheiro, etc.
    quitado = db.Column(db.Boolean, default=False)

    funcionario_id = db.Column(
        db.Integer,
        db.ForeignKey('funcionario.id', name='fk_venda_funcionario'),
        nullable=True
    )

    # ✅ Este relacionamento já cria venda.funcionario e funcionario.vendas
    funcionario = db.relationship('Funcionario', backref='vendas')

    # ✅ Itens da venda
    itens = db.relationship('ItemVenda', backref='venda', lazy=True)


# -----------------------------
# ItemVenda
# -----------------------------
class ItemVenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)

    produto = db.relationship('Produto', backref='itens')


# -----------------------------
# QuitarConsumo
# -----------------------------

class QuitacaoMensal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    data_quitacao = db.Column(db.DateTime, default=datetime.utcnow)

