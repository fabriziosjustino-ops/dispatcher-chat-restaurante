# dispatcher-chat-restaurante

Roteador de perguntas em **linguagem natural** (português) para um chat de
análise de dados: entende "como foi o faturamento do shopping norte essa
semana?" sem exigir formulário/filtro técnico, decide qual análise aplicar,
resolve período e loja mencionados, e sabe lidar com **perguntas de
acompanhamento** ("e ontem?") usando o contexto da conversa.

Extraído e generalizado de um módulo de produção da **Mafê**, assistente de
dados por IA para redes de restaurantes, hoje em uso por clientes reais. As
intenções, lojas e handlers aqui são **de exemplo** — no sistema original
existem ~30 intenções reais e handlers que consultam banco de verdade; este
repositório demonstra o **mecanismo de roteamento**, não a análise de dados
em si (que é específica de cada negócio).

## Por que não simplesmente perguntar tudo a um LLM?

Dá, e o sistema original também usa LLM — mas só nos dois pontos onde ele
realmente compensa o custo/latência/variância: **gerar a resposta final em
linguagem natural** e, quando necessário, **reescrever uma pergunta de
acompanhamento curta** usando o histórico da conversa. Entender "isso é uma
pergunta sobre faturamento, de qual loja, de qual período" é um problema de
classificação — resolvido aqui com correspondência de palavra-chave
(determinística, auditável, sem custo de API) com um reforço por
similaridade de token (tipo Jaccard) para pegar variações que não usam a
expressão exata.

```python
from dispatcher import ContextoConversa, processar_pergunta

contexto = ContextoConversa()
r = processar_pergunta("Como foi o faturamento do shopping norte essa semana?", contexto)
# {'status': 'ok', 'intencao': 'faturamento_periodo', 'lojas': ['shopping_norte'],
#  'periodo': 'esta semana', 'resposta': '...'}

r2 = processar_pergunta("E o cmv do produto principal?", contexto)
# herda 'shopping_norte' e 'esta semana' do turno anterior, sem precisar repetir
```

## Pergunta de acompanhamento "pronominal"

Quando a pergunta de acompanhamento não tem NENHUMA palavra-chave própria
("E ontem?"), não tem como herdar a intenção — é preciso reescrever o texto
primeiro. O dispatcher aceita um hook opcional `resolver_llm` pra isso:

```python
def resolver_llm(pergunta: str, historico: list[str]) -> str:
    # chamada de LLM real aqui, com o histórico da conversa no prompt
    ...

r3 = processar_pergunta("E ontem?", contexto, historico_textos=[...], resolver_llm=resolver_llm)
```

No sistema original esse passo é **estreito de propósito**: o LLM só
reescreve texto (nunca gera SQL, nunca lê dado), e qualquer reescrita
suspeita (vazia, ou muito maior que a pergunta original) é descartada em
favor da pergunta original — a mesma blindagem está implementada aqui em
`dispatcher/dispatcher.py`. `demo.py` simula esse hook com uma função local
bem simples, só pra mostrar o ponto de integração sem exigir nenhuma API key
pra rodar o repositório.

## Rodando o demo

```bash
python demo.py
```

Sem nenhuma dependência externa (só biblioteca padrão do Python).

## Estrutura

```
dispatcher/
  intents.py       # catálogo de intenções de exemplo (nome -> palavras-chave -> handler)
  deteccao.py       # detecção de loja, período e intenção (determinístico)
  handlers.py       # handlers de exemplo (resposta fixa — não consultam banco nenhum)
  dispatcher.py     # orquestração + contexto de conversa + hook de LLM opcional
demo.py              # conversa de exemplo, incluindo acompanhamento
```

## Licença

MIT — ver [LICENSE](LICENSE).
