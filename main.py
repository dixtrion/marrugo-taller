import streamlit as st
import math

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema Marrugo Pro", page_icon="🛠️", layout="centered")

# Estilo Industrial Personalizado (Colores de taller: Negro, Gris y Rojo de advertencia)
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
    div[data-testid="stMetricValue"] { font-size: 28px; color: #0e1117; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- BANCO DE DATOS (Persistencia en la sesión web) ---
if "banco" not in st.session_state:
    st.session_state.banco = {"pulg": None, "cal": None, "mat": None}


def decimal_a_fraccion(decimal):
    """Convierte decimales a la fracción comercial más cercana en octavos"""
    fracciones = {
        0.0: "",
        0.125: "1/8",
        0.25: "1/4",
        0.375: "3/8",
        0.5: "1/2",
        0.625: "5/8",
        0.75: "3/4",
        0.875: "7/8",
    }
    entero = int(decimal)
    residuo = round(decimal - entero, 3)
    # Encuentra la fracción más cercana en el banco de datos de octavos
    cercano = min(fracciones.keys(), key=lambda x: abs(x - residuo))
    frac_txt = fracciones[cercano]

    if entero > 0:
        return f"{entero} {frac_txt}".strip()
    return frac_txt if frac_txt else "0"


# --- INTERFAZ PRINCIPAL ---
st.title("🛠️ Sistema Técnico Marrugo")
st.write("Control de Calidad e Ingeniería de Doblado")

# Barra lateral con información de autor y estado
st.sidebar.header("📍 Resumen del Banco")
st.sidebar.markdown(f"**Tubo:** {st.session_state.banco['pulg'] or '---'}")
st.sidebar.markdown(f"**Calibre:** {st.session_state.banco['cal'] or '---'}")
st.sidebar.markdown(f"**Material:** {st.session_state.banco['mat'] or '---'}")

if st.sidebar.button("🧹 Limpiar Banco"):
    st.session_state.banco = {"pulg": None, "cal": None, "mat": None}
    st.rerun()

# SELLO DE AUTORÍA: Dixtrion Electronic
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.85em;'>
        Desarrollado por:<br>
        <strong style='color: #0e1117;'>Dixtrion Electronic</strong><br>
        <a href='mailto:marrugonelson@gmail.com' style='color: #ed1c24; text-decoration: none;'>marrugonelson@gmail.com</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Organización por pestañas (Tabs) para facilitar el uso en móvil
tabs = st.tabs(["📏 Medición", "📐 Calibre", "🚀 Diagnóstico", "📐 Geometría"])

# --- PESTAÑA 1: CONVERSIÓN DE MEDIDA ---
with tabs[0]:
    st.write("### Centímetros a Pulgadas")
    cm = st.number_input(
        "Circunferencia del tubo (cm):", min_value=0.0, step=0.1, key="cm_web"
    )
    if st.button("Procesar Medida"):
        # Fórmula maestra: cm / 8
        v_dec = cm / 8
        frac = decimal_a_fraccion(v_dec)
        st.session_state.banco["pulg"] = f'{v_dec:.2f}" ({frac}")'
        st.success(f"Registrado: {st.session_state.banco['pulg']}")

# --- PESTAÑA 2: IDENTIFICACIÓN DE CALIBRE ---
with tabs[1]:
    st.write("### Identificador de Calibre (Ga)")
    mm = st.number_input(
        "Espesor de pared (mm):", min_value=0.0, step=0.01, format="%.2f", key="mm_web"
    )
    if st.button("Identificar Calibre"):
        # Banco de datos de referencia (Incluye calibres prohibidos para seguridad)
        ref = {
            "10": 3.40,
            "12": 2.60,
            "14": 1.90,
            "16": 1.50,
            "18": 1.20,
            "19": 1.00,
            "20": 0.90,
        }
        cal = min(ref.items(), key=lambda x: abs(x[1] - mm))[0]
        st.session_state.banco["cal"] = cal
        st.success(f"Calibre Detectado: Ga {cal}")

# --- PESTAÑA 3: DIAGNÓSTICO Y SEGURIDAD ---
with tabs[2]:
    st.write("### Verificación Final")

    if st.session_state.banco["pulg"] and st.session_state.banco["cal"]:
        cal_num = int(st.session_state.banco["cal"])

        # BLOQUEO DE SEGURIDAD PARA MAQUINARIA DE 8 HP (Límite Ga 14)
        if cal_num < 14:
            st.error("🚨 ALERTA DE SEGURIDAD CRÍTICA")
            st.markdown(
                f"""
            **CALIBRE DETECTADO:** Ga {cal_num} (Muy Grueso)
            
            **ADVERTENCIA:** Este material excede la capacidad estructural de la dobladora.
            
            **ESTADO:** BLOQUEADO. No se permite el cálculo de zapata para evitar:
            * Rotura de mangueras y sellos hidráulicos.
            * Fatiga del motor de 8 HP.
            * Deformación permanente de troqueles.
            """
            )
        else:
            mat = st.radio("Seleccione material:", ["Acero Negro", "Galvanizado"])
            st.session_state.banco["mat"] = mat

            # Visualización de resultados principales
            col1, col2 = st.columns(2)
            col1.metric("ZAPATA SUGERIDA", st.session_state.banco["pulg"])
            col2.metric("ESPESOR REAL", f"Ga {cal_num}")

            if mat == "Galvanizado":
                st.warning(
                    "⚠️ AVISO: Material rígido. Realizar dobleces con progresión lenta."
                )
            else:
                st.success(
                    "🟢 AVISO: Acero Negro maleable. Óptimo para sistemas de escape."
                )
    else:
        st.warning(
            "⚠️ Faltan datos. Ingrese medida y calibre en las pestañas anteriores."
        )

# --- PESTAÑA 4: GEOMETRÍA DE PRECISIÓN ---
with tabs[3]:
    st.write("### Cálculos de Geometría")
    op_geo = st.selectbox(
        "Seleccione herramienta:",
        [
            "Altura Triángulo (86.6%)",
            "Diagonal Cuadrado (1.41)",
            "Escuadra (Hipotenusa)",
        ],
    )
    v1 = st.number_input("Medida base A (cm):", min_value=0.0)

    if op_geo == "Escuadra (Hipotenusa)":
        v2 = st.number_input("Medida base B (cm):", min_value=0.0)
        st.info(f"**Longitud de Hipotenusa:** {math.sqrt(v1**2 + v2**2):.2f} cm")
    elif "Triángulo" in op_geo:
        st.info(f"**Altura del Triángulo:** {v1 * 0.866:.2f} cm")
    else:
        st.info(f"**Longitud de Diagonal:** {v1 * 1.41:.2f} cm")
