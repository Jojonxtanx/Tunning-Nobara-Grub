#!/usr/bin/env python3
"""
Módulo de configuración GRUB.
Maneja lectura, parseo y generación de configuración con validación de seguridad.
Soporta múltiples distribuciones Linux (Nobara, Fedora, Ubuntu, Debian, Arch, etc.)
"""

import subprocess
import re
import os
from pathlib import Path
from typing import Tuple, Optional, Dict

from .utils import SecurityUtils, ValidationUtils, Logger
from .distro import get_distro_info, DistroInfo


class GrubConfig:
    """Gestor de configuración GRUB con validación de seguridad y soporte multi-distro."""
    
    def __init__(self):
        self.config = {}
        self.distro_info: DistroInfo = get_distro_info()
        
        # Usar rutas configur específicas de la distro
        self.GRUB_CONFIG_PATH = self.distro_info.get_grub_config_path()
        self.GRUB_DIR = self.distro_info.get_grub_dir()
        self.BOOT_DIR = "/boot"
        self.EFI_GRUB_PATHS = self.distro_info.get_efi_paths()
        self.GRUB_MKCONFIG = self.distro_info.get_grub_mkconfig_cmd()
        self.THEMES_DIR = self.distro_info.get_themes_dir()
        self.ENTRIES_DIR = self.distro_info.get_entries_dir()
        
        Logger.initialize()
        Logger.info(f"Inicializando GrubConfig para: {self.distro_info}")
        
        if not self.distro_info.is_supported():
            Logger.warning(
                f"Distribución '{self.distro_info.distro.value}' puede no ser totalmente soportada. "
                "Se usarán valores por defecto."
            )
        
        self.load_current_config()
    
    def load_current_config(self) -> bool:
        """
        Lee la configuración actual de /etc/default/grub.
        
        Returns:
            True si se cargó correctamente, False si hubo error
        """
        self.config = {}
        try:
            if not os.path.exists(self.GRUB_CONFIG_PATH):
                Logger.warning(f"Archivo GRUB no encontrado: {self.GRUB_CONFIG_PATH}")
                return False
            
            with open(self.GRUB_CONFIG_PATH, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip().strip('"')
            
            Logger.info("Configuración GRUB cargada exitosamente")
            return True
        except Exception as e:
            Logger.error(f"Error leyendo GRUB config: {e}")
            raise Exception(f"Error leyendo GRUB config: {e}")
    
    def get_current_value(self, key: str, default: str = "") -> str:
        """
        Obtiene valor actual de configuración.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto
            
        Returns:
            Valor de configuración o default
        """
        return self.config.get(key, default)
    
    def detect_resume_uuid(self) -> Optional[str]:
        """
        Detecta automáticamente el UUID de la partición swap.
        
        Returns:
            UUID de la partición swap o None
        """
        try:
            # Busca particiones swap
            output = subprocess.check_output(
                ["lsblk", "-no", "UUID,TYPE"],
                text=True,
                timeout=5
            ).strip().splitlines()
            
            for line in output:
                parts = line.split()
                if len(parts) >= 2 and parts[-1] == "swap":
                    uuid = parts[0]
                    # Validar que sea UUID válido
                    if uuid and SecurityUtils.validate_uuid(uuid):
                        Logger.info(f"UUID de swap detectado: {uuid}")
                        return uuid
            
            Logger.warning("No se encontró partición swap")
            return None
        except subprocess.TimeoutExpired:
            Logger.error("Timeout al detectar UUID de swap")
            return None
        except Exception as e:
            Logger.error(f"Error detectando UUID: {e}")
            return None
    
    def detect_all_swap_devices(self) -> Dict[str, str]:
        """
        Detecta todos los dispositivos swap disponibles.
        
        Returns:
            Diccionario con nombre_dispositivo: uuid
        """
        swap_devices = {}
        try:
            output = subprocess.check_output(
                ["lsblk", "-no", "NAME,UUID,TYPE"],
                text=True,
                timeout=5
            ).strip().splitlines()
            
            for line in output:
                parts = line.split()
                if len(parts) >= 3 and parts[-1] == "swap":
                    name = parts[0]
                    uuid = parts[1]
                    if uuid and SecurityUtils.validate_uuid(uuid):
                        swap_devices[name] = uuid
                        Logger.info(f"Dispositivo swap encontrado: {name} ({uuid})")
            
            return swap_devices
        
        except subprocess.TimeoutExpired:
            Logger.error("Timeout al detectar dispositivos swap")
            return swap_devices
        except Exception as e:
            Logger.error(f"Error detectando dispositivos swap: {e}")
            return swap_devices
    
    def get_current_timeout(self) -> int:
        """
        Obtiene timeout actual.
        
        Returns:
            Timeout en segundos (0-30)
        """
        try:
            timeout = int(self.get_current_value("GRUB_TIMEOUT", "3"))
            return max(0, min(30, timeout))  # Limita entre 0 y 30
        except:
            return 3
    
    def get_current_theme(self) -> str:
        """
        Obtiene tema actual.
        
        Returns:
            Nombre del tema GRUB
        """
        theme_path = self.get_current_value("GRUB_THEME", "")
        if theme_path and "/themes/" in theme_path:
            # Extrae nombre del tema de la ruta
            match = re.search(r'/themes/([^/]+)/', theme_path)
            if match:
                return match.group(1)
        return "nobara"
    
    def get_submenu_disabled(self) -> bool:
        """
        Obtiene estado de GRUB_DISABLE_SUBMENU.
        
        Returns:
            True si el submenú está deshabilitado
        """
        value = self.get_current_value("GRUB_DISABLE_SUBMENU", "true")
        return value.lower() == "true"
    
    def generate_config(
        self, 
        timeout: int, 
        theme: str, 
        disable_submenu: bool, 
        custom_params: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str]:
        """
        Genera nueva configuración GRUB con validación.
        
        Args:
            timeout: Segundos antes de boot automático
            theme: Nombre del tema
            disable_submenu: Boolean para deshabilitar submenú
            custom_params: Dict opcional con parámetros personalizados
            
        Returns:
            (éxito: bool, contenido_o_error: str)
        """
        # Validar timeout
        is_valid, error_msg = ValidationUtils.validate_timeout(timeout)
        if not is_valid:
            Logger.error(f"Timeout inválido: {error_msg}")
            return False, error_msg
        
        # Validar tema
        is_valid, error_msg = ValidationUtils.validate_theme_exists(theme)
        if not is_valid:
            Logger.error(f"Tema inválido: {error_msg}")
            return False, error_msg
        
        # Validar parámetros personalizados
        if custom_params:
            is_valid, error_msg = ValidationUtils.validate_custom_params(custom_params)
            if not is_valid:
                Logger.error(f"Parámetros inválidos: {error_msg}")
                return False, error_msg
        
        submenu = "true" if disable_submenu else "false"
        theme_path = f"/boot/grub2/themes/{theme}/theme.txt"
        
        # Resume UUID
        resume_uuid = self.detect_resume_uuid()
        resume_param = f"resume=UUID={resume_uuid}" if resume_uuid else ""
        
        # Obtener valores actuales o usar defaults
        current_cmdline = self.get_current_value("GRUB_CMDLINE_LINUX_DEFAULT", "quiet splash")
        if resume_param and resume_param not in current_cmdline:
            current_cmdline = f"{current_cmdline} {resume_param}".strip()
        
        # Validar línea de comandos
        is_valid, error_msg = ValidationUtils.validate_cmdline_linux(current_cmdline)
        if not is_valid:
            Logger.warning(f"Advertencia en CMDLINE: {error_msg}")
        
        config_lines = [
            f"GRUB_TIMEOUT={timeout}",
            f"GRUB_DEFAULT=saved",
            f"GRUB_SAVEDEFAULT=true",
            f"GRUB_DISTRIBUTOR=\"Nobara Linux\"",
            f"GRUB_TERMINAL_OUTPUT=\"gfxterm\"",
            f"GRUB_GFXMODE=1920x1080,auto",
            f"GRUB_GFXPAYLOAD_LINUX=keep",
            f'GRUB_THEME="{theme_path}"',
            f"GRUB_DISABLE_RECOVERY=true",
            f"GRUB_DISABLE_SUBMENU={submenu}",
            f"GRUB_DISABLE_OS_PROBER=false",
            f"GRUB_CMDLINE_LINUX_DEFAULT=\"{current_cmdline}\"",
            f"GRUB_CMDLINE_LINUX=\"rd.driver.blacklist=nouveau rd.driver.blacklist=nova-core\"",
        ]
        
        # Aplicar parámetros personalizados
        if custom_params:
            for key, value in custom_params.items():
                # Sanitizar y validar
                sanitized_value = SecurityUtils.sanitize_grub_value(value, allowed_special="-._/=")
                config_lines.append(f"{key}=\"{sanitized_value}\"")
        
        config_content = "\n".join(config_lines)
        Logger.info("Configuración GRUB generada correctamente")
        return True, config_content
    
    def validate_theme(self, theme_name: str) -> bool:
        """
        Valida que el tema exista.
        
        Args:
            theme_name: Nombre del tema
            
        Returns:
            True si existe el tema
        """
        is_valid, _ = ValidationUtils.validate_theme_exists(theme_name)
        return is_valid
    
    def create_backup(self) -> Tuple[bool, str]:
        """
        Crea backup de la configuración actual.
        
        Returns:
            (éxito: bool, ruta_backup_o_error: str)
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"/etc/default/grub.backup-{timestamp}"
        
        try:
            result = subprocess.run(
                ["sudo", "cp", self.GRUB_CONFIG_PATH, backup_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                Logger.success(f"Backup creado: {backup_path}")
                return True, backup_path
            else:
                error = result.stderr or "Error desconocido"
                Logger.error(f"Error en backup: {error}")
                return False, error
                
        except subprocess.TimeoutExpired:
            Logger.error("Timeout al crear backup")
            return False, "Timeout al crear backup"
        except Exception as e:
            Logger.error(f"Excepción en backup: {e}")
            return False, str(e)
    
    def apply_config(self, config_content: str) -> Tuple[bool, str]:
        """
        Aplica nueva configuración GRUB con manejo robusto de errores.
        
        Args:
            config_content: Contenido de la nueva configuración
            
        Returns:
            (éxito: bool, mensaje: str)
        """
        temp_path = "/tmp/grub_config"
        
        try:
            Logger.info("Iniciando aplicación de configuración GRUB...")
            
            # Escribir a archivo temporal
            with open(temp_path, "w") as f:
                f.write(config_content)
            Logger.debug(f"Archivo temporal creado: {temp_path}")
            
            # Copiar a /etc/default/grub
            result = subprocess.run(
                ["sudo", "cp", temp_path, self.GRUB_CONFIG_PATH],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                Logger.error(f"Error copiando configuración: {result.stderr}")
                return False, f"❌ Error al copiar configuración: {result.stderr}"
            
            Logger.info("Configuración copiada a /etc/default/grub")
            
            # Regenerar GRUB config
            result = subprocess.run(
                ["sudo", self.GRUB_MKCONFIG, "-o", f"{self.GRUB_DIR}/grub.cfg"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                Logger.error(f"Error regenerando GRUB: {result.stderr}")
                return False, f"❌ Error al regenerar GRUB: {result.stderr}"
            
            Logger.info("GRUB config regenerado")
            
            # Regenerar EFI GRUB si existen los paths
            for efi_path in self.EFI_GRUB_PATHS:
                if os.path.exists(efi_path):
                    result = subprocess.run(
                        ["sudo", self.GRUB_MKCONFIG, "-o", efi_path],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    if result.returncode != 0:
                        Logger.warning(f"Advertencia regenerando EFI GRUB ({efi_path}): {result.stderr}")
                    else:
                        Logger.info(f"EFI GRUB config regenerado ({efi_path})")
            
            # Limpiar archivo temporal
            try:
                os.remove(temp_path)
            except:
                pass
            
            Logger.success("Configuración GRUB aplicada correctamente")
            return True, "✅ Configuración aplicada correctamente"
        
        except subprocess.TimeoutExpired:
            Logger.error("Timeout al aplicar configuración")
            return False, "❌ Timeout al aplicar configuración"
        except Exception as e:
            Logger.error(f"Excepción al aplicar configuración: {e}")
            return False, f"❌ Error: {str(e)}"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
        finally:
            # Limpiar temporal
            try:
                os.remove(temp_path)
            except:
                pass


class BootEntryManager:
    """Gestor de orden de entradas de boot en GRUB."""
    
    def __init__(self):
        self.distro_info = get_distro_info()
        self.boot_entries = []
        self.grub_cfg_path = f"{self.distro_info.get_grub_dir()}/grub.cfg"
        self.custom_entry_order_file = "/etc/grub.d/06_custom_order"
        
    def detect_boot_entries(self) -> Dict[str, str]:
        """
        Detecta todas las entradas de boot disponibles.
        
        Returns:
            Dict con {nombre: indices_grub}
        """
        entries = {}
        
        try:
            with open(self.grub_cfg_path, 'r') as f:
                content = f.read()
            
            # Buscar líneas menuentry
            pattern = r"menuentry\s+['\"]([^'\"]+)['\"]"
            matches = re.finditer(pattern, content)
            
            for idx, match in enumerate(matches):
                entry_name = match.group(1)
                if entry_name:
                    entries[entry_name] = idx
                    Logger.debug(f"Boot entry detectado: {entry_name} (índice {idx})")
            
            self.boot_entries = list(entries.keys())
            Logger.success(f"Se encontraron {len(entries)} entradas de boot")
            return entries
            
        except FileNotFoundError:
            Logger.error(f"Archivo no encontrado: {self.grub_cfg_path}")
            return {}
        except Exception as e:
            Logger.error(f"Error al detectar boot entries: {e}")
            return {}
    
    def get_boot_entries(self) -> list:
        """Retorna lista de entradas de boot actuales."""
        if not self.boot_entries:
            self.detect_boot_entries()
        return self.boot_entries.copy()
    
    def reorder_entries(self, new_order: list) -> Tuple[bool, str]:
        """
        Reordena las entradas de boot.
        
        Args:
            new_order: Lista con el nuevo orden de entradas
            
        Returns:
            (éxito, mensaje)
        """
        # Validar que todas las entradas existen
        for entry in new_order:
            if entry not in self.boot_entries:
                return False, f"Entrada de boot no válida: {entry}"
        
        try:
            # Leer grub.cfg actual
            with open(self.grub_cfg_path, 'r') as f:
                original_content = f.read()
            
            # Extraer todas las entradas de boot
            boot_entries_content = {}
            pattern = r"(menuentry\s+['\"]([^'\"]+)['\"]\s+[^{]*\{[^}]*\})"
            
            for match in re.finditer(pattern, original_content, re.DOTALL):
                full_entry = match.group(1)
                entry_name = match.group(2)
                boot_entries_content[entry_name] = full_entry
            
            # Guardar el nuevo orden en un archivo custom
            custom_script = self._generate_custom_order_script(new_order)
            
            result = subprocess.run(
                ["sudo", "tee", self.custom_entry_order_file],
                input=custom_script,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, "Error al escribir el archivo custom"
            
            # Hacer ejecutable
            subprocess.run(["sudo", "chmod", "+x", self.custom_entry_order_file])
            
            Logger.success(f"Orden de boot reordenado: {', '.join(new_order)}")
            return True, "✅ Orden de boot reordenado correctamente"
            
        except Exception as e:
            Logger.error(f"Error al reordenar boot entries: {e}")
            return False, f"❌ Error: {str(e)}"
    
    def _generate_custom_order_script(self, order: list) -> str:
        """Genera script custom para /etc/grub.d/06_custom_order."""
        script = """#!/bin/bash
# Custom boot order script
# Auto-generado por Nobara GRUB Tuner

which gettext >/dev/null 2>&1 || gettext() { echo "$@"; }

CLASS="--class gnu-linux --class os"

"""
        
        for idx, entry in enumerate(order):
            script += f'menuentry_id_option="--id {entry.lower().replace(" ", "_")}"\\n'
        
        return script
    
    def set_default_entry(self, entry_name: str) -> Tuple[bool, str]:
        """
        Establece la entrada de boot por defecto.
        
        Args:
            entry_name: Nombre de la entrada a establecer como predeterminada
            
        Returns:
            (éxito, mensaje)
        """
        grub_config = GrubConfig()
        
        # Validar que la entrada existe
        if entry_name not in self.boot_entries:
            return False, f"Entrada de boot no válida: {entry_name}"
        
        try:
            # Buscar el índice de la entrada
            entries = self.detect_boot_entries()
            entry_index = entries.get(entry_name)
            
            if entry_index is None:
                return False, "Entrada no encontrada"
            
            # Modificar GRUB_DEFAULT
            grub_config.config['GRUB_DEFAULT'] = str(entry_index)
            
            # Guardar configuración
            config_content = grub_config.generate_config()
            success, message = grub_config.apply_config(config_content)
            
            if success:
                Logger.success(f"Entrada por defecto establecida: {entry_name}")
            
            return success, message
            
        except Exception as e:
            Logger.error(f"Error al establecer entrada predeterminada: {e}")
            return False, f"❌ Error: {str(e)}"
