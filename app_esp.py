# ============================================
# ANALIZADOR DE SENTIMIENTOS CON VOZ
# Versión completa para local y Streamlit Cloud
# ============================================

# Importar todas las librerías necesarias
import streamlit as st  # Para crear la aplicación web
from textblob import TextBlob  # Para análisis de sentimientos
from deep_translator import GoogleTranslator  # Para traducción español-inglés
import speech_recognition as sr  # Para reconocimiento de voz
import os  # Para detectar si estamos en la nube

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Analizador de Sentimientos IA",  # Título en la pestaña del navegador
    page_icon="😊",  # Ícono
    layout="wide"  # Diseño amplio
)

# ============================================
# ENCABEZADO DE LA APLICACIÓN
# ============================================
st.title("😊 Analizador de Sentimientos en Español")
st.markdown("""
Escribe tu texto o **usa tu voz** (solo en versión local) para analizar el sentimiento.
La IA detectará si es positivo, negativo o neutral.
""")

# Línea divisora
st.divider()

# ============================================
# DETECCIÓN DE ENTORNO (LOCAL O NUBE)
# ============================================
# Verificar si estamos en local (tu PC) o en Streamlit Cloud
def verificar_entorno():
    """
    Detecta si la aplicación se ejecuta localmente o en la nube.
    Devuelve True si es local, False si es en la nube.
    """
    try:
        # Intentar importar PyAudio (solo funciona localmente)
        import pyaudio
        
        # Verificar variables de entorno de Streamlit Cloud
        variables_nube = ['STREAMLIT_SHARING', 'STREAMLIT_SERVER', 'STREAMLIT_DEPLOYMENT']
        
        # Si NO tenemos variables de la nube, estamos en local
        for variable in variables_nube:
            if variable in os.environ:
                return False  # Estamos en la nube
        
        return True  # Estamos en local
        
    except ImportError:
        return False  # PyAudio no instalado = estamos en la nube o sin micrófono

# Guardar el resultado en una variable
esta_en_local = verificar_entorno()

# ============================================
# SECCIÓN 1: ENTRADA POR VOZ (SOLO LOCAL)
# ============================================
st.subheader("🎤 Entrada por Voz")

if esta_en_local:
    # MOSTRAR BOTÓN DE GRABACIÓN (solo en local)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Grabación en tiempo real desde tu micrófono**")
    
    with col2:
        if st.button("🎤 **Comenzar a grabar**", type="primary", use_container_width=True):
            # Inicializar el reconocedor de voz
            reconocedor = sr.Recognizer()
            
            # Usar el micrófono como fuente de audio
            with sr.Microphone() as fuente:
                # Mostrar indicador de grabación
                with st.spinner("🎤 **Grabando... Habla ahora**"):
                    try:
                        # Ajustar para ruido ambiental
                        reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)
                        
                        # Grabar audio (10 segundos máximo)
                        audio = reconocedor.listen(
                            fuente, 
                            timeout=10, 
                            phrase_time_limit=10
                        )
                        
                        # Convertir audio a texto
                        with st.spinner("🔄 Procesando audio..."):
                            texto_reconocido = reconocedor.recognize_google(
                                audio, 
                                language="es-ES"  # Español de España
                            )
                        
                        # Mostrar resultado del reconocimiento
                        st.success("✅ **Audio reconocido con éxito!**")
                        st.info(f"**Texto:** {texto_reconocido}")
                        
                        # Guardar en estado de sesión para usar en el análisis
                        st.session_state['texto_para_analizar'] = texto_reconocido
                        
                    except sr.WaitTimeoutError:
                        st.error("⏰ Tiempo agotado. No se detectó voz.")
                    except sr.UnknownValueError:
                        st.error("❌ No se pudo entender el audio. Habla más claro.")
                    except sr.RequestError:
                        st.error("🌐 Error de conexión. Verifica tu internet.")
                    except Exception as e:
                        st.error(f"⚠️ Error inesperado: {str(e)}")
    
    # Instrucciones para uso de voz
    with st.expander("📌 Instrucciones para uso de voz"):
        st.markdown("""
        1. Haz clic en **"Comenzar a grabar"**
        2. Espera el mensaje "Grabando..."
        3. Habla claramente en español
        4. Espera a que se procese el audio
        5. El texto aparecerá automáticamente abajo
        """)

else:
    # MENSAJE PARA USUARIOS EN LA NUBE
    st.warning("⚠️ **Función de voz no disponible en esta versión web**")
    
    with st.expander("¿Quieres usar la función de voz?"):
        st.markdown("""
        ### 📥 Descarga la versión local:
        
        1. **Descarga el código** de GitHub
        2. **Abre terminal** en la carpeta del proyecto
        3. **Instala dependencias:**
           ```bash
           pip install -r requirements.txt
           pip install pyaudio
           ```
        4. **Ejecuta la app:**
           ```bash
           streamlit run app_esp.py
           ```
        5. **Disfruta de todas las funciones** incluyendo voz
        
        [🔗 Ver código en GitHub](#) *(pon tu enlace aquí)*
        """)

