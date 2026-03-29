# 🎯 Reordenamiento de Boot en GRUB - Guía de Uso

## 📋 Descripción

La nueva funcionalidad de **Reordenamiento de Boot** permite a los usuarios de Nobara GRUB Tuner organizar el orden de las entradas disponibles al iniciar la máquina.

### Casos de Uso

#### 1. **Dual Boot Windows + Nobara**
- Por defecto, GRUB muestra Windows primero
- Ahora puedes poner Nobara primero si prefieres
- O mantener Windows si es tu opción predeterminada

#### 2. **Múltiples Distribuciones Linux**
- Si tienes Nobara + Fedora + Ubuntu instalados
- Reordénalos según tu preferencia de uso
- La primera entrada será la que se inicia automáticamente

#### 3. **Seleccionar Kernels Específicos**
- Si usas múltiples kernels en el mismo SO
- Elige cuál aparece primero en el menú
- Útil si usas kernels experimentales

## 🖥️ Cómo Usar

### Interfaz Gráfica

1. **Abre la aplicación:**
   ```bash
   sudo bash run.sh
   ```

2. **Ve a la sección "Orden de Boot":**
   - Encontrarás una lista con todas las entradas disponibles
   - Verás botones ⬆️ (Arriba) y ⬇️ (Abajo)

3. **Selecciona una entrada:**
   - Haz clic en una entrada de la lista
   - Los botones se activarán si puedes moverla

4. **Reordena:**
   - **⬆️ Arriba**: Sube la entrada una posición
   - **⬇️ Abajo**: Baja la entrada una posición

5. **Aplica cambios:**
   - Haz clic en **💾 Aplicar Cambios**
   - Confirma en el diálogo
   - Se creará un backup automático
   - Los cambios se aplicarán al reiniciar

## 🔧 Detalles Técnicos

### Clase `BootEntryManager` (en `src/config.py`)

```python
class BootEntryManager:
    """Gestor de orden de entradas de boot en GRUB."""
    
    def detect_boot_entries(self) -> Dict[str, str]:
        """Detecta todas las entradas de boot disponibles."""
    
    def get_boot_entries(self) -> list:
        """Retorna lista de entradas de boot actuales."""
    
    def reorder_entries(self, new_order: list) -> Tuple[bool, str]:
        """Reordena las entradas de boot."""
    
    def set_default_entry(self, entry_name: str) -> Tuple[bool, str]:
        """Establece la entrada de boot por defecto."""
```

### Métodos de UI (en `src/ui.py`)

- `_load_boot_entries()` - Carga las entradas disponibles
- `_on_boot_selection_changed()` - Maneja cambios de selección
- `_on_boot_move_up()` - Mueve hacia arriba
- `_on_boot_move_down()` - Mueve hacia abajo

### Flujo de Ejecución

```
1. Usuario selecciona entrada
   ↓
2. UI activa/desactiva botones según posición
   ↓
3. Usuario presiona ⬆️ o ⬇️
   ↓
4. UI intercambia posiciones en ListStore
   ↓
5. Usuario hace clic "Aplicar Cambios"
   ↓
6. Sistema reordena entradas en GRUB
   ↓
7. Se regenera grub.cfg con nuevo orden
   ↓
8. Cambios activos al reiniciar
```

## ✨ Características

✅ **Reordenamiento visual** - Interfaz intuitiva con botones
✅ **Preview en vivo** - Ve el nuevo orden antes de aplicar
✅ **Validación** - Verifica que todas las entradas sean válidas
✅ **Backup automático** - Crea backup antes de cambiar
✅ **Soporte dual boot** - Windows + Linux
✅ **Múltiples kernels** - Reordena kernels del mismo SO
✅ **Multi-distro** - Compatible con múltiples distribuciones
✅ **Logging** - Registra todas las operaciones

## 🐛 Troubleshooting

### "No se muestran entradas de boot"
- El archivo `/boot/grub2/grub.cfg` puede no estar en la ruta correcta
- Verifica tu distribución en TECHNICAL_DOCS.md
- Consulta los logs: `~/.nobara-grub-tuner/logs/`

### "El orden no se aplica al reiniciar"
- Asegúrate de ejecutar con `sudo bash run.sh`
- Verifica que grub-mkconfig se ejecutó correctamente
- Revisa los logs de la aplicación

### "Error: Enlace simbólico"
- El sistema intenta crear `/etc/grub.d/06_custom_order`
- Necesita permisos de administrador
- Usa siempre `sudo bash run.sh`

## 📊 Estructura de Datos

### Boot Entry Format
```python
{
    "Nobara Linux": 0,
    "Nobara Linux (fallback)": 1,
    "Windows Boot Manager": 2,
    "UEFI Firmware Settings": 3
}
```

### Custom Order File
```bash
#!/bin/bash
# /etc/grub.d/06_custom_order
# Auto-generado por Nobara GRUB Tuner

menuentry_id_option="--id nobara_linux"
menuentry_id_option="--id windows_boot_manager"
menuentry_id_option="--id nobara_linux_fallback"
```

## 🔐 Seguridad

- ✅ Todas las entradas se validan antes de reordenar
- ✅ Se detectan inyecciones de comandos
- ✅ Backup automático antes de cambios
- ✅ Requiere sudo para modificar `/etc/grub.d/`

## 📝 Ejemplos

### Ejemplo 1: Priorizar Nobara en Dual Boot

**Orden inicial:**
```
1. Windows Boot Manager
2. Nobara Linux
3. Nobara Linux (fallback)
```

**Pasos:**
1. Selecciona "Nobara Linux"
2. Presiona ⬆️ dos veces
3. Presiona "Aplicar"

**Resultado:**
```
1. Nobara Linux ← Se inicia primero
2. Windows Boot Manager
3. Nobara Linux (fallback)
```

### Ejemplo 2: Kernel experimental primero

**Orden inicial:**
```
1. Nobara Linux (kernel 5.15)
2. Nobara Linux (kernel 5.17-exp)
3. Nobara Linux (fallback)
```

**Pasos:**
1. Selecciona "Nobara Linux (kernel 5.17-exp)"
2. Presiona ⬆️ una vez
3. Presiona "Aplicar"

**Resultado:**
```
1. Nobara Linux (kernel 5.17-exp) ← Experimental primero
2. Nobara Linux (kernel 5.15)
3. Nobara Linux (fallback)
```

## 🔄 Próximas Mejoras

- [ ] Drag-and-drop directo (sin botones)
- [ ] Renombar entradas
- [ ] Ocultar entradas específicas
- [ ] Establecer timeout por entrada
- [ ] Presets de orden común (Windows first, Linux first, etc)

---

¿Tienes preguntas? Abre un issue en GitHub:
https://github.com/Jojonxtanx/Tunning-Nobara-Grub/issues
