#!/bin/bash
# Script para ejecutar Nobara GRUB Tuner

# Ir al directorio del proyecto
cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar la aplicación
python3 -m src.main