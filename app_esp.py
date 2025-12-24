import streamlit as st # Importa la librería principal para crear la interfaz web
from textblob import TextBlob # Importa la librería para análisis de sentimientos
from deep_translator import GoogleTranslator # Importa la herramienta de traducción
from streamlit_mic_recorder import speech_to_text # Importa la función para convertir voz a texto

# Configuración de la pestaña del navegador
st.set_page_config(page_title="IA: Voz y Sentimiento", page_icon="🎙️")

st.title("🎙️ Analizador de Voz y Sentimiento")
st.markdown("Puedes **escribir** o **hablar** para que la IA analice tu tono.")

# --- SECCIÓN DE ENTRADA DE VOZ ---
st.subheader("Paso 1: Grabación de voz")
# Crea un botón que activa el micrófono y transcribe el audio a español
texto_voz = speech_to_text(
    language='es', 
    start_prompt="Click para hablar 🎤", 
    stop_prompt="Detener grabación ⏹️", 
    key='recorder'
)

# --- SECCIÓN DE ENTRADA DE TEXTO ---
st.subheader("Paso 2: Confirmación de texto")
# Si hubo voz, el texto se pone en el área; si no, queda el texto por defecto
texto_final = st.text_area(
    "Texto detectado o ingresado:", 
    value=texto_voz if texto_voz else "¡Estoy muy feliz de aprender!",
    height=100
)

# --- PROCESAMIENTO ---
if st.button("Analizar Sentimiento"): # Crea el botón de acción
    if texto_final: # Verifica que el texto no esté vacío
        try:
            # --- PASO 1: TRADUCCIÓN ---
            # Traducimos de español (es) a inglés (en) porque TextBlob funciona mejor en inglés
            traductor = GoogleTranslator(source='es', target='en')
            texto_ingles = traductor.translate(texto_final)
            
            # Muestra una nota pequeña del texto traducido
            st.caption(f"⚙️ Procesado internamente como: *'{texto_ingles}'*")

            # --- PASO 2: ANÁLISIS ---
            blob = TextBlob(texto_ingles) # Crea un objeto TextBlob con el texto en inglés
            polaridad = blob.sentiment.polarity # Calcula qué tan positivo o negativo es (-1 a 1)
            subjetividad = blob.sentiment.subjectivity # Calcula qué tan subjetivo es (0 a 1)
            
            # --- PASO 3: MOSTRAR RESULTADOS ---
            st.write("---")
            st.subheader("Resultados:")
            
            # Clasificación visual según la polaridad
            if polaridad > 0.1:
                st.success(f"😊 Positivo (Score: {polaridad:.2f})") # Verde si es positivo
            elif polaridad < -0.1:
                st.error(f"😠 Negativo (Score: {polaridad:.2f})") # Rojo si es negativo
            else:
                st.warning(f"😐 Neutral (Score: {polaridad:.2f})") # Amarillo si es neutro

            # Muestra el nivel de opinión o subjetividad
            st.info(f"🧐 Subjetividad: {subjetividad:.2f} ({(subjetividad * 100):.0f}% opinión)")

        except Exception as e:
            st.error(f"Hubo un error en el proceso: {e}") # Captura errores en caso de fallos
            
    else:
        st.warning("Por favor, ingresa texto o usa el micrófono.") # Aviso si no hay datos