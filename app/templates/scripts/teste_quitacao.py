# Script para teste de quitação de funcionários
# Cria uma venda no mês anterior para que possamos validar a quitação.
# Deve ser aplicado no routes.py acima de PAGAMENTO, depois basta chamar a rota "testar_quitacao" no navegador

@main.route('/testar_quitacao')
def testar_quitacao():
    from dateutil.relativedelta import relativedelta

    # Busca primeiro funcionário e produto
    funcionario = Funcionario.query.first()
    produto = Produto.query.first()

    if not funcionario or not produto:
        flash("Você precisa cadastrar ao menos 1 funcionário e 1 produto para testar.", "danger")
        return redirect(url_for('main.index'))

    # Cria venda no mês anterior
    data_mes_passado = datetime.now() - relativedelta(months=1)

    venda = Venda(
        data_hora=data_mes_passado,
        cliente_tipo="Funcionário",
        forma_pagamento=None,
        funcionario_id=funcionario.id
    )
    db.session.add(venda)
    db.session.flush()

    item = ItemVenda(
        venda_id=venda.id,
        produto_id=produto.id,
        quantidade=1,
        valor_unitario=produto.valor_unitario
    )
    db.session.add(item)

    db.session.commit()
    flash(f"Venda de teste no mês anterior criada para {funcionario.nome}.", "success")
    return redirect(url_for('main.listar_funcionarios'))
