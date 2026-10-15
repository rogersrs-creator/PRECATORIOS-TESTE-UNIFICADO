"""Subnacional - Proposta 2027 (origem: gemini-code-1784317105352.py, ramo ano_proposta == 2027)."""
from motores.base import (JUROS_MENSAL, Regra, meses_inteiros, passo_correcao, passo_ipca_juros,
                          var_ipca)


class Regra2027(Regra):
    esfera = "Subnacional"
    nome = "Proposta 2027"
    ano_ini, ano_fim = 2027, 2027
    descricao = "Graça: IPCA sem juros → após a graça: IPCA + juros 0,1666% a.m."

    def atualizar(self, p, j, d_ini, d_fim, graca, bases):
        t = d_ini
        while t < d_fim:
            if t < graca:
                next_t = min(d_fim, graca)
                p, j = passo_correcao(p, j, var_ipca(bases, t, next_t))
            else:
                next_t = d_fim
                p, j = passo_ipca_juros(p, j, bases, t, next_t)
            t = next_t
        return p, j

    def classificar(self, data_ref, last_date, graca, bases):
        if data_ref <= graca:
            return "IPCA (Graça)", var_ipca(bases, last_date, data_ref), 0.0
        m = max(last_date, graca)
        return "IPCA + JUROS", var_ipca(bases, m, data_ref), meses_inteiros(m, data_ref) * JUROS_MENSAL
