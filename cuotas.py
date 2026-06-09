import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Leer credenciales secretas desde GitHub
EMAIL_REMITENTE = os.environ.get("EMAIL_REMITENTE")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def enviar_correo_deuda(nombre, correo, meses_deuda):
    if not meses_deuda:
        return
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMITENTE
    msg['To'] = correo
    msg['Subject'] = "🏉 Recordatorio de Cuotas Pendientes - Calafate Rugby Club"
    
    # Unir los meses con comas (Ej: Enero, Febrero, Marzo)
    meses_texto = ", ".join(meses_deuda)
    
    cuerpo = f"""
    <html>
    <body>
        <h2 style="color: #000000;">Estimado/a {nombre},</h2>
        <p style="color: #000000; font-size: 14px;">Esperamos que estés muy bien.</p>
        <p style="color: #000000; font-size: 14px;">Te escribimos desde la administración de <strong>Calafate Rugby Club</strong> para informarte sobre el estado actual de tus cuotas mensuales.</p>
        <p style="color: #000000; font-size: 14px;">Registramos que actualmente tienes pendiente la regularización de los siguientes meses:</p>
        
        <p style="font-size: 16px; color: #d32f2f; font-weight: bold; background-color: #fbaeae; padding: 10px; border-radius: 5px; display: inline-block;">
            ⚠️ {meses_texto}
        </p>
        
        <p style="color: #000000; font-size: 14px;">Por favor, ponte en contacto con tesorería para coordinar el pago o enviar tu comprobante de transferencia si ya lo realizaste.</p>
        <br>
        <p style="color: #000000; font-size: 14px;">¡Agradecemos tu constante compromiso con el club!</p>
        <br>
        <p style="color: #000000; font-size: 14px;">Atentamente,</p>
        <p style="color: #000000; font-size: 14px;"><strong>Directiva Calafate Rugby Club</strong></p>
    </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
        server.sendmail(EMAIL_REMITENTE, correo, msg.as_string())
        server.quit()
        print(f"✅ Correo de deuda enviado correctamente a {nombre} ({correo})")
    except Exception as e:
        print(f"❌ Error al enviar correo a {correo}: {e}")

def procesar_cuotas():
    archivo = "cuotas.xlsx"
    if not os.path.exists(archivo):
        print(f"❌ Error: No se encontró el archivo '{archivo}' en el repositorio.")
        return
        
    # Cargar los datos del Excel
    df = pd.read_excel(archivo)
    
    # Columnas de los meses a evaluar
    meses_columnas = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    for index, row in df.iterrows():
        nombre = row["Nombre"]
        correo = row["Correo"]
        
        # Validar que tenga un correo ingresado
        if pd.isna(correo) or str(correo).strip() == "":
            continue
            
        meses_deuda = []
        
        # Revisar cada mes de la fila actual
        for mes in meses_columnas:
            if mes in df.columns:
                valor_celda = str(row[mes]).strip().lower()
                if valor_celda == "debe":
                    meses_deuda.append(mes)
                    
        # Si tiene deudas, gatillar el correo
        if meses_deuda:
            enviar_correo_deuda(nombre, correo, meses_deuda)
        else:
            print(f"ℹ️ {nombre} está al día. No se requiere envío.")

if __name__ == "__main__":
    print("Iniciando procesamiento de cuotas mensuales...")
    procesar_cuotas()
    print("Procesamiento finalizado.")
