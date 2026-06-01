import streamlit as st
import base64
from supabase import create_client, Client

# Configuración inicial
st.set_page_config(page_title="App Entrenadores - Calafate RC", page_icon="🏉", layout="centered")

# --- CONFIGURACIÓN DE ADMINISTRADOR ---
CORREO_ADMIN = "b.neirarc@gmail.com" 

# Fondo y Diseño Visual
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
            /* Forzar texto negro en cajas de texto normales */
            input {{
                color: #000000 !important;
            }}
            /* Forzar texto negro en botones de acción */
            button p {{
                color: #000000 !important;
            }}
            /* Letras blancas para las pestañas de navegación */
            button[data-baseweb="tab"] p {{
                color: #FFFFFF !important;
            }}
            /* Forzar texto negro en listas desplegables y calendarios */
            div[data-baseweb="select"] * {{
                color: #000000 !important;
            }}
            div[role="listbox"] * {{
                color: #000000 !important;
            }}
            div[data-baseweb="popover"] * {{
                color: #000000 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"No se encontró la imagen '{ruta_imagen}'.")

agregar_fondo_local("fondo.png")

# Conexión a Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# --- MAPA DE COORDENADAS DE LA CANCHA DE RUGBY (1 al 15) ---
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

# --- INICIALIZAR VARIABLES DE SESIÓN ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'materiales_copiados' not in st.session_state:
    st.session_state.materiales_copiados = None

# --- PANTALLAS DE ACCESO ---
if st.session_state.usuario is None:
    st.title("🏉 Calafate Rugby Club")
    st.subheader("Acceso Restringido")
    
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
                    st.error("Error al iniciar sesión. Verifica tu correo y contraseña.")

    with tab_registro:
        with st.form("form_registro"):
            email_reg = st.text_input("Nuevo correo electrónico")
            pass_reg = st.text_input("Crear contraseña (mínimo 6 caracteres)", type="password")
            btn_reg = st.form_submit_button("Crear cuenta")
            if btn_reg:
                try:
                    supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                    st.success("¡Registro exitoso! Ahora puedes ir a 'Iniciar Sesión' y entrar.")
                except Exception as e:
                    st.error("Hubo un error en el registro.")

# --- APLICACIÓN PRINCIPAL ---
else:
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("🏉 Panel de Entrenadores")
        st.write(f"👤 Conectado como: **{st.session_state.usuario.email}**")
        if st.session_state.usuario.email == CORREO_ADMIN:
            st.caption("👑 Tienes permisos de Administrador")
            
    with col2:
        if st.button("Cerrar Sesión"):
            supabase.auth.sign_out()
            st.session_state.usuario = None
            st.rerun()

    st.write("---")

    tab_lista, tab_crear = st.tabs(["📅 Próximos Eventos", "➕ Registrar Evento"])

    with tab_lista:
        st.header("Cronograma")
        respuesta = supabase.table("eventos").select("*").order("fecha_hora").execute()
        eventos = respuesta.data
        
        if not eventos:
            st.info("Aún no hay eventos registrados.")
        else:
            for evento in eventos:
                with st.expander(f"➔ {evento['titulo']} ({evento['tipo']})"):
                    # Agregada la pestaña 'Materiales'
                    sub_info, sub_alineacion, sub_cancha, sub_materiales = st.tabs([
                        "Detalles y Comentarios", "📋 Editar Alineación", "🏟️ Cancha Virtual", "📦 Materiales"
                    ])
                    
                    # 1. DETALLES Y COMENTARIOS
                    with sub_info:
                        fecha_str = evento["fecha_hora"].replace("T", " ")[:16]
                        st.write(f"🕒 **Cuándo:** {fecha_str}")
                        st.write(f"📍 **Dónde:** {evento['lugar']}")
                        if evento["link_maps"]:
                            st.markdown(f"[📍 Ver ubicación en Google Maps]({evento['link_maps']})")
                        
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
                                supabase.table("comentarios").insert({"evento_id": evento["id"], "email_usuario": st.session_state.usuario.email, "texto": nuevo_com}).execute()
                                st.rerun()

                        if st.session_state.usuario.email == CORREO_ADMIN:
                            st.write("---")
                            if st.button("🗑️ Eliminar Evento Completo", key=f"borrar_{evento['id']}", type="primary"):
                                supabase.table("eventos").delete().eq("id", evento["id"]).execute()
                                st.success("Evento eliminado.")
                                st.rerun()

                    # Cargar alineación actual
                    res_alineacion = supabase.table("alineaciones").select("*").eq("evento_id", evento["id"]).execute()
                    alineacion_actual = {item["numero"]: item["jugador"] for item in res_alineacion.data}

                    # 2. EDITAR ALINEACIÓN
                    with sub_alineacion:
                        st.write("Ingresa los nombres de los jugadores. Cualquier entrenador puede modificar esto.")
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

                    # 3. CANCHA VIRTUAL
                    with sub_cancha:
                        st.markdown("### Alineación Titular")
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

                    # 4. NUEVA PESTAÑA: MATERIALES (MÁXIMO 30 ELEMENTOS Y COPIAR/PEGAR)
                    with sub_materiales:
                        st.write("Gestiona la logística y los materiales requeridos para la actividad.")
                        
                        # Cargar materiales guardados
                        res_mat = supabase.table("materiales").select("*").eq("evento_id", evento["id"]).order("id").execute()
                        materiales_actuales = res_mat.data
                        
                        # Botones para Copiar y Pegar listas entre eventos
                        col_cp1, col_cp2 = st.columns(2)
                        with col_cp1:
                            if st.button("📋 Copiar esta Lista de Materiales", key=f"btn_copy_mat_{evento['id']}"):
                                st.session_state.materiales_copiados = [
                                    {"elemento": m["elemento"], "cantidad": m["cantidad"], "estado": m["estado"]} 
                                    for m in materiales_actuales
                                ]
                                st.success("¡Lista copiada! Ya puedes ir a otro evento y pegarla.")
                        with col_cp2:
                            if st.session_state.materiales_copiados is not None:
                                if st.button("📋 Pegar Lista Copiada Aquí", key=f"btn_paste_mat_{evento['id']}"):
                                    supabase.table("materiales").delete().eq("evento_id", evento["id"]).execute()
                                    datos_pegar = [
                                        {"evento_id": evento["id"], "elemento": mc["elemento"], "cantidad": mc["cantidad"], "estado": mc["estado"]}
                                        for mc in st.session_state.materiales_copiados
                                    ]
                                    if datos_pegar:
                                        supabase.table("materiales").insert(datos_pegar).execute()
                                    st.success("¡Lista pegada exitosamente!")
                                    st.rerun()

                        st.write("---")
                        
                        # Formulario de cuadrícula para los 30 elementos
                        with st.form(f"form_mat_{evento['id']}"):
                            nuevos_materiales = []
                            
                            # Ciclo para construir las 30 filas dinámicas
                            for i in range(30):
                                # Pre-cargar valores existentes si es que hay
                                val_el = materiales_actuales[i]["elemento"] if i < len(materiales_actuales) else ""
                                val_cant = materiales_actuales[i]["cantidad"] if i < len(materiales_actuales) else ""
                                val_est = materiales_actuales[i]["estado"] if i < len(materiales_actuales) else "Ok"
                                idx_est = 0 if val_est == "Ok" else 1
                                
                                c1, c2, c3 = st.columns([0.5, 0.2, 0.3])
                                with c1:
                                    el = st.text_input("Elemento / Material", value=val_el, key=f"mat_el_{evento['id']}_{i}", label_visibility="visible" if i == 0 else "collapsed")
                                with c2:
                                    cant = st.text_input("Cantidad", value=val_cant, key=f"mat_ca_{evento['id']}_{i}", label_visibility="visible" if i == 0 else "collapsed")
                                with c3:
                                    est = st.selectbox("Estado", ["Ok", "Falta"], index=idx_est, key=f"mat_es_{evento['id']}_{i}", label_visibility="visible" if i == 0 else "collapsed")
                                
                                # Si el campo de texto tiene contenido, lo añadimos a la lista para guardar
                                if el.strip() != "":
                                    nuevos_materiales.append({
                                        "evento_id": evento["id"],
                                        "elemento": el,
                                        "cantidad": cant,
                                        "estado": est
                                    })
                            
                            if st.form_submit_button("Guardar Lista de Materiales"):
                                # Reemplazar la lista completa en la base de datos
                                supabase.table("materiales").delete().eq("evento_id", evento["id"]).execute()
                                if nuevos_materiales:
                                    supabase.table("materiales").insert(nuevos_materiales).execute()
                                st.success("¡Inventario de materiales guardado con éxito!")
                                st.rerun()

    with tab_crear:
        st.header("Nuevo Evento")
        with st.form("form_nuevo_evento", clear_on_submit=True):
            titulo = st.text_input("Título del Evento")
            # Añadido 'Festival' a las opciones del menú
            tipo = st.selectbox("Tipo", ["Partido", "Entrenamiento", "Festival", "Reunión", "Tercer Tiempo"])
            fecha = st.date_input("Fecha")
            hora = st.time_input("Hora")
            lugar = st.text_input("Lugar / Cancha")
            link = st.text_input("Link de Google Maps (Opcional)")
            
            submit = st.form_submit_button("Guardar Evento")
            
            if submit:
                fecha_hora_str = f"{fecha}T{hora}"
                nuevo_evento = {"titulo": titulo, "tipo": tipo, "fecha_hora": fecha_hora_str, "lugar": lugar, "link_maps": link}
                supabase.table("eventos").insert(nuevo_evento).execute()
                st.success("¡Evento registrado exitosamente!")
                st.rerun()
