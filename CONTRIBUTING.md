# Guía de Contribución

¡Gracias por tu interés en contribuir a Nobara GRUB Tuner! 🎉

## Cómo Reportar Bugs

Para reportar un bug:

1. Ve a [Issues](https://github.com/Jojonxtanx/Tunning-Nobara-Grub/issues)
2. Haz clic en **New Issue**
3. Selecciona **Bug report**
4. Completa los siguientes campos:
   - **Descripción clara** del problema
   - **Pasos para reproducir**
   - **Comportamiento esperado**
   - **Comportamiento actual**
   - **Sistema operativo y versión**
   - **Logs relevantes** (si están disponibles)

### Ejemplo:
```
Título: SpinRow no responde a botones +/- en Ubuntu 24.04

Descripción:
Los botones +/- del spinner de timeout del menú GRUB no funcionan.

Pasos:
1. Abre la aplicación: sudo bash run.sh
2. Intenta aumentar el timeout con el botón +
3. El valor no cambia

Sistema:
- Ubuntu 24.04
- GTK4 4.12.3
- Libadwaita 1.4
```

## Cómo Sugerir Mejoras

Para sugerir una mejora:

1. Ve a [Issues](https://github.com/Jojonxtanx/Tunning-Nobara-Grub/issues)
2. Haz clic en **New Issue**
3. Selecciona **Feature request**
4. Describe tu idea detalladamente

### Ejemplo:
```
Título: Agregar soporte para personalizar font del bootloader

Descripción:
Sería útil poder personalizar la fuente que se muestra en el menú 
de GRUB para mejor legibilidad en pantallas de alta resolución.

Caso de uso:
Usuarios con pantallas 4K necesitan fuentes más grandes.
```

## Cómo Enviar un Pull Request

### 1. Prepara tu entorno

```bash
# Fork el repositorio en GitHub

# Clonar tu fork
git clone https://github.com/TU_USUARIO/Tunning-Nobara-Grub.git

# Entrar al directorio
cd Tunning-Nobara-Grub

# Crear rama para tu feature
git checkout -b feature/descripcion-corta

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
```

### 2. Realiza tus cambios

```bash
# Edita archivos según sea necesario
# Asegúrate de seguir el estilo de código existente

# Ejecuta tests antes de hacer commit
python3 -m pytest src/tests.py -v

# Si agregas funcionalidad nueva, escribe tests
# Nuevo archivo de test: tests/test_mi_feature.py
```

### 3. Haz Commit

```bash
# Agregar cambios
git add .

# Commit con mensaje descriptivo
git commit -m "Agrega soporte para [feature]

- Cambio 1
- Cambio 2
- Relacionado con #123 (si es issue existente)
"
```

### 4. Push y abrir Pull Request

```bash
# Push a tu fork
git push origin feature/descripcion-corta

# En GitHub, se mostrará un botón "Compare & pull request"
# Haz clic y completa la descripción
```

## Pautas de Código

### Estilo Python
- Seguimos **PEP 8**
- Usa nombres descriptivos para variables y funciones
- Máximo 79 caracteres por línea
- Comenta código complejo

### Ejemplo:
```python
def validate_timeout(value: int) -> Tuple[bool, str]:
    """
    Valida que el timeout sea un número válido.
    
    Args:
        value: Timeout en segundos
        
    Returns:
        (es_válido, mensaje_error)
    """
    if not isinstance(value, int):
        return False, "Debe ser un número entero"
    
    if value < 0 or value > 300:
        return False, "Timeout debe estar entre 0 y 300 segundos"
    
    return True, ""
```

### Commits
- Commits pequeños y enfocados
- Mensajes claros y descriptivos
- Usa verbos en imperativo: "Agrega", "Corrige", "Mejora"

### Pruebas
- Escribe tests para código nuevo
- Ejecuta: `python3 -m pytest src/tests.py -v`
- Tests deben pasar 100%

## Áreas de Contribución

### Alta Prioridad
- [ ] **i18n - Internacionalización**: Agregar soporte para múltiples idiomas
  - Archivos: `src/main.py`, todos los archivos con strings de UI
  - Requiere: Configuración de gettext, archivos .po
  
- [ ] **Soporte UEFI**: Mejorar manejo de UEFI Secure Boot
  - Archivos: `src/config.py`, `src/distro.py`
  - Requiere: Testing en sistemas UEFI
  
- [ ] **Más distribuciones**: Agregar soporte a más distros
  - Archivos: `src/distro.py`
  - Requiere: Verificación de rutas específicas

### Media Prioridad
- [ ] **Exportar/Importar**: Guardar y cargar configuraciones
- [ ] **Interfaz CLI**: Versión de línea de comandos
- [ ] **Temas adicionales**: Más temas gráficos de GRUB

### Baja Prioridad
- [ ] **Documentación**: Mejorar README, tutoriales
- [ ] **Optimizaciones**: Mejorar rendimiento
- [ ] **Tests**: Aumentar cobertura de tests

## Proceso de Review

Antes de mergear, un PR debe:

✅ Pasar todos los tests automatizados
✅ Tener cobertura de tests para código nuevo
✅ Seguir las pautas de código
✅ Tener descripción clara
✅ Ser revisado por al menos 1 mantenedor

## Comunicación

- **GitHub Issues**: Para bugs y features
- **Discussions** (si está habilitado): Para preguntas generales
- **Code**: En los PRs via comments

## Código de Conducta

Esperamos que todos los contribuidores:

✅ Sean respetuosos
✅ Acepten críticas constructivas
✅ Se enfoquen en lo que es mejor para el proyecto
✅ Respeten la privacidad y seguridad

## Reconocimientos

Los contribuidores serán reconocidos en:
- Lista de contribuidores en README.md
- Release notes de cada versión

¡Muchas gracias por contribuir al proyecto! 🚀
