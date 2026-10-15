"""Subnacional - Propostas 2021 a 2024 (origem: PREC-EXTRA-2021-2024.py)."""
from motores.base import (MARCO_INICIO_IPCA as FASE2, JUROS_MENSAL, Regra, meses_inteiros,
                          passo_correcao, passo_ipca_juros, passo_selic_simples,
                          var_ipca, var_ipca15, var_selic)


class Regra2021a2024(Regra):
    esfera = "Subnacional"
    nome = "Propostas 2021 a 2024"
    ano_ini, ano_fim = 2021, 2024
    descricao = ("Graça: IPCA-15 → fim da graça a 07/2025: SELIC simples (sem poupança) "
                 "→ a partir de 08/2025: IPCA + juros 0,1666% a.m.")

    def atualizar(self, p, j, d_ini, d_fim, graca, bases):
        t = d_ini
        while t < d_fim:
            if t < graca:
                next_t = min(d_fim, graca)
                p, j = passo_correcao(p, j, var_ipca15(bases, t, next_t))
            elif t < FASE2:
                next_t = min(d_fim, FASE2)
                p, j = passo_selic_simples(p, j, var_selic(bases, t, next_t))
            else:
                next_t = d_fim
                p, j = passo_ipca_juros(p, j, bases, t, next_t)
            t = next_t
        return p, j

    def classificar(self, data_ref, last_date, graca, bases):
        if data_ref <= graca:
            return "IPCA-15 (Graça)", var_ipca15(bases, last_date, data_ref), 0.0
        if data_ref <= FASE2:
            m = max(last_date, graca)
            return "SELIC SIMPLES", var_selic(bases, m, data_ref), 0.0
        m = max(last_date, max(FASE2, graca))
        return "IPCA + JUROS", var_ipca(bases, m, data_ref), meses_inteiros(m, data_ref) * JUROS_MENSAL
