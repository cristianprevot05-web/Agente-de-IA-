import streamlit as st
import openai
import json
import os
import requests
from fuzzywuzzy import fuzz

# ================= ⚙️ CONFIGURAÇÕES MESTRES =================
LOGO_FILE = "WhatsApp Image 2026-02-07 at 01.07.55.jpeg" 
JSON_FILE = "cerebro_netflex.json"

st.set_page_config(
    page_title="Sofia v2 | Netflex Intelligence", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ================= 🔐 CREDENCIAIS IXC =================
LOOKER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3NzA0MjkzNDQsImlzcyI6Il8iLCJuYmYiOjE3NzA0MjkzNDQsImlkIjoiMTg2IiwiY2xhc3MiOiJ1c3VhcmlvIiwidHlwZSI6eyJtb2R1bGUiOiJxdWVyeS1idWlsZGVyIiwidXJsUm91dGUiOiIvYXV0aGVudGljYXRpb24vcXVlcnktYnVpbGRlci9nZW5lcmF0ZS10b2tlbnMiLCJ1cmxBY3Rpb25Sb3V0ZSI6IkF1dGguZ2VuZXJhdGVUb2tlbnMiLCJ1cmxHcm91cFJvdXRlIjoiYXV0aGVudGljYXRpb24ifX0.o4Rsrv1Ez8QHJQNtKv1647uLbTVUvAj26TZdnkNoqwEw0q9ztt72q3mvrEyvajRpjwul99HO3pi09SkZLA5MLw" 
LOOKER_URL = "https://ixc.netflexisp.com.br/webservice/v1/suporte_atendimento" 

# ================= 💎 UI DESIGN (DIAMOND RECOVERY) =================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;400;600;800&display=swap');
    
    :root {
        --netflex-orange: #FF6B00;
        --neon-cyan: #00f2ff;
        --deep-bg: #05070a;
        --danger-red: #ff4b4b;
    }

    .stApp {
        background-color: var(--deep-bg);
        background-image: radial-gradient(circle at 50% 0%, #1a2c4e 0%, #05070a 70%);
        font-family: 'Outfit', sans-serif;
    }

    /* BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid rgba(0, 242, 255, 0.1);
        min-width: 290px !important;
    }

    /* BOTÃO LIMPAR CUSTOMIZADO */
    div.stButton > button:first-child {
        background-color: transparent !important;
        color: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid rgba(255, 75, 75, 0.3) !important;
        border-radius: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 0.7rem !important;
        width: 100% !important;
        transition: 0.4s ease;
    }

    div.stButton > button:first-child:hover {
        border-color: var(--danger-red) !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.2) !important;
        transform: translateY(-2px);
    }

    /* BALÕES DE CHAT */
    .stChatMessage { background: transparent !important; padding: 6px 0; }
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px;
        padding: 12px 18px;
        font-size: 0.92rem;
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, var(--neon-cyan));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    header, footer { visibility: hidden; }
    hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, #1f293a, transparent); margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# ================= 🧠 LÓGICA DE IDENTIFICAÇÃO DE PERGUNTA =================

# 1. TABELA DA VERDADE (SENHAS EXTRAÍDAS DOS SEUS PDFS)
TABELA_VERDADE = {
    "2flex": """
| MODELO | USUÁRIO | SENHA |
| :--- | :--- | :--- |
| **ONT 2FLEX 1200AC** | superadmin | super1234 |
| **ONT 2FLEX FG300M** | admin | 1234 |
""",
    "zte": "| MODELO | USUÁRIO | SENHA |\n| :--- | :--- | :--- |\n| **ZTE Multilaser** | multipro | multipro |",
    "greatek": "| MODELO | USUÁRIO | SENHA |\n| :--- | :--- | :--- |\n| **Padrão Greatek** | super | super123 |",
    "tp-link": "| MODELO | USUÁRIO | SENHA |\n| :--- | :--- | :--- |\n| **Antigos / Padrão** | admin | admin |",
    "padrao_netflex": """
### 🔐 SENHAS PADRÃO NETFLEX (PÓS-CONFIGURAÇÃO)
1. `netflex@123` (minúsculo)
2. `Netflex@123` (N maiúsculo)
3. `40638488` (Apenas números)
4. **PPPOE:** Tente o usuário PPPOE com a 1ª letra maiúscula e @ no fim (ex: `42673Henrique@`).
"""
}

