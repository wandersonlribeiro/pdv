from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask import render_template, redirect, url_for, flash
from .models import Produto, Venda, ItemVenda, Funcionario, QuitacaoMensal
from dateutil.relativedelta import relativedelta
from .forms import ProdutoForm
from decimal import Decimal
from datetime import datetime, timedelta
from . import db
import os

main = Blueprint('main', __name__)

logo_path = os.path.abspath('static/images/logo.png')

# -------------------- INDEX --------------------

@main.route('/')
def index():
    # Produtos com validade em até 3 dias
    hoje = datetime.now().date()
    limite = hoje + timedelta(days=3)
    produtos_vencendo = Produto.query.filter(
        Produto.validade >= hoje,
        Produto.validade <= limite,
        Produto.ciente_vencimento == False,
        Produto.ativo == True
    ).all()

    # Últimas 5 vendas com JOIN de funcionário e itens
    vendas = (
        db.session.query(Venda)
        .order_by(Venda.data_hora.desc())
        .limit(5)
        .all()
    )

    return render_template('index.html', produtos_vencendo=produtos_vencendo, vendas=vendas)



# -------------------- PRODUTOS --------------------


#CADASTRAR PRODUTO
@main.route('/produtos/cadastrar', methods=['GET', 'POST'])
def cadastrar_produto():
    form = ProdutoForm()

    print("Método:", form.is_submitted())
    print("Validado:", form.validate())
    print("Erros:", form.errors)

    if form.validate_on_submit():
        produto = Produto(
             nome=form.nome.data,
            tipo=form.tipo.data,
            quantidade=form.quantidade.data,
            valor_unitario=form.valor_unitario.data,
            validade=form.validade.data,
            fornecedor=form.fornecedor.data,
            data_compra=form.data_compra.data,
            valor_compra=form.valor_compra.data
        )
        db.session.add(produto)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('main.listar_produtos'))
    return render_template('cadastrar_produto.html', form=form)



@main.route('/produtos')
def listar_produtos():
    mostrar_inativos = request.args.get('inativos') == '1'
    busca = request.args.get('busca', '')
    sort_by = request.args.get('sort', 'nome')  # padrão: nome
    order = request.args.get('order', 'asc')    # padrão: ascendente

    query = Produto.query

    if mostrar_inativos:
        query = query.filter_by(ativo=False)
    else:
        query = query.filter_by(ativo=True)

    if busca:
        query = query.filter(Produto.nome.ilike(f'%{busca}%'))

    # Ordenação dinâmica
    if sort_by == 'nome':
        column = Produto.nome
    elif sort_by == 'quantidade':
        column = Produto.quantidade
    elif sort_by == 'validade':
        column = Produto.validade
    else:
        column = Produto.nome  # fallback

    if order == 'desc':
        column = column.desc()

    produtos = query.order_by(column).all()

    return render_template(
        'listar_produtos.html',
        produtos=produtos,
        mostrar_inativos=mostrar_inativos,
        sort_by=sort_by,
        order=order
    )


#EDITAR PRODUTOS
@main.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    form = ProdutoForm(obj=produto)

    if form.validate_on_submit():
        produto.nome = form.nome.data
        produto.tipo = form.tipo.data
        produto.quantidade = form.quantidade.data
        produto.valor_unitario = form.valor_unitario.data
        produto.validade = form.validade.data
        produto.fornecedor = form.fornecedor.data
        produto.data_compra = form.data_compra.data
        produto.valor_compra = form.valor_compra.data
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('main.listar_produtos'))

    return render_template('cadastrar_produto.html', form=form, editar=True)


#EXCLUIR PRODUTO
@main.route('/produtos/excluir/<int:id>')
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído com sucesso!', 'info')
    return redirect(url_for('main.listar_produtos'))

#ATIVAR PRODUTOS

