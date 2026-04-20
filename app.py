import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Machete-Bus V2", layout="wide")
st.title("🚌 Machete-Bus: Gestión de Memoria Avanzada")
st.markdown("### 'Ciencia y Tecnología al Servicio del Hombre' - MTI. Víctor Bianchi")

# Inicializar estado del bus (40 asientos)
if 'memoria' not in st.session_state:
    st.session_state.memoria = ["Libre"] * 40
    st.session_state.procesos = {}

# --- LÓGICA DE LOS ALGORITMOS ---
def obtener_huecos_libres():
    huecos = []
    inicio = None
    for i, estado in enumerate(st.session_state.memoria):
        if estado == "Libre":
            if inicio is None: inicio = i
        else:
            if inicio is not None:
                huecos.append((inicio, i - inicio)) # Guarda (indice_de_inicio, tamaño_del_hueco)
                inicio = None
    if inicio is not None:
        huecos.append((inicio, 40 - inicio))
    return huecos

def asignar_memoria(nombre, tam, algo, asientos_manuales=None):
    # MODO CINE (Manual)
    if algo == "Manual" and asientos_manuales:
        for i in asientos_manuales:
            st.session_state.memoria[i] = nombre
        return True
    
    huecos = [h for h in obtener_huecos_libres() if h[1] >= tam]
    if not huecos: return False # No hay espacio contiguo

    # LÓGICA DE ASIGNACIÓN
    if algo == "First-Fit":
        seleccionado = huecos[0] # El primer hueco que encuentre
    elif algo == "Best-Fit":
        seleccionado = min(huecos, key=lambda x: x[1]) # El hueco que quede más justo
    elif algo == "Worst-Fit":
        seleccionado = max(huecos, key=lambda x: x[1]) # El hueco más grande disponible
    
    # Sentar al pasajero
    for i in range(seleccionado[0], seleccionado[0] + tam):
        st.session_state.memoria[i] = nombre
    return True

# --- INTERFAZ LATERAL (Controles) ---
with st.sidebar:
    st.header("🎟️ Despacho de Pasajeros")
    nombre = st.text_input("Nombre del Proceso", "Rap_Track_01")
    res = st.number_input("Asientos Reales (RES)", 1, 40, 5)
    virt = st.number_input("Espacio Prometido (VIRT)", res, 40, 10)
    
    tipo_asignacion = st.selectbox("Algoritmo de Asignación", ["First-Fit", "Best-Fit", "Worst-Fit", "Manual"])
    
    # Selector tipo cine si eliges "Manual"
    asientos_eleccion = []
    if tipo_asignacion == "Manual":
        st.info("Modo Cine: Selecciona exactamente los asientos libres.")
        asientos_libres = [i for i, x in enumerate(st.session_state.memoria) if x == "Libre"]
        asientos_eleccion = st.multiselect("Elige tus asientos:", asientos_libres)

    if st.button("Vender Boleto"):
        if tipo_asignacion == "Manual" and len(asientos_eleccion) != res:
            st.error(f"Error: Debes seleccionar exactamente {res} asientos (RES).")
        elif asignar_memoria(nombre, res, tipo_asignacion, asientos_eleccion):
            st.session_state.procesos[nombre] = {"RES": res, "VIRT": virt, "Algoritmo": tipo_asignacion}
            st.success(f"¡{nombre} abordó con éxito!")
        else:
            st.error("Error: No hay espacio contiguo suficiente (Fragmentación Externa).")

# --- VISUALIZACIÓN DEL BUS ---
st.subheader("🗺
