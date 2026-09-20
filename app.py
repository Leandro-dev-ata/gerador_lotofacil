import random
from collections import Counter
import streamlit as st
import requests
import qrcode
from io import BytesIO
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gerador Inteligente Lotofácil",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOMIZADO PARA ESTILIZAÇÃO ---
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .custom-card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
    }
    .number-badge {
        display: inline-block;
        width: 38px;
        height: 38px;
        line-height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        text-align: center;
        font-weight: bold;
        margin: 4px;
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    .game-badge {
        display: inline-block;
        width: 36px;
        height: 36px;
        line-height: 36px;
        border-radius: 50%;
        background-color: #334155;
        color: #e2e8f0;
        text-align: center;
        font-weight: 600;
        margin: 3px;
        font-size: 0.95rem;
        border: 1px solid #475569;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #8b5cf6, #d946ef);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        font-size: 1.1rem;
        font-weight: 700;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES UTILITÁRIAS ---
def gerar_qrcode(url):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def exportar_txt(lista_jogos):
    conteudo = "=== PALPITES GERADOS - LOTOFÁCIL ===\n\n"
    for i, jogo in enumerate(lista_jogos, 1):
        jogo_str = " - ".join(f"{num:02d}" for num in jogo)
        conteudo += f"Jogo {i:02d}: {jogo_str}\n"
    return conteudo.encode('utf-8')

def exportar_excel(lista_jogos):
    colunas = [f"Bola {i}" for i in range(1, 16)]
    df = pd.DataFrame(lista_jogos, columns=colunas)
    df.index = [f"Jogo {i+1}" for i in range(len(lista_jogos))]
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Jogos Lotofácil")
    return buffer.getvalue()

@st.cache_data(ttl=3600)
def carregar_dados_reais():
    url = "https://raw.githubusercontent.com/maickon/free-apiloterias/refs/heads/master/database/lotofacil/_todos.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            return [[int(num) for num in c["listaDezenas"]] for c in dados]
        return None
    except Exception:
        return None

historico_completo = carregar_dados_reais()

# --- BARRA LATERAL ---
st.sidebar.markdown("### ⚙️ Configurações")

if historico_completo:
    st.sidebar.success(f"✅ API Online: {len(historico_completo)} concursos")
else:
    st.sidebar.error("⚠️ Usando dados simulados")
    historico_completo = [random.sample(range(1, 26), 15) for _ in range(200)]

qtd_analise = st.sidebar.slider("Analisar concursos anteriores:", 10, min(500, len(historico_completo)), 200)
qtd_jogos = st.sidebar.number_input("Quantidade de jogos a gerar:", 1, 20, 3)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Seleção de Dezenas Fixas")

modo_fixo = st.sidebar.radio(
    "Como deseja fixar as dezenas?",
    ["Automático (Mais frequentes)", "Manual (Escolher meus números)"]
)

numeros_fixos_finais = []

# Processamento do histórico
historico_analise = historico_completo[-qtd_analise:]
todos_numeros = [num for jogo in historico_analise for num in jogo]
frequencia = Counter(todos_numeros)

if modo_fixo == "Automático (Mais frequentes)":
    qtd_fixos = st.sidebar.slider("Quantidade de números mais frequentes:", 5, 13, 10)
    numeros_fixos_finais = [num for num, _ in frequencia.most_common(qtd_fixos)]
else:
    numeros_fixos_finais = st.sidebar.multiselect(
        "Selecione de 1 a 14 números fixos (ex: números do sonho):",
        options=list(range(1, 26)),
        default=[1, 2, 3, 4, 5, 6, 7, 8]
    )
    if len(numeros_fixos_finais) == 0:
        st.sidebar.warning("⚠️ Selecione pelo menos 1 número para fixar!")
    elif len(numeros_fixos_finais) >= 15:
        st.sidebar.error("⚠️ Selecione no máximo 14 números fixos!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Versão Mobile")
url_app = st.sidebar.text_input("Link do App:", value="https://share.streamlit.io")
if url_app:
    st.sidebar.image(gerar_qrcode(url_app), caption="Acesse no celular", use_container_width=True)

# --- CABEÇALHO PRINCIPAL ---
st.markdown('<p class="main-header">🎲 Lotofácil - Gerador de Palpites</p>', unsafe_allow_html=True)
st.write("Análise estatística e combinações automáticas em tempo real.")

# --- CARTÃO DE DEZENAS FIXADAS ---
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
if modo_fixo == "Automático (Mais frequentes)":
    st.markdown(f'<h4>🔥 Top {len(numeros_fixos_finais)} Dezenas Mais Frequentes (Últimos {qtd_analise} Jogos)</h4>', unsafe_allow_html=True)
else:
    st.markdown(f'<h4>⭐ As Suas {len(numeros_fixos_finais)} Dezenas Fixas Escolhidas</h4>', unsafe_allow_html=True)

if numeros_fixos_finais:
    esferas_html = "".join([f'<span class="number-badge">{num:02d}</span>' for num in sorted(numeros_fixos_finais)])
    st.markdown(f'<div>{esferas_html}</div>', unsafe_allow_html=True)
else:
    st.info("Nenhuma dezena selecionada.")
st.markdown('</div>', unsafe_allow_html=True)

# --- GERAÇÃO DOS JOGOS ---
if st.button("🚀 Gerar Palpites Otimizados"):
    if len(numeros_fixos_finais) == 0 or len(numeros_fixos_finais) >= 15:
        st.error("Ajuste a quantidade de números fixos no menu lateral antes de gerar os jogos.")
    else:
        jogos_gerados = []
        # Números disponíveis para completar o jogo
        outros_numeros = [n for n in range(1, 26) if n not in numeros_fixos_finais]
        qtd_necessaria = 15 - len(numeros_fixos_finais)
        
        for _ in range(qtd_jogos):
            faltantes = random.sample(outros_numeros, qtd_necessaria)
            jogo_final = sorted(numeros_fixos_finais + faltantes)
            jogos_gerados.append(jogo_final)
        
        st.session_state["jogos_gerados"] = jogos_gerados

# --- EXIBIÇÃO E BOTÕES DE DOWNLOAD ---
if "jogos_gerados" in st.session_state:
    jogos = st.session_state["jogos_gerados"]
    
    st.markdown("### 📋 Seus Jogos Gerados")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="📄 Baixar em TXT",
            data=exportar_txt(jogos),
            file_name="jogos_lotofacil.txt",
            mime="text/plain"
        )
    with col_btn2:
        st.download_button(
            label="📊 Baixar em Excel (.xlsx)",
            data=exportar_excel(jogos),
            file_name="jogos_lotofacil.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    for i, jogo in enumerate(jogos, 1):
        bolinhas_jogo = "".join([f'<span class="game-badge">{num:02d}</span>' for num in jogo])
        coluna_alvo = col1 if i % 2 != 0 else col2
        
        with coluna_alvo:
            coluna_alvo.markdown(f"""
            <div class="custom-card">
                <strong style="color: #a855f7; font-size: 1.1rem;">Jogo #{i:02d}</strong>
                <div style="margin-top: 10px;">{bolinhas_jogo}</div>
            </div>
            """, unsafe_allow_html=True)
