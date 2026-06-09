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
        
        <p style="color: #000000; font-size: 14px;">Para regularizar tu situación, por favor realiza una transferencia electrónica con los siguientes datos:</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; border-left: 4px solid #000000; margin: 15px 0; color: #000000; font-size: 14px; max-width: 400px;">
            <strong style="font-size: 15px;">Datos de Depósito:</strong><br><br>
            • <strong>Nombre:</strong> Katherine Torres<br>
            • <strong>RUT:</strong> 19.947.230-5<br>
            • <strong>Tipo de Cuenta:</strong> Cuenta Corriente<br>
            • <strong>Número de Cuenta:</strong> 18330098221<br>
            • <strong>Banco:</strong> Banco Falabella<br>
            • <strong>Correo:</strong> katherine.tor.rod@gmail.com
        </div>
        
        <p style="color: #000000; font-size: 14px;">Una vez realizado el pago, por favor envía el comprobante de transferencia al correo indicado arriba.</p>
        
        <p style="color: #555555; font-size: 13px; font-style: italic; margin-top: 20px;">
            ℹ️ En caso de dudas, aclaraciones o reclamos, por favor contactar directamente a la tesorera del club al teléfono: <strong>+569 7604 5865</strong>.
        </p>
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
        
        if pd.isna(correo) or str(correo).strip() == "":
            continue
            
        meses_deuda = []
        
        for mes in meses_columnas:
            if mes in df.columns:
                valor_celda = str(row[mes]).strip().lower()
                if valor_celda == "debe":
                    meses_deuda.append(mes)
                    
        if meses_deuda:
            enviar_correo_deuda(nombre, correo, meses_deuda)
        else:
            print(f"ℹ️ {nombre} está al día. No se requiere envío.")

if __name__ == "__main__":
    print("Iniciando procesamiento de cuotas mensuales...")
    procesar_cuotas()
    print("Procesamiento finalizado.")
