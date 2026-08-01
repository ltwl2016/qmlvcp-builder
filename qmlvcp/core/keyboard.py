import os
import configparser
from PySide6.QtCore import QObject, QEvent, Qt

class GlobalKeyFilter(QObject):
    def __init__(self, backend_interface, config_path, parent=None):
        super().__init__(parent)
        self.backend = backend_interface
        
        # Mappings (内置默认回退值 / Default Fallback)
        self.jog_continuous_map = {
            Qt.Key_Left:      (0, -1),
            Qt.Key_Right:     (0, 1),
            Qt.Key_Down:      (1, -1),
            Qt.Key_Up:        (1, 1),
            Qt.Key_PageDown:  (2, -1),
            Qt.Key_PageUp:    (2, 1),
            Qt.Key_BracketLeft:  (3, -1),
            Qt.Key_BracketRight: (3, 1),
        }
        # Pre-allocate others for future use
        self.actions_simple_map = {}
        self.actions_param_map = {}
        self.mdi_commands_map = {}
        
        self.load_config(config_path)

    def _string_to_qt_key(self, key_str):
        # Maps string "Left" to Qt.Key_Left
        key_name = f"Key_{key_str.strip()}"
        return getattr(Qt, key_name, None)

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            print(f"[KeyFilter] Config file not found: {config_path}. Using built-in defaults.")
            return
            
        config = configparser.ConfigParser()
        # Preserve case of keys
        config.optionxform = str
        config.read(config_path)
        
        if 'JOG_CONTINUOUS' in config:
            for key_str, val_str in config['JOG_CONTINUOUS'].items():
                qt_key = self._string_to_qt_key(key_str)
                if qt_key:
                    parts = [p.strip() for p in val_str.split(',')]
                    if len(parts) >= 2:
                        try:
                            axis = int(parts[0])
                            direction = int(parts[1])
                            self.jog_continuous_map[qt_key] = (axis, direction)
                            print(f"[KeyFilter] Mapped {key_str} to JOG axis {axis} dir {direction}")
                        except ValueError:
                            pass

    def eventFilter(self, obj, event):
        # In the future, we can add logic here to ignore keys if QGuiApplication.focusObject() is a Text Input.
        
        if event.type() == QEvent.KeyPress and not event.isAutoRepeat():
            key = event.key()
            
            # 1. Check JOG_CONTINUOUS
            if key in self.jog_continuous_map:
                # 仅在“手动”模式下才拦截快捷键，否则当做普通按键放行（用于 MDI 打字）
                if hasattr(self.backend, 'cnc_status') and self.backend.cnc_status.taskMode != "手动":
                    return super().eventFilter(obj, event)

                axis, direction = self.jog_continuous_map[key]
                self.backend.jogAxis(axis, direction)
                return True

        elif event.type() == QEvent.KeyRelease and not event.isAutoRepeat():
            key = event.key()
            
            # Stop JOG_CONTINUOUS
            if key in self.jog_continuous_map:
                if hasattr(self.backend, 'cnc_status') and self.backend.cnc_status.taskMode != "手动":
                    return super().eventFilter(obj, event)

                axis, direction = self.jog_continuous_map[key]
                self.backend.stopJog(axis)
                return True

        return super().eventFilter(obj, event)