def consultar_looker():
    try:
        headers = {'Authorization': f'Bearer {LOOKER_TOKEN}', 'Content-Type': 'application/json', 'ixcsoft': 'listar'}
        payload = {"qtype": "suporte_atendimento.id", "query": "0", "oper": ">", "page": "1", "rp": "5", "sortname": "suporte_atendimento.id", "sortorder": "desc"}
        response = requests.post(LOOKER_URL, headers=headers, json=payload, timeout=4)
        return response.json() if response.status_code == 200 else None
    except: return None

def busca_inteligente(pergunta, base_json):
    p_low = pergunta.lower()
    contexto_final = ""
    img_final = None
    nome_final = None

    # IDENTIFICAÇÃO PRIORITÁRIA (SENHAS)
    if "senha" in p_low or "acesso" in p_low or "login" in p_low:
        contexto_final += TABELA_VERDADE["padrao_netflex"] + "

"
        for marca, dados in TABELA_VERDADE.items():
            if marca in p_low:
                contexto_final += f"--- [DADOS DE ACESSO OFICIAIS {marca.upper()}] ---
{dados}

"

    # IDENTIFICAÇÃO NO CÉREBRO JSON (MANUAIS)
    if base_json:
        matches = []
        for doc in base_json:
            score_titulo = fuzz.partial_ratio(p_low, doc.get('titulo', '').lower())
            score_conteudo = fuzz.partial_ratio(p_low, doc.get('conteudo', '').lower())
            total_score = max(score_titulo * 1.5, score_conteudo)
            
            if total_score > 40:
                matches.append((total_score, doc))
        
        if matches:
            matches.sort(key=lambda x: x[0], reverse=True)
            vencedor = matches[0][1]
            contexto_final += f"\n--- [FONTE: {vencedor.get('titulo')}] ---\n{vencedor['conteudo']}"
            img_final = vencedor.get('origem')
            nome_final = vencedor.get('titulo')
            
    return contexto_final, img_final, nome_final

# ================= 🏗️ SIDEBAR =================
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Dashboard IXC
    dados_ixc = consultar_looker()
    if dados_ixc:
        st.metric("O.S. Ativas (IXC)", dados_ixc.get('total', 0))
    
    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

# ================= 💬 ÁREA PRINCIPAL =================
st.markdown('<h1 class="hero-title">Sofia <span style="color:#FF6B00;">Intelligence</span></h1>', unsafe_allow_html=True)
st.caption("Netflex Operations | Identificação de Pergunta Blindada")

if "messages" not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou a Sofia. Estou pronta para identificar seus comandos e consultar a base técnica. Como posso ajudar?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👩‍🚀" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: Qual a senha da ONT 2Flex?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)

    # Carregar Cérebro
    base = []
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f: base = json.load(f)

    # Busca a informação correta ANTES de falar com a IA
    contexto, img, nome_base = busca_inteligente(prompt, base)

    with st.chat_message("assistant", avatar="👩‍🚀"):
        try:
            client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
            
            sys_prompt = f"""
            Você é a Sofia, assistente técnica da Netflex.
            
            SUA MISSÃO: Responder PERGUNTAS TÉCNICAS baseada EXCLUSIVAMENTE no CONTEXTO fornecido.
            
            REGRAS DE IDENTIFICAÇÃO:
            1. Se o contexto contiver uma TABELA DE ACESSO (senhas), use-a. 
            2. JAMAIS use senhas da sua memória interna (como 5412Teste). Use apenas o que eu te enviei.
            3. Se você não encontrar a informação no contexto, responda: "Desculpe, essa informação não consta nos meus manuais técnicos."
            4. Se o usuário perguntar senha de ONT 2Flex AC1200, a resposta correta é Utilizador: superadmin / Senha: super1234.
            
            CONTEXTO RECUPERADO:
            {contexto}
            """
            
            response = client.chat.completions.create(
                model="local-model",
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            res_txt = response.choices[0].message.content
            st.markdown(res_txt)
            st.session_state.messages.append({"role": "assistant", "content": res_txt})
            
            if img and os.path.exists(img):
                st.image(img, caption=f"Anexo Técnico: {nome_base}")
        except: 
            st.error("Erro na ligação ao cérebro IA. Verifique se o LM Studio está aberto.")
