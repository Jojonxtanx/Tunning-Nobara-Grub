#!/usr/bin/env python3
"""
Tests unitarios para Nobara GRUB Tuner.
Prueba funcionalidades críticas de configuración y seguridad.
"""

import unittest
from unittest.mock import patch, MagicMock
from .utils import SecurityUtils, ValidationUtils, Logger
from .config import GrubConfig


class TestSecurityUtils(unittest.TestCase):
    """Tests para SecurityUtils."""
    
    def test_validate_uuid_valid_format(self):
        """Valida formato UUID correcto."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        self.assertTrue(SecurityUtils.validate_uuid(valid_uuid))
    
    def test_validate_uuid_invalid_format(self):
        """Rechaza formato UUID incorrecto."""
        invalid_uuids = [
            "550e8400-e29b-41d4-a716",  # Incompleto
            "550e8400e29b41d4a716446655440000",  # Sin guiones
            "xxx-xxx-xxx-xxx-xxxxxxxxxxxx",  # Caracteres inválidos
        ]
        for uuid in invalid_uuids:
            self.assertFalse(SecurityUtils.validate_uuid(uuid))
    
    def test_detect_command_injection_semicolon(self):
        """Detecta inyección de comandos con semicolon."""
        self.assertTrue(SecurityUtils.detect_command_injection("value; rm -rf /"))
    
    def test_detect_command_injection_pipe(self):
        """Detecta inyección de comandos con pipe."""
        self.assertTrue(SecurityUtils.detect_command_injection("value | cat /etc/passwd"))
    
    def test_detect_command_injection_backticks(self):
        """Detecta inyección de comandos con backticks."""
        self.assertTrue(SecurityUtils.detect_command_injection("value `malicious`"))
    
    def test_detect_command_injection_subshell(self):
        """Detecta inyección de comandos con subshell."""
        self.assertTrue(SecurityUtils.detect_command_injection("value $(whoami)"))
    
    def test_detect_safe_value(self):
        """No detecta como inyección valores seguros."""
        safe_values = [
            "1920x1080",
            "nobara",
            "quiet splash",
            "rd.driver.blacklist=nouveau",
            "uuid-123-456",
        ]
        for value in safe_values:
            self.assertFalse(SecurityUtils.detect_command_injection(value))
    
    def test_sanitize_grub_value(self):
        """Sanitiza valores GRUB correctamente."""
        result = SecurityUtils.sanitize_grub_value("1920x1080")
        self.assertEqual(result, "1920x1080")
    
    def test_sanitize_grub_value_removes_dangerous_chars(self):
        """Remueve caracteres peligrosos."""
        result = SecurityUtils.sanitize_grub_value("value;dangerous`command")
        self.assertNotIn(";", result)
        self.assertNotIn("`", result)
    
    def test_validate_grub_param_valid(self):
        """Valida parámetros GRUB válidos."""
        valid_params = [
            "GRUB_TIMEOUT",
            "GRUB_DEFAULT",
            "GRUB_THEME",
            "GRUB_CMDLINE_LINUX",
        ]
        for param in valid_params:
            self.assertTrue(SecurityUtils.validate_grub_param(param))
    
    def test_validate_grub_param_invalid(self):
        """Rechaza parámetros GRUB inválidos."""
        invalid_params = [
            "INVALID_PARAM",
            "grub_timeout",  # Minúsculas
            "GRUB-TIMEOUT",  # Guion en lugar de subrayado
        ]
        for param in invalid_params:
            self.assertFalse(SecurityUtils.validate_grub_param(param))


class TestValidationUtils(unittest.TestCase):
    """Tests para ValidationUtils."""
    
    def test_validate_timeout_valid_range(self):
        """Valida timeouts dentro del rango permitido."""
        for timeout in [0, 1, 15, 30]:
            is_valid, msg = ValidationUtils.validate_timeout(timeout)
            self.assertTrue(is_valid, f"Timeout {timeout} debería ser válido")
    
    def test_validate_timeout_out_of_range(self):
        """Rechaza timeouts fuera de rango."""
        for timeout in [-1, 31, 100]:
            is_valid, msg = ValidationUtils.validate_timeout(timeout)
            self.assertFalse(is_valid, f"Timeout {timeout} debería ser inválido")
    
    def test_validate_timeout_non_integer(self):
        """Rechaza timeouts no numéricos."""
        is_valid, msg = ValidationUtils.validate_timeout("abc")
        self.assertFalse(is_valid)
    
    def test_validate_cmdline_linux_valid(self):
        """Valida línea de comando GRUB válida."""
        valid_cmdlines = [
            "quiet splash",
            "quiet splash resume=UUID:123-456-789",
            "rd.driver.blacklist=nouveau",
        ]
        for cmdline in valid_cmdlines:
            is_valid, msg = ValidationUtils.validate_cmdline_linux(cmdline)
            self.assertTrue(is_valid, f"Cmdline '{cmdline}' debería ser válida: {msg}")
    
    def test_validate_cmdline_linux_injection_attempt(self):
        """Rechaza intentos de inyección en línea de comando."""
        injection_attempts = [
            "quiet; rm -rf /",
            "quiet $(malicious)",
            "quiet `whoami`",
        ]
        for cmdline in injection_attempts:
            is_valid, msg = ValidationUtils.validate_cmdline_linux(cmdline)
            self.assertFalse(is_valid, f"Cmdline con inyección '{cmdline}' debería ser inválida")
    
    def test_validate_cmdline_linux_too_long(self):
        """Rechaza línea de comando demasiado larga."""
        long_cmdline = "a" * 300
        is_valid, msg = ValidationUtils.validate_cmdline_linux(long_cmdline)
        self.assertFalse(is_valid)
    
    def test_validate_custom_params_valid(self):
        """Valida parámetros personalizados válidos."""
        params = {
            "GRUB_TIMEOUT": "10",
            "GRUB_GFXMODE": "1920x1080",
        }
        is_valid, msg = ValidationUtils.validate_custom_params(params)
        self.assertTrue(is_valid)
    
    def test_validate_custom_params_invalid_key(self):
        """Rechaza parámetros con clave inválida."""
        params = {
            "INVALID_KEY": "value",
        }
        is_valid, msg = ValidationUtils.validate_custom_params(params)
        self.assertFalse(is_valid)
    
    def test_validate_custom_params_injection_in_value(self):
        """Rechaza parámetros con inyección en valor."""
        params = {
            "GRUB_TIMEOUT": "10; malicious",
        }
        is_valid, msg = ValidationUtils.validate_custom_params(params)
        self.assertFalse(is_valid)


class TestLogger(unittest.TestCase):
    """Tests para sistema de logging."""
    
    def setUp(self):
        """Limpia logs antes de cada test."""
        Logger.clear()
    
    def test_logger_clear(self):
        """Limpia correctamente los logs."""
        Logger.info("Test message")
        self.assertGreater(len(Logger.get_logs()), 0)
        Logger.clear()
        self.assertEqual(len(Logger.get_logs()), 0)
    
    def test_logger_info(self):
        """Registra mensajes de información."""
        Logger.info("Info message")
        logs = Logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "info")
        self.assertIn("Info message", logs[0][1])
    
    def test_logger_success(self):
        """Registra mensajes de éxito."""
        Logger.success("Success message")
        logs = Logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "success")
    
    def test_logger_warning(self):
        """Registra mensajes de advertencia."""
        Logger.warning("Warning message")
        logs = Logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "warning")
    
    def test_logger_error(self):
        """Registra mensajes de error."""
        Logger.error("Error message")
        logs = Logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "error")
    
    def test_logger_debug(self):
        """Registra mensajes de debug."""
        Logger.debug("Debug message")
        logs = Logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][0], "debug")
    
    def test_logger_get_formatted_logs(self):
        """Obtiene logs formateados correctamente."""
        Logger.info("Message 1")
        Logger.error("Message 2")
        formatted = Logger.get_formatted_logs()
        self.assertIn("Message 1", formatted)
        self.assertIn("Message 2", formatted)
    
    def test_logger_multiple_messages(self):
        """Maneja múltiples mensajes correctamente."""
        messages = ["Msg 1", "Msg 2", "Msg 3"]
        for msg in messages:
            Logger.info(msg)
        logs = Logger.get_logs()
        self.assertEqual(len(logs), 3)


class TestGrubConfigValidation(unittest.TestCase):
    """Tests para validación en GrubConfig."""
    
    @patch('src.config.subprocess.check_output')
    def test_detect_resume_uuid_valid(self, mock_check_output):
        """Detecta UUID de swap válido."""
        mock_check_output.return_value = "550e8400-e29b-41d4-a716-446655440000 swap\n"
        
        config = GrubConfig()
        uuid = config.detect_resume_uuid()
        
        self.assertIsNotNone(uuid)
        self.assertEqual(uuid, "550e8400-e29b-41d4-a716-446655440000")
    
    @patch('src.config.subprocess.check_output')
    def test_detect_resume_uuid_no_swap(self, mock_check_output):
        """Retorna None si no hay swap."""
        mock_check_output.return_value = ""
        
        config = GrubConfig()
        uuid = config.detect_resume_uuid()
        
        self.assertIsNone(uuid)


if __name__ == "__main__":
    unittest.main()
