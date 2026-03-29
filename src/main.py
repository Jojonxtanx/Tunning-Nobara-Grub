#!/usr/bin/env python3
"""
Nobara GRUB Tuner - Punto de entrada de la aplicación.
Configurador gráfico avanzado para GRUB en Nobara Linux.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw
from .ui import NobaraGrubTunerApp
from .utils import Logger


def main():
    """Función principal."""
    # Inicializar sistema de logging
    Logger.initialize()
    Logger.info("Iniciando Nobara GRUB Tuner - GTK4/Adwaita")
    
    app = NobaraGrubTunerApp()
    
    return app.run()


if __name__ == "__main__":
    exit(main())