import streamlit as st
import requests
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gerador de Conceito de Marca 💡",
    page_icon="💡",
    layout="centered",
)

# --- Funções da API ---

def get_api_key():
    """
    Verifica e retorna a API key dos secrets do Streamlit.
    Para a execução se a chave não for encontrada.
    """
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("Erro: GOOGLE_API_KEY não encontrada nos secrets do Streamlit.")
        st.caption("Por favor, adicione sua chave da API do Google AI Studio aos 'Secrets' do seu app no Streamlit Community Cloud.")
        st.stop()
    return st.secrets["GOOGLE_API_KEY"]

def generate_brand_concept(produto, vibe, api_key):
    """
    Chama a API do Gemini 2.5 Flash para gerar Nome, Slogan, Descrição
    e um PROMPT DE IMAGEM.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    # PROMPT ATUALIZADO: Pede 4 itens, incluindo o prompt de imagem
    prompt = f"""
    Você é um especialista em branding de classe mundial e um 'prompt engineer' de IA.
    Sua tarefa é criar um conceito de marca para um novo produto.

    **Produto/Serviço:** "{produto}"
    **Vibe/Estilo da Marca:** "{vibe}"

    **Gere o seguinte conteúdo:**
    1.  **Nome da Marca:** (Um nome curto e memorável)
    2.  **Slogan:** (Uma frase de efeito curta)
    3.  **Descrição de Marketing:** (Um parágrafo (3-4 frases) descrevendo a marca e atraindo clientes)
    4.  **Prompt de Imagem para Logo (em inglês):** (Um prompt detalhado para uma IA de imagem como DALL-E ou Midjourney,
        para criar um logo vetorial minimalista. Deve começar com "A minimalist vector logo..."
        e incluir o nome da marca e a vibe.)
    
    Responda em Markdown. Coloque o Prompt de Imagem dentro de um bloco de código (```).
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() 
        
        data = response.json()
        
        if "candidates" not in data or not data["candidates"]:
            if "promptFeedback" in data:
                 st.error(f"A API bloqueou o prompt. Razão: {data['promptFeedback'].get('blockReason')}")
                 return None
            st.error("A API não retornou candidatos. Verifique o log do app no Streamlit.")
            return None
        
        if data["candidates"][0].get("finishReason") == "SAFETY":
            st.error("A resposta foi bloqueada pelo filtro de segurança da IA. Tente um prompt diferente.")
            return None

        # Retorna o texto completo em markdown
        return data["candidates"][0]["content"]["parts"][0]["text"]
        
    except requests.exceptions.RequestException as e:
        if e.response is not None and e.response.status_code == 429:
            st.error("Erro: Muitas requisições enviadas à API.")
            st.warning("Por favor, aguarde alguns minutos antes de tentar novamente.")
        else:
            st.error(f"Erro de rede ou HTTP ao chamar a API de texto: {e}")
        return None
    except KeyError:
        st.error("Resposta da API de texto em formato inesperado. Verifique os logs.")
        return None
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu (texto): {e}")
        return None

# --- Interface do Streamlit (UI) ---

st.title("Gerador de Conceito de Marca 💡")
st.markdown("Descreva seu produto e nós criamos o nome, slogan, descrição e o prompt ideal para o logo!")

# Pega a API Key (e para se não existir)
api_key = get_api_key()

# --- Formulário de Inputs ---
with st.form("brand_form"):
    produto_input = st.text_input(
        "Qual é o seu produto ou serviço?",
        placeholder="Ex: Café artesanal, App de meditação, Pizzaria..."
    )
    
    vibe_input = st.selectbox(
        "Qual é a 'vibe' ou estilo da marca?",
        [
            "Moderno e Minimalista",
            "Rústico e Aconchegante",
            "Divertido e Jovem",
            "Elegante e Premium",
            "Tecnológico e Inovador"
        ]
    )
    
    submitted = st.form_submit_button("Gerar Conceito!")

# --- Lógica de Execução (Simplificada) ---
if submitted:
    if not produto_input:
        st.warning("Por favor, descreva seu produto ou serviço.")
    else:
        # 1. Gerar todo o conceito de uma vez
        with st.spinner(f"Criando o conceito de marca para '{produto_input}'... ✍️"):
            full_concept = generate_brand_concept(produto_input, vibe_input, api_key)
        
        if full_concept:
            st.divider()
            st.subheader("Aqui está sua Ideia de Marca:")
            st.markdown(full_concept)
        else:
            st.error("Não foi possível gerar o conceito da marca.")

st.divider()
st.caption("Um projeto de exemplo com Python, Streamlit e Gemini (para texto e prompt de imagem).")
