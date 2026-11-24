"""Handlers de EXEMPLO — cada um representaria, no sistema original, uma
consulta real ao banco (réplica da loja) + formatação de tabela/gráfico. Aqui
devolvem só um texto fixo, porque o que este repositório demonstra é o
MECANISMO DE ROTEAMENTO (entender a pergunta e chegar no handler certo), não
a análise de dados em si — essa parte é específica de cada negócio/cliente
real e não faz sentido genérica."""

from typing import Optional


def faturamento_periodo(lojas: list[str], periodo) -> str:
    rotulo = periodo[2] if periodo else "hoje"
    return f"[exemplo] Faturamento de {', '.join(lojas)} em '{rotulo}': consultaria o banco aqui."


def comparativo_lojas(lojas: list[str], periodo) -> str:
    rotulo = periodo[2] if periodo else "o período padrão"
    return f"[exemplo] Comparativo entre {', '.join(lojas)} em '{rotulo}': montaria a tabela comparativa aqui."


def top_produtos(lojas: list[str], periodo) -> str:
    rotulo = periodo[2] if periodo else "o período padrão"
    return f"[exemplo] Top produtos de {', '.join(lojas)} em '{rotulo}': listaria o ranking aqui."


def impacto_clima(lojas: list[str], periodo) -> str:
    return f"[exemplo] Impacto do clima em {', '.join(lojas)}: cruzaria previsão do tempo com histórico de vendas aqui."


def cmv_produto(lojas: list[str], periodo) -> str:
    return f"[exemplo] CMV por produto de {', '.join(lojas)}: calcularia ficha técnica x custo do insumo aqui."


def sazonalidade(lojas: list[str], periodo) -> str:
    return f"[exemplo] Sazonalidade de {', '.join(lojas)}: compararia feriados/datas especiais contra dias comuns aqui."


HANDLERS = {
    "faturamento_periodo": faturamento_periodo,
    "comparativo_lojas": comparativo_lojas,
    "top_produtos": top_produtos,
    "impacto_clima": impacto_clima,
    "cmv_produto": cmv_produto,
    "sazonalidade": sazonalidade,
}
