#!/usr/bin/env python3
"""
Módulo de detección y compatibilidad con múltiples distribuciones Linux.
Gestiona diferencias entre Nobara, Fedora, Ubuntu, Arch, etc.
"""

import os
import re
import subprocess
from typing import Dict, Optional, Tuple
from enum import Enum


class LinuxDistro(Enum):
    """Distribuciones Linux soportadas."""
    NOBARA = "nobara"
    FEDORA = "fedora"
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    ARCH = "arch"
    MANJARO = "manjaro"
    OPENSUSE = "opensuse"
    UNKNOWN = "unknown"


class DistroInfo:
    """Información sobre la distribución Linux actual."""
    
    def __init__(self):
        self.distro = self._detect_distro()
        self.distro_name = self._get_distro_name()
        self.distro_version = self._get_distro_version()
        self.config = self._get_distro_config()
    
    @staticmethod
    def _detect_distro() -> LinuxDistro:
        """
        Detecta la distribución Linux ejecutándose.
        
        Returns:
            LinuxDistro detectada
        """
        try:
            # Intenta leer /etc/os-release (estándar moderno)
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    
                    if "nobara" in content:
                        return LinuxDistro.NOBARA
                    elif "fedora" in content:
                        return LinuxDistro.FEDORA
                    elif "ubuntu" in content:
                        return LinuxDistro.UBUNTU
                    elif "debian" in content:
                        return LinuxDistro.DEBIAN
                    elif "arch" in content:
                        return LinuxDistro.ARCH
                    elif "manjaro" in content:
                        return LinuxDistro.MANJARO
                    elif "opensuse" in content or "suse" in content:
                        return LinuxDistro.OPENSUSE
            
            # Fallback a /etc/issue
            if os.path.exists("/etc/issue"):
                with open("/etc/issue", "r") as f:
                    content = f.read().lower()
                    
                    if "nobara" in content:
                        return LinuxDistro.NOBARA
                    elif "fedora" in content:
                        return LinuxDistro.FEDORA
                    elif "ubuntu" in content:
                        return LinuxDistro.UBUNTU
                    elif "debian" in content:
                        return LinuxDistro.DEBIAN
            
            return LinuxDistro.UNKNOWN
        
        except Exception:
            return LinuxDistro.UNKNOWN
    
    def _get_distro_name(self) -> str:
        """
        Obtiene nombre legible de la distribución.
        
        Returns:
            Nombre de la distribución
        """
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        match = re.search(r'"([^"]+)"', line)
                        if match:
                            return match.group(1)
        except:
            pass
        
        return self.distro.value.capitalize()
    
    def _get_distro_version(self) -> Optional[str]:
        """
        Obtiene versión de la distribución.
        
        Returns:
            Versión o None
        """
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("VERSION_ID"):
                        match = re.search(r'"([^"]+)"', line)
                        if match:
                            return match.group(1)
        except:
            pass
        
        return None
    
    def _get_distro_config(self) -> Dict[str, str]:
        """
        Obtiene configuración específica de la distribución.
        
        Returns:
            Diccionario con rutas y comandos específicos
        """
        config_map = {
            LinuxDistro.NOBARA: {
                "grub_config_path": "/etc/default/grub",
                "grub_dir": "/boot/grub2",
                "grub_mkconfig": "grub2-mkconfig",
                "efi_paths": ["/boot/efi/EFI/fedora/grub.cfg"],
                "themes_dir": "/boot/grub2/themes",
                "entries_dir": "/boot/loader/entries",
                "package_manager": "dnf",
            },
            LinuxDistro.FEDORA: {
                "grub_config_path": "/etc/default/grub",
                "grub_dir": "/boot/grub2",
                "grub_mkconfig": "grub2-mkconfig",
                "efi_paths": ["/boot/efi/EFI/fedora/grub.cfg"],
                "themes_dir": "/boot/grub2/themes",
                "entries_dir": "/boot/loader/entries",
                "package_manager": "dnf",
            },
            LinuxDistro.UBUNTU: {
                "grub_config_path": "/etc/default/grub",
                "grub_dir": "/boot/grub",
                "grub_mkconfig": "grub-mkconfig",
                "efi_paths": ["/boot/efi/EFI/ubuntu/grub.cfg"],
                "themes_dir": "/boot/grub/themes",
                "entries_dir": "/boot/grub.d",
                "package_manager": "apt",
            },
            LinuxDistro.DEBIAN: {
                "grub_config_path": "/etc/default/grub",
                "grub_dir": "/boot/grub",
                "grub_mkconfig": "grub-mkconfig",
                "efi_paths": ["/boot/efi/EFI/debian/grub.cfg"],
                "themes_dir": "/boot/grub/themes",
                "entries_dir": "/boot/grub.d",
                "package_manager": "apt",
            },
            LinuxDistro.ARCH: {
                "grub_config_path": "/etc/default/grub",
                "grub_dir": "/boot/grub",
                "grub_mkconfig": "grub-mkconfig",
                "efi_paths": ["/boot/efi/EFI/BOOT/grub.cfg"],
                "themes_dir": "/boot/grub/themes",
                "entries_dir": "/boot",
                "package_manager": "pacman",
            },
            LinuxDistro.MANJARO: {
                "grub_config_path": "/etc/default/grub",
                "grub_dir": "/boot/grub",
                "grub_mkconfig": "grub-mkconfig",
                "efi_paths": ["/boot/efi/EFI/Manjaro/grub.cfg"],
                "themes_dir": "/boot/grub/themes",
                "entries_dir": "/boot",
                "package_manager": "pacman",
            },
            LinuxDistro.OPENSUSE: {
                "grub_config_path": "/etc/default/grub",
                "grub_dir": "/boot/grub2",
                "grub_mkconfig": "grub2-mkconfig",
                "efi_paths": ["/boot/efi/EFI/opensuse/grub.cfg"],
                "themes_dir": "/boot/grub2/themes",
                "entries_dir": "/boot/loader/entries",
                "package_manager": "zypper",
            },
        }
        
        distro_config = config_map.get(self.distro)
        
        if distro_config:
            return distro_config
        
        # Default para distros desconocidas (basado en Fedora)
        return config_map[LinuxDistro.FEDORA]
    
    def get_grub_config_path(self) -> str:
        """Obtiene ruta del archivo de configuración GRUB."""
        return self.config["grub_config_path"]
    
    def get_grub_dir(self) -> str:
        """Obtiene directorio principal de GRUB."""
        return self.config["grub_dir"]
    
    def get_grub_mkconfig_cmd(self) -> str:
        """Obtiene comando para regenerar GRUB."""
        return self.config["grub_mkconfig"]
    
    def get_efi_paths(self) -> list:
        """Obtiene rutas de configuración EFI de GRUB."""
        return self.config["efi_paths"]
    
    def get_themes_dir(self) -> str:
        """Obtiene directorio de temas GRUB."""
        return self.config["themes_dir"]
    
    def get_entries_dir(self) -> str:
        """Obtiene directorio de entradas de boot."""
        return self.config["entries_dir"]
    
    def get_package_manager(self) -> str:
        """Obtiene administrador de paquetes de la distro."""
        return self.config["package_manager"]
    
    def is_supported(self) -> bool:
        """
        Verifica si la distro es soportada.
        
        Returns:
            True si es soportada, False si es desconocida/no soportada
        """
        return self.distro != LinuxDistro.UNKNOWN
    
    def __str__(self) -> str:
        """Representación en string."""
        return f"{self.distro_name} ({self.distro.value})"


# Instancia global de info de distro
_distro_info = None


def get_distro_info() -> DistroInfo:
    """
    Obtiene información de la distro Linux (con caching).
    
    Returns:
        DistroInfo con información de la distro actual
    """
    global _distro_info
    if _distro_info is None:
        _distro_info = DistroInfo()
    return _distro_info
