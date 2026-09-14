# 🧾 Extractor de Recibos a Excel

Aplicación de escritorio que extrae automáticamente información de **facturas, recibos y boletas** (PDFs digitales, PDFs escaneados e imágenes) y los vuelca a un **Excel** con columnas detectadas dinámicamente según los rubros que se repiten entre los distintos modelos de recibo.

> Detecta automáticamente país/moneda (México, Argentina, Brasil, Chile, Colombia, Perú, Paraguay, Uruguay, USA, España). Español como idioma principal, con soporte multi-idioma para OCR.

## ⚠️ Windows SmartScreen

Al ejecutar el `.exe` por primera vez, Windows puede mostrar una advertencia azul diciendo que el archivo es "poco confiable" o "potencialmente dañino".

**Esto NO es un virus** — es la advertencia genérica para cualquier `.exe` que no esté firmado con un certificado de pago (~$300 USD/año). El código es open source y auditable en este repositorio.

**Cómo desbloquear:**
1. Click derecho en `ExtractorRecibos.exe` → **Propiedades** → tildá **"Desbloquear"** → Aceptar
2. O cuando aparece la pantalla azul: **"Más información"** → **"Ejecutar de todas formas"**

Más detalles en [ANTIVIRUS_NOTICE.md](./ANTIVIRUS_NOTICE.md).

---

## ✨ Características

- 📥 Acepta **carpeta con archivos**, **uno o varios ZIP**, o **archivos sueltos** mezclados.
- 📄 Lee PDFs con texto seleccionable (sin OCR, rápido).
- 🔍 Lee PDFs escaneados e imágenes vía **Tesseract OCR** (Español + Inglés + Portugués).
- 🧠 **Detección dinámica de columnas**: agrupa campos similares con fuzzy matching para unificar `Total:`, `TOTAL`, `Total Final` en una sola columna.
- 🌍 **Auto-detección de locale**: MX, AR, BR, CL, CO, PE, PY, UY, US, ES.
- 💾 **Mapeos persistentes**: lo aprendido en una ejecución se reutiliza en las próximas.
- ⚡ **Procesamiento paralelo** (configurable, hasta N-1 núcleos).
- 🖥️ **Interfaz amigable** con CustomTkinter (tema oscuro/claro).
- 🎬 **Wizard de primera ejecución**: descarga Tesseract automáticamente.
- 📊 Genera Excel con hoja **Datos** + hoja **Resumen** (locale, métricas).
- 👁️ Vista previa de la tabla antes de abrir el Excel.
- 📝 Log en vivo exportable a `.txt`.

---

## 📁 Estructura del proyecto

```
PROYECTO DE EXTRACTOR DE PDF/
├── main.py                 # Punto de entrada
├── build_exe.bat           # Empaqueta en .exe con PyInstaller
├── requirements.txt
├── README.md
├── assets/                 # (opcional) iconos
├── samples/                # PDFs/imágenes de prueba
└── src/
    ├── core/
    │   ├── pdf_reader.py        # Texto de PDFs digitales
    │   ├── ocr_reader.py        # OCR (PDFs escaneados + imágenes)
    │   ├── locale_detector.py   # Detecta país/moneda/idioma
    │   ├── field_detector.py    # Regex + fuzzy clustering
    │   ├── mappings.py          # Persistencia JSON
    │   ├── input_loader.py      # Carpeta + ZIP
    │   └── excel_writer.py      # openpyxl
    ├── gui/
    │   ├── main_window.py       # Ventana principal
    │   ├── wizard.py            # Wizard de instalación inicial
    │   └── widgets.py           # Componentes compartidos
    └── installer/
        └── tesseract_installer.py   # Descarga Tesseract
```

---

## 🚀 Uso desde código fuente

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Instalar Tesseract OCR (necesario para PDFs escaneados e imágenes)

**Windows** (más sencillo):

