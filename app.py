import streamlit as st
import google.generativeai as genai
import time

# --- Configuração da Página ---
st.set_page_config(
    page_title="Decodificador de Gírias 🧐",
    page_icon="🧐",
    layout="centered",
)

# --- Chamada da API e Configuração do Modelo ---

# Função para carregar o modelo de forma segura
# O @st.cache_resource garante que o modelo seja carregado apenas uma vez.
@st.cache_resource
def load_model():
    """
    Carrega o modelo generativo do Gemini.
    Levanta uma exceção se a API key não estiver configurada nos secrets do Streamlit.
    """
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("Erro: GOOGLE_API_KEY não encontrada nos secrets do Streamlit.")
        st.caption("Por favor, adicione sua chave da API do Google AI Studio aos 'Secrets' do seu app no Streamlit Community Cloud.")
        st.stop() # Para a execução se a chave não estiver presente

    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # Configurações de segurança para o modelo
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # Configurações de geração (criatividade vs. precisão)
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 512,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-09-2025",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        return model
    except Exception as e:
        st.error(f"Erro ao inicializar o modelo: {e}")
        st.stop()

# --- Construtor do Prompt ---
def build_prompt(giria, publico_alvo):
    """
    Cria o prompt formatado para enviar ao modelo Gemini.
    """
    # Persona do LLM
    prompt = f"""
    Você é o "Decodificador de Gírias", um especialista em cultura da internet e linguística moderna. 
    Sua tarefa é explicar uma gíria de forma clara, concisa e adaptada ao público-alvo.

    **Gíria a ser explicada:** "{giria}"
    
    **Público-alvo da explicação:** "{publico_alvo}"

    **Formato da Resposta (Obrigatório):**
    1.  **Definição:** Comece com uma definição direta (O que significa?).
    2.  **Origem/Contexto:** (Se souber) Explique brevemente de onde veio (jogo, rede social, etc.).
    3.  **Exemplo de Uso:** Dê 1 ou 2 frases de exemplo.
    
    Adapte o tom da explicação para o público-alvo solicitado.
    """
    return prompt

# --- Interface do Streamlit (UI) ---

# Carrega o modelo
try:
    model = load_model()
except Exception as e:
    st.error(f"Não foi possível carregar a aplicação. Erro: {e}")
    # Se o load_model() falhar (ex: API key), ele já terá mostrado o erro,
    # mas garantimos que a UI não tente ser renderizada.
    st.stop()


# Título e Subtítulo
st.title("Decodificador de Gírias 🧐")
st.markdown("Não entendeu o que o 'cria' falou? Ou o que significa 'rizz'? Deixa que eu traduzo!")

# --- Formulário de Inputs ---
with st.form("giria_form"):
    giria_input = st.text_input(
        "Qual gíria você quer entender?",
        placeholder="Ex: tankar, cringe, 'meter o shape', rizz..."
    )
    
    publico_alvo_input = st.selectbox(
        "Como você quer a explicação?",
        [
            "Para meus pais (bem simples e didático)",
            "Para um colega de trabalho (tom casual, mas profissional)",
            "Para um amigo (descontraído)",
            "Técnica (etimologia e contexto cultural)"
        ]
    )
    
    submitted = st.form_submit_button("Decodificar!")

# --- Lógica de Execução ---
if submitted:
    if not giria_input:
        st.warning("Por favor, digite uma gíria para decodificar.")
    else:
        # 1. Construir o prompt
        prompt_final = build_prompt(giria_input, publico_alvo_input)
        
        # 2. Chamar a API com spinner (indicador de carregamento)
        with st.spinner(f"Decodificando '{giria_input}'... 🧠"):
            try:
                # 3. Gerar a resposta
                response = model.generate_content(prompt_final)
                
                # 4. Mostrar a resposta
                st.divider()
                st.subheader(f"Aqui está a decodificação de '{giria_input}':")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Houve um problema ao contatar a IA: {e}")
                st.caption("Isso pode ser um problema temporário na API. Tente novamente em alguns segundos.")

st.divider()
st.caption("Um projeto de exemplo construído com Python, Streamlit e a API do Gemini.")
