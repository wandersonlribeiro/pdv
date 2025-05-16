from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.fields import DateField, DecimalField

# ----------- ProdutoForm -----------
class ProdutoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    tipo = StringField('Tipo', validators=[DataRequired(), Length(max=50)])
    data_compra = DateField('Data da Compra', format='%Y-%m-%d', validators=[Optional()])
    valor_compra = DecimalField('Valor da Compra (R$)', places=2, validators=[Optional()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired()])
    valor_unitario = FloatField('Valor Unitário (R$)', validators=[DataRequired()])
    validade = DateField('Validade', format='%Y-%m-%d', validators=[DataRequired()])
    fornecedor = StringField('Fornecedor')
    submit = SubmitField('Cadastrar Produto')

# ----------- FuncionarioForm -----------
class FuncionarioForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    cargo = StringField('Cargo', validators=[DataRequired(), Length(max=50)])
    telefone = StringField('Telefone', validators=[Length(max=20)])
    submit = SubmitField('Salvar')
