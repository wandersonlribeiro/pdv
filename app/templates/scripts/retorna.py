# Retorna com itens vendidos para o estoque.
# Executar com comando: python retorna.py na pasta do app

from app import create_app, db
from app.models import Venda, Produto, ItemVenda

app = create_app()

with app.app_context():
    venda_id = 5
    venda = Venda.query.get(venda_id)

    if venda:
        for item in venda.itens:
            produto = Produto.query.get(item.produto_id)
            if produto:
                produto.quantidade += item.quantidade
        db.session.commit()

        for item in venda.itens:
            db.session.delete(item)

        db.session.delete(venda)
        db.session.commit()

        print(f"✅ Venda {venda_id} revertida com sucesso!")
    else:
        print(f"❌ Venda com ID {venda_id} não encontrada.")
