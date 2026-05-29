import streamlit as st
from supabase import create_client, Client

# Configuración inicial de la página
st.set_page_config(page_title="App Entrenadores - Calafate RC", page_icon="🏉", layout="centered")

# Conexión real a Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("🏉 Calafate Rugby Club - Entrenadores")

# Pestañas principales
tab_lista, tab_crear = st.tabs(["📅 Próximos Eventos", "➕ Registrar Evento"])

with tab_lista:
    st.header("Cronograma")
    
    # 1. LEER LOS DATOS DESDE SUPABASE
    respuesta = supabase.table("eventos").select("*").order("fecha_hora").execute()
    eventos = respuesta.data
    
    if not eventos:
        st.info("Aún no hay eventos registrados. ¡Ve a la pestaña de al lado y agrega el primero!")
    else:
        for evento in eventos:
            with st.container(border=True):
                st.subheader(evento["titulo"])
                st.write(f"**Tipo:** {evento['tipo']}")
                
                # Formatear la fecha y hora para que se vea bonita
                fecha_str = evento["fecha_hora"].replace("T", " ")[:16]
                st.write(f"🕒 **Cuándo:** {fecha_str}")
                st.write(f"📍 **Dónde:** {evento['lugar']}")
                
                if evento["link_maps"]:
                    st.markdown(f"[📍 Ver ubicación en Google Maps]({evento['link_maps']})")

with tab_crear:
    st.header("Nuevo Evento")
    with st.form("form_nuevo_evento", clear_on_submit=True):
        titulo = st.text_input("Título del Evento (Ej: Partido Amistoso vs UFRO)")
        tipo = st.selectbox("Tipo", ["Partido", "Entrenamiento", "Reunión", "Tercer Tiempo"])
        fecha = st.date_input("Fecha")
        hora = st.time_input("Hora")
        lugar = st.text_input("Lugar / Cancha (Ej: Cancha Labranza)")
        link = st.text_input("Link de Google Maps (Opcional)")
        
        submit = st.form_submit_button("Guardar Evento")
        
        if submit:
            # 2. GUARDAR LOS DATOS EN SUPABASE
            # Unimos la fecha y la hora en el formato que exige la base de datos
            fecha_hora_str = f"{fecha}T{hora}"
            
            nuevo_evento = {
                "titulo": titulo,
                "tipo": tipo,
                "fecha_hora": fecha_hora_str,
                "lugar": lugar,
                "link_maps": link
            }
            
            supabase.table("eventos").insert(nuevo_evento).execute()
            st.success("¡Evento registrado exitosamente en la base de datos!")
            st.rerun() # Recarga la página para que el evento aparezca en la lista
