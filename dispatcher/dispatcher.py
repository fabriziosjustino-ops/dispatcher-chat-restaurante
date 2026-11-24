"""Orquestração: recebe a pergunta em texto livre + o estado da conversa,
detecta intenção/loja/período, resolve pergunta de acompanhamento (herdando
entidades do turno anterior quando fizer sentido) e roteia pro handler certo.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

from .deteccao import detectar_intencao, detectar_lojas, detectar_periodo
from .intents import INTENTS
from .handlers import HANDLERS


@dataclass
class ContextoConversa:
    """Guarda só o que foi RESOLVIDO no último turno (loja(s) e período) —
    nunca o texto da resposta em si. Passado explicitamente a cada chamada
    (sem estado escondido global), pra ficar fácil de testar e de rodar
    várias conversas em paralelo."""
    ultima_loja: Optional[list] = None
    ultimo_periodo: Optional[tuple] = None


def processar_pergunta(
    pergunta: str,
    contexto: ContextoConversa,
    historico_textos: Optional[list[str]] = None,
    resolver_llm: Optional[Callable[[str, list[str]], str]] = None,
) -> dict:
    """Ponto único de entrada do dispatcher.

    `resolver_llm`: hook OPCIONAL (a demo roda sem ele). No sistema original,
    uma pergunta de acompanhamento curta ("e ontem?", "e a zona sul?") passa
    antes por uma chamada de LLM ESTREITA que só reescreve o TEXTO usando o
    histórico da conversa — nunca gera SQL, nunca lê dado — devolvendo uma
    pergunta autocontida ("como foi o faturamento de ontem na zona sul?").
    A blindagem abaixo (rejeitar reescrita vazia ou monstruosamente maior que
    o original) é a mesma usada em produção: qualquer coisa suspeita faz o
    dispatcher cair de volta pra pergunta original, nunca deixa uma reescrita
    ruim virar uma consulta errada silenciosa.

    Sem o hook (como no `demo.py`), o dispatcher ainda resolve a maioria dos
    casos comuns de acompanhamento de forma determinística: se a nova
    pergunta não menciona loja/período nenhum, herda do último turno
    resolvido."""
    pergunta_efetiva = pergunta
    if resolver_llm is not None and historico_textos:
        try:
            candidata = resolver_llm(pergunta, historico_textos).strip().strip('"')
            if candidata and len(candidata) <= len(pergunta) * 4 + 100:
                pergunta_efetiva = candidata
        except Exception:
            pass

    intencao = detectar_intencao(pergunta_efetiva)
    lojas = detectar_lojas(pergunta_efetiva)
    periodo = detectar_periodo(pergunta_efetiva)

    lojas_herdadas = lojas is None and contexto.ultima_loja is not None
    periodo_herdado = periodo is None and contexto.ultimo_periodo is not None
    if lojas is None:
        lojas = contexto.ultima_loja
    if periodo is None:
        periodo = contexto.ultimo_periodo

    if intencao is None:
        return {
            "status": "nao_entendi",
            "pergunta_recebida": pergunta,
            "pergunta_resolvida": pergunta_efetiva,
        }
    if lojas is None:
        return {"status": "falta_loja", "intencao": intencao, "pergunta_resolvida": pergunta_efetiva}

    contexto.ultima_loja = lojas
    contexto.ultimo_periodo = periodo

    handler = HANDLERS[INTENTS[intencao]["handler"]]
    resposta = handler(lojas=lojas, periodo=periodo)

    return {
        "status": "ok",
        "pergunta_recebida": pergunta,
        "pergunta_resolvida": pergunta_efetiva,
        "intencao": intencao,
        "lojas": lojas,
        "lojas_herdadas_do_contexto": lojas_herdadas,
        "periodo": periodo[2] if periodo else None,
        "periodo_herdado_do_contexto": periodo_herdado,
        "resposta": resposta,
    }
