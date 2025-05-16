# 🍔 PDV Lanchonete - Sistema de Ponto de Venda

Este é um sistema web simples de PDV (Ponto de Venda) criado para uso na lanchonete da minha empresa (APAE-RIO), desenvolvido com **Flask**. Foi pensado para atender situações específicas como controle de consumo por funcionário e pagamentos mensais.

---

## 🚀 Funcionalidades

- 📦 Cadastro, listagem e controle de produtos
- 👨‍💼 Cadastro de funcionários com controle de limite mensal
- 🧾 Registro e visualização de vendas
- 📊 Relatórios:
  - Consumo mensal do funcionário
  - Receitas
  - Despesas
  - Lucro
  - Fechamento por período
- 📁 Exportação para PDF e Excel
- 📆 Filtro por data com calendário moderno (Flatpickr)
- 💳 Suporte a múltiplas formas de pagamento

---

## 🛠 Tecnologias usadas

- Python 3
- Flask
- SQLAlchemy
- WTForms
- Bootstrap
- xhtml2pdf (para PDF)
- Flatpickr (Javascript para datas)

---

## 📦 Instalação

**1. Clone este repositório:**
git clone https://github.com/wandersonlribeiro/pdv.git

**2. Crie um ambiente virtual:**
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

**3. Insale as dependências:**
pip install -r requirements.txt

**4. Crie a pasta "instance":**
mkdir instance

**5. Inicialize o sistema de migrações, no terminal com o ambiente virtual ativado ((venv)), execute:**
flask db init

**6. Crie a primeira migração:**
flask db migrate -m "Criação inicial das tabelas"
** Isso gera um arquivo de migração em migrations/versions/ com os comandos SQL para criar as tabelas.**

**7. Aplicar a migração (criar as tabelas):**
flask db upgrade

**8. Rode a aplicação:**
flask run --host=0.0.0.0


