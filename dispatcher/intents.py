"""Catálogo de intenções reconhecidas pelo dispatcher, no formato
nome_da_intencao -> conjunto de palavras/expressões-gatilho.

No sistema original (Mafê) esse catálogo tem ~30 intenções de verdade, cada
uma carregada de um YAML separado do código (pra poder editar os sinônimos
sem mexer em lógica). Aqui ficam só algumas intenções GENÉRICAS de exemplo,
pra manter o repositório auditável/rodável sem depender de taxonomia real de
cliente nenhum.

Cada handler (em `handlers.py`) é uma função de exemplo que devolve uma
resposta FICTÍCIA — o que importa pra esse repositório é o mecanismo de
roteamento, não o conteúdo da análise em si.
"""

INTENTS: dict[str, dict] = {
    "faturamento_periodo": {
        "palavras_chave": {
            "faturamento", "faturou", "vendeu", "receita", "quanto vendemos",
            "quanto faturamos", "total de vendas",
        },
        "handler": "faturamento_periodo",
    },
    "comparativo_lojas": {
        "palavras_chave": {
            "compara", "comparativo", "entre as lojas", "qual loja vendeu mais",
            "ranking de lojas", "qual unidade",
        },
        "handler": "comparativo_lojas",
    },
    "top_produtos": {
        "palavras_chave": {
            "mais vendido", "mais vendidos", "top produtos", "ranking de produtos",
            "produto que mais vendeu", "o que mais saiu",
        },
        "handler": "top_produtos",
    },
    "impacto_clima": {
        "palavras_chave": {
            "clima", "chuva", "tempo", "previsão do tempo", "vai chover",
            "impacto da chuva",
        },
        "handler": "impacto_clima",
    },
    "cmv_produto": {
        "palavras_chave": {
            "cmv", "custo da mercadoria", "margem", "custo do prato",
            "quanto custa produzir",
        },
        "handler": "cmv_produto",
    },
    "sazonalidade": {
        "palavras_chave": {
            "sazonalidade", "feriado", "época do ano", "data comemorativa",
        },
        "handler": "sazonalidade",
    },
}
