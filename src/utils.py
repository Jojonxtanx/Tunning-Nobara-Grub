#!/usr/bin/env python3
"""
Módulo de utilidades.
Funciones auxiliares comunes.
"""

import subprocess
import os
import re
import shlex
from typing import Tuple, List, Optional, Dict
import logging


# Configurar logging base
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SecurityUtils:
    """Utilidades de seguridad para sanitizar entradas."""
    
    # Caracteres peligrosos en GRUB
    DANGEROUS_CHARS_REGEX = re.compile(r'[;&|`$(){}[\]<>\\"\']')
    # Parámetros GRUB válidos
    VALID_GRUB_PARAMS = {
        'GRUB_TIMEOUT', 'GRUB_DEFAULT', 'GRUB_SAVEDEFAULT', 
        'GRUB_DISTRIBUTOR', 'GRUB_TERMINAL_OUTPUT', 'GRUB_GFXMODE',
        'GRUB_GFXPAYLOAD_LINUX', 'GRUB_THEME', 'GRUB_DISABLE_RECOVERY',
        'GRUB_DISABLE_SUBMENU', 'GRUB_DISABLE_OS_PROBER', 
        'GRUB_CMDLINE_LINUX_DEFAULT', 'GRUB_CMDLINE_LINUX'
    }
    
    @staticmethod
    def sanitize_grub_value(value: str, allowed_special: str = "") -> str:
        """
        Sanitiza valores GRUB eliminando caracteres peligrosos.
        
        Args:
            value: Valor a sanitizar
            allowed_special: Caracteres especiales permitidos (ej: ".-/_")
            
        Returns:
            Valor sanitizado
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Permitir solo alfanuméricos, guiones, puntos y caracteres especiales permitidos
        safe_pattern = f"[a-zA-Z0-9._/{re.escape(allowed_special)}]"
        sanitized = re.sub(f"[^{re.escape('a-zA-Z0-9._/' + allowed_special)}]", "", value)
        
        return sanitized.strip()
    
    @staticmethod
    def detect_command_injection(value: str) -> bool:
        """
        Detecta intentos de inyección de comandos.
        
        Args:
            value: Valor a verificar
            
        Returns:
            True si se detecta inyección, False si es seguro
        """
        injection_patterns = [
            r'[;&|`$]',           # Separadores de comandos
            r'\$\(',              # Sustitución de comandos
            r'`.*`',              # Backticks
            r'\\\x00',            # Null bytes
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, value):
                logger.warning(f"Posible inyección detectada en: {value}")
                return True
        
        return False
    
    @staticmethod
    def validate_uuid(uuid_value: str) -> bool:
        """
        Valida formato UUID.
        
        Args:
            uuid_value: UUID a validar
            
        Returns:
            True si es UUID válido
        """
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, uuid_value.lower()))
    
    @staticmethod
    def validate_grub_param(param_name: str) -> bool:
        """
        Valida que el parámetro sea un válido de GRUB conocido.
        
        Args:
            param_name: Nombre del parámetro
            
        Returns:
            True si es válido
        """
        return param_name.upper() in SecurityUtils.VALID_GRUB_PARAMS


class SystemUtils:
    """Utilidades del sistema con manejo robusto de errores."""
    
    @staticmethod
    def check_sudo_access() -> bool:
        """
        Verifica que la aplicación tenga acceso a sudo sin contraseña.
        
        Returns:
            True si tiene acceso sudo, False en caso contrario
        """
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                logger.debug("Verificano de acceso sudo exitoso")
                return True
            else:
                logger.warning("Acceso sudo denegado o requiere contraseña")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Timeout verificando acceso sudo")
            return False
        except FileNotFoundError:
            logger.error("Comando 'sudo' no encontrado en el sistema")
            return False
        except Exception as e:
            logger.debug(f"Error al verificar acceso sudo: {e}")
            return False
    
    @staticmethod
    def get_available_themes_nobara() -> List[str]:
        """
        Obtiene lista de temas GRUB disponibles.
        
        Returns:
            Lista de nombres de temas
        """
        themes_dir = "/boot/grub2/themes"
        themes = []
        
        try:
            if not os.path.exists(themes_dir):
                logger.warning(f"Directorio de temas no encontrado: {themes_dir}")
                return themes
            
            for folder in sorted(os.listdir(themes_dir)):
                try:
                    folder_path = os.path.join(themes_dir, folder)
                    if os.path.isdir(folder_path):
                        theme_file = os.path.join(folder_path, "theme.txt")
                        if os.path.exists(theme_file):
                            themes.append(folder)
                except (OSError, PermissionError) as e:
                    logger.debug(f"Error procesando tema {folder}: {e}")
                    continue
            
            logger.info(f"Se encontraron {len(themes)} temas GRUB disponibles")
            return themes
        
        except PermissionError:
            logger.error(f"Permisos insuficientes para acceder a {themes_dir}")
            return themes
        except Exception as e:
            logger.error(f"Error al obtener lista de temas: {e}")
            return themes
    
    @staticmethod
    def get_kernel_entries() -> List[str]:
        """
        Obtiene lista de entradas de kernel BLS disponibles.
        
        Returns:
            Lista de entradas de kernel
        """
        entries = []
        entries_dir = "/boot/loader/entries"
        
        try:
            if not os.path.exists(entries_dir):
                logger.warning(f"Directorio de entradas no encontrado: {entries_dir}")
                return entries
            
            for entry_file in sorted(os.listdir(entries_dir)):
                try:
                    if entry_file.endswith(".conf") and not entry_file.endswith(("-rescue.conf", "-memtest86+.conf")):
                        # Extrae nombre legible del kernel
                        name = entry_file.replace(".conf", "").split('-')[-1]
                        entries.append(f"Nobara - {name}")
                except Exception as e:
                    logger.debug(f"Error procesando entrada {entry_file}: {e}")
                    continue
            
            logger.info(f"Se encontraron {len(entries)} entradas de kernel")
            return sorted(entries)
        
        except PermissionError:
            logger.error(f"Permisos insuficientes para acceder a {entries_dir}")
            return entries
        except Exception as e:
            logger.error(f"Error al obtener lista de kernels: {e}")
            return entries
    
    @staticmethod
    def run_command(cmd: List[str], use_sudo=False) -> Tuple[bool, str]:
        """
        Ejecuta comando del sistema con manejo robusto de errores.
        
        Args:
            cmd: Lista con comando y argumentos
            use_sudo: Si requiere elevación de privilegios
            
        Returns:
            (success: bool, output: str)
        """
        try:
            if use_sudo:
                cmd = ["sudo"] + cmd
            
            logger.debug(f"Ejecutando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.debug(f"Comando ejecutado exitosamente")
                return True, result.stdout
            else:
                error_msg = result.stderr or f"Comando retornó código {result.returncode}"
                logger.warning(f"Error ejecutando comando: {error_msg}")
                return False, error_msg
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout al ejecutar comando (timeout=30s)")
            return False, "Timeout: el comando tardó demasiado en ejecutarse"
        
        except FileNotFoundError as e:
            logger.error(f"Comando no encontrado: {cmd[0 if not use_sudo else 1]}")
            return False, f"Comando no encontrado: {str(e)}"
        
        except PermissionError:
            logger.error("Permiso denegado al ejecutar comando")
            return False, "Permiso denegado: acceso insuficiente para ejecutar el comando"
        
        except Exception as e:
            logger.error(f"Error inesperado executing comando: {type(e).__name__}: {e}")
            return False, f"Error inesperado: {str(e)}"



class Logger:
    """Sistema de logging mejorado con persistencia a archivo."""
    
    _logs = []
    _log_file = None
    
    @classmethod
    def initialize(cls, log_dir: str = None):
        """
        Inicializa el sistema de logging con archivo.
        
        Args:
            log_dir: Directorio para guardar logs (default: ~/.nobara-grub-tuner/logs)
        """
        if log_dir is None:
            log_dir = os.path.expanduser("~/.nobara-grub-tuner/logs")
        
        try:
            os.makedirs(log_dir, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cls._log_file = os.path.join(log_dir, f"grub_tuner_{timestamp}.log")
            
            # Crear archivo de log
            with open(cls._log_file, "w") as f:
                f.write(f"=== Nobara GRUB Tuner Log - {datetime.now().isoformat()} ===\n\n")
            
            logger.info(f"Archivo de log creado: {cls._log_file}")
        except Exception as e:
            logger.error(f"No se pudo inicializar logging a archivo: {e}")
    
    @classmethod
    def _write_to_file(cls, level: str, message: str):
        """Escribe log a archivo."""
        if cls._log_file:
            try:
                with open(cls._log_file, "a") as f:
                    from datetime import datetime
                    timestamp = datetime.now().isoformat()
                    f.write(f"[{timestamp}] [{level}] {message}\n")
            except Exception as e:
                logger.error(f"Error escribiendo log a archivo: {e}")
    
    @classmethod
    def clear(cls):
        """Limpia el log en memoria."""
        cls._logs = []
    
    @classmethod
    def info(cls, message: str):
        """Agrega mensaje de información."""
        cls._logs.append(("info", message))
        cls._write_to_file("INFO", message)
        print(f"ℹ️  {message}")
    
    @classmethod
    def success(cls, message: str):
        """Agrega mensaje de éxito."""
        cls._logs.append(("success", message))
        cls._write_to_file("SUCCESS", message)
        print(f"✅ {message}")
    
    @classmethod
    def warning(cls, message: str):
        """Agrega mensaje de advertencia."""
        cls._logs.append(("warning", message))
        cls._write_to_file("WARNING", message)
        print(f"⚠️  {message}")
    
    @classmethod
    def error(cls, message: str):
        """Agrega mensaje de error."""
        cls._logs.append(("error", message))
        cls._write_to_file("ERROR", message)
        print(f"❌ {message}")
    
    @classmethod
    def debug(cls, message: str):
        """Agrega mensaje de debug."""
        cls._logs.append(("debug", message))
        cls._write_to_file("DEBUG", message)
        print(f"🔍 {message}")
    
    @classmethod
    def get_logs(cls) -> List[Tuple[str, str]]:
        """Obtiene todos los logs."""
        return cls._logs.copy()
    
    @classmethod
    def get_formatted_logs(cls) -> str:
        """Obtiene logs formateados para mostrar."""
        formatted = []
        for level, message in cls._logs:
            formatted.append(message)
        return "\n".join(formatted)
    
    @classmethod
    def get_log_file_path(cls) -> Optional[str]:
        """Retorna la ruta del archivo de log."""
        return cls._log_file


class ValidationUtils:
    """Utilidades de validación mejoradas."""
    
    @staticmethod
    def validate_timeout(value: int) -> Tuple[bool, str]:
        """
        Valida rango de timeout.
        
        Args:
            value: Valor de timeout
            
        Returns:
            (es_válido, mensaje_error)
        """
        try:
            timeout = int(value)
            if not (0 <= timeout <= 30):
                return False, "El timeout debe estar entre 0 y 30 segundos"
            return True, ""
        except (ValueError, TypeError):
            return False, "El timeout debe ser un número entero"
    
    @staticmethod
    def validate_theme_exists(theme_name: str) -> Tuple[bool, str]:
        """
        Valida que el tema exista.
        
        Args:
            theme_name: Nombre del tema GRUB
            
        Returns:
            (existe, mensaje_error)
        """
        if SecurityUtils.detect_command_injection(theme_name):
            return False, "Nombre de tema contiene caracteres peligrosos"
        
        theme_path = f"/boot/grub2/themes/{theme_name}/theme.txt"
        if os.path.exists(theme_path):
            return True, ""
        return False, f"El tema '{theme_name}' no existe en {theme_path}"
    
    @staticmethod
    def validate_grub_config_writable() -> Tuple[bool, str]:
        """
        Verifica que se puede escribir en la configuración GRUB.
        
        Returns:
            (es_escribible, mensaje_error)
        """
        test_path = "/tmp/grub_test_write"
        try:
            with open(test_path, "w") as f:
                f.write("test")
            os.remove(test_path)
            return True, ""
        except PermissionError:
            return False, "Permisos insuficientes para escribir configuración GRUB"
        except Exception as e:
            return False, f"Error al verificar permisos: {str(e)}"
    
    @staticmethod
    def validate_cmdline_linux(cmdline: str) -> Tuple[bool, str]:
        """
        Valida GRUB_CMDLINE_LINUX.
        
        Args:
            cmdline: Línea de comando
            
        Returns:
            (es_válida, mensaje_error)
        """
        if SecurityUtils.detect_command_injection(cmdline):
            return False, "Línea de comando contiene caracteres peligrosos"
        
        if len(cmdline) > 256:
            return False, "La línea de comando es demasiado larga (máx 256 caracteres)"
        
        return True, ""
    
    @staticmethod
    def validate_custom_params(params: Dict[str, str]) -> Tuple[bool, str]:
        """
        Valida parámetros personalizados GRUB.
        
        Args:
            params: Diccionario de parámetros
            
        Returns:
            (son_válidos, mensaje_error)
        """
        for key, value in params.items():
            # Validar nombre de parámetro
            if not re.match(r'^GRUB_[A-Z_]+$', key):
                return False, f"Nombre de parámetro inválido: {key}"
            
            # Validar valor
            if SecurityUtils.detect_command_injection(value):
                return False, f"Valor del parámetro {key} contiene caracteres peligrosos"
            
            if len(value) > 512:
                return False, f"Valor del parámetro {key} es demasiado largo"
        
        return True, ""
