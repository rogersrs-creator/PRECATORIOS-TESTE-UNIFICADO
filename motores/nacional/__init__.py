"""
Precatórios NACIONAIS (União) - modelos em desenvolvimento.

Para incluir um modelo nacional quando estiver pronto:
  1. Crie um arquivo aqui (ex.: p2025_2026.py) com uma classe que herda de motores.base.Regra,
     com esfera = "Nacional", a faixa de anos e os métodos atualizar() e classificar().
     Use os arquivos de motores/subnacional/ como modelo.
  2. Importe a classe abaixo e acrescente uma instância à lista REGRAS.
  3. Pronto: o app passa a oferecer esses anos na opção "Nacional".
"""
from motores.base import Regra


class NacionalEmDesenvolvimento(Regra):
    esfera = "Nacional"
    nome = "Precatórios nacionais"
    ano_ini, ano_fim = 1900, 2027
    descricao = "Modelo de cálculo dos precatórios nacionais ainda em desenvolvimento."
    disponivel = False


REGRAS = [
    NacionalEmDesenvolvimento(),
]
