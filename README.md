# Atualização de Precatórios – App Streamlit (todas as propostas até 2027)

Reúne num só app os cálculos que antes eram feitos por 5 scripts locais:

| Esfera | Regime | Anos de proposta | Script de origem |
|---|---|---|---|
| Subnacional | Propostas até 2017 | até 2017 | `PREC-EXTRA-ATE-2017.py` |
| Subnacional | Propostas 2018 a 2020 | 2018–2020 | `PREC-EXTRA-2018-2020.py` |
| Subnacional | Propostas 2021 a 2024 | 2021–2024 | `PREC-EXTRA-2021-2024.py` |
| Subnacional | Propostas 2025 e 2026 | 2025–2026 | `PREC-EXTRA-2025-2026.py` |
| Subnacional | Proposta 2027 | 2027 | `gemini-code-...py` (ramo 2027) |
| Nacional | — | — | em desenvolvimento |

O usuário escolhe a **esfera** e o **ano da proposta**; o app seleciona o motor sozinho e mostra
na tela qual regime está sendo aplicado. Os motores foram conferidos contra os scripts
originais em 1.050 cenários aleatórios, com diferença zero.

## Estrutura

```
app.py                     # interface (esfera, ano, formulário, resultado, downloads)
fontes.py                  # leitura das bases (Google Sheets ou CSV local)
relatorio.py               # geração do Excel e do CSV
config.py                  # links das planilhas do Google Sheets
requirements.txt
motores/
├── __init__.py            # registro: escolhe o motor por (esfera, ano)
├── base.py                # índices, passos de atualização e esteira de amortização (comuns)
├── subnacional/
│   ├── __init__.py        # lista dos regimes subnacionais
│   ├── ate_2017.py
│   ├── p2018_2020.py
│   ├── p2021_2024.py
│   ├── p2025_2026.py
│   └── p2027.py
└── nacional/
    └── __init__.py        # espaço reservado para os modelos nacionais
dados/                     # CSVs de reserva (usados se um link do config.py estiver vazio)
.streamlit/config.toml
```

**As pastas `motores/`, `motores/subnacional/` e `motores/nacional/` são obrigatórias.**
Sem elas o app não abre.

## Planilha do período de graça (GRACA)

Todas as propostas usam **uma única** tabela de período de graça, com as colunas
`ANO_PROPOSTA;DATA_BASE_INICIAL_CALCULOS;FIM_PER_GRACA`.
O arquivo `dados/BASE-ANO-PROPOSTA-PERIODO-GRACA.csv` já reúne as propostas de 2012 a 2027
(junção dos antigos arquivos ATE-2020, 2021-ATE-2024, 2025-2026 e 2027). Importe esse arquivo na
planilha GRACA do Google Sheets, substituindo o conteúdo atual.
Para uma proposta nova (ex.: 2028), basta acrescentar a linha na planilha e criar o regime em `motores/`.
O app só oferece os anos que existem nessa planilha e avisa quais estão faltando.

## Como incluir os precatórios nacionais

1. Crie um arquivo em `motores/nacional/` (ex.: `p2025_2026.py`), copiando o regime subnacional
   mais parecido e ajustando o que muda nos métodos `atualizar()` e `classificar()`.
   Defina `esfera = "Nacional"` e a faixa `ano_ini`/`ano_fim`.
2. Em `motores/nacional/__init__.py`, importe a classe nova e coloque-a na lista `REGRAS`
   (removendo `NacionalEmDesenvolvimento` quando todos os anos estiverem cobertos).
3. Faça o commit. O app passa a liberar a opção "Nacional" automaticamente.

Se os nacionais usarem datas de graça diferentes, será preciso uma planilha de graça própria;
isso é um ajuste pequeno em `fontes.py` e `app.py`.

## Publicar

1. Crie um repositório novo no GitHub (ex.: `PRECATORIOS-CALCULO`).
2. Envie **todo** o conteúdo desta pasta mantendo as subpastas: arraste a pasta inteira para a
   tela de upload do GitHub ou use "Publish to GitHub" no VS Code.
3. Em share.streamlit.io: Create app → repositório novo → branch `main` → arquivo `app.py` → Deploy.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```
