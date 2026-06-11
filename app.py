import streamlit as st
import base64
from supabase import create_client, Client

st.set_page_config(page_title="App Entrenadores - Calafate RC", page_icon="🏉", layout="centered")

# --- CONTROL DE ACCESOS ---
CORREO_ADMIN = "b.neirarc@gmail.com" 

# Agrega aquí los correos de todos los que deben tener permisos de Entrenador
CORREOS_ENTRENADORES = [
    "b.neirarc@gmail.com",
    "bastian.venegasenois@gmail.com",
    "claudio.leiva.temuco@gmail.com",
    "jmgonz652@gmail.com"
    "eamcfit@gmail.com"
]

def agregar_fondo_local(ruta_imagen):
    try:
        with open(ruta_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            div[data-testid="stExpander"] {{
                background-color: rgba(0, 0, 0, 0.75);
                border-radius: 10px;
                border: 1px solid #444;
            }}
            input {{ color: #000000 !important; }}
            button p {{ color: #000000 !important; }}
            button[data-baseweb="tab"] p {{ color: #FFFFFF !important; }}
            div[data-baseweb="select"] * {{ color: #000000 !important; }}
            div[role="listbox"] * {{ color: #000000 !important; }}
            div[data-baseweb="popover"] * {{ color: #000000 !important; }}
            
            /* --- CORRECCIÓN PARA CELULARES --- */
            @media (max-width: 768px) {{
                div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {{
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                }}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"No se encontró la imagen '{ruta_imagen}'.")

agregar_fondo_local("fondo.png")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

POSICIONES_CANCHA = {
    1: {"x": 30, "y": 10}, 2: {"x": 50, "y": 10}, 3: {"x": 70, "y": 10},
    4: {"x": 40, "y": 20}, 5: {"x": 60, "y": 20},
    6: {"x": 20, "y": 30}, 8: {"x": 50, "y": 35}, 7: {"x": 80, "y": 30},
    9: {"x": 50, "y": 45},
    10: {"x": 30, "y": 55},
    12: {"x": 40, "y": 65}, 13: {"x": 60, "y": 65},
    11: {"x": 10, "y": 70}, 14: {"x": 90, "y": 70},
    15: {"x": 50, "y": 85}
}

if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'materiales_copiados' not in st.session_state:
    st.session_state.materiales_copiados = None

if st.session_state.usuario is None:
    st.title("🏉 Calafate Rugby Club")
    st.subheader("Portal del Club")
    
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab_login:
        with st.form("form_login"):
            email_login = st.text_input("Correo electrónico")
            pass_login = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("Entrar")
            if btn_login:
                try:
                    respuesta = supabase.auth.sign_in_with_password({"email": email_login, "password": pass_login})
                    st.session_state.usuario = respuesta.user
                    st.rerun()
                except Exception as e:
                    st.error("Error al iniciar sesión.")

    with tab_registro:
        with st.form("form_registro"):
            email_reg = st.text_input("Nuevo correo electrónico")
            pass_reg = st.text_input("Crear contraseña (mínimo 6 caracteres)", type="password")
            btn_reg = st.form_submit_button("Crear cuenta")
            if btn_reg:
                try:
                    supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                    st.success("¡Registro exitoso! Ahora inicia sesión.")
                except Exception as e:
                    st.error("Hubo un error en el registro.")

else:
    # --- VERIFICAR ROL DEL USUARIO ACTUAL ---
    correo_actual = st.session_state.usuario.email
    es_entrenador = correo_actual in CORREOS_ENTRENADORES
    es_admin = correo_actual == CORREO_ADMIN

    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        if es_entrenador:
            st.title("🏉 Panel de Entrenadores")
        else:
            st.title("🏉 Portal de Jugadores")
        
        st.write(f"👤 Conectado como: **{correo_actual}**")
        
        if es_admin:
            st.caption("👑 Administrador General")
        elif es_entrenador:
            st.caption("📋 Permisos de Entrenador")
            
    with col2:
        if st.button("Cerrar Sesión"):
            supabase.auth.sign_out()
            st.session_state.usuario = None
            st.rerun()

    st.write("---")
    
    # --- DISTRIBUCIÓN DE PESTAÑAS PRINCIPALES SEGÚN EL ROL ---
    if es_entrenador:
        tabs_principales = st.tabs(["📅 Próximos Eventos", "➕ Registrar Evento"])
        tab_lista = tabs_principales[0]
        tab_crear = tabs_principales[1]
    else:
        tabs_principales = st.tabs(["📅 Próximos Eventos"])
        tab_lista = tabs_principales[0]
        tab_crear = None

    with tab_lista:
        st.header("Cronograma")
        respuesta = supabase.table("eventos").select("*").order("fecha_hora").execute()
        eventos = respuesta.data
        
        if not eventos:
            st.info("Aún no hay eventos registrados.")
        else:
            for evento in eventos:
                with st.expander(f"➔ {evento['titulo']} ({evento['tipo']})"):
                    
                    # --- DISTRIBUCIÓN DE PESTAÑAS INTERNAS SEGÚN EL ROL ---
                    if es_entrenador:
                        tabs_evento = st.tabs(["Detalles", "📋 Alineación", "🏟️ Cancha", "📦 Materiales", "👥 Editar Encargados"])
                        sub_info = tabs_evento[0]
                        sub_alineacion = tabs_evento[1]
                        sub_cancha = tabs_evento[2]
                        sub_materiales = tabs_evento[3]
                        sub_encargados = tabs_evento[4]
                    else:
                        tabs_evento = st.tabs(["ℹ️ Detalles del Evento"])
                        sub_info = tabs_evento[0]
                    
                    # 1. PESTAÑA DE DETALLES (Visible para todos)
                    with sub_info:
                        fecha_str = evento["fecha_hora"].replace("T", " ")[:16]
                        st.write(f"🕒 **Cuándo:** {fecha_str}")
                        st.write(f"📍 **Dónde:** {evento['lugar']}")
                        if evento["link_maps"]:
                            st.markdown(f"[📍 Ver ubicación en Google Maps]({evento['link_maps']})")
                        
                        res_enc_ver = supabase.table("encargados").select("*").eq("evento_id", evento["id"]).order("id").execute()
                        if res_enc_ver.data:
                            nombres_enc = [e["nombre"] for e in res_enc_ver.data]
                            st.write(f"👥 **Encargados:** {', '.join(nombres_enc)}")
                        
                        st.write("---")
                        st.write("💬 **Comentarios:**")
                        res_comentarios = supabase.table("comentarios").select("*").eq("evento_id", evento["id"]).order("creado_en").execute()
                        if res_comentarios.data:
                            for com in res_comentarios.data:
                                st.markdown(f"**{com['email_usuario'].split('@')[0]}**: {com['texto']}")
                        else:
                            st.caption("No hay comentarios.")
                        
                        col_i, col_b = st.columns([0.7, 0.3])
                        with col_i:
                            nuevo_com = st.text_input("Comentar...", key=f"in_com_{evento['id']}", label_visibility="collapsed")
                        with col_b:
                            if st.button("Enviar", key=f"btn_com_{evento['id']}") and nuevo_com:
                                supabase.table("comentarios").insert({"evento_id": evento["id"], "email_usuario": correo_actual, "texto": nuevo_com}).execute()
                                st.rerun()

                        if es_admin:
                            st.write("---")
                            if st.button("🗑️ Eliminar Evento", key=f"borrar_{evento['id']}", type="primary"):
                                supabase.table("eventos").delete().eq("id", evento["id"]).execute()
                                st.success("Evento eliminado.")
                                st.rerun()

                    # BLOQUE EXCLUSIVO PARA ENTRENADORES
                    if es_entrenador:
                        res_alineacion = supabase.table("alineaciones").select("*").eq("evento_id", evento["id"]).execute()
                        alineacion_actual = {item["numero"]: item["jugador"] for item in res_alineacion.data}

                        with sub_alineacion:
                            with st.form(f"form_al_{evento['id']}"):
                                cols_form = st.columns(3)
                                nuevos_jugadores = {}
                                for num in range(1, 24):
                                    col_idx = (num - 1) % 3
                                    valor_actual = alineacion_actual.get(num, "")
                                    with cols_form[col_idx]:
                                        nuevos_jugadores[num] = st.text_input(f"N° {num}", value=valor_actual, key=f"jug_{evento['id']}_{num}")
                                
                                if st.form_submit_button("Guardar Alineación"):
                                    supabase.table("alineaciones").delete().eq("evento_id", evento["id"]).execute()
                                    datos_insertar = [{"evento_id": evento["id"], "numero": n, "jugador": nom} for n, nom in nuevos_jugadores.items() if nom.strip() != ""]
                                    if datos_insertar:
                                        supabase.table("alineaciones").insert(datos_insertar).execute()
                                    st.success("Alineación guardada.")
                                    st.rerun()

                        with sub_cancha:
                            html_cancha = """<div style="background-color: #2e7d32; border: 3px solid white; border-radius: 8px; position: relative; height: 500px; width: 100%; overflow: hidden; margin-bottom: 20px;">
    <div style="position: absolute; top: 15%; left: 0; width: 100%; border-top: 2px dashed rgba(255,255,255,0.4);"></div>
    <div style="position: absolute; top: 50%; left: 0; width: 100%; border-top: 3px solid rgba(255,255,255,0.8);"></div>
    <div style="position: absolute; top: 85%; left: 0; width: 100%; border-top: 2px dashed rgba(255,255,255,0.4);"></div>
    """
                            for num in range(1, 16):
                                nombre = alineacion_actual.get(num, "---")
                                opacidad = "1.0" if nombre != "---" else "0.4"
                                pos = POSICIONES_CANCHA[num]
                                html_cancha += f"""<div style="position: absolute; top: {pos['y']}%; left: {pos['x']}%; transform: translate(-50%, -50%); text-align: center; opacity: {opacidad};">
    <div style="background-color: #000; color: #fff; border: 2px solid white; border-radius: 50%; width: 28px; height: 28px; line-height: 24px; font-size: 12px; font-weight: bold; margin: 0 auto;">{num}</div>
    <div style="color: white; font-size: 11px; font-weight: bold; text-shadow: 1px 1px 2px black; background: rgba(0,0,0,0.5); padding: 2px 4px; border-radius: 4px; margin-top: 2px; white-space: nowrap;">{nombre}</div>
    </div>
    """
                            html_cancha += "</div>"
                            st.markdown(html_cancha, unsafe_allow_html=True)
                            
                            st.markdown("### Reservas")
                            reservas = [f"**{num}:** {alineacion_actual.get(num, '---')}" for num in range(16, 24)]
                            col_r1, col_r2 = st.columns(2)
                            with col_r1:
                                for r in reservas[:4]: st.markdown(r)
                            with col_r2:
                                for r in reservas[4:]: st.markdown(r)

                        with sub_materiales:
                            res_mat = supabase.table("materiales").select("*").eq("evento_id", evento["id"]).order("id").execute()
                            materiales_actuales = res_mat.data
                            
                            col_cp1, col_cp2 = st.columns(2)
                            with col_cp1:
                                if st.button("📋 Copiar Lista", key=f"btn_copy_mat_{evento['id']}"):
                                    st.session_state.materiales_copiados = [{"elemento": m["elemento"], "cantidad": m["cantidad"], "estado": m["estado"]} for m in materiales_actuales]
                                    st.success("¡Lista copiada!")
                            with col_cp2:
                                if st.session_state.materiales_copiados is not None:
                                    if st.button("📋 Pegar Lista", key=f"btn_paste_mat_{evento['id']}"):
                                        supabase.table("materiales").delete().eq("evento_id", evento["id"]).execute()
                                        datos_pegar = [{"evento_id": evento["id"], "elemento": mc["elemento"], "cantidad": mc["cantidad"], "estado": mc["estado"]} for mc in st.session_state.materiales_copiados]
                                        if datos_pegar:
                                            supabase.table("materiales").insert(datos_pegar).execute()
                                        st.success("¡Lista pegada!")
                                        st.rerun()

                            with st.form(f"form_mat_{evento['id']}"):
                                nuevos_materiales = []
                                filas_totales = len(materiales_actuales) + 3
                                if filas_totales > 30: filas_totales = 30
                                if filas_totales == 0: filas_totales = 3 
                                
                                for i in range(filas_totales):
                                    val_el = materiales_actuales[i]["elemento"] if i < len(materiales_actuales) else ""
                                    val_cant = materiales_actuales[i]["cantidad"] if i < len(materiales_actuales) else ""
                                    val_est = materiales_actuales[i]["estado"] if i < len(materiales_actuales) else "Ok"
                                    idx_est = 0 if val_est == "Ok" else 1
                                    
                                    c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
                                    with c1: el = st.text_input("Elemento", value=val_el, key=f"mat_el_{evento['id']}_{i}", label_visibility="visible" if i == 0 else "collapsed")
                                    with c2: cant = st.text_input("Cant.", value=val_cant, key=f"mat_ca_{evento['id']}_{i}", label_visibility="visible" if i == 0 else "collapsed")
                                    with c3: est = st.selectbox("Estado", ["Ok", "Falta"], index=idx_est, key=f"mat_es_{evento['id']}_{i}", label_visibility="visible" if i == 0 else "collapsed")
                                    
                                    if el.strip() != "":
                                        nuevos_materiales.append({"evento_id": evento["id"], "elemento": el, "cantidad": cant, "estado": est})
                                
                                if st.form_submit_button("Guardar Lista de Materiales"):
                                    supabase.table("materiales").delete().eq("evento_id", evento["id"]).execute()
                                    if nuevos_materiales:
                                        supabase.table("materiales").insert(nuevos_materiales).execute()
                                    st.success("¡Inventario guardado con éxito!")
                                    st.rerun()

                        with sub_encargados:
                            st.write("Edita a los responsables de esta actividad si es necesario.")
                            res_enc_edit = supabase.table("encargados").select("*").eq("evento_id", evento["id"]).order("id").execute()
                            encargados_actuales = res_enc_edit.data

                            with st.form(f"form_enc_edit_{evento['id']}"):
                                nuevos_encargados = []
                                for i in range(5):
                                    val_nombre = encargados_actuales[i]["nombre"] if i < len(encargados_actuales) else ""
                                    nombre = st.text_input(f"Responsable {i+1}", value=val_nombre, key=f"enc_edit_{evento['id']}_{i}")
                                    
                                    if nombre.strip() != "":
                                        nuevos_encargados.append({"evento_id": evento["id"], "nombre": nombre})

                                if st.form_submit_button("Actualizar Encargados"):
                                    supabase.table("encargados").delete().eq("evento_id", evento["id"]).execute()
                                    if nuevos_encargados:
                                        supabase.table("encargados").insert(nuevos_encargados).execute()
                                    st.success("Responsables actualizados con éxito.")
                                    st.rerun()

    # --- PESTAÑA PARA CREAR EVENTO (Exclusiva para entrenadores) ---
    if es_entrenador and tab_crear is not None:
        with tab_crear:
            st.header("Nuevo Evento")
            with st.form("form_nuevo_evento", clear_on_submit=True):
                titulo = st.text_input("Título del Evento")
                tipo = st.selectbox("Tipo", ["Partido", "Entrenamiento", "Festival", "Reunión", "Tercer Tiempo"])
                fecha = st.date_input("Fecha")
                hora = st.time_input("Hora")
                lugar = st.text_input("Lugar / Cancha")
                link = st.text_input("Link de Google Maps (Opcional)")
                
                st.write("---")
                st.write("👥 **Designar Encargados (Máximo 5)**")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    enc1 = st.text_input("Encargado 1")
                    enc3 = st.text_input("Encargado 3")
                    enc5 = st.text_input("Encargado 5")
                with col_e2:
                    enc2 = st.text_input("Encargado 2")
                    enc4 = st.text_input("Encargado 4")
                
                submit = st.form_submit_button("Guardar Evento")
                
                if submit:
                    fecha_hora_str = f"{fecha}T{hora}"
                    nuevo_evento = {"titulo": titulo, "tipo": tipo, "fecha_hora": fecha_hora_str, "lugar": lugar, "link_maps": link}
                    
                    respuesta_insercion = supabase.table("eventos").insert(nuevo_evento).execute()
                    nuevo_id = respuesta_insercion.data[0]['id']
                    
                    lista_encargados = [enc1, enc2, enc3, enc4, enc5]
                    datos_encargados = [{"evento_id": nuevo_id, "nombre": e.strip()} for e in lista_encargados if e.strip() != ""]
                    
                    if datos_encargados:
                        supabase.table("encargados").insert(datos_encargados).execute()
                    
                    st.success("¡Evento registrado exitosamente!")
                    st.rerun()