@main.route('/produtos/ativar/<int:id>')
def ativar_produto(id):
    produto = Produto.query.get_or_404(id)
    produto.ativo = True
    db.session.commit()
    flash('✅ Produto reativado com sucesso!', 'success')
    return redirect(url_for('main.listar_produtos', inativos=1))


#INATIVAR PRODUTOS
@main.route('/produtos/inativar/<int:id>')
def inativar_produto(id):
    produto = Produto.query.get_or_404(id)
    produto.ativo = False
    db.session.commit()
    flash('✅ Produto inativado com sucesso!', 'info')
    return redirect(url_for('main.listar_produtos'))

#CIENTE PRAZO DE VALIDADE
@main.route('/produtos/ciente/<int:id>')
def marcar_ciente(id):
    produto = Produto.query.get_or_404(id)
    produto.usuario_ciente = True
    db.session.commit()
    flash('Produto marcado como ciente do vencimento.', 'info')
    return redirect(url_for('main.index'))


# -------------------- FUNCIONÁRIOS --------------------


from flask import render_template, redirect, url_for, flash
from . import db
from .models import Funcionario
from .forms import FuncionarioForm
from flask import Blueprint
from sqlalchemy import func

# Cadastrar Funcionário
@main.route('/funcionarios/cadastrar', methods=['GET', 'POST'])
def cadastrar_funcionario():
    form = FuncionarioForm()
    if form.validate_on_submit():
        funcionario = Funcionario(
            nome=form.nome.data,
            cargo=form.cargo.data,
            telefone=form.telefone.data
        )
        db.session.add(funcionario)
        db.session.commit()
        flash('Funcionário cadastrado com sucesso!', 'success')
        return redirect(url_for('main.listar_funcionarios'))
    return render_template('funcionarios/cadastrar_funcionario.html', form=form)

# Listar Funcionários

from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Funcionario, QuitacaoMensal, Venda

@main.route('/funcionarios')
def listar_funcionarios():
    funcionarios = Funcionario.query.order_by(Funcionario.nome).all()

    hoje = datetime.now()
    mes_anterior = hoje.month - 1 if hoje.month > 1 else 12
    ano_anterior = hoje.year if hoje.month > 1 else hoje.year - 1
    LIMITE_MENSAL = 150.00

    funcionarios_detalhados = []

    for f in funcionarios:
        # Verifica se quitou o mês anterior
        quitado = QuitacaoMensal.query.filter_by(
            funcionario_id=f.id,
            mes=mes_anterior,
            ano=ano_anterior
        ).first()

        # Calcula o total consumido no mês atual
        vendas_mes = Venda.query.filter_by(funcionario_id=f.id, quitado=False)\
            .filter(db.extract('month', Venda.data_hora) == hoje.month)\
            .filter(db.extract('year', Venda.data_hora) == hoje.year)\
            .all()

        total_consumido = sum(
            item.quantidade * item.valor_unitario
            for venda in vendas_mes for item in venda.itens
        )

        saldo_disponivel = LIMITE_MENSAL - total_consumido

        funcionarios_detalhados.append({
            'id': f.id,
            'nome': f.nome,
            'cargo': f.cargo,
            'telefone': f.telefone,
            'quitado_mes_anterior': bool(quitado),
            'saldo_disponivel': saldo_disponivel
        })

    return render_template('funcionarios/listar_funcionarios.html', funcionarios=funcionarios_detalhados)



