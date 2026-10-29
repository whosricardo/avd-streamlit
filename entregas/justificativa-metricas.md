# Justificativa das métricas — Dashboard 2

## Público e recorte

O painel foi pensado para jogadores e analistas interessados em entender como o
estado da partida aos 10 minutos se relaciona com o resultado final. As métricas
são descritivas: mostram associações observadas nas partidas Diamond/Master da
base e não provam que uma ação isolada cause a vitória.

## Métrica 1: taxa de vitória do time azul

- **Variável:** `blueWins`.
- **O que mede:** percentual das partidas do recorte vencidas pelo time azul.
- **Por que foi escolhida:** conecta todos os indicadores do início da partida ao
  desfecho final analisado no notebook.
- **Qual decisão pode apoiar:** comparar quais cenários aos 10 minutos aparecem
  com maior ou menor frequência nas vitórias azuis.
- **O que comunica:** se o recorte selecionado favorece mais o lado azul ou o
  vermelho em relação à base completa.

## Métrica 2: vantagem média de ouro

- **Variável:** `blueGoldDiff` (`blueTotalGold - redTotalGold`).
- **O que mede:** diferença média de ouro entre os times aos 10 minutos.
- **Por que foi escolhida:** ouro resume a capacidade econômica para comprar
  itens; a diferença compara os dois times diretamente e evita interpretar dois
  totais isolados.
- **Qual decisão pode apoiar:** avaliar se uma faixa de nível, primeiro abate ou
  vencedor está associada a vantagem ou desvantagem econômica precoce.
- **O que comunica:** valores positivos indicam vantagem azul; negativos,
  vantagem vermelha.

## Métrica 3: vantagem média de abates

- **Variáveis:** `blueKills` e `redKills`.
- **O que mede:** média de `blueKills - redKills` no recorte.
- **Por que foi escolhida:** representa o domínio de combate de forma relativa e
  complementa o indicador econômico.
- **Qual decisão pode apoiar:** verificar se o cenário filtrado envolve vantagem
  em confrontos ou se a diferença de ouro foi construída por outros meios.
- **O que comunica:** valores positivos indicam mais abates azuis; negativos,
  mais abates vermelhos.

## Métrica 4: participação azul nos objetivos

- **Variáveis:** dragões, arautos e torres destruídas de ambos os times.
- **O que mede:** parcela dos objetivos registrados no recorte conquistada pelo
  time azul.
- **Por que foi escolhida:** objetivos traduzem controle de mapa e progressão
  estratégica, uma dimensão diferente de ouro e abates.
- **Qual decisão pode apoiar:** comparar a conversão de vantagem em controle de
  mapa entre faixas de nível e resultados.
- **O que comunica:** 50% representa divisão equilibrada; valores acima ou abaixo
  disso mostram maior participação azul ou vermelha, respectivamente.

## Comparação e interação

Os deltas dos quatro cartões usam a base completa como referência. O gráfico de
faixa de nível funciona como filtro cruzado: ao clicar em uma barra, os KPIs e o
gráfico de controle de objetivos são recalculados apenas para aquela faixa. Os
filtros explícitos de vencedor, primeiro abate e nível médio são aplicados antes
dessa seleção.
