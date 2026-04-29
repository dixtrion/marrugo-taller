import streamlit as st
import math

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema Marrugo Pro", page_icon="🛠️", layout="centered")

# Estilo Industrial Personalizado
st.markdown(
    """
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background-color: #0e1117; color: white; font-weight: bold;
        border: 2px solid #ed1c24;
    }
    div[data-testid="stMetricValue"] * {
        font-size: 28px; color: inherit !important; font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- DICCIONARIO DE CAPACIDADES ---
CAPACIDADES_INDUSTRIALES = {
    3.0: {"calibre_seguro": 14, "calibre_critico": 12},
    5.0: {"calibre_seguro": 12, "calibre_critico": 10},
    7.5: {"calibre_seguro": 10, "calibre_critico": 8},
    10.0: {"calibre_seguro": 7, "calibre_critico": 5},
}

# --- FUNCIONES DE APOYO ---
def update_material_callback():
    """Sincroniza el material seleccionado con el banco de forma inmediata"""
    st.session_state.banco["mat"] = st.session_state.mat_selector

def decimal_a_fraccion(decimal):
    fracciones = {0.0: "", 0.125: "1/8", 0.25: "1/4", 0.375: "3/8", 0.5: "1/2", 0.625: "5/8", 0.75: "3/4", 0.875: "7/8"}
    entero = int(decimal)
    residuo = round(decimal - entero, 3)
    cercano = min(fracciones.keys(), key=lambda x: abs(x - residuo))
    frac_txt = fracciones[cercano]
    return f"{entero} {frac_txt}".strip() if entero > 0 else (frac_txt if frac_txt else "0")

# --- INICIALIZACIÓN DE ESTADO ---
if "banco" not in st.session_state:
    st.session_state.banco = {"pulg": None, "cal": None, "mat": None}

# --- BARRA LATERAL (Resumen del Banco) ---
st.sidebar.header("⚙️ Configuración")
potencia_input = st.sidebar.number_input("Potencia Dobladora (HP):", 3.0, 10.0, 3.0, 0.5)
st.sidebar.success(f"✅ Sistema: {potencia_input} HP")

st.sidebar.header("📍 Resumen del Banco")
st.sidebar.markdown(f"**Tubo:** {st.session_state.banco['pulg'] or '---'}")
st.sidebar.markdown(f"**Calibre:** {st.session_state.banco['cal'] or '---'}")
# Aquí usamos directamente el valor del banco que el callback mantiene al día
st.sidebar.markdown(f"**Material:** {st.session_state.banco['mat'] or '---'}")

if st.sidebar.button("🧹 Limpiar Banco"):
    st.session_state.banco = {"pulg": None, "cal": None, "mat": None}
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: gray; font-size: 0.85em;'>Desarrollado por:<br><strong>Dixtrion Electronic</strong></div>", unsafe_allow_html=True)

# --- CUERPO PRINCIPAL ---
st.title("🛠️ Sistema Técnico Marrugo")
tabs = st.tabs(["📏 Medición", "📐 Calibre", "🚀 Diagnóstico", "📐 Geometría"])

with tabs[0]:
    cm = st.number_input("Circunferencia (cm):", min_value=0.0, step=0.1, key="cm_input")
    if st.button("Procesar Medida"):
        v_dec = cm / 8
        st.session_state.banco["pulg"] = f'{v_dec:.2f}" ({decimal_a_fraccion(v_dec)}")'
        st.rerun()

with tabs[1]:
    mm = st.number_input("Espesor (mm):", min_value=0.0, step=0.01, format="%.2f")
    if st.button("Identificar Calibre"):
        ref = {"10": 3.40, "12": 2.60, "14": 1.90, "16": 1.50, "18": 1.20, "20": 0.90}
        cal = min(ref.items(), key=lambda x: abs(x[1] - mm))[0]
        st.session_state.banco["cal"] = f"Ga {cal}"
        st.rerun()

with tabs[2]:
    st.write("### Verificación Final")
    if st.session_state.banco["pulg"] and st.session_state.banco["cal"]:
        cal_num = int(st.session_state.banco["cal"].replace("Ga ", ""))
        cap = CAPACIDADES_INDUSTRIALES.get(potencia_input, CAPACIDADES_INDUSTRIALES[3.0])
        
        if cal_num >= cap["calibre_seguro"]:
            st.success(f"🟢 OPERACIÓN SEGURA para {potencia_input} HP")
            mostrar_selector = True
        elif cal_num >= cap["calibre_critico"]:
            st.warning("⚠️ RIESGO DE SELLOS HIDRÁULICOS")
            mostrar_selector = st.checkbox("Continuar bajo responsabilidad")
        else:
            st.error("🚨 EXCESO DE CAPACIDAD")
            mostrar_selector = False

        if mostrar_selector:
            # EL TRUCO: 'on_change' actualiza el banco antes de que se dibuje la barra lateral
            st.radio(
                "Seleccione material:", 
                ["Acero Negro", "Galvanizado"], 
                key="mat_selector", 
                on_change=update_material_callback
            )
            
            c1, c2 = st.columns(2)
            c1.metric("ZAPATA", st.session_state.banco["pulg"])
            c2.metric("CALIBRE", st.session_state.banco["cal"])
    else:
        st.warning("⚠️ Ingrese medida y calibre en las pestañas anteriores.")

with tabs[3]:
    st.write("### Geometría")
    v1 = st.number_input("Base A (cm):", min_value=0.0)
    st.info(f"Diagonal (Cuadrado): {v1 * 1.41:.2f} cm")