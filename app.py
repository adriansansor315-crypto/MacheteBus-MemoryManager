import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Machete-Bus V3", layout="wide")
st.title("🚌 Machete-Bus: Gestión de Memoria y Swap")
st.markdown("### 'Ciencia y Tecnología al Servicio del Hombre' - MTI. Víctor Bianchi")

# Inicializar estado del bus y la banqueta
if 'memoria' not in st.session_state:
    st.session_state.memoria = ["Libre"] * 40
    st.session_state.procesos = {}
    st.session_state.swap = [] # La "Banqueta" para el desborde

def obtener_huecos_libres():
    huecos = []
    inicio = None
    for i, estado in enumerate(st.session_state.memoria):
        if estado == "Libre":
            if inicio is None: inicio = i
        else:
            if inicio is not None:
                huecos.append((inicio, i - inicio))
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

    if algo == "First-Fit": seleccionado = huecos[0]
    elif algo == "Best-Fit": seleccionado = min(huecos, key=lambda x: x[1])
    elif algo == "Worst-Fit": seleccionado = max(huecos, key=lambda x: x[1])
    
    for i in range(seleccionado[0], seleccionado[0] + tam):
        st.session_state.memoria[i] = nombre
    return True

# --- INTERFAZ LATERAL ---
with st.sidebar:
    st.header("🎟️ Despacho de Pasajeros")
    nombre = st.text_input("Nombre del Proceso", "Juego_Pesado")
    
    # Aumentamos el límite a 100 para permitir el desborde intencional
    res = st.number_input("Asientos Reales (RES)", 1, 100, 40)
    virt = st.number_input("Espacio Prometido (VIRT)", res, 150, res + 10)
    
    tipo_asignacion = st.selectbox("Algoritmo de Asignación", ["First-Fit", "Best-Fit", "Worst-Fit", "Manual"])
    
    asientos_eleccion = []
    if tipo_asignacion == "Manual":
        asientos_libres = [i for i, x in enumerate(st.session_state.memoria) if x == "Libre"]
        asientos_eleccion = st.multiselect("Elige tus asientos:", asientos_libres)

    if st.button("Vender Boleto"):
        if tipo_asignacion == "Manual" and len(asientos_eleccion) != res:
            st.error(f"Error: Selecciona exactamente {res} asientos.")
        elif asignar_memoria(nombre, res, tipo_asignacion, asientos_eleccion):
            st.session_state.procesos[nombre] = {"RES": res, "VIRT": virt, "Algoritmo": tipo_asignacion}
            st.success(f"¡{nombre} abordó el bus con éxito!")
        else:
            # LÓGICA DE DESBORDE (SWAP)
            st.warning(f"⚠️ Alerta de Desborde: El bus no tiene capacidad. Enviando a '{nombre}' a la Banqueta (Swap-Out).")
            st.session_state.swap.append({"Nombre": nombre, "RES": res, "VIRT": virt})

# --- VISUALIZACIÓN DEL BUS (RAM) ---
st.subheader("🗺️ Mapa de Ocupación (RAM Física)")
cols = st.columns(10)
for i, estado in enumerate(st.session_state.memoria):
    color = "🟩" if estado == "Libre" else "🟥"
    label = f"{i}: {color}" if estado == "Libre" else f"{i}: {estado}"
    cols[i % 10].info(label)

# --- VISUALIZACIÓN DE LA BANQUETA (SWAP) ---
st.divider()
st.subheader("🚏 La Banqueta (Memoria Swap)")
if st.session_state.swap:
    cols_swap = st.columns(min(len(st.session_state.swap), 5)) # Hasta 5 columnas para la banqueta
    for idx, proceso in enumerate(st.session_state.swap):
        cols_swap[idx % 5].error(f"🧍‍♂️ {proceso['Nombre']}\n(Pide {proceso['RES']} asientos)")
else:
    st.success("La banqueta está vacía (Uso de Swap: 0 bytes)")

# --- MONITOR Y OOM KILLER ---
st.divider()
st.subheader("📊 Monitor de Procesos Activos (htop)")
if st.session_state.procesos:
    st.table(pd.DataFrame(st.session_state.procesos).T)

if st.button("🚨 Activar OOM Killer"):
    if st.session_state.procesos:
        borrar = max(st.session_state.procesos, key=lambda x: st.session_state.procesos[x]['RES'])
        st.error(f"OOM Killer: El Kernel expulsó a '{borrar}' para salvar el sistema.")
        st.session_state.memoria = ["Libre" if x == borrar else x for x in st.session_state.memoria]
        del st.session_state.procesos[borrar]
        st.rerun()
