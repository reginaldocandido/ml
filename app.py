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

def generate_brand_text(produto, vibe, api_key):
    """
    Chama a API do Gemini 2.5 Flash para gerar Nome, Slogan e Descrição.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    
    prompt = f"""
    Você é um especialista em branding de classe mundial. Sua tarefa é criar um conceito de marca para um novo produto.

    **Produto/Serviço:** "{produto}"
    **Vibe/Estilo da Marca:** "{vibe}"

    **Gere o seguinte conteúdo:**
    1.  **Nome da Marca:** (Um nome curto e memorável)
    2.  **Slogan:** (Uma frase de efeito curta)
    3.  **Descrição de Marketing:** (Um parágrafo (3-4 frases) descrevendo a marca e atraindo clientes)
    
    Responda em Markdown.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        # Vamos manter as configurações de segurança permissivas
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
        response.raise_for_status() # Lança um erro para respostas HTTP ruins (ex: 404, 500)
        
        data = response.json()
        
        # Verificação de segurança (finish_reason)
        if "candidates" not in data or not data["candidates"]:
            st.error("A API não retornou candidatos. Verifique o log do app no Streamlit.")
            return None
        
        if data["candidates"][0].get("finishReason") == "SAFETY":
            st.error("A resposta foi bloqueada pelo filtro de segurança da IA. Tente um prompt diferente.")
            return None

        return data["candidates"][0]["content"]["parts"][0]["text"]
        
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de rede ou HTTP ao chamar a API de texto: {e}")
        return None
    except KeyError:
        st.error("Resposta da API de texto em formato inesperado. Verifique os logs.")
        return None
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu (texto): {e}")
        return None

def generate_logo_image(produto, vibe, api_key):
    """
    Chama a API do Gemini 2.5 Flash Image Preview para gerar um conceito de logo.
    Esta função foi MODIFICADA para usar um modelo compatível com a API do AI Studio.
    """
    # Usamos o endpoint generateContent do modelo de imagem
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={api_key}"
    
    logo_prompt = f"Um logo vetorial profissional, design limpo, {vibe}, para uma marca de '{produto}'. Fundo branco."

    payload = {
        "contents": [{
            "parts": [{"text": logo_prompt}]
        }],
        "generationConfig": {
            "responseModalities": ['IMAGE'] # Pedimos uma imagem como resposta
        },
        # Mantemos as configurações de segurança permissivas
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

        # A estrutura da resposta é diferente
        if "candidates" not in data or not data["candidates"]:
            st.error("A API de imagem não retornou candidatos.")
            return None

        # Verificação de segurança
        if data["candidates"][0].get("finishReason") == "SAFETY":
            st.error("A resposta da imagem foi bloqueada pelo filtro de segurança da IA. Tente um prompt diferente.")
            return None
        
        # Encontrar a parte da imagem
        image_part = None
        for part in data["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                image_part = part
                break
        
        if image_part:
            return image_part["inlineData"]["data"] # Retorna a imagem em base64
        else:
            st.error("A API não retornou dados de imagem, embora a chamada tenha sido bem-sucedida.")
            return None
        
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de rede ou HTTP ao chamar a API de imagem: {e}")
        return None
    except KeyError:
        st.error("Resposta da API de imagem em formato inesperado. Verifique os logs.")
        return None
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu (imagem): {e}")
        return None

# --- Interface do Streamlit (UI) ---

st.title("Gerador de Conceito de Marca 💡")
st.markdown("Descreva seu produto e nós criamos o nome, slogan, descrição e até um conceito de logo!")

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

# --- Lógica de Execução ---
if submitted:
    if not produto_input:
        st.warning("Por favor, descreva seu produto ou serviço.")
    else:
        # 1. Gerar o Texto
        with st.spinner(f"Criando o conceito de marca para '{produto_input}'... ✍️"):
            text_result = generate_brand_text(produto_input, vibe_input, api_key)
        
        if text_result:
            st.divider()
            st.subheader("Aqui está sua Ideia de Marca:")
            st.markdown(text_result)
            
            # 2. Gerar a Imagem (Logo)
            with st.spinner(f"Desenhando um logo com vibe '{vibe_input}'... 🎨"):
                image_b64 = generate_logo_image(produto_input, vibe_input, api_key)
            
            if image_b64:
                st.divider()
                st.subheader("Conceito de Logo:")
                st.image(
                    f"data:image/png;base64,{image_b64}",
                    caption=f"Logo conceitual para {produto_input}"
                )
            else:
                st.error("Não foi possível gerar o conceito de logo.")
        else:
            st.error("Não foi possível gerar o conceito da marca.")

st.divider()
st.caption("Um projeto de exemplo com Python, Streamlit, Gemini (texto) e Imagen (imagem).")
