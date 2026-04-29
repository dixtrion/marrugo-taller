import streamlit as st
import math

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema Marrugo Pro", page_icon="🛠️", layout="centered")

# Estilo Industrial Personalizado (Mantenido tal cual)
st.markdown(
    """
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        height: 3.5em; 
        background-color: #0e1117; 
        color: white; 
        font-weight: bold;
        border: 2px solid #ed1c24;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        font-size: 28px;
        color: inherit !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- DICCIONARIO DE CAPACIDADES INDUSTRIALES (Completo) ---
CAPACIDADES_INDUSTRIALES = {
    3.0: {"calibre_seguro": 14, "calibre_critico": 12, "diametro_max": 2.0},
    5.0: {"calibre_seguro": 12, "calibre_critico": 10, "diametro_max": 2.5},
    7.5: {"calibre_seguro": 10, "calibre_critico": 8, "diametro_max": 3.0},
    10.0: {"calibre_seguro": 7, "calibre_critico": 5, "diametro_max": 4.0},
}

# --- FUNCIONES DE SINCRONIZACIÓN (La mejora para el lag) ---
def sync_material():
    """Sincroniza el material seleccionado con el banco antes de renderizar la barra lateral"""
    if "mat_selector_key" in st.session_state:
        st.session_state.banco["mat"] = st.session_state.mat_selector_key

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if "banco" not in st.session_state:
    st.session_state.banco = {"pulg": None, "cal": None, "mat": None}

if "potencia_maquina" not in st.session_state:
    st.session_state.potencia_maquina = 3.0

def decimal_a_fraccion(decimal):
    """Convierte decimales a la fracción comercial más cercana en octavos"""
    fracciones = {0.0: "", 0.125: "1/8", 0.25: "1/4", 0.375: "3/8", 0.5: "1/2", 0.625: "5/8", 0.75: "3/4", 0.875: "7/8"}
    entero = int(decimal)
    residuo = round(decimal - entero, 3)
    cercano = min(fracciones.keys(), key=lambda x: abs(x - residuo))
    frac_txt = fracciones[cercano]
    if entero > 0:
        return f"{entero} {frac_txt}".strip()
    return frac_txt if frac_txt else "0"

def obtener_potencia_valida(potencia_input):
    potencias_disponibles = list(CAPACIDADES_INDUSTRIALES.keys())
    return min(potencias_disponibles, key=lambda x: abs(x - potencia_input))

def validar_capacidad_maquina(calibre_usuario):
    potencia = obtener_potencia_valida(st.session_state.potencia_maquina)
    st.session_state.potencia_maquina = potencia 
    capacidad = CAPACIDADES_INDUSTRIALES[potencia]
    calibre_num = int(calibre_usuario)
    
    if calibre_num >= capacidad["calibre_seguro"]:
        return {"estado": "seguro", "mensaje": f"🟢 OPERACIÓN NORMAL - Calibre Ga {calibre_num} dentro de rango seguro para {potencia} HP", "alerta": None}
    elif calibre_num >= capacidad["calibre_critico"]:
        return {"estado": "critico", "mensaje": "⚠️ ADVERTENCIA CRÍTICA", "alerta": f"¡PELIGRO! Riesgo inminente de rotura de sellos hidráulicos para dobladora de {potencia} HP.\n\nCálculo continuará bajo responsabilidad."}
    else:
        return {"estado": "error", "mensaje": "🚨 ERROR DE CAPACIDAD", "alerta": f"Esta labor requiere mayor potencia. Calibre Ga {calibre_num} INCOMPATIBLE con {potencia} HP."}

# --- INTERFAZ PRINCIPAL ---
st.title("🛠️ Sistema Técnico Marrugo")
st.write("Control de Calidad e Ingeniería de Doblado")

# --- BARRA LATERAL (Resumen siempre actualizado) ---
st.sidebar.header("⚙️ Configuración de Máquina")
potencia_input = st.sidebar.number_input("Potencia Dobladora (HP):", 3.0, 10.0, st.session_state.potencia_maquina, 0.5)
st.session_state.potencia_maquina = potencia_input
st.sidebar.success(f"✅ Sistema operando a {obtener_potencia_valida(potencia_input)} HP")

st.sidebar.header("📍 Resumen del Banco")
st.sidebar.markdown(f"**Tubo:** {st.session_state.banco['pulg'] or '---'}")
st.sidebar.markdown(f"**Calibre:** {st.session_state.banco['cal'] or '---'}")
st.sidebar.markdown(f"**Material:** {st.session_state.banco['mat'] or '---'}")

if st.sidebar.button("🧹 Limpiar Banco"):
    st.session_state.banco = {"pulg": None, "cal": None, "mat": None}
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: gray; font-size: 0.85em;'>Desarrollado por:<br><strong>Dixtrion Electronic</strong></div>", unsafe_allow_html=True)

# Organización por pestañas
tabs = st.tabs(["📏 Medición", "📐 Calibre", "🚀 Diagnóstico", "📐 Geometría"])

with tabs[0]:
    st.write("### Centímetros a Pulgadas")
    cm = st.number_input("Circunferencia (cm):", min_value=0.0, step=0.1, key="cm_web")
    if st.button("Procesar Medida"):
        v_dec = cm / 8
        st.session_state.banco["pulg"] = f'{v_dec:.2f}" ({decimal_a_fraccion(v_dec)}")'
        st.rerun() # Actualiza el resumen lateral inmediatamente

with tabs[1]:
    st.write("### Identificador de Calibre (Ga)")
    mm = st.number_input("Espesor (mm):", min_value=0.0, step=0.01, format="%.2f", key="mm_web")
    if st.button("Identificar Calibre"):
        ref = {"10": 3.40, "12": 2.60, "14": 1.90, "16": 1.50, "18": 1.20, "19": 1.00, "20": 0.90}
        cal = min(ref.items(), key=lambda x: abs(x[1] - mm))[0]
        st.session_state.banco["cal"] = f"Ga {cal}"
        st.rerun() # Actualiza el resumen lateral inmediatamente

with tabs[2]:
    st.write("### Verificación Final")
    if st.session_state.banco["pulg"] and st.session_state.banco["cal"]:
        cal_val = st.session_state.banco["cal"].replace("Ga ", "")
        diag = validar_capacidad_maquina(cal_val)
        
        if diag["estado"] != "error":
            if diag["estado"] == "seguro": st.success(diag["mensaje"])
            else: 
                st.error(diag["mensaje"])
                st.markdown(diag["alerta"])
                if not st.checkbox("Continuar bajo responsabilidad"): st.stop()
            
            # EL TRUCO: 'on_change' ejecuta la sincronización antes de redibujar la página
            mat = st.radio(
                "Seleccione material:", 
                ["Acero Negro", "Galvanizado"], 
                key="mat_selector_key", 
                on_change=sync_material
            )
            # Respaldo inmediato del material
            st.session_state.banco["mat"] = mat
            
            col1, col2 = st.columns(2)
            col1.metric("ZAPATA SUGERIDA", st.session_state.banco["pulg"])
            col2.metric("ESPESOR REAL", st.session_state.banco["cal"])
        else:
            st.error(diag["mensaje"])
            st.markdown(diag["alerta"])
    else:
        st.warning("⚠️ Faltan datos. Ingrese medida y calibre en las pestañas anteriores.")

with tabs[3]:
    st.write("### Cálculos de Geometría")
    op_geo = st.selectbox("Seleccione herramienta:", ["Altura Triángulo (86.6%)", "Diagonal Cuadrado (1.41)", "Escuadra (Hipotenusa)"])
    v1 = st.number_input("Medida base A (cm):", min_value=0.0)
    if op_geo == "Escuadra (Hipotenusa)":
        v2 = st.number_input("Medida base B (cm):", min_value=0.0)
        st.info(f"**Longitud de Hipotenusa:** {math.sqrt(v1**2 + v2**2):.2f} cm")
    elif "Triángulo" in op_geo:
        st.info(f"**Altura del Triángulo:** {v1 * 0.866:.2f} cm")
    else:
        st.info(f"**Longitud de Diagonal:** {v1 * 1.41:.2f} cm")