# Editar Funcionário
@main.route('/funcionarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    form = FuncionarioForm(obj=funcionario)
    if form.validate_on_submit():
        funcionario.nome = form.nome.data
        funcionario.cargo = form.cargo.data
        funcionario.telefone = form.telefone.data
        db.session.commit()
        flash('Funcionário atualizado com sucesso!', 'success')
        return redirect(url_for('main.listar_funcionarios'))
    return render_template('funcionarios/cadastrar_funcionario.html', form=form, editar=True)

# Excluir Funcionário
@main.route('/funcionarios/excluir/<int:id>')
def excluir_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    db.session.delete(funcionario)
    db.session.commit()
    flash('Funcionário excluído com sucesso!', 'info')
    return redirect(url_for('main.listar_funcionarios'))


# -------------------- VENDAS --------------------

# Iniciar uma nova venda
@main.route('/vendas/iniciar')
def iniciar_venda():
    session['carrinho'] = []
    return redirect(url_for('main.adicionar_item'))

# Adicionar item à venda
@main.route('/vendas/adicionar_item', methods=['GET', 'POST'])
def adicionar_item():
    produtos = Produto.query.all()

    if request.method == 'POST':
        produto_id = int(request.form['produto_id'])
        quantidade = int(request.form['quantidade'])

        produto = Produto.query.get(produto_id)

        # Verifica se o produto existe e se tem quantidade suficiente
        if produto and produto.quantidade >= quantidade:

            # Se não existir carrinho na sessão, cria um
            if 'carrinho' not in session:
                session['carrinho'] = []

            # Cria o item e adiciona ao carrinho
            item = {
                'produto_id': produto.id,
                'nome': produto.nome,
                'quantidade': quantidade,
                'valor_unitario': float(produto.valor_unitario)
            }
            session['carrinho'].append(item)
            session.modified = True

            flash('Produto adicionado à venda!', 'success')
        else:
            flash(f'Estoque insuficiente para {produto.nome}. Disponível: {produto.quantidade}', 'danger')

    # 🔁 Mostra os produtos e o carrinho na tela
    return render_template('vendas/adicionar_item.html', produtos=produtos, carrinho=session.get('carrinho', []))


# Remover item da venda
@main.route('/vendas/remover_item/<int:index>')
def remover_item(index):
    carrinho = session.get('carrinho', [])
    if 0 <= index < len(carrinho):
        carrinho.pop(index)
        session['carrinho'] = carrinho
        session.modified = True
        flash('Item removido do carrinho.', 'info')
    return redirect(url_for('main.adicionar_item'))


#Mensagem de venda realizada
@main.route('/vendas/sucesso')
def venda_sucesso():
        return render_template('vendas/venda_sucesso.html')

# Finalizar Venda
@main.route('/vendas/finalizar', methods=['GET', 'POST'])
def finalizar_venda():
    LIMITE_MENSAL = 150.00
    carrinho = session.get('carrinho', [])
    consumo_funcionario = None

    # Carregar funcionários e calcular saldo disponível
    funcionarios_obj = Funcionario.query.order_by(Funcionario.nome).all()
    funcionarios = []
    for f in funcionarios_obj:
        hoje = datetime.now()
        vendas_mes = Venda.query.filter_by(funcionario_id=f.id, quitado=False)\
            .filter(db.extract('month', Venda.data_hora) == hoje.month)\
            .filter(db.extract('year', Venda.data_hora) == hoje.year)\
            .all()


        total_consumido = sum(
            item.quantidade * item.valor_unitario
            for venda in vendas_mes for item in venda.itens
        )

        saldo_disponivel = LIMITE_MENSAL - total_consumido

        funcionarios.append({
            'id': f.id,
            'nome': f.nome,
            'cargo': f.cargo,
            'saldo': saldo_disponivel
        })

    if request.method == 'POST':
        if not carrinho:
            flash("Carrinho vazio!", "danger")
            return redirect(url_for('main.iniciar_venda'))

        cliente_tipo = request.form.get('cliente_tipo')
        if not cliente_tipo:
            flash("Tipo de cliente não informado. Tente novamente.", "danger")
            return redirect(url_for('main.finalizar_venda'))

        forma_pagamento = request.form.get('forma_pagamento')
        funcionario_id = request.form.get('funcionario_id') if cliente_tipo == 'Funcionário' else None

        # ✅ Se for funcionário, verifica consumo mensal e mês anterior quitado antes de permitir a venda
        if cliente_tipo == 'Funcionário' and funcionario_id:
            funcionario = Funcionario.query.get(funcionario_id)
            hoje = datetime.now()

            # Verifica se o mês anterior foi quitado
            mes_anterior = hoje.month - 1 if hoje.month > 1 else 12
            ano_anterior = hoje.year if hoje.month > 1 else hoje.year - 1

            quitado_anterior = QuitacaoMensal.query.filter_by(
                funcionario_id=funcionario.id,
                mes=mes_anterior,
                ano=ano_anterior
            ).first()

            if not quitado_anterior:
                flash(f"O funcionário {funcionario.nome} ainda não quitou o mês anterior ({mes_anterior}/{ano_anterior}).", "danger")
                return redirect(url_for('main.adicionar_item'))

            # Verifica limite mensal de consumo
            vendas_mes = Venda.query.filter_by(funcionario_id=funcionario.id, quitado=False)\
                .filter(db.extract('month', Venda.data_hora) == hoje.month)\
                .filter(db.extract('year', Venda.data_hora) == hoje.year)\
                .all()


            total_consumido = sum(
                item.quantidade * item.valor_unitario
                for venda in vendas_mes for item in venda.itens
            )

            total_nova_venda = sum(item['quantidade'] * item['valor_unitario'] for item in carrinho)

            if total_consumido + total_nova_venda > LIMITE_MENSAL:
                return render_template(
                    'vendas/finalizar_venda.html',
                    funcionarios=funcionarios,
                    carrinho=carrinho,
                    consumo_funcionario={
                        "nome": funcionario.nome,
                        "consumido": total_consumido,
                        "limite": LIMITE_MENSAL
                    }
                )

        # ✅ Criação da venda
        nova_venda = Venda(
            data_hora=datetime.now(),
            cliente_tipo=cliente_tipo,
            forma_pagamento=forma_pagamento,
            funcionario_id=funcionario_id
        )
        db.session.add(nova_venda)
        db.session.flush()

        # ✅ Criação dos itens da venda e baixa no estoque
        for item in carrinho:
            produto = Produto.query.get(item['produto_id'])
            if produto:
                produto.quantidade -= item['quantidade']

                item_venda = ItemVenda(
                    venda_id=nova_venda.id,
                    produto_id=produto.id,
                    quantidade=item['quantidade'],
                    valor_unitario=item['valor_unitario']
                )
                db.session.add(item_venda)

        db.session.commit()
        session.pop('carrinho', None)
        return redirect(url_for('main.venda_sucesso'))

    # GET — Exibe tela normalmente e mostra consumo do funcionário selecionado
    funcionario_id = request.args.get('funcionario_id')

    if funcionario_id:
        funcionario = Funcionario.query.get(funcionario_id)
        hoje = datetime.now()

        vendas_mes = Venda.query.filter_by(funcionario_id=funcionario.id, quitado=False)\
                .filter(db.extract('month', Venda.data_hora) == hoje.month)\
                .filter(db.extract('year', Venda.data_hora) == hoje.year)\
                .all()

        total_consumido = sum(
            item.quantidade * item.valor_unitario
            for venda in vendas_mes for item in venda.itens
        )

        consumo_funcionario = {
            "nome": funcionario.nome,
            "consumido": total_consumido,
            "limite": LIMITE_MENSAL
        }

    return render_template(
        'vendas/finalizar_venda.html',
        funcionarios=funcionarios,
        carrinho=carrinho,
        consumo_funcionario=consumo_funcionario
    )


# -------------------- RELATORIOS --------------------

from flask import make_response, render_template, request, redirect, url_for
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.models import Funcionario, Venda, ItemVenda, Produto  # certifique-se que esses estão importados

@main.route('/funcionarios/<int:funcionario_id>/relatorio_pdf')
def gerar_relatorio_funcionario(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)

    # Pega mês/ano da query ou do mês atual
    mes = int(request.args.get('mes', datetime.now().month))
    ano = int(request.args.get('ano', datetime.now().year))

    # Carrega vendas com os itens e produtos
    vendas = Venda.query.options(
        joinedload(Venda.itens).joinedload(ItemVenda.produto)
    ).filter_by(funcionario_id=funcionario.id)\
     .filter(db.extract('month', Venda.data_hora) == mes)\
     .filter(db.extract('year', Venda.data_hora) == ano)\
     .all()

    # Calcula total do mês
    total_mes = 0
    for venda in vendas:
        for item in venda.itens:
            total_mes += item.quantidade * item.valor_unitario

    # Gera o HTML com os dados
    html = render_template(
        'funcionarios/relatorio_pdf.html',
        funcionario=funcionario,
        vendas=vendas,
        mes=mes,
        ano=ano,
        hoje=datetime.now(),
        total_mes=total_mes
    )

    # Converte para PDF
    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{funcionario.nome}_{mes}_{ano}.pdf'
    return response

@main.route('/funcionarios/<int:funcionario_id>/selecionar_periodo', methods=['GET', 'POST'])
def selecionar_periodo(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)

    if request.method == 'POST':
        mes = request.form['mes']
        ano = request.form['ano']
        return redirect(url_for('main.gerar_relatorio_funcionario', funcionario_id=funcionario_id, mes=mes, ano=ano))

    return render_template(
        'funcionarios/selecionar_periodo.html',
        funcionario=funcionario,
        now=datetime.now  # Passa a função para usar no template
    )

#RELATÓRIO RECEITAS PDF

from flask import request
from sqlalchemy import func
from collections import defaultdict
from datetime import datetime, timedelta

@main.route('/relatorios/fechamento', methods=['GET'])
def relatorio_fechamento():
    hoje = datetime.now().date()
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    formas_selecionadas = request.args.getlist('formas_pagamento')

    vendas = []
    totais_pagamento = defaultdict(float)
    total_geral = 0.0
    produtos_vendidos = defaultdict(int)
    dados_filtrados = False
    
    # Só filtra se o formulário tiver sido enviado
    if data_inicio and data_fim:
        dados_filtrados = True
        data_inicio_dt = datetime.strptime(data_inicio, '%d-%m-%Y')
        data_fim_dt = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

    
        # Puxa todas as vendas no período
        query = Venda.query.filter(Venda.data_hora >= data_inicio_dt, Venda.data_hora < data_fim_dt)


        # Filtra por forma de pagamento se necessário
        if formas_selecionadas:
            condicoes = []
    
            # Inclui vendas de funcionários se "Funcionário" estiver nas selecionadas
            if "Funcionário" in formas_selecionadas:
                condicoes.append(Venda.cliente_tipo == 'Funcionário')
            
            # Inclui cada forma de pagamento externa (Pix, Dinheiro, Cartão de Crédito/Débito)
            formas_externas = [f for f in formas_selecionadas if f != "Funcionário"]
            if formas_externas:
                condicoes.append(
                    db.and_(
                        Venda.cliente_tipo == 'Externo',
                        Venda.forma_pagamento.in_(formas_externas)
                    )
                )
            # Aplica os filtros combinados
            if condicoes:
                query = query.filter(db.or_(*condicoes))
                 
        vendas = query.all()

        # Soma produtos e pagamentos
        for venda in vendas:
            total_venda = 0
            for item in venda.itens:
                subtotal = item.quantidade * item.valor_unitario
                total_venda += subtotal
                produtos_vendidos[item.produto.nome] += item.quantidade

            forma = venda.forma_pagamento if venda.cliente_tipo == "Externo" else "Funcionário"
            totais_pagamento[forma] += total_venda
            total_geral += total_venda

    return render_template(
        'relatorios/fechamento.html',
        vendas=vendas,
        total_geral=total_geral,
        totais_pagamento=totais_pagamento,
        produtos_vendidos=produtos_vendidos,
        data_inicio=data_inicio or hoje.strftime('%d-%m-%Y'),
        data_fim=data_fim or hoje.strftime('%d-%m-%Y'),
        now=datetime.now,
        formas_selecionadas=formas_selecionadas,
        dados_filtrados=dados_filtrados
    )
    

#RELATÓRIO RECEITAS EXCEL

@main.route('/relatorios/fechamento/excel')
def exportar_fechamento_excel():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    formas_selecionadas = request.args.getlist('formas_pagamento')

    if not data_inicio or not data_fim:
        flash("Selecione um período para exportar o relatório.", "warning")
        return redirect(url_for('main.relatorio_fechamento'))

    inicio = datetime.strptime(data_inicio, '%d-%m-%Y')
    fim = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

    # Consulta as vendas no intervalo
    query = Venda.query.filter(Venda.data_hora >= inicio, Venda.data_hora < fim)

    if formas_selecionadas:
        condicoes = []
        if "Funcionário" in formas_selecionadas:
            condicoes.append(Venda.cliente_tipo == "Funcionário")
        formas_externas = [f for f in formas_selecionadas if f != "Funcionário"]
        if formas_externas:
            condicoes.append(
                db.and_(
                    Venda.cliente_tipo == "Externo",
                    Venda.forma_pagamento.in_(formas_externas)
                )
            )
        if condicoes:
            query = query.filter(db.or_(*condicoes))

    vendas = query.all()

    # Totais
    produtos_vendidos = defaultdict(int)
    totais_pagamento = defaultdict(float)
    total_geral = 0.0

    for venda in vendas:
        total_venda = 0
        for item in venda.itens:
            subtotal = item.quantidade * item.valor_unitario
            produtos_vendidos[item.produto.nome] += item.quantidade
            total_venda += subtotal

        forma = venda.forma_pagamento if venda.cliente_tipo == "Externo" else "Funcionário"
        totais_pagamento[forma] += total_venda
        total_geral += total_venda

    # Dados para o Excel
    linhas = []

    linhas.append({"Categoria": "Produtos Vendidos"})
    for nome, qtd in produtos_vendidos.items():
        linhas.append({"Item": nome, "Quantidade": qtd})

    linhas.append({})  # linha em branco

    linhas.append({"Categoria": "Totais por Forma de Pagamento"})
    for forma, total in totais_pagamento.items():
        linhas.append({"Forma de Pagamento": forma, "Valor (R$)": f"{total:.2f}".replace('.', ',')})

    linhas.append({})  # linha em branco
    linhas.append({"Total Geral (R$)": f"{total_geral:.2f}".replace('.', ',')})

    # Geração do arquivo
    df = pd.DataFrame(linhas)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Receitas')

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'receitas_{data_inicio}_a_{data_fim}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    

# RELATORIO DESPESAS   

@main.route('/relatorios/despesas')
def relatorio_despesas():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    # Garantir que as variáveis existem sempre
    produtos = []
    total_despesas = 0

    if data_inicio and data_fim:
        inicio = datetime.strptime(data_inicio, '%d-%m-%Y')
        fim = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

        produtos = Produto.query.filter(
            Produto.data_compra >= inicio,
            Produto.data_compra < fim
        ).all()

        total_despesas = sum(p.valor_compra for p in produtos if p.valor_compra)

    return render_template(
        'relatorios/despesas.html',
        produtos=produtos,
        total_despesas=total_despesas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        now=datetime.now 
    )


#RELATORIO LUCRO

@main.route('/relatorios/lucro')
def relatorio_lucro():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    total_receita = 0
    total_despesas = 0
    lucro = None

    if data_inicio and data_fim:
        inicio = datetime.strptime(data_inicio, '%d-%m-%Y')
        fim = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

        # Calcula RECEITA: soma de todas as vendas no período
        vendas = Venda.query.filter(Venda.data_hora >= inicio, Venda.data_hora < fim).all()
        total_receita = sum(Decimal(item.quantidade) * Decimal(item.valor_unitario)
                    for venda in vendas
                    for item in venda.itens)

        # Calcula DESPESAS: soma de todos os valores de compra dos produtos no período
        produtos = Produto.query.filter(Produto.data_compra >= inicio, Produto.data_compra < fim).all()
        total_despesas = sum(p.valor_compra for p in produtos if p.valor_compra)

        lucro = Decimal(total_receita) - total_despesas

    return render_template(
        'relatorios/lucro.html',
        receitas=total_receita,
        despesas=total_despesas,
        lucro=lucro,
        data_inicio=data_inicio,
        data_fim=data_fim,
        now=datetime.now
    )




#PDF DO RELATÓRIO RECEITA

from xhtml2pdf import pisa
from io import BytesIO
from flask import make_response

@main.route('/relatorios/fechamento/pdf')
def exportar_pdf_fechamento():
    hoje = datetime.now().date()
    data_inicio = request.args.get('data_inicio', hoje.strftime('%d-%m-%Y'))
    data_fim = request.args.get('data_fim', hoje.strftime('%d-%m-%Y'))
    formas_selecionadas = request.args.getlist('formas_pagamento')  # Recebe múltiplos valores

    data_inicio_dt = datetime.strptime(data_inicio, '%d-%m-%Y')
    data_fim_dt = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

    # Vendas no intervalo
    query = Venda.query.filter(Venda.data_hora >= data_inicio_dt, Venda.data_hora < data_fim_dt)

    # ✅ Aplica filtro por forma de pagamento, se houver seleção
    if formas_selecionadas:
        condicoes = []

        if "Funcionário" in formas_selecionadas:
            condicoes.append(Venda.cliente_tipo == "Funcionário")

        formas_externas = [f for f in formas_selecionadas if f != "Funcionário"]
        if formas_externas:
            condicoes.append(
                db.and_(
                    Venda.cliente_tipo == "Externo",
                    Venda.forma_pagamento.in_(formas_externas)
                )
            )

        if condicoes:
            query = query.filter(db.or_(*condicoes))

    vendas = query.all()

    # Totais por forma de pagamento
    totais_pagamento = defaultdict(float)
    total_geral = 0.0
    produtos_vendidos = defaultdict(int)

    for venda in vendas:
        total_venda = 0
        for item in venda.itens:
            subtotal = item.quantidade * item.valor_unitario
            total_venda += subtotal
            produtos_vendidos[item.produto.nome] += item.quantidade

        forma = venda.forma_pagamento if venda.cliente_tipo == "Externo" else "Funcionário"
        totais_pagamento[forma] += total_venda
        total_geral += total_venda

    # Gera o HTML do relatório PDF
    html = render_template(
        'relatorios/fechamento_pdf.html',
        data_inicio=data_inicio,
        data_fim=data_fim,
        produtos_vendidos=produtos_vendidos,
        totais_pagamento=totais_pagamento,
        total_geral=total_geral,
        logo_path=logo_path
    )

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=fechamento_{data_inicio}_a_{data_fim}.pdf'
    return response

#RELATÓRIO DESPESAS PDF


@main.route('/relatorios/despesas/pdf')
def exportar_despesas_pdf():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if not data_inicio or not data_fim:
        flash("Selecione um período para exportar o relatório.", "warning")
        return redirect(url_for('main.relatorio_despesas'))

    inicio = datetime.strptime(data_inicio, '%d-%m-%Y')
    fim = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

    produtos = Produto.query.filter(
        Produto.data_compra >= inicio,
        Produto.data_compra < fim
    ).all()

    total_despesas = sum(p.valor_compra for p in produtos if p.valor_compra)

    html = render_template(
        'relatorios/despesas_pdf.html',
        produtos=produtos,
        total_despesas=total_despesas,
        data_inicio=data_inicio,
        data_fim=data_fim,
        logo_path=logo_path
    )

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=despesas_{data_inicio}_a_{data_fim}.pdf'
    return response

#RELATÓRIO DESPESAS EXCEL

import pandas as pd

@main.route('/relatorios/despesas/excel')
def exportar_despesas_excel():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if not data_inicio or not data_fim:
        flash("Selecione um período para exportar o relatório.", "warning")
        return redirect(url_for('main.relatorio_despesas'))

    inicio = datetime.strptime(data_inicio, '%d-%m-%Y')
    fim = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

    produtos = Produto.query.filter(
        Produto.data_compra >= inicio,
        Produto.data_compra < fim
    ).all()

    dados = [{
        'Produto': p.nome,
        'Data da Compra': p.data_compra.strftime('%d/%m/%Y') if p.data_compra else '',
        'Valor da Compra (R$)': f"{p.valor_compra:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".") if p.valor_compra else '',
        'Fornecedor': p.fornecedor or ''
    } for p in produtos]

    df = pd.DataFrame(dados)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Despesas')

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=despesas_{data_inicio}_a_{data_fim}.xlsx'
    return response

# RELATÓRIO LUCRO PDF

@main.route('/relatorios/lucro/pdf')
def exportar_lucro_pdf():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    inicio = datetime.strptime(data_inicio, '%d-%m-%Y')
    fim = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

    vendas = Venda.query.filter(Venda.data_hora >= inicio, Venda.data_hora < fim).all()
    produtos = Produto.query.filter(Produto.data_compra >= inicio, Produto.data_compra < fim).all()

    receita_total = sum(Decimal(item.quantidade) * Decimal(item.valor_unitario) for venda in vendas for item in venda.itens)
    despesa_total = sum(Decimal(p.valor_compra) for p in produtos if p.valor_compra)
    lucro = receita_total - despesa_total

    html = render_template('relatorios/lucro_pdf.html',
        data_inicio=data_inicio,
        data_fim=data_fim,
        receita_total=receita_total,
        despesa_total=despesa_total,
        lucro=lucro,
        logo_path=logo_path
    )

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=lucro_{data_inicio}_a_{data_fim}.pdf'
    return response


#RELATÓRIO LUCRO EXCEL

@main.route('/relatorios/lucro/excel')
def exportar_lucro_excel():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    inicio = datetime.strptime(data_inicio, '%d-%m-%Y')
    fim = datetime.strptime(data_fim, '%d-%m-%Y') + timedelta(days=1)

    vendas = Venda.query.filter(Venda.data_hora >= inicio, Venda.data_hora < fim).all()
    produtos = Produto.query.filter(Produto.data_compra >= inicio, Produto.data_compra < fim).all()

    receita_total = Decimal(sum(item.quantidade * item.valor_unitario for venda in vendas for item in venda.itens))
    despesa_total = sum(p.valor_compra for p in produtos if p.valor_compra)
    lucro = Decimal(receita_total) - despesa_total

    df = pd.DataFrame([{
        'Período': f'{data_inicio} a {data_fim}',
        'Receita (R$)': f"{receita_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
        'Despesa (R$)': f"{despesa_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
        'Lucro (R$)': f"{lucro:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    }])


    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lucro')

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'lucro_{data_inicio}_a_{data_fim}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# -------------------- PAGAMENTO --------------------

@main.route('/funcionarios/<int:funcionario_id>/quitar_mes')
def quitar_mes_funcionario(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)

    # Data de referência: mês anterior
    hoje = datetime.now()
    mes_anterior = hoje - relativedelta(months=1)
    mes = mes_anterior.month
    ano = mes_anterior.year

    # Verifica se já foi quitado
    quitado = QuitacaoMensal.query.filter_by(
        funcionario_id=funcionario.id,
        mes=mes,
        ano=ano
    ).first()

    if quitado:
        flash(f"O mês {mes:02}/{ano} já está quitado para {funcionario.nome}.", "info")
    else:
        # Marca como quitado
        nova_quitacao = QuitacaoMensal(
            funcionario_id=funcionario.id,
            mes=mes,
            ano=ano,
            data_quitacao=datetime.now()
        )
        db.session.add(nova_quitacao)
        db.session.commit()
        flash(f'Mês {mes:02}/{ano} quitado para {funcionario.nome}!', 'success')

    return redirect(url_for('main.listar_funcionarios'))