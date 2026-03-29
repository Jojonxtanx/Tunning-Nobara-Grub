# Documentación Técnica - Nobara GRUB Tuner

## Índice
1. [Arquitectura](#arquitectura)
2. [Módulos](#módulos)
3. [Flujo de Operación](#flujo-de-operación)
4. [Seguridad](#seguridad)
5. [Testing](#testing)
6. [Logging](#logging)

---

## Arquitectura

```
┌──────────────────────────────────────┐
│          main.py                     │
│    (Punto de entrada GTK4/Adwaita)   │
└──────────────────┬───────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────┴─────┐      ┌──────┴──────┐
    │   ui.py  │      │ config.py   │
    │  GTK4    │      │ GRUB Config │
    │Interface │      │  Handler    │
    └────┬─────┘      └──────┬──────┘
         │                   │
         └─────────┬─────────┘
                   │
            ┌──────┴──────┐
            │ utils.py    │
            │ - Security  │
            │ - Validation│
            │ - Logging   │
            └─────────────┘
```

## Módulos

### main.py
**Punto de entrada de la aplicación.**

- Inicializa el sistema de logging
- Crea instancia de `NobaraGrubTunerApp`
- Ejecuta el event loop de GTK4

```python
from src.main import main
exit(main())
```

### ui.py
**Interfaz gráfica usando GTK4 y Libadwaita.**

**Clases principales:**
- `ConfirmDialog` - Diálogo de confirmación modal
- `InfoDialog` - Diálogo de información con soporte para errores
- `EditParametersDialog` - Ventana para parámetros avanzados
- `NobaraGrubTunerWindow` - Ventana principal con preferencias
- `NobaraGrubTunerApp` - Aplicación principal Adwaita

**Características:**
- UI moderna y responsiva
- Operaciones pesadas en threading separado (no bloquea UI)
- Diálogos de confirmación antes de aplicar cambios
- Soporte para múltiples temas

### config.py
**Gestión de configuración GRUB.**

**Clase: GrubConfig**

Métodos principales:
- `load_current_config()` - Lee `/etc/default/grub`
- `detect_resume_uuid()` - Detecta UUID de swap automáticamente
- `detect_all_swap_devices()` - Lista todos los dispositivos swap
- `generate_config()` - Genera nueva configuración con validación
- `apply_config()` - Aplica cambios de forma segura con backups
- `create_backup()` - Crea backup automático con timestamp

**Validaciones:**
- Todas las entradas se validan antes de ser procesadas
- Se sanitizan valores para prevenir inyección de comandos
- Los UUIDs se validan con regex

### utils.py
**Utilidades, seguridad, validación y logging.**

**Clases:**

#### SecurityUtils
Funciones de seguridad para prevenir ataques:
- `sanitize_grub_value()` - Elimina caracteres peligrosos
- `detect_command_injection()` - Detecta intentos de inyección
- `validate_uuid()` - Valida formato UUID
- `validate_grub_param()` - Verifica parámetro GRUB válido

**Patrones de inyección detectados:**
- Separadores de comandos (`;`, `|`, `&`)
- Sustitución de comandos (`$()`, backticks)
- Null bytes

#### ValidationUtils
Funciones de validación de entrada:
- `validate_timeout()` - Valida rango 0-30 segundos
- `validate_theme_exists()` - Verifica tema GRUB existe
- `validate_cmdline_linux()` - Valida línea de comando Linux
- `validate_custom_params()` - Valida parámetros personalizados

#### SystemUtils
Interacción con el sistema:
- `check_sudo_access()` - Verifica acceso sudo sin contraseña
- `get_available_themes_nobara()` - Lista temas GRUB disponibles
- `get_kernel_entries()` - Lista entradas de kernel BLS
- `run_command()` - Ejecuta comandos del sistema con timeout

**Manejo de errores:**
- Detecta excepciones específicas (Timeout, FileNotFound, Permission)
- Proporciona mensajes de error descriptivos
- Registra en logs todos los errores

#### Logger
Sistema de logging persistente:
- `initialize()` - Crea directorio `~/.nobara-grub-tuner/logs/`
- `info()`, `success()`, `warning()`, `error()`, `debug()`
- Logs guardados a archivo con timestamp
- También escribe a stdout con emojis

---

## Flujo de Operación

### 1. Inicio de la Aplicación
```
1. main.py ejecuta
2. Logger.initialize() crea directorio de logs
3. NobaraGrubTunerApp se instancia
4. Verifica acceso sudo sin contraseña
5. UI se construye
6. Event loop comienza
```

### 2. Aplicar Cambios
```
1. Usuario modifica timeout, tema, etc.
2. Usuario hace click en "Aplicar Cambios"
3. Validación de entrada (ValidationUtils)
4. Confirmación modal (ConfirmDialog)
5. Si confirma:
   a. Se ejecuta en hilo separado (_apply_changes_async)
   b. Genera configuración (generate_config)
   c. Crea backup automático (create_backup)
   d. Aplica cambios (apply_config)
   e. Regenera GRUB con grub2-mkconfig
   f. Muestra resultado en UI (no bloquea)
```

### 3. Manejo de Errores
```
1. Todo error se registra en Logger
2. Se muestra en diálogo de error
3. La aplicación continúa funcionando
4. Los logs se guardan en archivo
```

---

## Seguridad

### Validación de Entrada en Capas

**Capa 1: Detección de Inyección**
```python
is_injection = SecurityUtils.detect_command_injection(value)
if is_injection:
    raise ValueError("Inyección detectada")
```

**Capa 2: Sanitización**
```python
safe_value = SecurityUtils.sanitize_grub_value(value)
```

**Capa 3: Validación Específica**
```python
is_valid, msg = ValidationUtils.validate_cmdline_linux(cmdline)
```

### Patrones Detectados
- `;` - Separador de comandos
- `|` - Pipe
- `&` - Background execution
- `$(...)` - Command substitution
- `` ` ...` `` - Backticks
- `\x00` - Null bytes

### Límites de Entrada
- Timeout: 0-30 segundos (rango estricto)
- CMDLINE: máximo 256 caracteres
- Parámetros: máximo 512 caracteres por valor

---

## Testing

### Ejecutar Tests
```bash
cd '/home/jojonxtanx/Documentos/Programacion/Lenguajes/Python/Proyectos/tunning nobara grub'
python3 -m pytest src/tests.py -v
```

### Suites de Test

**SecurityUtils Tests** (10 tests)
- Validación de UUIDs
- Detección de inyección de comandos
- Sanitización de valores

**ValidationUtils Tests** (10 tests)
- Validación de timeout
- Validación de línea de comando
- Validación de parámetros personalizados

**Logger Tests** (8 tests)
- Funcionalidad básica de logging
- Múltiples niveles (info, warning, error, debug)
- Formato de logs

**GrubConfig Tests** (2 tests)
- Detección de UUID de swap
- Manejo de casos sin swap

---

## Logging

### Ubicación de Logs
```
~/.nobara-grub-tuner/logs/grub_tuner_YYYYMMDD_HHMMSS.log
```

### Niveles de Log
- `INFO` - Operaciones normales
- `SUCCESS` - Operación exitosa completada
- `WARNING` - Advertencias no críticas
- `ERROR` - Errores importantes
- `DEBUG` - Información de debugging

### Ejemplo de Log
```
[2026-03-28T14:30:45.123456] [INFO] Iniciando Nobara GRUB Tuner - GTK4/Adwaita
[2026-03-28T14:30:46.234567] [INFO] Configuración GRUB cargada exitosamente
[2026-03-28T14:30:47.345678] [INFO] UUID de swap detectado: 550e8400-e29b-41d4
[2026-03-28T14:30:48.456789] [SUCCESS] Backup creado: /etc/default/grub.backup-20260328-143048
[2026-03-28T14:30:49.567890] [SUCCESS] Configuración GRUB aplicada correctamente
```

---

## Dependencias del Sistema

### Requeridas
- `grub2-tools` - Para comandos grub2-mkconfig
- `lsblk` - Para detección de UUID
- `sudo` - Acceso a comandos privilegiados (sin contraseña)

### Python
- `gi` (PyGObject) - Bindings para GTK4/Adwaita
- Python 3.6+

---

## Contribuciones y Mejoras Futuras

### Planeado
- [ ] Interfaz para editar parámetros personalizados
- [ ] Integraci internacionalización (i18n)
- [ ] Sistema de versionado de cambios (rollback)
- [ ] Compatibilidad con otras distribuciones Linux
- [ ] Visualización previa de configuración

### Bugs Conocidos
- Ninguno conocido actualmente

---

**Última actualización:** 28 de marzo de 2026
**Versión:** 2.1.0
