"""
Núcleo comum a todos os regimes de cálculo.

Contém:
  - busca de índices e funções de variação (iguais em todos os scripts originais);
  - a classe Regra, que cada regime implementa;
  - a esteira unificada com amortização proporcional (igual em todos os scripts).

O que muda entre os regimes fica SÓ nos métodos `atualizar` e `classificar` de cada Regra.
"""
from collections import namedtuple

import pandas as pd

# Bases de índices na ordem usada pelos scripts originais
Bases = namedtuple("Bases", ["ipca15", "poup", "selic", "ipca"])

JUROS_MENSAL = 0.001666666666            # 0,1666...% ao mês (2% a.a. simples)
MARCO_FIM_POUPANCA = pd.Timestamp("2021-12-01")   # início da SELIC (EC 113/2021)
MARCO_INICIO_IPCA = pd.Timestamp("2025-08-01")    # início de IPCA + juros (EC 136/2025)

COLUNAS_RELATORIO = [
    "ordem_pagamento", "data_pagamento", "Regra_Ativa", "IPCA_Selic_Aplicado", "Juros_Aplicado",
    "valor_principal_proposta", "juros_proposta", "Total_data_pagto",
    "Valor_Depositado", "Per_Prin_Pagto", "Per_Juros_Pagto",
    "Saldo_Principal", "Saldo_Juros", "Saldo_Total",
]


# ==============================================================================
# ÍNDICES
# ==============================================================================
def obter_n_indice(df_idx, data_alvo):
    data_alvo_padrao = data_alvo.replace(day=1)
    mascara = df_idx["data"] == data_alvo_padrao
    if not mascara.any():
        df_filtrado = df_idx[df_idx["data"] <= data_alvo_padrao]
        if df_filtrado.empty:
            return 0.0
        return df_filtrado.iloc[-1]["n_indice"]
    return df_idx.loc[mascara, "n_indice"].values[0]


def var_ipca15(bases, d_ini, d_fim):
    if d_ini >= d_fim:
        return 0.0
    idx_ini = obter_n_indice(bases.ipca15, d_ini)
    idx_fim = obter_n_indice(bases.ipca15, d_fim)
    if idx_ini == 0:
        return 0.0
    return (idx_fim / idx_ini) - 1.0


def var_poupanca(bases, d_ini, d_fim):
    if d_ini >= d_fim:
        return 0.0
    return (obter_n_indice(bases.poup, d_fim) - obter_n_indice(bases.poup, d_ini)) / 100.0


def var_selic(bases, d_ini, d_fim):
    if d_ini >= d_fim:
        return 0.0
    return obter_n_indice(bases.selic, d_fim) - obter_n_indice(bases.selic, d_ini)


def var_ipca(bases, d_ini, d_fim):
    if d_ini >= d_fim:
        return 0.0
    idx_ini = obter_n_indice(bases.ipca, d_ini)
    idx_fim = obter_n_indice(bases.ipca, d_fim)
    if idx_ini == 0:
        return 0.0
    return (idx_fim / idx_ini) - 1.0


def meses_inteiros(data_inicio, data_fim):
    if data_inicio >= data_fim:
        return 0
    return (data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month)


# Passos de atualização reutilizados pelos regimes ---------------------------
def passo_correcao(p, j, var):
    """Corrige principal e juros pelo mesmo índice, sem juros novos."""
    return p * (1 + var), j * (1 + var)


def passo_selic_simples(p, j, var):
    """SELIC simples: incide sobre (principal + juros) e é lançada nos juros."""
    return p, j + ((p + j) * var)


def passo_ipca_juros(p, j, bases, t, next_t):
    """IPCA no principal e nos juros + juros simples de 0,1666% a.m. sobre o principal corrigido."""
    var = var_ipca(bases, t, next_t)
    p_new = p * (1 + var)
    var_juros = meses_inteiros(t, next_t) * JUROS_MENSAL   # mesma ordem de operações do original
    j = j * (1 + var) + (p_new * var_juros)
    return p_new, j


