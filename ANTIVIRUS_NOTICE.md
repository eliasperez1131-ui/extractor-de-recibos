## ⚠️ Aviso de Windows SmartScreen

Windows puede mostrar una advertencia azul diciendo que el archivo "no es de confianza" o que "podría dañar tu computadora".

**Esto NO es un virus.** Es una advertencia genérica que aparece con cualquier `.exe` que no esté firmado con un certificado de pago (code signing). El archivo es código abierto que vos podés auditar en este mismo repositorio.

### Cómo desbloquear el `.exe`

#### Opción 1 — Desbloquear antes de abrir (recomendado)
1. Click derecho en `ExtractorRecibos.exe` → **Propiedades**
2. En la pestaña **General**, abajo a la derecha, tildá la casilla **"Desbloquear"** (solo aparece en archivos descargados)
3. Click **Aplicar** → **Aceptar**
4. Ahora doble clic normal y se abre

#### Opción 2 — Cuando aparece la pantalla azul de SmartScreen
1. Click en **"Más información"** (abajo a la izquierda)
2. Aparece el botón **"Ejecutar de todas formas"**
3. Click ahí y la app abre

#### Opción 3 — Desactivar SmartScreen (solo para esta PC)
1. **Inicio** → buscá "Seguridad de Windows"
2. **Protección contra virus y amenazas** → **Administrar configuración**
3. Buscá "SmartScreen de Microsoft Defender" → desactivá
4. Volvé a abrir el `.exe`

### ¿Por qué pasa esto?

Microsoft exige que los `.exe` estén firmados con un certificado digital de pago (~$300 USD/año) para evitar el aviso. Como este proyecto es gratuito y open source, no se compra el certificado. Cualquier `.exe` que descargues de internet de un autor desconocido puede mostrar este aviso.

### Verificación de seguridad (si querés comprobar)

El `.exe` se construye de forma reproducible con `build_exe.bat`. Si querés verificar que es seguro:
1. Instalá Python 3.11+ y las dependencias: `pip install -r requirements.txt`
2. Ejecutá la app directo desde código: `python main.py`
3. Comparalo con el `.exe` — el código fuente es público y auditable
