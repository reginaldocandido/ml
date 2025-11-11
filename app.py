import streamlit as st
import requests
import json

# --- Configuração da Página ---
# ... existing code ...
    layout="centered",
)

# --- Funções da API ---

def get_api_key():
# ... existing code ...
    return st.secrets["GOOGLE_API_KEY"]

def generate_brand_text(produto, vibe, api_key):
# ... existing code ...
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu (texto): {e}")
        return None

def generate_logo_image(produto, vibe, api_key):
# ... existing code ...
    except Exception as e:
        st.error(f"Um erro inesperado ocorreu (imagem): {e}")
        return None

# --- Interface do Streamlit (UI) ---

st.title("Gerador de Conceito de Marca 💡")
# ... existing code ...
# Pega a API Key (e para se não existir)
api_key = get_api_key()

# --- NOVO: Inicializar o estado de processamento ---
if 'processing' not in st.session_state:
    st.session_state.processing = False

# --- Formulário de Inputs ---
with st.form("brand_form"):
# ... existing code ...
            "Tecnológico e Inovador"
        ]
    )
    
    # --- MODIFICADO: Adicionamos o 'disabled' ---
    submitted = st.form_submit_button(
        "Gerar Conceito!", 
        disabled=st.session_state.processing # Desativa o botão se estiver a processar
    )

# --- Lógica de Execução ---
if submitted:
    if not produto_input:
        st.warning("Por favor, descreva seu produto ou serviço.")
    else:
        # --- NOVO: Bloquear o botão ---
        st.session_state.processing = True
        
        try:
            # 1. Gerar o Texto
# ... existing code ...
            with st.spinner(f"Criando o conceito de marca para '{produto_input}'... ✍️"):
                text_result = generate_brand_text(produto_input, vibe_input, api_key)
            
            if text_result:
# ... existing code ...
                st.markdown(text_result)
                
                # 2. Gerar a Imagem (Logo)
# ... existing code ...
                    f"data:image/png;base64,{image_b64}",
                    caption=f"Logo conceitual para {produto_input}"
                )
                else:
                    st.error("Não foi possível gerar o conceito de logo.")
            else:
                st.error("Não foi possível gerar o conceito da marca.")
                
        finally:
            # --- NOVO: Libertar o botão, quer funcione ou falhe ---
            st.session_state.processing = False
            st.rerun() # Atualiza a interface para reativar o botão

st.divider()
