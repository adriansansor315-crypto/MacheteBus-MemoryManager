import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Machete-Bus V2", layout="wide")
st.title("🚌 Machete-Bus: Gestión de Memoria Avanzada")

# Inicializar estado del bus (40 asientos)
if 'memoria' not in st.session_state:
    st.session_state.memoria = ["Libre"] * 40
    st.session_state.procesos = {}

# --- FUNCIONES DE ALGORITMOS ---
def obtener_huecos_libres():
    huecos = []
    inicio = None
    for i, estado in enumerate(st.session_state.memoria):
        if estado == "Libre":
            if inicio is None: inicio = i
        else:
            if inicio is not None:
                huecos.append((inicio, i - inicio)) # (indice_inicio, tamaño)
                inicio = None
    if inicio is not None:
        huecos.append((inicio, 40 - inicio))
    return huecos

def asignar_memoria(nombre, tam, algo, asientos_manuales=None):
    if algo == "Manual" and asientos_manuales:
        for i in asientos_manuales:
            st.session_state.memoria[i] = nombre
        return True
    
    huecos = [h for h in obtener_huecos_libres() if h[1] >= tam]
    if not huecos: return False

    # Lógica por Algoritmo
    if algo == "First-Fit":
        seleccionado = huecos[0]
    elif algo == "Best-Fit":
        seleccionado = min(huecos, key=lambda x: x[1])
    elif algo == "Worst-Fit":
        seleccionado = max(huecos, key=lambda x: x[1])
    
    for i in range(seleccionado[0], seleccionado[0] + tam):
        st.session_state.memoria[i] = nombre
    return True

# --- SIDEBAR: DESPACHO ---
with st.sidebar:
    st.header("🎟️ Despacho de Pasajeros")
    nombre = st.text_input("Nombre del Proceso", "Rap_Track_02")
    res = st.number_input("Asientos Reales (RES)", 1, 40, 5)
    virt = st.number_input("Espacio Prometido (VIRT)", res, 40, 10)
    
    tipo_asignacion = st.selectbox("Algoritmo", ["First-Fit", "Best-Fit", "Worst-Fit", "Manual"])
    
    asientos_eleccion = []
    if tipo_asignacion == "Manual":
        st.info("Selecciona exactamente los asientos en el mapa principal.")
        asientos_eleccion = st.multiselect("Asientos elegidos:", 
                                         [i for i, x in enumerate(st.session_state.memoria) if x == "Libre"])

    if st.button("Vender Boleto"):
        if tipo_asignacion == "Manual" and len(asientos_eleccion) != res:
            st.error(f"Debes seleccionar exactamente {res} asientos.")
        elif asignar_memoria(nombre, res, tipo_asignacion, asientos_eleccion):
            st.session_state.procesos[nombre] = {"RES": res, "VIRT": virt, "Algo": tipo_asignacion}
            st.success("¡Abordaje exitoso!")
        else:
            st.error("Error: No hay espacio suficiente (Fragmentación Externa).")

# --- VISUALIZACIÓN ---
st.subheader("🗺️ Mapa de Ocupación (RAM)")
cols = st.columns(10)
for i, estado in enumerate(st.session_state.memoria):
    color = "🟩" if estado == "Libre" else "🟥"
    label = f"{i}: {color}" if estado == "Libre" else f"{i}: {estado}"
    cols[i % 10].info(label)

# --- MONITOR ---
st.divider()
if st.session_state.procesos:
    st.table(pd.DataFrame(st.session_state.procesos).T)

if st.button("🚨 OOM Killer"):
    if st.session_state.procesos:
        borrar = max(st.session_state.procesos, key=lambda x: st.session_state.procesos[x]['RES'])
        st.session_state.memoria = ["Libre" if x == borrar else x for x in st.session_state.memoria]
        del st.session_state.procesos[borrar]
        st.rerun()
