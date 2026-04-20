import streamlit as st
import pandas as pd
import random

# Configuración de la página con tu estilo
st.set_page_config(page_title="Machete-Bus: Memory Manager", layout="wide")

st.title("🚌 Machete-Bus: Gestión de Memoria Urbana")
st.markdown("### 'Ciencia y Tecnología al Servicio del Hombre' - MTI. Víctor Bianchi")

# --- LÓGICA DE MEMORIA ---
if 'memoria' not in st.session_state:
    # Representamos 40 asientos (bloques de memoria) [cite: 10]
    st.session_state.memoria = ["Libre"] * 40
    st.session_state.procesos = {} # Para rastrear VIRT vs RES [cite: 18, 19]

def asignar_memoria(nombre, tamaño_res, tamaño_virt, algoritmo):
    # Aquí implementarías la lógica de First-Fit, Best-Fit o Worst-Fit 
    # Por ahora, una simulación simple de ocupación:
    espacios_libres = [i for i, x in enumerate(st.session_state.memoria) if x == "Libre"]
    
    if len(espacios_libres) >= tamaño_res:
        for i in range(tamaño_res):
            idx = espacios_libres[i]
            st.session_state.memoria[idx] = nombre
        st.session_state.procesos[nombre] = {"RES": tamaño_res, "VIRT": tamaño_virt}
        return True
    return False

# --- INTERFAZ LATERAL (Controles) ---
with st.sidebar:
    st.header("🎟️ Despacho de Pasajeros")
    nombre_p = st.text_input("Nombre del Proceso (Pasajero)", "Rap_Track_01")
    res = st.number_input("Asientos Reales (RES)", min_value=1, max_value=10)
    virt = st.number_input("Espacio Prometido (VIRT)", min_value=res, max_value=20)
    
    algo = st.selectbox("Algoritmo de Asignación", ["First-Fit", "Best-Fit", "Worst-Fit"])
    
    if st.button("Vender Boleto"):
        if asignar_memoria(nombre_p, res, virt, algo):
            st.success(f"Pasajero {nombre_p} abordó con éxito.")
        else:
            st.error("¡No hay asientos contiguos! (Fragmentación Externa)")

# --- VISUALIZACIÓN DEL BUS ---
st.subheader("🗺️ Mapa de Ocupación (RAM)")
cols = st.columns(10) # 10 columnas para los 40 asientos
for i, asiento in enumerate(st.session_state.memoria):
    color = "🟩" if asiento == "Libre" else "🟥"
    cols[i % 10].write(f"{i+1}: {color}\n({asiento})")

# --- MONITOR DE RECURSOS (Actividad 2) ---
st.divider()
st.subheader("📊 Monitor de Procesos (htop style)")
if st.session_state.procesos:
    df = pd.DataFrame(st.session_state.procesos).T
    st.table(df)
    st.info("VIRT: Espacio que el pasajero dice que podría ocupar. RES: Asientos reales ocupados. [cite: 19, 20]")

# --- BOTÓN DE EMERGENCIA (OOM Killer) ---
if st.button("🚨 Activar OOM Killer"):
    # El Kernel decide matar al proceso más voraz 
    if st.session_state.procesos:
        voraz = max(st.session_state.procesos, key=lambda x: st.session_state.procesos[x]['RES'])
        st.warning(f"El Kernel ha expulsado a: {voraz} por exceso de equipaje.")
        st.session_state.memoria = ["Libre" if x == voraz else x for x in st.session_state.memoria]
        del st.session_state.procesos[voraz]
        st.rerun()