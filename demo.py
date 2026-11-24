"""Demo de uma conversa de várias perguntas, SEM precisar de API key nenhuma —
o hook de LLM pra resolver acompanhamento (`resolver_llm`) é opcional; aqui
ele é simulado por uma função local bem simples, só pra mostrar o PONTO DE
INTEGRAÇÃO sem depender de nenhum serviço externo.

Mostra três casos:

1. Pergunta completa — detecção de intenção + loja + período de uma vez.
2. Acompanhamento que ainda tem palavra-chave própria ("Qual o cmv...?",
   sem mencionar loja) — resolvido de forma 100% determinística, herdando
   loja/período do turno anterior.
3. Acompanhamento "pronominal", sem palavra-chave nenhuma ("E ontem?") — SEM
   o hook de LLM isso cai em "não entendi" (mostrado primeiro); COM um
   resolver (aqui, um stand-in bem simples) ele reescreve pro texto completo
   antes de rotear, do mesmo jeito que o sistema original faz com um LLM de
   verdade (ver README).
4. Pergunta fora do catálogo de intenções — devolve "nao_entendi" em vez de
   arriscar um palpite.

Rodar: `python demo.py`
"""

from dispatcher import ContextoConversa, processar_pergunta


def resolver_llm_simulado(pergunta: str, historico: list[str]) -> str:
    """Stand-in BEM simples pro hook de LLM — só pra demo rodar sem API key.
    Em produção isso é uma chamada de LLM real, com o histórico inteiro da
    conversa no prompt (ver README): 'E ontem?' + ['Como foi o faturamento
    do shopping norte essa semana?'] -> 'Como foi o faturamento de ontem no
    shopping norte?'."""
    gatilhos_acompanhamento = ("e ontem", "e hoje", "e essa semana", "e esse mês")
    if pergunta.strip().lower().startswith(gatilhos_acompanhamento) and historico:
        return f"{historico[-1].rstrip('?')}, mas {pergunta.strip().lower()}"
    return pergunta


def mostrar(pergunta: str, resultado: dict):
    print(f"> {pergunta}")
    status = resultado["status"]
    if status == "ok":
        marca = " (herdou loja do contexto)" if resultado["lojas_herdadas_do_contexto"] else ""
        marca += " (herdou período do contexto)" if resultado["periodo_herdado_do_contexto"] else ""
        if resultado["pergunta_resolvida"] != resultado["pergunta_recebida"]:
            print(f"  reescrita pro contexto: \"{resultado['pergunta_resolvida']}\"")
        print(f"  intenção: {resultado['intencao']}{marca}")
        print(f"  lojas: {resultado['lojas']}  |  período: {resultado['periodo']}")
        print(f"  resposta: {resultado['resposta']}")
    elif status == "falta_loja":
        print(f"  intenção reconhecida ({resultado['intencao']}), mas falta saber de qual loja.")
    else:
        print("  não entendi essa pergunta.")
    print()


def main():
    historico: list[str] = []

    print("=== 1) Pergunta completa ===")
    contexto = ContextoConversa()
    p1 = "Como foi o faturamento do shopping norte essa semana?"
    r1 = processar_pergunta(p1, contexto)
    mostrar(p1, r1)
    historico.append(p1)

    print("=== 2) Acompanhamento com palavra-chave própria (resolve sem LLM) ===")
    p2 = "E o cmv do produto principal?"
    r2 = processar_pergunta(p2, contexto)
    mostrar(p2, r2)
    historico.append(p2)

    print("=== 3) Acompanhamento 'pronominal', sem palavra-chave — SEM hook de LLM ===")
    p3 = "E ontem?"
    r3 = processar_pergunta(p3, contexto)
    mostrar(p3, r3)

    print("=== 3b) o MESMO acompanhamento, agora COM o hook (stand-in local) ===")
    r3b = processar_pergunta(p3, contexto, historico_textos=historico, resolver_llm=resolver_llm_simulado)
    mostrar(p3, r3b)

    print("=== 4) Fora do catálogo de intenções ===")
    p4 = "Qual é a capital da Bulgária?"
    r4 = processar_pergunta(p4, contexto)
    mostrar(p4, r4)


if __name__ == "__main__":
    main()
