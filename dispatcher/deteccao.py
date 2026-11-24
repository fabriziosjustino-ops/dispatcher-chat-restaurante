"""Reconhecimento de entidades na pergunta em texto livre: qual(is) loja(s),
qual período, e (via `intents.py`) qual intenção.

Tudo aqui é DETERMINÍSTICO (sem chamada de LLM) — rápido, sem custo de API e
fácil de testar/depurar linha a linha. A ideia (do sistema original) é que só
o passo de GERAR a resposta final em linguagem natural usa um LLM; entender
"o que foi perguntado" é tratado como um problema de classificação simples,
que não precisa de um modelo de linguagem pra ser resolvido bem.
"""

import re
from datetime import date, timedelta

from .intents import INTENTS

# Lojas de EXEMPLO (fictícias) — no sistema original isso vem de configuração
# por cliente, cada loja com sua lista de apelidos (como o PDV é mencionado
# informalmente: "centro", "matriz", apelido popular do bairro etc.).
LOJAS_EXEMPLO: dict[str, set[str]] = {
    "centro": {"centro", "matriz", "loja do centro"},
    "shopping_norte": {"shopping norte", "shopping", "norte"},
    "zona_sul": {"zona sul", "zona-sul", "unidade sul"},
}

_NUMEROS_POR_EXTENSO = {
    2: "duas", 3: "três", 4: "quatro", 5: "cinco", 6: "seis",
    7: "sete", 8: "oito", 9: "nove", 10: "dez",
}


def detectar_lojas(pergunta: str, lojas_disponiveis: dict[str, set[str]] = LOJAS_EXEMPLO) -> list[str] | None:
    """Retorna a lista de ids de loja mencionados na pergunta, ou None se
    nenhuma loja foi mencionada (nesse caso quem chama decide o padrão: pedir
    pra especificar, ou assumir 'todas', dependendo do contexto)."""
    texto = pergunta.lower()
    mencionadas = [loja for loja, apelidos in lojas_disponiveis.items() if any(a in texto for a in apelidos)]
    if mencionadas:
        return mencionadas
    if _pede_todas_as_lojas(texto, n_lojas=len(lojas_disponiveis)):
        return list(lojas_disponiveis.keys())
    return None


def _pede_todas_as_lojas(texto: str, n_lojas: int) -> bool:
    """"todas as lojas" é óbvio — mas "das três lojas" ou "comparando as 3
    unidades" também precisam bater, mesmo com um número (por extenso ou
    dígito) no meio da frase, e mesmo que a pessoa diga 'unidades' em vez de
    'lojas'."""
    palavra_numero = _NUMEROS_POR_EXTENSO.get(n_lojas)
    gatilhos = [
        "todas as lojas", "as lojas", "das lojas", "todas as unidades",
        "as unidades", "das unidades", f"{n_lojas} lojas", f"{n_lojas} unidades",
    ]
    if palavra_numero:
        gatilhos += [f"{palavra_numero} lojas", f"{palavra_numero} unidades"]
    return any(g in texto for g in gatilhos)


def detectar_periodo(pergunta: str, hoje: date | None = None) -> tuple[date, date, str] | None:
    """Reconhece períodos relativos comuns em português falado. Retorna
    (data_inicio, data_fim, rótulo) ou None se nada foi reconhecido (quem
    chama decide o padrão, normalmente 'hoje')."""
    hoje = hoje or date.today()
    texto = pergunta.lower()

    if "ontem" in texto:
        d = hoje - timedelta(days=1)
        return d, d, "ontem"
    if "hoje" in texto:
        return hoje, hoje, "hoje"
    if re.search(r"\besta semana\b|\bessa semana\b", texto):
        inicio = hoje - timedelta(days=hoje.weekday())
        return inicio, hoje, "esta semana"
    if "semana passada" in texto:
        fim_semana_passada = hoje - timedelta(days=hoje.weekday() + 1)
        inicio_semana_passada = fim_semana_passada - timedelta(days=6)
        return inicio_semana_passada, fim_semana_passada, "semana passada"
    if re.search(r"\beste m[eê]s\b|\besse m[eê]s\b", texto):
        return hoje.replace(day=1), hoje, "este mês"
    if "mês passado" in texto or "mes passado" in texto:
        primeiro_dia_mes_atual = hoje.replace(day=1)
        ultimo_dia_mes_passado = primeiro_dia_mes_atual - timedelta(days=1)
        primeiro_dia_mes_passado = ultimo_dia_mes_passado.replace(day=1)
        return primeiro_dia_mes_passado, ultimo_dia_mes_passado, "mês passado"
    return None


_PALAVRA = re.compile(r"[a-zà-ú]+")


def _tokens(texto: str) -> set[str]:
    return set(_PALAVRA.findall(texto.lower()))


def pontuar_intencoes(pergunta: str) -> list[tuple[str, float]]:
    """Dá um score de 0 a 1 pra cada intenção do catálogo: combina (a) se
    alguma expressão-gatilho aparece literalmente na pergunta (peso maior,
    é o caso comum e mais confiável) com (b) similaridade por sobreposição
    de palavras (tipo Jaccard — pega perguntas que não usam a expressão
    exata mas usam palavras parecidas). Retorna ordenado do mais provável
    pro menos provável."""
    texto = pergunta.lower()
    tokens_pergunta = _tokens(texto)
    scores = []
    for nome, config in INTENTS.items():
        gatilhos = config["palavras_chave"]
        bateu_literal = any(gatilho in texto for gatilho in gatilhos)

        tokens_gatilhos = _tokens(" ".join(gatilhos))
        intersecao = tokens_pergunta & tokens_gatilhos
        uniao = tokens_pergunta | tokens_gatilhos
        jaccard = len(intersecao) / len(uniao) if uniao else 0.0

        score = (0.7 + 0.3 * jaccard) if bateu_literal else (0.3 * jaccard)
        scores.append((nome, round(score, 3)))
    return sorted(scores, key=lambda par: par[1], reverse=True)


def detectar_intencao(pergunta: str, limiar: float = 0.25) -> str | None:
    ranking = pontuar_intencoes(pergunta)
    if not ranking:
        return None
    melhor_nome, melhor_score = ranking[0]
    return melhor_nome if melhor_score >= limiar else None
