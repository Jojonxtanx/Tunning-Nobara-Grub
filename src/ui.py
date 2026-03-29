#!/usr/bin/env python3
"""
Módulo de interfaz gráfica.
Usando GTK4 y Libadwaita para UI moderna.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from .config import GrubConfig
from .utils import SystemUtils, Logger, ValidationUtils, SecurityUtils
import threading


class ConfirmDialog(Adw.MessageDialog):
    """Diálogo de confirmación usando Adwaita."""
    
    def __init__(self, parent, title, message, details=""):
        super().__init__(
            transient_for=parent,
            modal=True,
            heading=title,
            body=message
        )
        
        if details:
            details_text = details[:500] + "..." if len(details) > 500 else details
            expanded_body = f"{message}\n\n<small>{details_text}</small>"
            self.set_body(expanded_body)
        
        self.add_response("cancel", "Cancelar")
        self.add_response("ok", "Confirmar")
        self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        self.set_default_response("ok")
        self.set_close_response("cancel")


class InfoDialog(Adw.MessageDialog):
    """Diálogo de información usando Adwaita."""
    
    def __init__(self, parent, title, message, details="", is_error=False):
        super().__init__(
            transient_for=parent,
            modal=True,
            heading=title,
            body=message
        )
        
        if details:
            expanded_body = f"{message}\n\n<small>{details}</small>"
            self.set_body(expanded_body)
        
        if is_error:
            self.add_response("ok", "Cerrar")
            self.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        else:
            self.add_response("ok", "OK")
            self.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        
        self.set_default_response("ok")
        self.set_close_response("ok")


class EditParametersDialog(Adw.Window):
    """Diálogo para editar parámetros avanzados."""
    
    def __init__(self, parent):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(600, 500)
        self.set_title("Parámetros Avanzados GRUB")
        self.result_params = {}
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz del diálogo."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        
        desc = Gtk.Label(label="Edita parámetros adicionales de GRUB.\nFormato: CLAVE=valor (uno por línea)")
        desc.set_wrap(True)
        vbox.append(desc)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        text_view = Gtk.TextView()
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll.set_child(text_view)
        vbox.append(scroll)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_homogeneous(True)
        
        cancel_btn = Gtk.Button(label="Cancelar")
        cancel_btn.connect("clicked", lambda _: self.close())
        ok_btn = Gtk.Button(label="Guardar")
        ok_btn.add_css_class("suggested-action")
        ok_btn.connect("clicked", self._on_ok)
        
        button_box.append(cancel_btn)
        button_box.append(ok_btn)
        vbox.append(button_box)
        
        header = Adw.HeaderBar()
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.append(header)
        container.append(vbox)
        self.set_content(container)
    
    def _on_ok(self, btn):
        """Guarda cambios y cierra."""
        self.close()


class NobaraGrubTunerWindow(Adw.ApplicationWindow):
    """Ventana principal de la aplicación con GTK4/Adwaita."""
    
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Nobara GRUB Tuner")
        self.set_default_size(1000, 800)
        
        self.grub_config = GrubConfig()
        self.is_applying = False
        
        if not SystemUtils.check_sudo_access():
            self._show_error_dialog(
                "Error de privilegios",
                "Esta aplicación requiere acceso sudo sin contraseña.\n"
                "Por favor, configura sudo para esta aplicación."
            )
            return
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz principal."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        header = Adw.HeaderBar()
        main_box.append(header)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Título
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        title = Gtk.Label(label="Nobara GRUB Tuner")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        subtitle = Gtk.Label(label="Configuración avanzada del cargador de arranque")
        subtitle.add_css_class("subtitle")
        subtitle.set_halign(Gtk.Align.START)
        title_box.append(title)
        title_box.append(subtitle)
        content_box.append(title_box)
        
        content_box.append(Gtk.Separator())
        
        # Grupo: Comportamiento
        behavior_group = Adw.PreferencesGroup()
        behavior_group.set_title("Comportamiento")
        
        # Crear SpinButton para timeout
        timeout_adjustment = Gtk.Adjustment(
            value=int(self.grub_config.get_current_timeout()),
            lower=0,
            upper=30,
            step_increment=1,
            page_increment=5,
            page_size=0
        )
        timeout_adjustment.connect("value-changed", self._on_timeout_changed)
        
        timeout_spin = Gtk.SpinButton(adjustment=timeout_adjustment)
        timeout_spin.set_numeric(True)
        timeout_spin.set_size_request(80, -1)
        
        timeout_row = Adw.ActionRow()
        timeout_row.set_title("Timeout del menú GRUB (segundos)")
        
        # Agregar el spinner como child directo
        timeout_row.add_suffix(timeout_spin)
        
        self.timeout_row = timeout_spin
        self.timeout_adjustment = timeout_adjustment
        behavior_group.add(timeout_row)
        
        submenu_row = Adw.SwitchRow()
        submenu_row.set_title("Deshabilitar submenú de kernels")
        submenu_row.set_subtitle("Mostrar todas las entradas en el menú principal")
        submenu_row.set_active(self.grub_config.get_submenu_disabled())
        self.submenu_row = submenu_row
        behavior_group.add(submenu_row)
        
        content_box.append(behavior_group)
        
        # Grupo: Apariencia
        appearance_group = Adw.PreferencesGroup()
        appearance_group.set_title("Apariencia")
        
        theme_combo = Gtk.ComboBoxText()
        themes = SystemUtils.get_available_themes_nobara()
        current_theme = self.grub_config.get_current_theme()
        
        for i, theme in enumerate(themes):
            theme_combo.append_text(theme)
            if theme == current_theme:
                theme_combo.set_active(i)
        
        if theme_combo.get_model().iter_n_children(None) == 0:
            theme_combo.append_text("Sin temas disponibles")
        
        if theme_combo.get_active() < 0:
            theme_combo.set_active(0)
        
        self.theme_combo = theme_combo
        
        theme_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        theme_label = Gtk.Label(label="Tema GRUB")
        theme_label.set_halign(Gtk.Align.START)
        theme_label.add_css_class("subtitle")
        
        theme_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        theme_hbox.append(theme_combo)
        
        refresh_btn = Gtk.Button(label="Actualizar")
        refresh_btn.set_tooltip_text("Recarga la lista de temas")
        refresh_btn.connect("clicked", self._on_refresh_themes)
        theme_hbox.append(refresh_btn)
        
        theme_box.append(theme_label)
        theme_box.append(theme_hbox)
        
        action_row = Adw.ActionRow()
        action_row.set_child(theme_box)
        appearance_group.add(action_row)
        
        # Selector de tema de la aplicación (Claro/Oscuro)
        app_theme_combo = Gtk.ComboBoxText()
        app_theme_combo.append_text("Automático")
        app_theme_combo.append_text("Tema Claro")
        app_theme_combo.append_text("Tema Oscuro")
        app_theme_combo.set_active(0)
        app_theme_combo.connect("changed", self._on_app_theme_changed)
        
        app_theme_row = Adw.ActionRow()
        app_theme_row.set_title("Tema de la Aplicación")
        app_theme_row.add_suffix(app_theme_combo)
        self.app_theme_combo = app_theme_combo
        self.app_theme_row = app_theme_row
        appearance_group.add(app_theme_row)
        content_box.append(appearance_group)
        
        # Grupo: Orden de Boot
        boot_order_group = Adw.PreferencesGroup()
        boot_order_group.set_title("Orden de Boot")
        boot_order_group.set_description("Reordena las entradas disponibles al iniciar")
        
        # Frame para la lista de boots
        boot_frame = Gtk.Frame()
        boot_frame.set_margin_start(12)
        boot_frame.set_margin_end(12)
        boot_frame.set_margin_top(6)
        boot_frame.set_margin_bottom(6)
        
        boot_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        boot_frame.set_child(boot_list_box)
        
        # Botones para ordenar
        boot_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        boot_buttons_box.set_homogeneous(True)
        
        boot_up_btn = Gtk.Button(label="⬆️ Arriba")
        boot_up_btn.connect("clicked", self._on_boot_move_up)
        boot_buttons_box.append(boot_up_btn)
        self.boot_up_btn = boot_up_btn
        
        boot_down_btn = Gtk.Button(label="⬇️ Abajo")
        boot_down_btn.connect("clicked", self._on_boot_move_down)
        boot_buttons_box.append(boot_down_btn)
        self.boot_down_btn = boot_down_btn
        
        boot_list_box.append(boot_buttons_box)
        
        # ScrolledWindow para la lista de boots
        boot_scroll = Gtk.ScrolledWindow()
        boot_scroll.set_min_content_height(150)
        boot_scroll.set_min_content_width(250)
        
        self.boot_list_store = Gtk.ListStore(str)  # Nombre del boot
        self.boot_selection = None
        
        boot_tree = Gtk.TreeView(model=self.boot_list_store)
        boot_tree.set_headers_visible(False)
        
        # Columna para mostrar el nombre del boot
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Boot Entry", renderer, text=0)
        boot_tree.append_column(column)
        
        boot_tree.connect("cursor-changed", self._on_boot_selection_changed)
        self.boot_tree = boot_tree
        boot_scroll.set_child(boot_tree)
        boot_list_box.append(boot_scroll)
        
        boot_order_group.add(boot_frame)
        content_box.append(boot_order_group)
        
        # Cargar entradas de boot
        self._load_boot_entries()
        
        # Botones de acción
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        action_box.set_homogeneous(True)
        
        backup_btn = Gtk.Button(label="📦 Crear Backup")
        backup_btn.connect("clicked", self._on_create_backup)
        action_box.append(backup_btn)
        
        params_btn = Gtk.Button(label="⚙️ Parámetros Avanzados")
        params_btn.connect("clicked", self._on_edit_parameters)
        action_box.append(params_btn)
        
        apply_btn = Gtk.Button(label="💾 Aplicar Cambios")
        apply_btn.add_css_class("suggested-action")
        apply_btn.set_size_request(150, -1)
        apply_btn.connect("clicked", self._on_apply_changes)
        self.apply_btn = apply_btn
        action_box.append(apply_btn)
        
        content_box.append(action_box)
        scroll.set_child(content_box)
        main_box.append(scroll)
        self.set_content(main_box)
    
    def _on_refresh_themes(self, btn):
        """Actualiza lista de temas."""
        active = self.theme_combo.get_active_text()
        self.theme_combo.remove_all()
        themes = SystemUtils.get_available_themes_nobara()
        
        for i, theme in enumerate(themes):
            self.theme_combo.append_text(theme)
            if theme == active:
                self.theme_combo.set_active(i)
        
        if self.theme_combo.get_model().iter_n_children(None) == 0:
            self.theme_combo.append_text("Sin temas disponibles")
        
        if self.theme_combo.get_active() < 0:
            self.theme_combo.set_active(0)
        
        self._show_info_dialog("Temas actualizados", "Lista de temas recargada correctamente.")
    
    def _on_timeout_changed(self, adjustment):
        """Actualiza el valor de timeout cuando cambia el SpinRow."""
        new_timeout = int(adjustment.get_value())
        self.grub_config.timeout = new_timeout
    
    def _on_create_backup(self, btn):
        """Crea backup de la configuración."""
        btn.set_sensitive(False)
        
        def _backup_thread():
            success, result = self.grub_config.create_backup()
            GLib.idle_add(lambda: self._backup_done(btn, success, result))
        
        thread = threading.Thread(target=_backup_thread, daemon=True)
        thread.start()
    
    def _backup_done(self, btn, success, result):
        """Callback después de crear backup."""
        btn.set_sensitive(True)
        
        if success:
            self._show_info_dialog("✅ Backup creado", f"Backup guardado en:\n{result}")
        else:
            self._show_error_dialog("❌ Error en backup", result)
    
    def _on_edit_parameters(self, btn):
        """Abre diálogo de parámetros avanzados."""
        dialog = EditParametersDialog(self)
        dialog.present()
    
    def _on_apply_changes(self, btn):
        """Aplica los cambios a GRUB en un hilo separado."""
        if self.is_applying:
            return
        
        timeout = int(self.timeout_row.get_value())
        theme = self.theme_combo.get_active_text() or "nobara"
        disable_submenu = self.submenu_row.get_active()
        
        # Obtener nuevo orden de boots
        new_boot_order = []
        for row in self.boot_list_store:
            new_boot_order.append(row[0])
        
        is_valid, error_msg = ValidationUtils.validate_timeout(timeout)
        if not is_valid:
            self._show_error_dialog("❌ Timeout inválido", error_msg)
            return
        
        is_valid, error_msg = ValidationUtils.validate_theme_exists(theme)
        if not is_valid:
            self._show_error_dialog("❌ Tema no encontrado", error_msg)
            return
        
        dialog = ConfirmDialog(
            self,
            "Confirmar cambios en GRUB",
            "¿Estás seguro de que deseas aplicar estos cambios?\n"
            "Se creará un backup automático antes de aplicar.",
            details=f"Timeout: {timeout}s\nTema: {theme}\nSubmenu: {'Deshabilitado' if disable_submenu else 'Habilitado'}\nOrden de boots: {', '.join(new_boot_order[:3])}{'...' if len(new_boot_order) > 3 else ''}"
        )
        
        def on_response(dialog, response):
            if response == "ok":
                self._apply_changes_async(timeout, theme, disable_submenu, new_boot_order)
            dialog.close()
        
        dialog.connect("response", on_response)
        dialog.present()
    
    def _apply_changes_async(self, timeout, theme, disable_submenu, boot_order=None):
        """Aplica cambios de forma asincrónica."""
        self.is_applying = True
        self.apply_btn.set_sensitive(False)
        
        def _apply_thread():
            try:
                Logger.clear()
                success, config_content = self.grub_config.generate_config(
                    timeout, theme, disable_submenu
                )
                
                if not success:
                    GLib.idle_add(lambda: self._apply_error(config_content))
                    return
                
                Logger.info("Creando backup automático...")
                backup_success, backup_path = self.grub_config.create_backup()
                if backup_success:
                    Logger.success(f"Backup creado: {backup_path}")
                
                # Aplicar nuevo orden de boots si cambió
                if boot_order:
                    Logger.info("Aplicando nuevo orden de boots...")
                    from .config import BootEntryManager
                    boot_manager = BootEntryManager()
                    order_success, order_msg = boot_manager.reorder_entries(boot_order)
                    if order_success:
                        Logger.success(order_msg)
                    else:
                        Logger.warning(f"No se pudo reordenar boots: {order_msg}")
                
                Logger.info("Aplicando configuración GRUB...")
                success, message = self.grub_config.apply_config(config_content)
                logs = Logger.get_formatted_logs()
                
                GLib.idle_add(lambda: self._apply_success(success, message, logs))
            
            except Exception as e:
                Logger.error(f"Excepción: {str(e)}")
                logs = Logger.get_formatted_logs()
                GLib.idle_add(lambda: self._apply_error(f"Excepción: {str(e)}", logs))
        
        thread = threading.Thread(target=_apply_thread, daemon=True)
        thread.start()
    
    def _apply_success(self, success, message, logs):
        """Callback de aplicación exitosa."""
        self.is_applying = False
        self.apply_btn.set_sensitive(True)
        
        if success:
            self._show_info_dialog("✅ Cambios aplicados", message, logs)
        else:
            self._show_error_dialog("❌ Error al aplicar cambios", message, logs)
    
    def _apply_error(self, message, logs=""):
        """Callback de error en aplicación."""
        self.is_applying = False
        self.apply_btn.set_sensitive(True)
        self._show_error_dialog("❌ Error", message, logs)
    
    def _on_app_theme_changed(self, combo):
        """Cambia el tema de la aplicación (claro/oscuro)."""
        active = combo.get_active()
        style_manager = Adw.StyleManager.get_default()
        
        if active == 0:  # Automático
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
            Logger.debug("Tema automático activado")
        elif active == 1:  # Claro
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            Logger.debug("Tema claro activado")
        elif active == 2:  # Oscuro
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            Logger.debug("Tema oscuro activado")
    
    def _show_info_dialog(self, title, message, details=""):
        """Muestra diálogo de información."""
        dialog = InfoDialog(self, title, message, details, is_error=False)
        dialog.present()
    
    def _show_error_dialog(self, title, message, details=""):
        """Muestra diálogo de error."""
        dialog = InfoDialog(self, title, message, details, is_error=True)
        dialog.present()
    
    def _load_boot_entries(self):
        """Carga las entradas de boot disponibles."""
        try:
            from .config import BootEntryManager
            
            boot_manager = BootEntryManager()
            entries = boot_manager.get_boot_entries()
            
            self.boot_list_store.clear()
            for entry in entries:
                self.boot_list_store.append([entry])
            
            if len(entries) > 0:
                self.boot_tree.set_cursor(Gtk.TreePath.new_first())
                Logger.debug(f"Se cargaron {len(entries)} entradas de boot")
            else:
                Logger.warning("No se encontraron entradas de boot")
                
        except Exception as e:
            Logger.error(f"Error al cargar boot entries: {e}")
            self._show_error_dialog("Error", "No se pudieron cargar las entradas de boot")
    
    def _on_boot_selection_changed(self, tree):
        """Callback cuando cambia la selección de boot."""
        selection = tree.get_selection()
        if selection:
            model, iter = selection.get_selected()
            if iter:
                self.boot_selection = iter
                # Habilitar/deshabilitar botones según posición
                index = model.get_path(iter).get_indices()[0]
                self.boot_up_btn.set_sensitive(index > 0)
                self.boot_down_btn.set_sensitive(index < len(model) - 1)
                return
        
        self.boot_selection = None
        self.boot_up_btn.set_sensitive(False)
        self.boot_down_btn.set_sensitive(False)
    
    def _on_boot_move_up(self, btn):
        """Mueve la entrada de boot seleccionada hacia arriba."""
        if not self.boot_selection:
            return
        
        model = self.boot_list_store
        path = model.get_path(self.boot_selection)
        index = path.get_indices()[0]
        
        if index > 0:
            # Intercambiar con el anterior
            prev_iter = model.get_iter(index - 1)
            model.swap(self.boot_selection, prev_iter)
            
            # Mantener selección
            self.boot_tree.set_cursor(Gtk.TreePath.new_from_indices([index - 1]))
            Logger.debug(f"Boot movido hacia arriba (índice {index} → {index - 1})")
    
    def _on_boot_move_down(self, btn):
        """Mueve la entrada de boot seleccionada hacia abajo."""
        if not self.boot_selection:
            return
        
        model = self.boot_list_store
        path = model.get_path(self.boot_selection)
        index = path.get_indices()[0]
        
        if index < len(model) - 1:
            # Intercambiar con el siguiente
            next_iter = model.get_iter(index + 1)
            model.swap(self.boot_selection, next_iter)
            
            # Mantener selección
            self.boot_tree.set_cursor(Gtk.TreePath.new_from_indices([index + 1]))
            Logger.debug(f"Boot movido hacia abajo (índice {index} → {index + 1})")


class NobaraGrubTunerApp(Adw.Application):
    """Aplicación principal."""
    
    def __init__(self):
        super().__init__(application_id="org.nobara.GrubTuner")
        self.connect("activate", self.on_activate)
    
    def on_activate(self, app):
        """Método de activación de la aplicación."""
        window = NobaraGrubTunerWindow(app)
        window.present()
