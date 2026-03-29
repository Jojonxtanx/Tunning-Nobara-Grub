#!/usr/bin/env python3
"""
Módulo de versionado de configuración GRUB.
Permite ver el historial de cambios y revertir a configuraciones anteriores.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .utils import Logger


class ConfigVersion:
    """Representa una versión de configuración GRUB."""
    
    def __init__(self, version_id: str, timestamp: str, description: str, config_path: str):
        self.version_id = version_id
        self.timestamp = timestamp
        self.description = description
        self.config_path = config_path
        self.config_content = None
        
        # Cargar contenido de configuración
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.config_content = f.read()
        except Exception as e:
            Logger.error(f"Error cargando versión {version_id}: {e}")
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización JSON."""
        return {
            "version_id": self.version_id,
            "timestamp": self.timestamp,
            "description": self.description,
        }
    
    def get_summary(self) -> str:
        """Obtiene resumen de la versión."""
        if not self.config_content:
            return f"{self.version_id} - {self.timestamp} (vacío)"
        
        lines = len(self.config_content.splitlines())
        return f"{self.version_id} - {self.timestamp} - {self.description} ({lines} líneas)"


class ConfigVersionManager:
    """Gestor de versiones de configuración GRUB."""
    
    def __init__(self, grub_config_path: str = "/etc/default/grub"):
        self.grub_config_path = grub_config_path
        self.versions_dir = os.path.expanduser("~/.nobara-grub-tuner/versions")
        self.index_file = os.path.join(self.versions_dir, "index.json")
        self.versions: List[ConfigVersion] = []
        
        # Crear directorio de versiones si no existe
        os.makedirs(self.versions_dir, exist_ok=True)
        
        # Cargar índice de versiones existentes
        self._load_index()
        
        Logger.info(f"ConfigVersionManager inicializado. Versiones: {len(self.versions)}")
    
    def _load_index(self):
        """Carga el índice de versiones desde JSON."""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r') as f:
                    index_data = json.load(f)
                    self.versions = [
                        ConfigVersion(
                            v["version_id"],
                            v["timestamp"],
                            v.get("description", ""),
                            os.path.join(self.versions_dir, f"{v['version_id']}.grub")
                        )
                        for v in index_data.get("versions", [])
                    ]
        except Exception as e:
            Logger.warning(f"Error cargando índice de versiones: {e}")
            self.versions = []
    
    def _save_index(self):
        """Guarda el índice de versiones a JSON."""
        try:
            index_data = {
                "created": datetime.now().isoformat(),
                "version_count": len(self.versions),
                "versions": [v.to_dict() for v in self.versions]
            }
            
            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
        except Exception as e:
            Logger.error(f"Error guardando índice de versiones: {e}")
    
    def save_version(self, description: str = "Cambios aplicados") -> Tuple[bool, str]:
        """
        Guarda la versión actual de la configuración.
        
        Args:
            description: Descripción de los cambios realizados
            
        Returns:
            (éxito, version_id_o_error)
        """
        try:
            # Generar ID de versión
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_id = f"v{timestamp}"
            version_path = os.path.join(self.versions_dir, f"{version_id}.grub")
            
            # Copiar configuración actual
            if not os.path.exists(self.grub_config_path):
                Logger.error(f"Archivo de configuración no encontrado: {self.grub_config_path}")
                return False, "Archivo de configuración no encontrado"
            
            with open(self.grub_config_path, 'r') as src:
                config_content = src.read()
            
            with open(version_path, 'w') as dst:
                dst.write(config_content)
            
            # Agregar a índice
            version = ConfigVersion(
                version_id,
                timestamp,
                description,
                version_path
            )
            version.config_content = config_content
            self.versions.append(version)
            
            # Guardar índice
            self._save_index()
            
            Logger.success(f"Versión guardada: {version_id}")
            return True, version_id
        
        except Exception as e:
            Logger.error(f"Error guardando versión: {e}")
            return False, str(e)
    
    def get_version(self, version_id: str) -> Optional[ConfigVersion]:
        """
        Obtiene una versión específica.
        
        Args:
            version_id: ID de la versión
            
        Returns:
            ConfigVersion o None si no existe
        """
        for version in self.versions:
            if version.version_id == version_id:
                return version
        
        return None
    
    def list_versions(self, limit: int = 10) -> List[ConfigVersion]:
        """
        Lista las versiones más recientes.
        
        Args:
            limit: Número máximo de versiones a retornar
            
        Returns:
            Lista de ConfigVersion ordenadas por fecha (más recientes primero)
        """
        # Ordenar por timestamp descendente (más recientes primero)
        sorted_versions = sorted(self.versions, key=lambda v: v.timestamp, reverse=True)
        return sorted_versions[:limit]
    
    def restore_version(self, version_id: str) -> Tuple[bool, str]:
        """
        Restaura una versión anterior de la configuración.
        Requiere permisos de sudo.
        
        Args:
            version_id: ID de la versión a restaurar
            
        Returns:
            (éxito, mensaje)
        """
        try:
            version = self.get_version(version_id)
            if not version:
                return False, f"Versión no encontrada: {version_id}"
            
            if not version.config_content:
                return False, f"Configuración de versión {version_id} está vacía"
            
            # Crear backup de la versión actual antes de restaurar
            current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"backup_before_restore_{current_timestamp}"
            backup_success, backup_msg = self.save_version(
                f"Backup antes de restaurar {version_id}"
            )
            
            if not backup_success:
                Logger.warning(f"No se pudo crear backup: {backup_msg}")
            
            # Restaurar versión
            temp_path = "/tmp/grub_restore"
            with open(temp_path, 'w') as f:
                f.write(version.config_content)
            
            result = subprocess.run(
                ["sudo", "cp", temp_path, self.grub_config_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                error = result.stderr or "Error desconocido"
                Logger.error(f"Error restaurando versión: {error}")
                return False, f"Error al restaurar: {error}"
            
            # Regenerar GRUB (requiere detectar distro)
            try:
                result = subprocess.run(
                    ["sudo", "grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                if result.returncode != 0:
                    Logger.warning("No se pudo regenerar GRUB (posible distro diferente)")
            except:
                Logger.warning("No se pudo regenerar GRUB automáticamente")
            
            # Limpiar
            try:
                os.remove(temp_path)
            except:
                pass
            
            Logger.success(f"Versión restaurada: {version_id}")
            return True, f"Versión {version_id} restaurada exitosamente"
        
        except Exception as e:
            Logger.error(f"Excepción restaurando versión: {e}")
            return False, str(e)
    
    def delete_version(self, version_id: str) -> Tuple[bool, str]:
        """
        Elimina una versión específica.
        
        Args:
            version_id: ID de la versión a eliminar
            
        Returns:
            (éxito, mensaje)
        """
        try:
            version = self.get_version(version_id)
            if not version:
                return False, f"Versión no encontrada: {version_id}"
            
            # Eliminar archivo de configuración
            if os.path.exists(version.config_path):
                os.remove(version.config_path)
            
            # Eliminar del índice
            self.versions.remove(version)
            self._save_index()
            
            Logger.success(f"Versión eliminada: {version_id}")
            return True, f"Versión {version_id} eliminada"
        
        except Exception as e:
            Logger.error(f"Error eliminando versión: {e}")
            return False, str(e)
    
    def get_version_diff(self, version1_id: str, version2_id: str) -> Optional[str]:
        """
        Obtiene diferencias entre dos versiones.
        
        Args:
            version1_id: ID de la primera versión
            version2_id: ID de la segunda versión
            
        Returns:
            String con diff unificado o None si hay error
        """
        try:
            version1 = self.get_version(version1_id)
            version2 = self.get_version(version2_id)
            
            if not version1 or not version2:
                return None
            
            if not version1.config_content or not version2.config_content:
                return None
            
            # Usar diff del sistema
            import difflib
            
            diff = difflib.unified_diff(
                version1.config_content.splitlines(keepends=True),
                version2.config_content.splitlines(keepends=True),
                fromfile=version1_id,
                tofile=version2_id
            )
            
            return ''.join(diff)
        
        except Exception as e:
            Logger.error(f"Error calculando diff: {e}")
            return None
    
    def cleanup_old_versions(self, keep_last: int = 20) -> Tuple[bool, str]:
        """
        Elimina versiones antiguas manteniendo las últimas N.
        
        Args:
            keep_last: Número de versiones recientes a mantener
            
        Returns:
            (éxito, mensaje)
        """
        try:
            if len(self.versions) <= keep_last:
                return True, f"Ya hay {len(self.versions)} versiones (limite: {keep_last})"
            
            # Ordenar por timestamp y eliminar las antiguas
            sorted_versions = sorted(self.versions, key=lambda v: v.timestamp, reverse=True)
            versions_to_delete = sorted_versions[keep_last:]
            
            deleted_count = 0
            for version in versions_to_delete:
                try:
                    if os.path.exists(version.config_path):
                        os.remove(version.config_path)
                    self.versions.remove(version)
                    deleted_count += 1
                except Exception as e:
                    Logger.warning(f"No se pudo eliminar {version.version_id}: {e}")
            
            self._save_index()
            
            return True, f"Se eliminaron {deleted_count} versiones antiguas"
        
        except Exception as e:
            Logger.error(f"Error en limpieza de versiones: {e}")
            return False, str(e)