1. Descargar instalador: <https://github.com/UB-Mannheim/tesseract/releases>
2. Durante la instalación, marcar los idiomas: **Spanish**, **English**, **Portuguese** (si los querés).
3. Asegurarse de que `tesseract.exe` quede accesible (el instalador lo agrega al PATH).

> La primera vez que ejecutes la app, detectará automáticamente si Tesseract está instalado y descargará los modelos de idioma faltantes a `%LOCALAPPDATA%\ExtractorRecibos\tesseract\`.

### 3. Ejecutar

```bash
python main.py
```

La primera vez aparecerá un **wizard de bienvenida** que instala/verifica Tesseract. Luego, la ventana principal queda abierta para usar.

---

## 📦 Compilar el `.exe`

Desde Windows:

```bat
build_exe.bat
```

Resultado: `dist\ExtractorRecibos.exe` (~25 MB, no requiere Python instalado).

Para distribuir:

1. Copiá `dist\ExtractorRecibos.exe` a cualquier PC con Windows 10/11.
2. Al ejecutarlo por primera vez, descargará Tesseract automáticamente (requiere internet).

---

## 🎯 Flujo de uso en la app

1. **Agregar archivos**: pulsá *📂 Carpeta*, *🗜️ ZIP(s)* o *📄 Archivo(s)*.
2. **Configurar**:
   - Idioma OCR (default: `spa+eng+por`).
   - Cantidad de procesos paralelos (default: N-1 núcleos).
   - Ruta del Excel de salida.
3. **Procesar**: pulsá *▶️ Procesar*.
4. **Revisar**: log en vivo, barra de progreso.
5. **Vista previa**: pulsá *👁️ Vista previa* para ver la tabla antes de abrir.
6. **Abrir Excel**: pulsá *📊 Abrir Excel*.

---

## 🧠 Cómo detecta los rubros

Por cada archivo:

1. Extrae texto (PDF directo o Tesseract).
2. Aplica regex para fechas, montos, emails, teléfonos, URLs.
3. Detecta pares `ETIQUETA: valor` por línea.
4. Normaliza y agrupa con **fuzzy matching** (rapidfuzz, umbral 80%):
   - `TOTAL:`, `Total`, `TOTAL FINAL` → columna `TOTAL`
   - `R.F.C.`, `RFC:`, `RFC N°` → columna `RFC`
5. Toma la **unión** de todos los campos detectados en todos los archivos → columnas del Excel.
6. Si un recibo no tiene cierto campo, queda en blanco.
7. Las columnas aprendidas se **guardan** en `%APPDATA%\ExtractorRecibos\field_mappings.json` y se reutilizan en próximas ejecuciones.

---

## 🌍 Locales soportados

| Código | País | Moneda | ID tributario | Impuesto |
|---|---|---|---|---|
| MX | México | MXN | RFC | IVA |
| AR | Argentina | ARS | CUIT | IVA |
| BR | Brasil | BRL | CNPJ | ICMS |
| CL | Chile | CLP | RUT | IVA |
| CO | Colombia | COP | NIT | IVA |
| PE | Perú | PEN | RUC | IGV |
| PY | Paraguay | PYG | RUC | IVA |
| UY | Uruguay | UYU | RUT | IVA |
| US | USA | USD | EIN | Tax |
| ES | España | EUR | NIF | IVA |

Si no detecta ninguno, usa México como default.

---

## 🛠️ Troubleshooting

| Problema | Solución |
|---|---|
| "Tesseract no está instalado" | Instalá Tesseract manualmente o usá el wizard de primera ejecución con internet. |
| Excel sin columnas | Verificá que los PDFs contengan texto o que las imágenes no estén borrosas. |
| App muy lenta con 1000 archivos | Subí los workers o filtrá solo los archivos necesarios. |
| Columnas se mezclan raro | Borrá `%APPDATA%\ExtractorRecibos\field_mappings.json` para resetear. |
| Error de import en .exe | Recompilá con `build_exe.bat`; incluye `--add-data "src;src"`. |

---

## 📜 Licencia

MIT
