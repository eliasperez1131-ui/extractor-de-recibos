## ⚠️ Aviso de Windows SmartScreen (NO es un virus)

Al ejecutar `ExtractorRecibos.exe` por primera vez, Windows puede mostrar una pantalla azul diciendo que el archivo es "poco confiable" o "potencialmente dañino".

**Esto NO es un virus.** Es la advertencia genérica de Windows para cualquier `.exe` que no esté firmado con un certificado de pago (~$300 USD/año). El código fuente es público y auditable en este repositorio.

### ✅ Cómo desbloquear (3 métodos)

#### Método A — Más fácil (al abrir)
1. Doble clic en `ExtractorRecibos.exe`
2. Aparece pantalla azul → click **"Más información"** (abajo a la izquierda)
3. Aparece nuevo botón → click **"Ejecutar de todas formas"**
4. Listo, la app abre ✅

#### Método B — Antes de abrir (recomendado)
1. Click derecho en el `.exe` → **Propiedades**
2. Tildá la casilla **"Desbloquear"** (abajo a la derecha)
3. Click **Aplicar** → **Aceptar**
4. Doble clic normal

#### Método C — Desactivar SmartScreen (solo para esta PC)
1. **Inicio** → buscá "Seguridad de Windows"
2. **Protección contra virus y amenazas** → **Administrar configuración**
3. "SmartScreen de Microsoft Defender" → desactivá

### 🛡️ Por qué pasa

Microsoft exige code signing certificate de pago para evitar el aviso en `.exe` nuevos. Como este proyecto es open source gratuito, no se compra. Cualquier `.exe` descargado de un autor desconocido puede mostrar este aviso.

### 🔍 Verificación de seguridad

El `.exe` se construye con `build_exe.bat`. Para verificar que es seguro:
```bash
pip install -r requirements.txt
python main.py
```

---

## 📋 Cómo usar la app

1. **Primera vez**: el wizard descarga Tesseract OCR automáticamente
2. **Seleccionar archivos**: click `📂 Carpeta`, `🗜️ ZIP(s)` o `📄 Archivo(s)`
3. **Procesar**: click `▶️ Procesar`
4. **Resultado**: click `📊 Abrir Excel`

### Campos detectados automáticamente
- **Facturas**: RFC, RUC, CUIT, NIT, Subtotal, IVA, Total, Fecha
- **Recibos de pago**: Receptor, Cuenta, CLABE, Banco, Monto recibido
- **Locale auto-detectado**: 🇲🇽 MX, 🇦🇷 AR, 🇧🇷 BR, 🇨🇱 CL, 🇨🇴 CO, 🇵🇪 PE, 🇵🇾 PY, 🇺🇾 UY, 🇺🇸 US, 🇪🇸 ES
- **Nombre del PDF** aparece como primera columna del Excel