# ============================================
# SECCIÓN 2: ENTRADA DE TEXTO
# ============================================
st.subheader("✍️ Entrada de Texto")

# Crear área de texto con valor predeterminado o texto reconocido
texto_predeterminado = "¡Estoy muy feliz de aprender inteligencia artificial!"

# Usar texto reconocido si existe, sino usar el predeterminado
if 'texto_para_analizar' in st.session_state:
    texto_predeterminado = st.session_state['texto_para_analizar']

# Área de texto para entrada manual
texto_usuario = st.text_area(
    label="**Escribe o pega tu texto aquí:**",
    value=texto_predeterminado,
    height=150,
    placeholder="Ejemplo: Me encanta esta aplicación, es muy útil..."
)

# ============================================
# SECCIÓN 3: ANÁLISIS DE SENTIMIENTOS
# ============================================
st.divider()
st.subheader("📊 Análisis de Sentimientos")

# Botón para analizar
col_analizar1, col_analizar2, col_analizar3 = st.columns([1, 2, 1])

with col_analizar2:
    boton_analizar = st.button(
        "🔍 **Analizar Sentimiento**", 
        type="primary", 
        use_container_width=True
    )

if boton_analizar and texto_usuario:
    # Mostrar progreso
    with st.spinner("Analizando sentimiento..."):
        
        try:
            # ============================================
            # PASO 1: TRADUCCIÓN ESPAÑOL → INGLÉS
            # ============================================
            with st.status("🌍 Traduciendo texto...", expanded=True) as status:
                # Crear traductor
                traductor = GoogleTranslator(source='es', target='en')
                
                # Traducir texto
                texto_traducido = traductor.translate(texto_usuario)
                
                # Mostrar traducción
                st.write(f"**Texto original:** {texto_usuario}")
                st.write(f"**Texto traducido:** {texto_traducido}")
                status.update(label="✅ Traducción completada", state="complete")
            
            # ============================================
            # PASO 2: ANÁLISIS CON TEXTBLOB
            # ============================================
            with st.status("🤖 Analizando sentimiento...", expanded=True) as status:
                # Crear objeto TextBlob con texto en inglés
                analisis = TextBlob(texto_traducido)
                
                # Extraer polaridad (-1 a 1) y subjetividad (0 a 1)
                polaridad = analisis.sentiment.polarity
                subjetividad = analisis.sentiment.subjectivity
                
                status.update(label="✅ Análisis completado", state="complete")
            
            # ============================================
            # PASO 3: MOSTRAR RESULTADOS
            # ============================================
            st.success("✅ **Análisis completado con éxito!**")
            
            # Crear columnas para mostrar resultados
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                # BARRA DE PROGRESO PARA POLARIDAD
                st.markdown("#### 📈 Polaridad del Sentimiento")
                
                # Determinar sentimiento y color
                if polaridad > 0.3:
                    etiqueta = "😊 **MUY POSITIVO**"
                    color = "green"
                    emoji = "😊"
                elif polaridad > 0.1:
                    etiqueta = "🙂 **POSITIVO**"
                    color = "lightgreen"
                    emoji = "🙂"
                elif polaridad < -0.3:
                    etiqueta = "😠 **MUY NEGATIVO**"
                    color = "red"
                    emoji = "😠"
                elif polaridad < -0.1:
                    etiqueta = "😞 **NEGATIVO**"
                    color = "orange"
                    emoji = "😞"
                else:
                    etiqueta = "😐 **NEUTRAL**"
                    color = "gray"
                    emoji = "😐"
                
                # Mostrar barra de progreso
                st.progress(
                    value=(polaridad + 1) / 2,  # Convertir de (-1 a 1) a (0 a 1)
                    text=f"{emoji} {etiqueta} | Valor: {polaridad:.2f}"
                )
                
                # Explicación
                with st.expander("¿Qué significa la polaridad?"):
                    st.markdown("""
                    **Escala de polaridad:**
                    - **-1.0 a -0.3**: Muy negativo 😠
                    - **-0.3 a -0.1**: Negativo 😞
                    - **-0.1 a 0.1**: Neutral 😐
                    - **0.1 a 0.3**: Positivo 🙂
                    - **0.3 a 1.0**: Muy positivo 😊
                    """)
            
            with col_res2:
                # BARRA DE PROGRESO PARA SUBJETIVIDAD
                st.markdown("#### 🧠 Nivel de Subjetividad")
                
                # Determinar nivel de subjetividad
                if subjetividad > 0.7:
                    nivel = "💭 **MUY SUBJETIVO**"
                    color_sub = "blue"
                elif subjetividad > 0.4:
                    nivel = "💬 **SUBJETIVO**"
                    color_sub = "lightblue"
                else:
                    nivel = "📊 **OBJETIVO**"
                    color_sub = "gray"
                
                # Mostrar barra de progreso
                st.progress(
                    value=subjetividad,
                    text=f"{nivel} | Valor: {subjetividad:.2f}"
                )
                
                # Explicación
                with st.expander("¿Qué significa la subjetividad?"):
                    st.markdown("""
                    **Escala de subjetividad:**
                    - **0.0 a 0.4**: Texto objetivo (hechos, datos)
                    - **0.4 a 0.7**: Texto subjetivo (opiniones)
                    - **0.7 a 1.0**: Texto muy subjetivo (emociones fuertes)
                    
                    *Ejemplo:* "El cielo es azul" = 0.1 (objetivo)
                    *Ejemplo:* "Amo este día soleado" = 0.8 (subjetivo)
                    """)
            
            # ============================================
            # RESUMEN FINAL
            # ============================================
            st.divider()
            
            # Crear resumen en una tarjeta
            with st.container(border=True):
                st.markdown("### 📋 Resumen del Análisis")
                
                col_sum1, col_sum2 = st.columns(2)
                
                with col_sum1:
                    st.metric(
                        label="**Sentimiento detectado**",
                        value=etiqueta.split("**")[1],  # Extraer solo el texto
                        delta=f"{polaridad:.2f} puntos"
                    )
                
                with col_sum2:
                    st.metric(
                        label="**Nivel de subjetividad**",
                        value=f"{(subjetividad * 100):.0f}%",
                        delta=f"{subjetividad:.2f}"
                    )
                
                # Recomendación basada en el análisis
                st.markdown("#### 💡 Interpretación:")
                
                if polaridad > 0.2:
                    st.success("""
                    **✅ Texto positivo detectado:** El mensaje transmite emociones 
                    positivas como alegría, satisfacción o entusiasmo.
                    """)
                elif polaridad < -0.2:
                    st.error("""
                    **⚠️ Texto negativo detectado:** El mensaje contiene emociones 
                    negativas como tristeza, enojo o frustración.
                    """)
                else:
                    st.info("""
                    **📊 Texto neutral detectado:** El mensaje es principalmente 
                    factual o balanceado, sin emociones extremas.
                    """)
        
        except Exception as error:
            # Manejo de errores
            st.error(f"❌ **Error en el análisis:** {str(error)}")
            st.info("💡 **Solución:** Intenta con un texto diferente o más corto.")

