# Script para zerar banco de dados
# Apaga todas as entradas no banco preservando todas as tabelas criadas
# Deve ser colocada no final do código, depois basta chamar a rota "resetar_banco" no navegador

@main.route('/resetar_banco')
def resetar_banco():
    from .models import Produto, Funcionario, Venda, ItemVenda, QuitacaoMensal
    try:
        ItemVenda.query.delete()
        Venda.query.delete()
        QuitacaoMensal.query.delete()
        Produto.query.delete()
        Funcionario.query.delete()
        db.session.commit()
        return "✅ Banco de dados resetado com sucesso!"
    except Exception as e:
        db.session.rollback()
        return f"❌ Erro ao resetar banco: {str(e)}"