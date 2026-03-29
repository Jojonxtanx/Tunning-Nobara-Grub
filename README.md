# 🖥️ Nobara GRUB Tuner - GTK4/Adwaita Edition

**Configurador gráfico moderno y seguro para GRUB en Nobara Linux y otras distribuciones**

Una herramienta profesional con interfaz GTK4/Adwaita para personalizar la configuración de GRUB de forma visual, segura y eficiente. Desarrollada para la comunidad Nobara con soporte multi-distribución.

---

## 📋 Contenido

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Tecnologías Implementadas](#tecnologías-implementadas)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Características](#características)
- [Troubleshooting](#troubleshooting)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## 📝 Descripción del Proyecto

**Nobara GRUB Tuner** es una aplicación de escritorio que permite personalizar la configuración de GRUB de manera intuitiva, sin necesidad de editar archivos de configuración manualmente. 

### Propósito Principal
Proporcionar a los usuarios de Nobara (y otras distribuciones Linux) una herramienta gráfica eficaz para:
- ✅ Ajustar el timeout del menú de arranque
- ✅ Cambiar temas de GRUB
- ✅ **Reordenar entradas de boot** (Windows, Nobara, Fedora, etc.)
- ✅ Configurar parámetros del kernel
- ✅ Habilitar/deshabilitar bootloader features
- ✅ Crear backups automáticos de configuración
- ✅ Revertir cambios con historial de versiones
- ✅ Seleccionar tema claro/oscuro de la interfaz

### Ventajas
- **Interfaz moderna**: GTK4/Adwaita para una experiencia nativa en GNOME
- **Seguridad**: Validación multi-capa contra inyección de comandos
- **Multi-distro**: Soporta Nobara, Fedora, Ubuntu, Debian, Arch, Manjaro y openSUSE
- **Responsiva**: UI no bloqueante con threading para operaciones pesadas
- **Logging persistente**: Rastro completo de operaciones en `/root/.nobara-grub-tuner/logs/`
- **Versionado**: Guarda automáticamente versiones de configuración con rollback
- **Testing**: 30+ pruebas unitarias para garantizar fiabilidad

---

## 🛠️ Tecnologías Implementadas

### Núcleo
- **Python 3.6+** - Lenguaje principal
- **GTK 4.0** - Framework de interfaz gráfica moderna
- **Libadwaita 1.0** - Componentes UI nativos GNOME
- **PyGObject** - Bindings de Python para GTK/Adwaita

### Seguridad y Validación
- **SecurityUtils** - Detección de inyección de comandos, sanitización, validación de UUID
- **ValidationUtils** - Validación de rangos, formatos, caracteres especiales
- **3-layer validation** - Detección → Sanitización → Validación

### Características Avanzadas
- **Threading** - Operaciones sin bloqueo con `GLib.idle_add()`
- **Logging persistente** - Archivos de log con timestamps ISO en `~/.nobara-grub-tuner/logs/`
- **Versionado de configuración** - Snapshots automáticos en `~/.nobara-grub-tuner/versions/`
- **Detección multi-distro** - Automático con `/etc/os-release`
- **Detección multi-fuente de boot** - Lee desde grub.cfg + efibootmgr + /etc/grub.d/
- **Reordenamiento de boot entries** - Reordena visualmente Windows, Nobara, Fedora, etc.
- **Tema claro/oscuro** - Selector con cambio en tiempo real (AdwStyleManager)
- **Respaldo automático** - Backup pre-cambios con timestamp

### Testing
- **unittest + pytest** - Framework de testing
- **Mock objects** - Simulación de llamadas del sistema
- **30+ test cases** - Cobertura de paths críticos

---

## 📦 Requisitos Previos

### Sistema Operativo
- **Nobara 43** (recomendado), Fedora 43+, Ubuntu 22.04+, Debian 12+, Arch, Manjaro, openSUSE 15.5+

### Dependencias del Sistema

#### En **Nobara/Fedora**:
```bash
sudo dnf install python3-gi gir1.2-gtk-4.0 gir1.2-adwaita-1 git
```

#### En **Ubuntu/Debian**:
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adwaita-1 git
```

#### En **Arch/Manjaro**:
```bash
sudo pacman -S python-gobject gtk4 libadwaita git
```

#### En **openSUSE**:
```bash
sudo zypper install python3-gobject gtk4 libadwaita git
```

### Verificar Instalación
```bash
python3 -c "import gi; gi.require_version('Gtk', '4.0'); 
gi.require_version('Adw', '1'); 
from gi.repository import Gtk, Adw; 
print('✓ GTK4 y Libadwaita listos')"
```

---

## 📥 Instalación

### Opción 1: Clonar desde GitHub (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/Jojonxtanx/Tunning-Nobara-Grub.git

# Entrar al directorio
cd "Tunning-Nobara-Grub"

# (Opcional) Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
```

### Opción 2: Descarga Manual

1. Visita https://github.com/Jojonxtanx/Tunning-Nobara-Grub
2. Haz clic en **Code** → **Download ZIP**
3. Descomprime el archivo
4. Abre una terminal en el directorio extraído

---

## 🚀 Uso

### Ejecución Básica
```bash
# Con permisos de usuario (sin cambios de GRUB)
bash run.sh
```

### Ejecución con Permisos de Administrador
```bash
# Para que los cambios se apliquen efectivamente
sudo bash run.sh
```

### Interfaz Gráfica

Una vez abierta la aplicación, verás:

1. **Sección Comportamiento**
   - Timeout del menú GRUB (0-30 segundos)
   - Deshabilitar submenú de kernels

2. **Sección Apariencia**
   - Selector de temas GRUB
   - Botón para recargar temas
   - **Selector de tema de la aplicación** (Automático, Claro, Oscuro)

3. **Sección Orden de Boot** ⭐ NUEVO
   - Lista visual de todas las opciones de boot disponibles
   - Windows, Nobara, Fedora, Ubuntu, etc.
   - Botones ⬆️ Arriba y ⬇️ Abajo para reordenar
   - Validación en tiempo real

4. **Sección Kernel**
   - Parámetros del kernel
   - Detector automático de UUID de swap
   - Editor de parámetros personalizados

5. **Acciones**
   - Botón para crear backup
   - Botón para aplicar cambios
   - Historial de cambios

---

## ✨ Características

### Seguridad 🔒
- ✅ Detección de inyección de comandos
- ✅ Sanitización de variables
- ✅ Validación de UUID
- ✅ Backup automático antes de cambios
- ✅ Confirmaciones antes de aplicar

### Usabilidad 👥
- ✅ Interfaz intuitiva con GTK4/Adwaita
- ✅ Diálogos informativos con detalles de errores
- ✅ Botones +/- para ajustar timeouts
- ✅ Autocompletado de parámetros GRUB
- ✅ Indicadores visuales de estado
- ✅ **Reordenamiento visual de boot entries** (⬆️⬇️ botones)
- ✅ **Tema claro/oscuro con cambio en vivo**
- ✅ **Detección automática de todas las opciones de boot**

### Fiabilidad 📊
- ✅ 30+ pruebas unitarias
- ✅ Manejo robusto de errores
- ✅ Logging persistente a disco
- ✅ Versionado de cambios
- ✅ Rollback de configuración

### Compatibilidad 🐧
- ✅ Nobara 43 (primario)
- ✅ Fedora 43+
- ✅ Ubuntu 22.04+
- ✅ Debian 12+
- ✅ Arch Linux
- ✅ Manjaro
- ✅ openSUSE 15.5+

---

## 📁 Estructura del Proyecto

```
Tunning-Nobara-Grub/
├── README.md                          # Este archivo
├── run.sh                             # Script de ejecución
├── src/
│   ├── __init__.py                   # Paquete Python
│   ├── main.py                       # Punto de entrada (GTK4 init)
│   ├── ui.py                         # Interfaz gráfica (GTK4/Adwaita)
│   ├── config.py                     # Gestión de configuración GRUB
│   ├── utils.py                      # SecurityUtils, ValidationUtils, SystemUtils, Logger
│   ├── distro.py                     # Detección multi-distro
│   ├── version.py                    # Versionado de cambios
│   └── tests.py                      # Suite de pruebas unitarias
├── TECHNICAL_DOCS.md                 # Documentación técnica
├── IMPROVEMENTS_SUMMARY.md           # Resumen de mejoras
└── PROJECT_STRUCTURE.md              # Detalles de estructura

Directorios creados en tiempo de ejecución:
~/.nobara-grub-tuner/
├── logs/                             # Archivos de log
├── versions/                         # Snapshots de configuración
└── backups/                          # Backups de GRUB
```

---

## 🧪 Testing

### Ejecutar Pruebas Unitarias
```bash
cd "Tunning-Nobara-Grub"
python3 -m pytest src/tests.py -v
```

### Resultados Esperados
```
test_security_utils ............................ [100%]
test_validation_utils .......................... [100%]
test_logger .................................... [100%]
test_grub_config ............................... [100%]

====== 30 passed in 2.45s ======
```

---

## 📋 Archivos de Configuración

### Log Files
- Ubicación: `~/.nobara-grub-tuner/logs/grub_tuner_YYYYMMDD_HHMMSS.log`
- Contenido: Historial completo de operaciones
- Formato: ISO timestamp + nivel + mensaje

### Backups
- Ubicación: `~/.nobara-grub-tuner/backups/`
- Contenido: Copias de seguridad automáticas pre-cambios
- Nombre: `grub.backup-YYYYMMDD-HHMMSS`

### Versiones
- Ubicación: `~/.nobara-grub-tuner/versions/`
- Contenido: Snapshots de configuración
- Índice: `index.json` con metadatos
- Nombre: `v{TIMESTAMP}.grub`

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'gi'"
```bash
# Instalación de PyGObject
sudo dnf install python3-gi gir1.2-gtk-4.0 gir1.2-adwaita-1  # Fedora/Nobara
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adwaita-1   # Ubuntu/Debian
```

### "Cannot find GTK 4.0"
```bash
# Verificar instalación de GTK4
gtk4-demo  # Si se abre, GTK4 está instalado
```

### Permisos Denegados al Aplicar Cambios
```bash
# Necesario ejecutar con sudo
sudo bash run.sh
```

### Los logs no se guardan
```bash
# Verificar permisos del directorio
mkdir -p ~/.nobara-grub-tuner/logs
chmod 755 ~/.nobara-grub-tuner/logs
```

### Error al cargar temas
```bash
# Verificar dirección de temas según distro
# Nobara/Fedora: /boot/grub2/themes/
# Ubuntu/Debian: /boot/grub/themes/
ls -la /boot/grub*/themes/
```

---

## 🤝 Contribuir

Nos encanta recibir contribuciones de la comunidad. Para contribuir:

1. **Fork** el repositorio
2. **Crea una rama** para tu feature: `git checkout -b feature/mi-mejora`
3. **Commit** tus cambios: `git commit -am 'Agrega mi mejora'`
4. **Push** a la rama: `git push origin feature/mi-mejora`
5. **Abre un Pull Request**

### Áreas de Mejora
- [ ] Internacionalización (i18n) - 12 idiomas
- [ ] Soporte para UEFI
- [ ] Interfaz CLI alternativa
- [ ] Integración con bootloader alternos
- [ ] Más temas gráficos
- [ ] Editor gráfico de entries GRUB

---

## 📄 Licencia

MIT License - Ver `LICENSE` para detalles

---

## 👨‍💻 Autor

Desarrollado para la comunidad **Nobara Linux** por **Jojonxtanx**

- GitHub: https://github.com/Jojonxtanx
- Repositorio: https://github.com/Jojonxtanx/Tunning-Nobara-Grub

---

## 📞 Soporte

- 🐛 Reporta bugs: https://github.com/Jojonxtanx/Tunning-Nobara-Grub/issues
- 💡 Solicita features: https://github.com/Jojonxtanx/Tunning-Nobara-Grub/issues
- 📖 Documentación técnica: Ver `TECHNICAL_DOCS.md`

---

## 🎯 Roadmap

### v2.1 (Próximo)
- [ ] i18n - Soporte para múltiples idiomas
- [ ] Exportar/Importar configuraciones
- [ ] Comparar diferencias entre versiones

### v3.0 (Futuro)
- [ ] Gestor gráfico de entries GRUB
- [ ] Soporte para UEFI Secure Boot
- [ ] Integración con Bootupd
- [ ] Temas del bootloader descargables

---

**¡Gracias por usar Nobara GRUB Tuner! 🚀**
│   └── utils.py          # Utilidades y helpers
└── venv/                 # Entorno virtual
```

## Archivos Creados/Modificados

### Nuevos Archivos

#### `src/config.py` (148 líneas)
Gestiona lectura, parseo y generación de configuración GRUB:
- Lectura de `/etc/default/grub`
- Detección automática de UUID de swap
- Validación de temas
- Generación de configuración segura
- Aplicación de cambios con sudo
- Creación de backups automáticos

#### `src/utils.py` (147 líneas)
Utilidades y funciones compartidas:
- `SystemUtils`: Comandos del sistema, temas, kernels
- `Logger`: Sistema de logging con niveles
- `ValidationUtils`: Validação de parámetros

#### `src/ui.py` (267 líneas)
Interfaz gráfica moderna:
- Diálogos de confirmación personalizados
- Diálogos de información con logs
- Ventana principal refactorizada
- Edición de parámetros avanzados
- Detección de valores actuales

#### `src/__init__.py`
Marca src/ como paquete Python

### Archivos Modificados

#### `src/main.py` (25 líneas)
Totalmente refactorizado:
- Punto de entrada limpio
- Usa módulos separados
- Mejor manejo de inicialización

#### `run.sh`
Mejorado:
- Manejo correcto de PYTHONPATH
- Soporte para imports de módulos
- Más robusto

## Características Principales

### ✨ Nuevas Funcionalidades

1. **Lectura automática de configuración**
   - Lee valores actuales de `/etc/default/grub`
   - Muestra configuración existente en los campos

2. **Detección de UUID automática**
   - Detecta UUID de partición swap automáticamente
   - Configura parámetro `resume` correctamente

3. **Diálogos informativos**
   - Confirmación de cambios
   - Feedback de éxito/error
   - Logs visibles del proceso

4. **Validación inteligente**
   - Valida timeout dentro de rango (0-30)
   - Verifica que tema existe
   - Comprueba acceso sudo

5. **Backup automático**
   - Crea backup antes de aplicar cambios
   - Marca con timestamp

6. **Parámetros avanzados**
   - Edición manual de parámetros GRUB
   - Interfaz para usuarios avanzados

## Cómo Usar

### Instalación de Dependencias

```bash
# Con pip
pip install PyGObject pyaml

# O con el gestor de paquetes
sudo dnf install python3-gobject libadwaita-devel
```

### Ejecución

```bash
# Hacer ejecutable el script
chmod +x run.sh

# Ejecutar
./run.sh
```

O directamente:
```bash
python3 -m src.main
```

## Seguridad

- ✅ Crea backups automáticos antes de cambios
- ✅ Valida entrada del usuario
- ✅ Requiere sudo (con confirmación)
- ✅ Manejo de errores robusto

## 🎯 Roadmap

### v2.1 ✨ NUEVO (Actual)
- ✅ Reordenamiento de boot entries con UI intuitiva
- ✅ Soporte tema claro/oscuro
- ✅ Detección multi-fuente de boot (grub.cfg + efibootmgr + /etc/grub.d/)
- ✅ Mejor detección de distribuciones instaladas

### v2.2 (Próximo)
- [ ] i18n - Soporte para múltiples idiomas
- [ ] Exportar/Importar configuraciones
- [ ] Drag-and-drop para reordenar boots
- [ ] Comparar diferencias entre versiones

### v3.0 (Futuro)
- [ ] Gestor gráfico de entries GRUB
- [ ] Soporte para UEFI Secure Boot
- [ ] Integración con Bootupd
- [ ] Temas del bootloader descargables
- [ ] CLI (Interface de línea de comandos)

---

## 📊 Comparativa de Versiones

| Aspecto | v1.0 | v2.0 | v2.1 |
|--------|------|------|------|
| Arquitectura | Monolítica | Modular | Modular |
| Framework UI | GTK3 | GTK4 | GTK4 |
| Líneas de código | ~180 | ~600 | ~1000 |
| Módulos | 1 | 4 | 7 |
| Reordenamiento Boot | ✗ | ✗ | ✅ |
| Tema claro/oscuro | ✗ | ✗ | ✅ |
| Detección multi-fuente | ✗ | ✗ | ✅ |
| Detección actual | ✗ | ✅ | ✅ |
| UUID automático | ✗ | ✅ | ✅ |
| Diálogos | ✗ | ✅ | ✅ |
| Validación | Mínima | Completa | Avanzada |
| Logging | ✗ | ✅ | ✅ |
| Tests | ✗ | 30+ | 30+ |
| Parámetros avanzados | ✗ | ✅ | ✅ |
| Versionado | ✗ | ✅ | ✅ |
| Distros soportadas | 1 | 7 | 7 |

---

## Licencia

Parte del proyecto Nobara Linux
