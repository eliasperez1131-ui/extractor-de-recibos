## v1.0.5 - Fix bug CLABE repetido + instalador portable sin .exe

### Bug arreglado

La misma CLABE se repetia en todas las filas. Causa: cuando un PDF tenia "Cuenta receptora: 123456789012345678", la regex CLABE capturaba ese numero de 18 digitos ANTES de procesar las etiquetas. Ahora los labels se procesan primero y se evitan duplicados.

### 🆕 Alternativa sin instalador (.bat portable)

Si el aviso de Windows SmartScreen te sigue molestando con el instalador, proba este script BAT que instala TODO desde el codigo fuente sin generar ningun .exe:

**⬇️ [instalar_y_ejecutar.bat](https://raw.githubusercontent.com/eliasperez1131-ui/extractor-de-recibos/main/instalar_y_ejecutar.bat)**

Como usarlo:
1. Click derecho > Guardar enlace como... > guardalo en una carpeta
2. Doble clic
3. El script instala las dependencias Python y ejecuta la app directamente

NO genera ningun .exe, asi que NO aparece el aviso de virus.

Requisitos: Python 3.11+ ([descargar](https://www.python.org/downloads/)).

### Archivos para descargar

**Opcion A - Instalador (recomendado si ya lo tenias andando):**

**⬇️ [ExtractorRecibos_Setup_v1.0.5.exe](https://github.com/eliasperez1131-ui/extractor-de-recibos/releases/download/v1.0.5/ExtractorRecibos_Setup_v1.0.5.exe)** (59.6 MB)

**Opcion B - Script BAT portable (alternativa sin .exe):**

**⬇️ [instalar_y_ejecutar.bat](https://raw.githubusercontent.com/eliasperez1131-ui/extractor-de-recibos/releases/download/v1.0.5/instalar_y_ejecutar.bat)** (~3 KB)

### Como desbloquear el instalador (paso a paso)

```
1. Click DERECHO en ExtractorRecibos_Setup_v1.0.5.exe
2. Click "Propiedades"
3. En la pestaña General, abajo a la derecha hay una casilla:
   [ ] Desbloquear  <- MARCALA
4. Click "Aplicar" -> "Aceptar"
5. Doble clic normal
```

Si no ves la casilla "Desbloquear", el archivo ya esta OK.

### Si el aviso sigue apareciendo despues de desbloquear

Desactiva SmartScreen permanentemente:

```
1. Inicio -> escribi "Seguridad de Windows" -> Enter
2. Proteccion contra virus y amenazas
3. "Administrar configuracion" (bajo Configuracion de proteccion)
4. Busca "SmartScreen de Microsoft Defender"
5. Cambia a "Desactivado"
```

### Cambios anteriores

- v1.0.4: fix de cuelgue (ThreadPoolExecutor + watchdog)
- v1.0.3: layout arreglado, tema oscuro al iniciar