# ==============================================================================
# CONTRATO DE UM REGIME
# ==============================================================================
class Regra:
    """
    Cada regime (faixa de anos de proposta + esfera) implementa:
      atualizar(p, j, d_ini, d_fim, graca, bases) -> (p, j)
          atualização sem pagamento entre duas datas;
      classificar(data_ref, last_date, graca, bases) -> (nome_fase, taxa_indice, taxa_juros)
          rótulo e taxas exibidas no relatório para a linha.
    """
    esfera = ""          # "Subnacional" ou "Nacional"
    nome = ""            # ex.: "Propostas 2018 a 2020"
    ano_ini = 0
    ano_fim = 0
    descricao = ""       # resumo das fases, mostrado na tela
    disponivel = True    # False = modelo ainda em desenvolvimento

    def atende(self, ano):
        return self.ano_ini <= ano <= self.ano_fim

    def atualizar(self, p, j, d_ini, d_fim, graca, bases):
        raise NotImplementedError

    def classificar(self, data_ref, last_date, graca, bases):
        raise NotImplementedError


# ==============================================================================
# ESTEIRA UNIFICADA COM AMORTIZAÇÃO PROPORCIONAL (igual em todos os scripts)
# ==============================================================================
def processar_esteira(regra, pagamentos, principal_inicial, juros_inicial,
                      data_inicial, graca, data_atual, bases):
    """
    pagamentos: DataFrame com 'ordem_pagamento', 'data_pagamento' (datetime) e 'Valor_Depositado'.
    """
    pagamentos = pagamentos.copy()
    pagamentos["data_pagamento"] = pd.to_datetime(pagamentos["data_pagamento"]).apply(
        lambda dt: dt.replace(day=1))
    pagamentos = pagamentos.sort_values("data_pagamento", kind="stable")

    historico = []
    current_p, current_j, last_date = principal_inicial, juros_inicial, data_inicial

    for _, row in pagamentos.iterrows():
        current_date = row["data_pagamento"]
        deposito = float(row["Valor_Depositado"])

        val_p, val_j = regra.atualizar(current_p, current_j, last_date, current_date, graca, bases)
        total = val_p + val_j
        fase, taxa_idx, taxa_jur = regra.classificar(current_date, last_date, graca, bases)

        perc_p = val_p / total if total > 0 else 0.0
        perc_j = val_j / total if total > 0 else 0.0
        abat_p, abat_j = perc_p * deposito, perc_j * deposito
        saldo_p, saldo_j = max(0.0, val_p - abat_p), max(0.0, val_j - abat_j)

        historico.append({
            "ordem_pagamento": int(row["ordem_pagamento"]),
            "data_pagamento": current_date.strftime("%m/%Y"),
            "Regra_Ativa": fase,
            "IPCA_Selic_Aplicado": taxa_idx,
            "Juros_Aplicado": taxa_jur,
            "valor_principal_proposta": val_p,
            "juros_proposta": val_j,
            "Total_data_pagto": total,
            "Valor_Depositado": deposito,
            "Per_Prin_Pagto": abat_p,
            "Per_Juros_Pagto": abat_j,
            "Saldo_Principal": saldo_p,
            "Saldo_Juros": saldo_j,
            "Saldo_Total": saldo_p + saldo_j,
        })
        current_p, current_j, last_date = saldo_p, saldo_j, current_date

    if last_date < data_atual:
        val_p, val_j = regra.atualizar(current_p, current_j, last_date, data_atual, graca, bases)
        _, taxa_idx, taxa_jur = regra.classificar(data_atual, last_date, graca, bases)
        historico.append({
            "ordem_pagamento": "FINAL",
            "data_pagamento": data_atual.strftime("%m/%Y"),
            "Regra_Ativa": "ENCERRAMENTO",
            "IPCA_Selic_Aplicado": taxa_idx,
            "Juros_Aplicado": taxa_jur,
            "valor_principal_proposta": val_p,
            "juros_proposta": val_j,
            "Total_data_pagto": val_p + val_j,
            "Valor_Depositado": 0.0,
            "Per_Prin_Pagto": 0.0,
            "Per_Juros_Pagto": 0.0,
            "Saldo_Principal": val_p,
            "Saldo_Juros": val_j,
            "Saldo_Total": val_p + val_j,
        })

    return pd.DataFrame(historico, columns=COLUNAS_RELATORIO)