elif boton_analizar and not texto_usuario:
    # Advertencia si no hay texto
    st.warning("⚠️ Por favor, escribe algún texto o usa la voz para analizar.")

# ============================================
# SECCIÓN 4: INFORMACIÓN ADICIONAL
# ============================================
st.divider()

with st.expander("📚 Acerca de esta aplicación"):
    st.markdown("""
    ### 🤖 **Cómo funciona esta aplicación:**
    
    1. **Entrada de texto/voz**: Recibe texto en español
    2. **Traducción**: Traduce automáticamente a inglés
    3. **Análisis**: TextBlob analiza sentimientos en inglés
    4. **Resultados**: Muestra polaridad y subjetividad
    
    ### 🛠️ **Tecnologías utilizadas:**
    - **Streamlit**: Interfaz web
    - **TextBlob**: Análisis de sentimientos
    - **Google Translator**: Traducción español-inglés
    - **SpeechRecognition**: Reconocimiento de voz (local)
    
    ### 🌐 **Versiones disponibles:**
    - **Web (Streamlit Cloud)**: Solo análisis por texto
    - **Local (tu PC)**: Análisis por texto Y voz
    """)

with st.expander("❓ Preguntas frecuentes"):
    st.markdown("""
    **¿Por qué no funciona la voz en la web?**
    > Por limitaciones de seguridad de los navegadores, las aplicaciones web 
    > no pueden acceder directamente al micrófono sin permisos especiales.
    
    **¿Cómo instalo la versión local?**
    > 1. Descarga el código
    > 2. Ejecuta: `pip install -r requirements.txt`
    > 3. Ejecuta: `pip install pyaudio`
    > 4. Ejecuta: `streamlit run app_esp.py`
    
    **¿El análisis es 100% preciso?**
    > No, es una estimación basada en algoritmos de IA. 
    > Para análisis profesional, consulta a un experto.
    """)

# ============================================
# PIE DE PÁGINA
# ============================================
st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col2:
    st.caption("""
    **Analizador de Sentimientos con IA** | 
    [📁 GitHub](#) | 
    Versión 2.0 | 
    © 2024
    """)

