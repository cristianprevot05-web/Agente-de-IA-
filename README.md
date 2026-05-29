 Agente-de-IA-

A Sofia é um agente inteligente de operações desenvolvido em Python com Streamlit, projetado especificamente para atuar como assistente técnica integrada aos ecossistemas de provedores de internet (ISP). 

O sistema utiliza uma arquitetura robusta de RAG (Geração Aumentada por Recuperação) para mitigar alucinações e garantir precisão cirúrgica na entrega de credenciais de acesso e procedimentos internos.

> Funcionalidades Principais

> Identificação de Pergunta Blindada: Sistema de ponderação textual usando correspondência parcial via `fuzzywuzzy`. O título dos manuais e palavras-chave estruturadas têm prioridade máxima de identificação para evitar desvios da IA.
> Tabela da Verdade Estática: Proteção nativa hardcoded para credenciais sensíveis de fábrica (ex: ONTs 2Flex, ZTE, Greatek, TP-Link), impedindo o modelo de linguagem de inventar senhas aleatórias.
> Consulta Dinâmica ao Cérebro JSON: Varredura em tempo real em uma base de dados local (`cerebro_netflex.json`), permitindo anexar dinamicamente manuais operacionais e imagens técnicas diretamente no fluxo do chat.
> Integração com IXC Provider : Dashboard integrado na barra lateral exibindo métricas operacionais cruciais, como a contagem de Ordens de Serviço (O.S.) ativas em tempo real.
>Interface UI Customizada: Visual escuro e sofisticado de alta fidelidade construído sobre o ecossistema Streamlit através de injeção CSS nativa.

Para quem tem curiosidade das tecnologias utilizadas:

> Python 3.10
> Streamlit (Interface e Layout)
> OpenAI API / LM Studio (Engine local de inferência LLM com Temperatura 0.0)
> FuzzyWuzzy / Levenshtein Distance (Busca semântica e pareamento de strings)
> Requests (Consumo da API do WebService IXC)
> O arquivo de inteligência local (`cerebro_netflex.json`).
> Imagens operacionais e logos proprietários.
> Ambientes virtuais e chaves privadas.
