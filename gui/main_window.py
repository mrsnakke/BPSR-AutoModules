import sys
import os
import threading
from typing import List, Dict, Any, Optional

# Add parent/project root directory to path so it can import root-level files
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QCheckBox, QComboBox, QPushButton, QLineEdit, 
    QScrollArea, QFrame, QGridLayout, QProgressBar, QStackedWidget,
    QDialog
)
from PyQt6.QtGui import QPixmap, QFont, QIntValidator, QColor, QPalette, QIcon, QStandardItem, QStandardItemModel
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QObject, QFileSystemWatcher, QTimer

# Importar lógica del proyecto
from module_types import (
    ModuleInfo, ModulePart, ModuleCategory, MODULE_ATTR_NAMES, MODULE_ATTR_NAMES_EN,
    MODULE_ATTR_IDS, ATTR_CN_TO_EN, to_english_attr, to_english_module, MODULE_NAMES,
    to_spanish_attr, to_spanish_module, MODULE_ATTR_NAMES_ES, MODULE_NAMES_ES
)
from module_optimizer import ModuleOptimizer, ModuleSolution
from module_parser import ModuleParser
from packet_capture import PacketCapture
from network_interface_util import get_network_interfaces

class StartupInstructionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instructions / Instrucciones / 使用说明")
        self.setFixedSize(560, 480)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border: 2px solid #007acc;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header/Title
        title_lbl = QLabel("BPSR Module Optimizer Instructions")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #007acc;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)
        
        # Subtitle
        sub_lbl = QLabel("How to load modules / Cómo cargar módulos / 如何加载模组")
        sub_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        sub_lbl.setStyleSheet("color: #888;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_lbl)
        
        # Central instruction area
        instructions_text = """
<div style="line-height: 1.4;">
    <p style="color: #4fc3f7; font-weight: bold; font-size: 13px; margin-bottom: 2px;">🇬🇧 English</p>
    <p style="margin-top: 0; margin-bottom: 12px; font-size: 12px; color: #ddd;">Please <b>change channels (teleport / switch channel)</b> or <b>relogin</b> within the game to automatically capture and load your module inventory.</p>

    <p style="color: #4fc3f7; font-weight: bold; font-size: 13px; margin-bottom: 2px;">🇪🇸 Español</p>
    <p style="margin-top: 0; margin-bottom: 12px; font-size: 12px; color: #ddd;">Por favor, <b>cambia de canal (teletransporte o cambio de canal)</b> o <b>vuelve a iniciar sesión</b> dentro del juego para capturar y cargar automáticamente tu inventario de módulos.</p>

    <p style="color: #4fc3f7; font-weight: bold; font-size: 13px; margin-bottom: 2px;">🇨🇳 简体中文</p>
    <p style="margin-top: 0; margin-bottom: 0; font-size: 12px; color: #ddd;">请在游戏内进行<b>切换频道（换线 / 传送）</b>或<b>重新登录</b>，以自动捕获并加载您的模组仓库。</p>
</div>
        """
        
        body_lbl = QLabel(instructions_text)
        body_lbl.setTextFormat(Qt.TextFormat.RichText)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet("background-color: #242424; border: 1px solid #333; border-radius: 5px; padding: 15px;")
        layout.addWidget(body_lbl)
        
        layout.addStretch()
        
        # OK Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

class LoadingOverlay(QFrame):
    skip_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadingOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame#LoadingOverlay {
                background-color: #121212;
                border: 2px solid #007acc;
                border-radius: 12px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI';
                background: transparent;
                border: none;
            }
        """)
        
        # Main layout for the overlay is horizontal to split icon and text
        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(15, 10, 30, 10)
        
        # Icon label for Calcular.png
        self.icon_lbl = QLabel()
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "gui", "images", "Calcular.png")
        else:
            icon_path = os.path.join("gui", "images", "Calcular.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_lbl.setPixmap(pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        main_layout.addWidget(self.icon_lbl)
        
        # Text container (vertical)
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_layout.setSpacing(8)
        
        self.title_lbl = QLabel("<b>CALCULATING MODULE COMBINATIONS...</b>")
        self.title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet("color: #007acc; background: transparent;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        text_layout.addWidget(self.title_lbl)
        
        self.sub_lbl = QLabel("Please wait while the optimizer finds the best 5-module sets.\nCalculando combinaciones... Por favor espere.\n正在计算最佳的5模组组合... 请稍候。")
        self.sub_lbl.setFont(QFont("Segoe UI", 10))
        self.sub_lbl.setStyleSheet("color: #e0e0e0; background: transparent;")
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        text_layout.addWidget(self.sub_lbl)
        
        # Skip button
        self.skip_btn = QPushButton("Use Existing Data / Usar datos existentes / 使用现有数据")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 14px;
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        self.skip_btn.clicked.connect(self.skip_clicked.emit)
        self.skip_btn.hide()
        text_layout.addWidget(self.skip_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        
        main_layout.addLayout(text_layout)

    def set_image(self, image_name: str):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "gui", "images", image_name)
        else:
            icon_path = os.path.join("gui", "images", image_name)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_lbl.setPixmap(pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def set_text(self, title: str, subtitle: str):
        self.title_lbl.setText(f"<b>{title}</b>")
        self.sub_lbl.setText(subtitle)

    def show_skip_button(self, visible: bool):
        if visible:
            self.skip_btn.show()
        else:
            self.skip_btn.hide()

class PacketCaptureWorker(QThread):
    packet_captured = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, interface_name: Optional[str] = None):
        super().__init__()
        self.interface_name = interface_name
        self.capture = None

    def run(self):
        try:
            self.capture = PacketCapture(self.interface_name)
            self.capture.start_capture(self._on_packet)
            # Keep thread alive while capturing
            while self.capture.is_running:
                self.msleep(100)
        except Exception as e:
            self.error.emit(str(e))

    def _on_packet(self, data):
        v_data = data.get('v_data')
        if v_data:
            self.packet_captured.emit(v_data)

    def stop(self):
        if self.capture:
            self.capture.stop_capture()

class OptimizationWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, optimizer: ModuleOptimizer, modules: List[ModuleInfo], category: ModuleCategory):
        super().__init__()
        self.optimizer = optimizer
        self.modules = modules
        self.category = category

    def run(self):
        try:
            results = self.optimizer.optimize_modules(self.modules, self.category)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class StatPriorityWidget(QWidget):
    removed = pyqtSignal(object)
    moved_up = pyqtSignal(object)
    moved_down = pyqtSignal(object)

    def __init__(self, stat_id: int, name: str, icon_path: str, parent=None):
        super().__init__(parent)
        self.stat_id = stat_id
        self.name = name
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Reorder buttons
        btn_layout = QVBoxLayout()
        self.up_btn = QPushButton("▲")
        self.down_btn = QPushButton("▼")
        for btn in [self.up_btn, self.down_btn]:
            btn.setFixedSize(20, 18)
            btn.setStyleSheet("font-size: 8px;")
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setStyleSheet("border: none; background: transparent;")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        layout.addWidget(self.icon_label)

        # Name
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold; color: #ddd; border: none; background: transparent;")
        layout.addWidget(self.name_label)
        layout.addStretch(1)

        # Remove
        self.remove_btn = QPushButton("🗑️")
        self.remove_btn.setFixedSize(25, 25)
        self.remove_btn.setStyleSheet("background-color: #442222;")
        layout.addWidget(self.remove_btn)

        # Signals
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self))
        self.up_btn.clicked.connect(lambda: self.moved_up.emit(self))
        self.down_btn.clicked.connect(lambda: self.moved_down.emit(self))

        self.val_input = QLineEdit("0")

    def get_config(self):
        return {
            "stat_id": self.stat_id,
            "name": self.name,
            "min_val": 0,
            "mode": "at_least"
        }

class ModuleOptimizerGUI(QMainWindow):
    def get_vdata_path(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.getcwd()
        return os.path.join(base_dir, "modules.vdata")

    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.image_base_path = os.path.join(sys._MEIPASS, "gui/images")
        else:
            self.image_base_path = "gui/images"
        self.lang = "en"
        self.all_modules = []
        self.optimizer = None
        self.parser = ModuleParser(lang=self.lang)
        
        self.init_ui()
        self.load_initial_data()
        
        # Update dynamic status badge
        self.update_inventory_status_indicator()
        
        # File Watcher & Auto-Reload for modules.vdata
        self.watcher = QFileSystemWatcher(self)
        vdata_path = self.get_vdata_path()
        if os.path.exists(vdata_path):
            self.watcher.addPath(vdata_path)
        self.watcher.fileChanged.connect(self.on_vdata_changed)
        
        # Polling timer as backup / dynamic watch (checks every 2 seconds)
        self.vdata_poll_timer = QTimer(self)
        self.vdata_poll_timer.timeout.connect(self.check_vdata_modification)
        self.vdata_poll_timer.start(2000)
        self.last_vdata_mtime = 0
        if os.path.exists(vdata_path):
            self.last_vdata_mtime = os.path.getmtime(vdata_path)

        # Show Startup Instructions Popup with a slight delay
        QTimer.singleShot(150, self.show_startup_popup)

    def init_ui(self):
        self.setWindowTitle("BPSR Module Optimizer by MrSnake")
        self.setGeometry(100, 100, 1400, 850)
        
        # Set Window Icon
        win_icon_path = os.path.join(self.image_base_path, "icon.ico")
        if not os.path.exists(win_icon_path):
            win_icon_path = "icon.ico"
        if os.path.exists(win_icon_path):
            self.setWindowIcon(QIcon(win_icon_path))

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; color: #ffffff; }
            QLabel { color: #ffffff; border: none; background-color: transparent; }
            .QFrame { border: 1px solid #333; border-radius: 5px; background-color: #252525; }
            QPushButton { background-color: #3d3d3d; color: white; border: 1px solid #555; padding: 5px; border-radius: 3px; }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #2d2d2d; }
            QPushButton:checked { background-color: #007acc; border-color: #0098ff; }
            QPushButton#NavButton {
                background-color: transparent;
                color: #aaaaaa;
                border: none;
                border-bottom: 3px solid transparent;
                padding-bottom: 4px;
                border-radius: 0px;
            }
            QPushButton#NavButton:hover {
                color: #ffffff;
                border-bottom: 3px solid #0098ff;
                background-color: rgba(255, 255, 255, 0.05);
            }
            QPushButton#NavButton:checked {
                color: #ffffff;
                border-bottom: 3px solid #007acc;
                background-color: rgba(0, 122, 204, 0.1);
            }
            QPushButton#NavButton:pressed {
                background-color: rgba(0, 122, 204, 0.2);
            }
            QLineEdit { background-color: #333; color: white; border: 1px solid #555; border-radius: 3px; }
            QComboBox { background-color: #333; color: white; border: 1px solid #555; height: 26px; }
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header / Navigation Bar (Como en la referencia)
        header = QHBoxLayout()
        header.setContentsMargins(5, 5, 5, 5)
        
        logo = QLabel()
        logo_path = os.path.join(self.image_base_path, "icon.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(self.image_base_path, "icon.ico") # Fallback to .ico if .png not found
        if os.path.exists(logo_path):
            logo.setPixmap(QPixmap(logo_path).scaled(35, 35, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        header.addWidget(logo)

        title = QLabel("BPSR Module Optimizer")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.addWidget(title)

        header.addSpacing(20)

        # Tabs de Navegación
        self.tabs_layout = QHBoxLayout()
        self.tab_buttons = {}
        for tab_name in ["Optimizer", "Settings"]:
            btn = QPushButton(tab_name)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setChecked(tab_name == "Optimizer")
            btn.setFixedWidth(120)
            btn.setFont(QFont("Segoe UI Semibold", 10))
            self.tabs_layout.addWidget(btn)
            self.tab_buttons[tab_name] = btn
            btn.clicked.connect(lambda checked, t=tab_name: self.switch_tab(t))
        header.addLayout(self.tabs_layout)

        header.addSpacing(20)
        self.status_indicator = QLabel()
        header.addWidget(self.status_indicator)

        header.addStretch(1)

        main_layout.addLayout(header)

        # Content area using QStackedWidget
        self.stacked_widget = QStackedWidget()
        
        # 1. Optimizer Tab Widget
        self.optimizer_tab = QWidget()
        optimizer_layout = QHBoxLayout(self.optimizer_tab)
        optimizer_layout.setContentsMargins(0, 0, 0, 0)
        optimizer_layout.setSpacing(10)
        self.setup_config_panel(optimizer_layout)
        self.setup_results_panel(optimizer_layout)
        self.stacked_widget.addWidget(self.optimizer_tab)
        
        # 2. Inventory Tab Widget
        self.inventory_tab = QWidget()
        self.setup_inventory_tab()
        self.stacked_widget.addWidget(self.inventory_tab)
        
        # 3. Settings Tab Widget
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        self.stacked_widget.addWidget(self.settings_tab)
        
        main_layout.addWidget(self.stacked_widget)

    def switch_tab(self, name):
        for tab_name, btn in self.tab_buttons.items():
            btn.setChecked(tab_name == name)
            
        if name == "Optimizer":
            self.stacked_widget.setCurrentIndex(0)
        elif name == "Inventory":
            self.stacked_widget.setCurrentIndex(1)
            self.load_inventory_display()
        elif name == "Settings":
            self.stacked_widget.setCurrentIndex(2)

    def get_stat_icon_path(self, attr_id: int) -> str:
        icon_map = {
            1408: "mod_effect_icon_026.png", # Attack SPD
            1110: "mod_effect_icon_011.png", # Strength
            1113: "mod_effect_icon_002.png", # Special Attack
            1114: "mod_effect_icon_038.png", # Elite Strike
            1111: "mod_effect_icon_039.png", # Agility
            1112: "mod_effect_icon_034.png", # Intellect Boost
            1205: "mod_effect_icon_023.png", # Healing Boost
            1206: "mod_effect_icon_042.png", # Healing Enhance
            1307: "mod_effect_icon_009.png", # Resistance
            1308: "mod_effect_icon_014.png", # Armor
            1407: "mod_effect_icon_013.png", # Cast Focus
            1409: "mod_effect_icon_019.png", # Crit Focus
            1410: "mod_effect_icon_048.png", # Luck Focus
            2104: "mod_effect_icon_016.png", # DMG Stack
            2105: "mod_effect_icon_006.png", # Agile
            2204: "mod_effect_icon_012.png", # Life Condense
            2205: "mod_effect_icon_024.png", # First Aid
            2304: "mod_effect_icon_045.png", # Final Protection
            2404: "mod_effect_icon_004.png", # Life Wave
            2405: "mod_effect_icon_035.png", # Life Steal
            2406: "mod_effect_icon_017.png", # Team Luck & Crit
        }
        icon_name = icon_map.get(attr_id, f"mod_effect_icon_{attr_id%100:03d}.png")
        icon_path = os.path.join(self.image_base_path, icon_name)
        if not os.path.exists(icon_path):
            return os.path.join(self.image_base_path, "missing.png")
        return icon_path

    def setup_config_panel(self, parent_layout):
        config_container = QFrame()
        config_container.setObjectName("ConfigContainer")
        config_container.setStyleSheet("QFrame#ConfigContainer { background-color: #1e1e1e; border: 1px solid #2d2d2d; }")
        config_layout = QVBoxLayout(config_container)
        config_layout.setContentsMargins(10, 10, 10, 10)
        config_layout.setSpacing(10)
        
        # Quality
        self.qual_lbl = QLabel("<b>Quality</b>")
        config_layout.addWidget(self.qual_lbl)
        quality_row = QHBoxLayout()
        self.qual_checks = {}
        colors = {
            "Basic": "#3498DB",      # Azul
            "Advanced": "#9B59B6",   # Morado
            "Excellent": "#F1C40F"   # Dorado
        }
        for q in ["Basic", "Advanced", "Excellent"]:
            cb = QCheckBox(q)
            cb.setChecked(True)
            color = colors.get(q, "#ffffff")
            cb.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.qual_checks[q] = cb
            quality_row.addWidget(cb)
        config_layout.addLayout(quality_row)

        config_layout.addWidget(self.create_separator())

        # Controles Add Stat (Colocados arriba de la lista, justo debajo de Quality)
        self.add_stat_lbl = QLabel("<b>Add Stat to Priority / Constraints</b>")
        config_layout.addWidget(self.add_stat_lbl)
        add_stat_row = QHBoxLayout()
        self.stat_select = QComboBox()
        self.populate_stat_select()
        add_stat_row.addWidget(self.stat_select, 70)
        
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet("background-color: #007acc; font-weight: bold;")
        self.add_btn.clicked.connect(self.add_stat_priority)
        add_stat_row.addWidget(self.add_btn, 30)
        config_layout.addLayout(add_stat_row)

        config_layout.addWidget(self.create_separator())

        # Lista de Prioridad / Restricciones
        self.priority_lbl = QLabel("<b>Stat Priority / Constraints</b>")
        config_layout.addWidget(self.priority_lbl)
        self.stat_scroll = QScrollArea()
        self.stat_scroll.setWidgetResizable(True)
        self.stat_scroll.setStyleSheet("background-color: #1a1a1a; border: 1px solid #2a2a2a;")
        
        self.stat_list_widget = QWidget()
        self.stat_list_layout = QVBoxLayout(self.stat_list_widget)
        self.stat_list_layout.setContentsMargins(5, 5, 5, 5)
        self.stat_list_layout.setSpacing(5)
        self.stat_list_layout.addStretch(1)
        self.stat_scroll.setWidget(self.stat_list_widget)
        
        config_layout.addWidget(self.stat_scroll, 1) # Permitir que el Scroll de Stats Priority se expanda libremente

        config_layout.addWidget(self.create_separator())

        # Optimization Method
        self.method_lbl = QLabel("<b>Optimization Method</b>" if self.lang == "en" else "<b>优化方法</b>")
        config_layout.addWidget(self.method_lbl)
        self.method_select = QComboBox()
        if self.lang == "en":
            self.method_select.addItems(["Standard", "Priority Lv.6/Lv.5"])
        else:
            self.method_select.addItems(["Standard", "Priority Lv.6/Lv.5"])
        config_layout.addWidget(self.method_select)

        # Botón de Cálculo / Optimización (Anclado al fondo)
        self.calc_btn = QPushButton("Calculate 5 module combo sets")
        self.calc_btn.setStyleSheet("background-color: #2e5a2e; font-weight: bold; padding: 12px; font-size: 11px;")
        self.calc_btn.clicked.connect(self.run_optimization)
        config_layout.addWidget(self.calc_btn)

        parent_layout.addWidget(config_container, 32) # Proporción de ancho izquierda

    def setup_results_panel(self, parent_layout):
        results_container = QFrame()
        results_container.setObjectName("ResultsContainer")
        bg_path = os.path.join(self.image_base_path, "Background.webp").replace("\\", "/")
        results_container.setStyleSheet(f"""
            QFrame#ResultsContainer {{
                border: 1px solid #2d2d2d;
                background-image: url('{bg_path}');
                background-position: center;
                background-repeat: no-repeat;
            }}
        """)
        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(10, 10, 10, 10)
        results_layout.setSpacing(10)
        
        self.results_title_lbl = QLabel("<b>Optimization Results</b>")
        results_layout.addWidget(self.results_title_lbl)
        
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.results_grid_widget = QWidget()
        self.results_grid_widget.setStyleSheet("background-color: transparent;")
        self.results_grid = QGridLayout(self.results_grid_widget)
        self.results_grid.setContentsMargins(0, 0, 0, 0)
        self.results_grid.setSpacing(20)
        self.results_scroll.setWidget(self.results_grid_widget)
        
        results_layout.addWidget(self.results_scroll)
        
        # Initialize loading overlay as child of results_container
        self.loading_overlay = LoadingOverlay(results_container)
        self.loading_overlay.hide()
        self.loading_overlay.skip_clicked.connect(self.skip_packet_capture)
        
        parent_layout.addWidget(results_container, 68) # Proporción de ancho derecha

    def setup_inventory_tab(self):
        layout = QVBoxLayout(self.inventory_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        inventory_container = QFrame()
        inventory_container.setObjectName("InventoryContainer")
        bg_path = os.path.join(self.image_base_path, "Background.webp").replace("\\", "/")
        inventory_container.setStyleSheet(f"""
            QFrame#InventoryContainer {{
                border: none;
                background-image: url('{bg_path}');
                background-position: center;
                background-repeat: no-repeat;
            }}
        """)
        
        container_layout = QVBoxLayout(inventory_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        self.inv_title = QLabel("<b>Inventory</b>")
        self.inv_title.setFont(QFont("Segoe UI Semibold", 12))
        header_layout.addWidget(self.inv_title)
        
        self.inv_count_lbl = QLabel("Total: 0 modules")
        self.inv_count_lbl.setStyleSheet("color: #aaa;")
        header_layout.addWidget(self.inv_count_lbl)
        header_layout.addStretch(1)
        container_layout.addLayout(header_layout)
        
        self.inv_scroll = QScrollArea()
        self.inv_scroll.setWidgetResizable(True)
        self.inv_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.inv_grid_widget = QWidget()
        self.inv_grid_widget.setStyleSheet("background-color: transparent;")
        self.inv_grid = QGridLayout(self.inv_grid_widget)
        self.inv_grid.setContentsMargins(10, 10, 10, 10)
        self.inv_grid.setSpacing(10)
        self.inv_scroll.setWidget(self.inv_grid_widget)
        
        container_layout.addWidget(self.inv_scroll)
        layout.addWidget(inventory_container)

    def load_inventory_display(self):
        for i in reversed(range(self.inv_grid.count())):
            widget = self.inv_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        if self.lang == "en":
            self.inv_count_lbl.setText(f"Total: <span style='font-family: Consolas;'>{len(self.all_modules)}</span> modules")
            self.inv_title.setText("<b>Inventory</b>")
        elif self.lang == "es":
            self.inv_count_lbl.setText(f"Total: <span style='font-family: Consolas;'>{len(self.all_modules)}</span> módulos")
            self.inv_title.setText("<b>Inventario</b>")
        else:
            self.inv_count_lbl.setText(f"总计: <span style='font-family: Consolas;'>{len(self.all_modules)}</span> 个模组")
            self.inv_title.setText("<b>仓库</b>")
        
        cols = 4
        for idx, mod in enumerate(self.all_modules):
            card = self.create_inventory_module_card(mod)
            self.inv_grid.addWidget(card, idx // cols, idx % cols)

    def create_inventory_module_card(self, mod: ModuleInfo) -> QWidget:
        card = QFrame()
        card.setObjectName("InventoryModuleCard")
        card.setStyleSheet("""
            QFrame#InventoryModuleCard {
                background-color: rgba(30, 30, 30, 0.7); 
                border: 1px solid rgba(255, 255, 255, 0.15); 
                border-radius: 12px; 
                padding: 8px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        
        header = QHBoxLayout()
        
        icon_widget = QWidget()
        icon_widget.setFixedSize(40, 40)
        stacked = QVBoxLayout(icon_widget)
        stacked.setContentsMargins(0, 0, 0, 0)
        
        bg_lbl = QLabel(icon_widget)
        bg_lbl.setFixedSize(40, 40)
        q_icon = f"item_quality_{mod.quality}.png"
        bg_pixmap = QPixmap(os.path.join(self.image_base_path, q_icon))
        if bg_pixmap.isNull():
            bg_pixmap = QPixmap(os.path.join(self.image_base_path, "item_quality_3.png"))
        bg_lbl.setPixmap(bg_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        fg_lbl = QLabel(bg_lbl)
        fg_lbl.setFixedSize(40, 40)
        fg_lbl.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        prefix = "item_mod_device"
        if 5500101 <= mod.config_id <= 5500104:
            prefix = "item_mod_device_attack"
        elif 5500301 <= mod.config_id <= 5500304:
            prefix = "item_mod_device_protect"
            
        level = max(2, min(5, mod.quality))
        device_icon_name = f"{prefix}{level}.png"
        device_icon_path = os.path.join(self.image_base_path, device_icon_name)
        if not os.path.exists(device_icon_path):
            device_icon_path = os.path.join(self.image_base_path, "item_icons_mod_device_5.png")
            
        fg_pixmap = QPixmap(device_icon_path)
        if not fg_pixmap.isNull():
            fg_lbl.setPixmap(fg_pixmap.scaled(34, 34, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            fg_lbl.move(3, 3)
            
        header.addWidget(icon_widget)
        
        name_qual_layout = QVBoxLayout()
        name_qual_layout.setSpacing(2)
        
        if self.lang == 'en':
            mod_name = to_english_module(mod.config_id, mod.name)
        elif self.lang == 'es':
            mod_name = to_spanish_module(mod.config_id, mod.name)
        else:
            mod_name = mod.name
        name_lbl = QLabel(f"<b>{mod_name}</b>")
        name_lbl.setFont(QFont("Segoe UI Semibold", 10))
        name_qual_layout.addWidget(name_lbl)
        
        if self.lang == "en":
            qual_name = "Basic"
        elif self.lang == "es":
            qual_name = "Básico"
        else:
            qual_name = "普通"
        qual_color = "#3498DB" # Blue
        if mod.quality == 3:
            if self.lang == "en":
                qual_name = "Advanced"
            elif self.lang == "es":
                qual_name = "Avanzado"
            else:
                qual_name = "高级"
            qual_color = "#9B59B6" # Purple
        elif mod.quality >= 4:
            if self.lang == "en":
                qual_name = "Excellent"
            elif self.lang == "es":
                qual_name = "Excelente"
            else:
                qual_name = "卓越"
            qual_color = "#F1C40F" # Gold
            
        qual_lbl = QLabel(qual_name)
        qual_lbl.setStyleSheet(f"color: {qual_color}; font-weight: bold; font-size: 10px;")
        name_qual_layout.addWidget(qual_lbl)
        
        header.addLayout(name_qual_layout)
        header.addStretch(1)
        layout.addLayout(header)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        layout.addWidget(line)
        
        attrs_layout = QVBoxLayout()
        attrs_layout.setSpacing(2)
        for part in mod.parts:
            if self.lang == 'en':
                part_name = to_english_attr(part.name)
            elif self.lang == 'es':
                part_name = to_spanish_attr(part.name)
            else:
                part_name = part.name
            icon_p = self.get_stat_icon_path(part.id)
            
            part_row = QHBoxLayout()
            part_row.setSpacing(5)
            
            p_icon = QLabel()
            p_icon.setPixmap(QPixmap(icon_p).scaled(12, 12, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            part_row.addWidget(p_icon)
            
            part_lbl = QLabel(f"<font color='#aaa'>{part_name}:</font> <font color='#fff'><b>+<span style='font-family: Consolas;'>{part.value}</span></b></font>")
            part_lbl.setFont(QFont("Segoe UI Semibold", 8))
            part_row.addWidget(part_lbl)
            part_row.addStretch(1)
            attrs_layout.addLayout(part_row)
            
        layout.addLayout(attrs_layout)
        return card

    def setup_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.settings_title = QLabel("<b>Settings</b>")
        self.settings_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(self.settings_title)
        
        # Language Selection
        lang_group = QFrame()
        lang_group.setStyleSheet("background-color: #242424; border: 1px solid #3d3d3d; border-radius: 6px; padding: 10px;")
        lang_layout = QVBoxLayout(lang_group)
        
        self.lang_section_title = QLabel("<b>Language / 语言 / Idioma</b>")
        self.lang_section_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lang_layout.addWidget(self.lang_section_title)
        
        self.settings_lang_combo = QComboBox()
        self.settings_lang_combo.addItems(["English", "简体中文", "Español"])
        if self.lang == "en":
            self.settings_lang_combo.setCurrentIndex(0)
        elif self.lang == "zh":
            self.settings_lang_combo.setCurrentIndex(1)
        elif self.lang == "es":
            self.settings_lang_combo.setCurrentIndex(2)
        else:
            self.settings_lang_combo.setCurrentIndex(0)
        self.settings_lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.settings_lang_combo)
        
        layout.addWidget(lang_group)
        
        # Network Adapter Selection
        net_group = QFrame()
        net_group.setStyleSheet("background-color: #242424; border: 1px solid #3d3d3d; border-radius: 6px; padding: 10px;")
        net_layout = QVBoxLayout(net_group)
        
        self.net_section_title = QLabel("<b>Network Adapter / 网卡选择</b>")
        self.net_section_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        net_layout.addWidget(self.net_section_title)
        
        self.net_combo = QComboBox()
        self.interfaces = get_network_interfaces()
        for idx, iface in enumerate(self.interfaces):
            addrs = ", ".join([addr['addr'] for addr in iface['addresses']])
            self.net_combo.addItem(f"{iface['description']} ({addrs})", idx)
            
        net_layout.addWidget(self.net_combo)
        
        self.net_info_lbl = QLabel("Note: Network packet capture will use the selected adapter if automatic detection fails.")
        self.net_info_lbl.setStyleSheet("color: #888; font-size: 11px;")
        net_layout.addWidget(self.net_info_lbl)
        
        layout.addWidget(net_group)
        layout.addStretch(1)

    def change_language(self, index):
        if index == 0:
            self.lang = "en"
        elif index == 1:
            self.lang = "zh"
        elif index == 2:
            self.lang = "es"
        else:
            self.lang = "en"

        self.parser = ModuleParser(lang=self.lang)
        self.populate_stat_select()
        
        # Update tab texts
        if self.lang == "en":
            self.tab_buttons["Optimizer"].setText("Optimizer")
            if "Inventory" in self.tab_buttons:
                self.tab_buttons["Inventory"].setText("Inventory")
            self.tab_buttons["Settings"].setText("Settings")
        elif self.lang == "es":
            self.tab_buttons["Optimizer"].setText("Optimizador")
            if "Inventory" in self.tab_buttons:
                self.tab_buttons["Inventory"].setText("Inventario")
            self.tab_buttons["Settings"].setText("Ajustes")
        else:
            self.tab_buttons["Optimizer"].setText("优化器")
            if "Inventory" in self.tab_buttons:
                self.tab_buttons["Inventory"].setText("仓库")
            self.tab_buttons["Settings"].setText("设置")
        
        # Update Config Panel Labels and Buttons
        if self.lang == "en":
            self.qual_lbl.setText("<b>Quality</b>")
            self.add_stat_lbl.setText("<b>Add Stat to Priority / Constraints</b>")
            self.add_btn.setText("Add")
            self.priority_lbl.setText("<b>Stat Priority / Constraints</b>")
            self.results_title_lbl.setText("<b>Optimization Results</b>")
            self.calc_btn.setText("Calculate 5 module combo sets")
            self.settings_title.setText("<b>Settings</b>")
            self.lang_section_title.setText("<b>Language / 语言 / Idioma</b>")
            self.net_section_title.setText("<b>Network Adapter / 网卡选择</b>")
            self.net_info_lbl.setText("Note: Network packet capture will use the selected adapter if automatic detection fails.")
        elif self.lang == "es":
            self.qual_lbl.setText("<b>Calidad</b>")
            self.add_stat_lbl.setText("<b>Añadir Stat a Prioridad / Restricciones</b>")
            self.add_btn.setText("Añadir")
            self.priority_lbl.setText("<b>Prioridad de Stats / Restricciones</b>")
            self.results_title_lbl.setText("<b>Resultados de Optimización</b>")
            self.calc_btn.setText("Calcular conjuntos de 5 módulos")
            self.settings_title.setText("<b>Ajustes</b>")
            self.lang_section_title.setText("<b>Idioma / Language / 语言</b>")
            self.net_section_title.setText("<b>Adaptador de Red / Network Adapter</b>")
            self.net_info_lbl.setText("Nota: La captura de paquetes de red usará el adaptador seleccionado si la detección automática falla.")
        else:
            self.qual_lbl.setText("<b>Quality</b>") # Keep structure for other langs
            self.add_stat_lbl.setText("<b>Add Stat to Priority / Constraints</b>")
            self.add_btn.setText("Add")
            self.priority_lbl.setText("<b>Stat Priority / Constraints</b>")
            self.results_title_lbl.setText("<b>Optimization Results</b>")
            self.calc_btn.setText("计算5模组组合")
            self.settings_title.setText("<b>设置</b>")
            self.lang_section_title.setText("<b>语言 / Language / Idioma</b>")
            self.net_section_title.setText("<b>网卡选择 / Network Adapter</b>")
            self.net_info_lbl.setText("注意：如果自动检测失败，网络数据包捕获将使用所选的网卡。")

        # Update quality checkbox text
        if self.lang == "en":
            self.qual_checks["Basic"].setText("Basic")
            self.qual_checks["Advanced"].setText("Advanced")
            self.qual_checks["Excellent"].setText("Excellent")
        elif self.lang == "es":
            self.qual_checks["Basic"].setText("Básico")
            self.qual_checks["Advanced"].setText("Avanzado")
            self.qual_checks["Excellent"].setText("Excelente")
        else:
            self.qual_checks["Basic"].setText("普通")
            self.qual_checks["Advanced"].setText("高级")
            self.qual_checks["Excellent"].setText("卓越")
        
        # Update optimization method texts
        if hasattr(self, 'method_lbl') and self.method_lbl is not None:
            if self.lang == "en":
                self.method_lbl.setText("<b>Optimization Method</b>")
            elif self.lang == "es":
                self.method_lbl.setText("<b>Método de Optimización</b>")
            else:
                self.method_lbl.setText("<b>优化方法</b>")
        if hasattr(self, 'method_select') and self.method_select is not None:
            current_idx = self.method_select.currentIndex()
            self.method_select.blockSignals(True)
            self.method_select.clear()
            if self.lang == "en":
                self.method_select.addItems(["Standard", "Priority Lv.6/Lv.5"])
            elif self.lang == "es":
                self.method_select.addItems(["Standard", "Priority Lv.6/Lv.5"])
            else:
                self.method_select.addItems(["Standard", "Priority Lv.6/Lv.5"])
            self.method_select.setCurrentIndex(current_idx if current_idx >= 0 else 0)
            self.method_select.blockSignals(False)

        self.load_inventory_display()
        self.update_inventory_status_indicator()

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #2b2b2b;")
        return line

    def populate_stat_select(self):
        self.stat_select.clear()
        
        # Utilizaremos QStandardItemModel para soportar iconos en el ComboBox
        model = QStandardItemModel()
        
        # Primer item placeholder
        if self.lang == "en":
            placeholder_lbl = "Select Stat..."
        elif self.lang == "es":
            placeholder_lbl = "Seleccionar Stat..."
        else:
            placeholder_lbl = "选择属性..."
        placeholder_item = QStandardItem(placeholder_lbl)
        placeholder_item.setData(-1, Qt.ItemDataRole.UserRole)
        model.appendRow(placeholder_item)

        # Get currently added priority IDs to filter them out
        added_ids = set()
        if hasattr(self, 'stat_list_layout') and self.stat_list_layout is not None:
            for i in range(self.stat_list_layout.count()):
                w = self.stat_list_layout.itemAt(i).widget()
                if isinstance(w, StatPriorityWidget):
                    added_ids.add(w.stat_id)

        # Llenar con todos los stats disponibles y sus iconos representativos
        for attr_id, name in MODULE_ATTR_NAMES.items():
            if attr_id in added_ids:
                continue
            if self.lang == "en":
                disp_name = MODULE_ATTR_NAMES_EN.get(attr_id, name)
            elif self.lang == "es":
                disp_name = MODULE_ATTR_NAMES_ES.get(attr_id, name)
            else:
                disp_name = name
            item = QStandardItem(disp_name)
            item.setData(attr_id, Qt.ItemDataRole.UserRole)
            
            # Cargar el icono correspondiente
            icon_p = self.get_stat_icon_path(attr_id)
            if os.path.exists(icon_p):
                item.setIcon(QIcon(icon_p))
            
            model.appendRow(item)
            
        self.stat_select.setModel(model)
        self.stat_select.setCurrentIndex(0)

    def add_stat_priority(self):
        idx = self.stat_select.currentIndex()
        if idx <= 0: return
        
        # Extraer el attr_id almacenado como UserRole
        model = self.stat_select.model()
        item = model.item(idx)
        attr_id = item.data(Qt.ItemDataRole.UserRole)
        name = item.text()
        
        # Evitar duplicados
        for i in range(self.stat_list_layout.count()):
            w = self.stat_list_layout.itemAt(i).widget()
            if isinstance(w, StatPriorityWidget) and w.stat_id == attr_id:
                return

        icon_path = self.get_stat_icon_path(attr_id)
        
        w = StatPriorityWidget(attr_id, name, icon_path)
        w.removed.connect(self.remove_stat_priority)
        w.moved_up.connect(self.move_stat_up)
        w.moved_down.connect(self.move_stat_down)
        
        # Insertar antes del stretch
        self.stat_list_layout.insertWidget(self.stat_list_layout.count() - 1, w)
        self.populate_stat_select()

    def remove_stat_priority(self, widget):
        self.stat_list_layout.removeWidget(widget)
        widget.deleteLater()
        self.populate_stat_select()

    def move_stat_up(self, widget):
        idx = self.stat_list_layout.indexOf(widget)
        if idx > 0:
            self.stat_list_layout.removeWidget(widget)
            self.stat_list_layout.insertWidget(idx - 1, widget)

    def move_stat_down(self, widget):
        idx = self.stat_list_layout.indexOf(widget)
        if idx < self.stat_list_layout.count() - 2: # -2 porque el ultimo es stretch
            self.stat_list_layout.removeWidget(widget)
            self.stat_list_layout.insertWidget(idx + 1, widget)

    def load_initial_data(self):
        vdata_path = self.get_vdata_path()
        if os.path.exists(vdata_path):
            try:
                from BlueProtobuf_pb2 import CharSerialize
                with open(vdata_path, "rb") as f:
                    char_serialize = CharSerialize()
                    char_serialize.ParseFromString(f.read())
                
                modules = []
                mod_infos = char_serialize.Mod.ModInfos
                for package_type, package in char_serialize.ItemPackage.Packages.items():
                    for key, item in package.Items.items():
                        if item.HasField('ModNewAttr') and item.ModNewAttr.ModParts:
                            config_id = item.ConfigId
                            module_name = MODULE_NAMES.get(config_id, f"未知模组({config_id})")
                            mod_parts = list(item.ModNewAttr.ModParts)
                            mod_info = mod_infos.get(key) if mod_infos else None

                            module_info = ModuleInfo(
                                name=module_name,
                                config_id=config_id,
                                uuid=item.Uuid,
                                quality=item.Quality,
                                parts=[]
                            )

                            if mod_info:
                                init_link_nums = mod_info.InitLinkNums
                                for i, part_id in enumerate(mod_parts):
                                    if i < len(init_link_nums):
                                        attr_name = MODULE_ATTR_NAMES.get(part_id, f"未知属性({part_id})")
                                        attr_value = init_link_nums[i]
                                        module_part = ModulePart(
                                            id=part_id,
                                            name=attr_name,
                                            value=attr_value
                                        )
                                        module_info.parts.append(module_part)
                            modules.append(module_info)
                        else:
                            break
                
                self.all_modules = modules
                print(f"Loaded {len(self.all_modules)} modules from vdata")
            except Exception as e:
                print(f"Error loading vdata: {e}")

    def run_optimization(self):
        # Disable calculation button
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Waiting for packet..." if self.lang == "en" else ("Esperando paquete..." if self.lang == "es" else "等待数据包..."))

        # Setup texts based on language
        if self.lang == "en":
            title = "WAITING FOR NETWORK PACKET..."
            sub = "Please CHANGE CHANNEL (teleport / switch channel) or RELOGIN in the game to capture module data.\n(Or click below to bypass and use currently loaded offline data)"
        elif self.lang == "es":
            title = "ESPERANDO PAQUETE DE RED..."
            sub = "Por favor CAMBIA DE CANAL (teletransportarse o cambiar de canal) o REINICIA SESIÓN en el juego para capturar tus módulos.\n(O haz clic abajo para usar los datos ya cargados)"
        else:
            title = "等待网络数据包..."
            sub = "请在游戏内进行 切换频道（传送/换线） 或 重新登录 以捕获模组数据。\n（或者点击下方按钮以使用当前加载的数据）"

        # Show Loading Overlay and position it centered
        self.loading_overlay.set_image("welcome.png")
        self.loading_overlay.set_text(title, sub)
        self.loading_overlay.show_skip_button(True)
        self.loading_overlay.show()
        self.position_loading_overlay()
        QApplication.processEvents()

        # Start capture worker
        iface_idx = self.net_combo.currentIndex()
        iface_name = self.interfaces[iface_idx]['name'] if 0 <= iface_idx < len(self.interfaces) else None
        
        self.capture_worker = PacketCaptureWorker(iface_name)
        self.capture_worker.packet_captured.connect(self.on_packet_captured)
        self.capture_worker.error.connect(self.on_capture_error)
        self.capture_worker.start()

    def on_packet_captured(self, v_data):
        print("Packet captured successfully!")
        
        # Stop capture worker
        if hasattr(self, 'capture_worker') and self.capture_worker:
            self.capture_worker.stop()
            self.capture_worker.wait()
            self.capture_worker = None

        # Save to modules.vdata
        try:
            vdata_path = self.get_vdata_path()
            with open(vdata_path, "wb") as f:
                f.write(v_data.SerializeToString())
            print(f"Saved captured module data to: {vdata_path}")
        except Exception as e:
            print(f"Failed to save captured modules: {e}")

        # Reload data
        self.load_initial_data()
        self.update_inventory_status_indicator()
        if self.stacked_widget.currentIndex() == 1:
            self.load_inventory_display()

        # Process to optimization
        self.start_optimization_process()

    def skip_packet_capture(self):
        print("Skipping packet capture, using existing data...")
        
        # Stop capture worker
        if hasattr(self, 'capture_worker') and self.capture_worker:
            self.capture_worker.stop()
            self.capture_worker.wait()
            self.capture_worker = None

        # Load initial data if not already loaded (as backup)
        if not self.all_modules:
            self.load_initial_data()
            self.update_inventory_status_indicator()

        self.start_optimization_process()

    def on_capture_error(self, err_msg):
        print(f"Capture error: {err_msg}")
        self.skip_packet_capture()

    def start_optimization_process(self):
        if not self.all_modules:
            # If still no modules, show error message/warning and stop
            self.loading_overlay.hide()
            self.calc_btn.setEnabled(True)
            self.calc_btn.setText("Calculate 5 module combo sets" if self.lang == "en" else ("Calcular conjuntos de 5 módulos" if self.lang == "es" else "计算5模组组合"))
            
            # Show standard Qt warning dialog or change status label
            from PyQt6.QtWidgets import QMessageBox
            if self.lang == "en":
                QMessageBox.warning(self, "No Modules", "No modules detected or loaded. Please make sure you change channel in the game or have modules.vdata present.")
            elif self.lang == "es":
                QMessageBox.warning(self, "Sin Módulos", "No se detectaron ni cargaron módulos. Asegúrate de cambiar de canal en el juego o de tener el archivo modules.vdata.")
            else:
                QMessageBox.warning(self, "无模组", "未检测到或加载模组。请确保您在游戏内切换了频道或存在 modules.vdata 文件。")
            return

        # Hide skip button
        self.loading_overlay.show_skip_button(False)

        # Update overlay for calculation phase
        if self.lang == "en":
            title = "CALCULATING MODULE COMBINATIONS..."
            sub = "Please wait while the optimizer finds the best 5-module sets."
        elif self.lang == "es":
            title = "CALCULANDO COMBINACIONES..."
            sub = "Calculando combinaciones... Por favor espere."
        else:
            title = "正在计算最佳的5模组组合..."
            sub = "正在计算最佳的5模组组合... 请稍候。"
        
        self.loading_overlay.set_image("Calcular.png")
        self.loading_overlay.set_text(title, sub)
        self.calc_btn.setText("Optimizing..." if self.lang == "en" else ("Optimizando..." if self.lang == "es" else "优化中..."))

        # Recoger config
        target_attrs = []
        min_requirements = {}
        for i in range(self.stat_list_layout.count()):
            w = self.stat_list_layout.itemAt(i).widget()
            if isinstance(w, StatPriorityWidget):
                cfg = w.get_config()
                cn_name = MODULE_ATTR_NAMES.get(cfg["stat_id"])
                target_attrs.append(cn_name)
                if cfg["min_val"] > 0:
                    min_requirements[cn_name] = cfg["min_val"]

        opt_mode = 'standard'
        if hasattr(self, 'method_select'):
            if self.method_select.currentIndex() == 1:
                opt_mode = 'level_priority'

        self.optimizer = ModuleOptimizer(
            target_attributes=target_attrs,
            min_attr_sum_requirements=min_requirements,
            lang=self.lang,
            combination_size=5,
            optimization_mode=opt_mode
        )

        self.thread = QThread()
        self.worker = OptimizationWorker(self.optimizer, self.all_modules, ModuleCategory.ALL)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.display_results)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(lambda: self.calc_btn.setEnabled(True))
        
        # Reset calculation button text based on lang
        calc_text = "Calculate 5 module combo sets"
        if self.lang == "es":
            calc_text = "Calcular conjuntos de 5 módulos"
        elif self.lang == "zh":
            calc_text = "计算5模组组合"
        self.worker.finished.connect(lambda: self.calc_btn.setText(calc_text))
        
        self.worker.error.connect(lambda msg: print(f"Error: {msg}"))
        self.thread.start()

    def display_results(self, solutions: List[ModuleSolution]):
        # Hide loading overlay
        self.loading_overlay.hide()

        for i in reversed(range(self.results_grid.count())):
            widget = self.results_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for i, sol in enumerate(solutions[:10]):
            card = self.create_solution_card(sol, i + 1)
            self.results_grid.addWidget(card, i // 2, i % 2)

    def create_solution_card(self, solution: ModuleSolution, rank: int) -> QWidget:
        card = QFrame()
        card.setObjectName("SolutionCard")
        card.setStyleSheet("""
            QFrame#SolutionCard {
                background-color: rgba(30, 30, 30, 0.7); 
                border: 1px solid rgba(255, 255, 255, 0.15); 
                border-radius: 12px; 
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        header = QHBoxLayout()
        
        # Display custom info if available (which includes lv5/lv6 counts)
        if getattr(solution, 'custom_info', None):
            import re
            score_disp = re.sub(r'(\d+(?:\.\d+)?)', r"<span style='font-family: Consolas;'>\1</span>", solution.custom_info)
        else:
            if self.lang == 'en':
                score_disp = f"Score: <span style='font-family: Consolas;'>{solution.score:.2f}</span>"
            elif self.lang == 'es':
                score_disp = f"Puntos: <span style='font-family: Consolas;'>{solution.score:.2f}</span>"
            else:
                score_disp = f"战力: <span style='font-family: Consolas;'>{solution.score:.2f}</span>"
                
        rank_lbl = QLabel(f"<font color='#FFb700'><b>Rank <span style='font-family: Consolas;'>{rank}</span></b></font> <font color='#ffffff'>({score_disp})</font>")
        rank_lbl.setFont(QFont("Segoe UI Semibold", 11))
        header.addWidget(rank_lbl)
        header.addStretch(1)
        layout.addLayout(header)

        # Módulos en el combo (Estilo visual detallado e integrado como la imagen)
        mod_layout = QHBoxLayout()
        mod_layout.setSpacing(6)
        for mod in solution.modules:
            mod_widget = QWidget()
            mod_widget.setFixedSize(50, 50)
            
            # Contenedor apilado usando QLabel para renderizar el fondo de calidad y el icono de dispositivo
            stacked_layout = QVBoxLayout(mod_widget)
            stacked_layout.setContentsMargins(0, 0, 0, 0)
            
            bg_label = QLabel(mod_widget)
            bg_label.setFixedSize(50, 50)
            
            # Determinar fondo según calidad (3: Excelente/Amarillo-Naranja, 2: Avanzado/Morado, etc.)
            q_icon = f"item_quality_{mod.quality}.png"
            bg_pixmap = QPixmap(os.path.join(self.image_base_path, q_icon))
            if bg_pixmap.isNull():
                bg_pixmap = QPixmap(os.path.join(self.image_base_path, "item_quality_3.png"))
            bg_label.setPixmap(bg_pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            # Icono del dispositivo por encima del fondo
            fg_label = QLabel(bg_label)
            fg_label.setFixedSize(50, 50)
            fg_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            
            # Mapear el dispositivo según el config_id
            # 5500101-5500104 es Attack, 5500201-5500204 es Healing/Support, 5500301-5500304 es Protection/Guard
            prefix = "item_mod_device"
            if 5500101 <= mod.config_id <= 5500104:
                prefix = "item_mod_device_attack"
            elif 5500301 <= mod.config_id <= 5500304:
                prefix = "item_mod_device_protect"
                
            # Determinar la imagen del dispositivo (por ejemplo, item_mod_device_attack4.png para calidad 4 o similar)
            level = max(2, min(5, mod.quality)) # Niveles de imagen soportados: 2, 3, 4, 5
            device_icon_name = f"{prefix}{level}.png"
            device_icon_path = os.path.join(self.image_base_path, device_icon_name)
            
            if not os.path.exists(device_icon_path):
                # Fallback al icono genérico
                device_icon_path = os.path.join(self.image_base_path, "item_icons_mod_device_5.png")
                
            fg_pixmap = QPixmap(device_icon_path)
            if not fg_pixmap.isNull():
                fg_label.setPixmap(fg_pixmap.scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                fg_label.move(3, 3) # Centrarlo ligeramente en el contenedor de 50x50

            mod_layout.addWidget(mod_widget)
            
        layout.addLayout(mod_layout)

        # Desglose de Atributos
        attr_container = QWidget()
        attr_container.setStyleSheet("background-color: rgba(20, 20, 20, 0.5); border-radius: 6px; padding: 5px;")
        attr_vbox = QVBoxLayout(attr_container)
        attr_vbox.setContentsMargins(5, 5, 5, 5)
        attr_vbox.setSpacing(3)
        
        if self.lang == 'en':
            attr_dist_title = "Attribute Distribution:"
        elif self.lang == 'es':
            attr_dist_title = "Distribución de Atributos:"
        else:
            attr_dist_title = "属性分布:"
        attr_dist_lbl = QLabel(f"<font color='#888'>{attr_dist_title}</font>")
        attr_dist_lbl.setFont(QFont("Segoe UI Semibold", 9))
        attr_vbox.addWidget(attr_dist_lbl)

        for name, val in sorted(solution.attr_breakdown.items(), key=lambda x: x[1], reverse=True):
            if self.lang == 'en':
                disp_name = to_english_attr(name)
            elif self.lang == 'es':
                disp_name = to_spanish_attr(name)
            else:
                disp_name = name
            
            # Obtener el ID del stat para buscar su icono correspondiente
            stat_id = MODULE_ATTR_IDS.get(name, 1408)
            stat_icon_p = self.get_stat_icon_path(stat_id)
            
            stat_row = QHBoxLayout()
            stat_row.setSpacing(5)
            
            icon_lbl = QLabel()
            icon_lbl.setPixmap(QPixmap(stat_icon_p).scaled(14, 14, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            stat_row.addWidget(icon_lbl)
            
            stat_lbl = QLabel(f"<font color='#ddd'>{disp_name}</font> <font color='#FFd700'><b style='font-family: Consolas;'>+{val}</b></font>")
            stat_lbl.setFont(QFont("Segoe UI Semibold", 9))
            stat_row.addWidget(stat_lbl)
            stat_row.addStretch(1)
            
            attr_vbox.addLayout(stat_row)
            
        layout.addWidget(attr_container)

        return card

    def update_inventory_status_indicator(self):
        if not hasattr(self, 'status_indicator') or self.status_indicator is None:
            return
            
        count = len(self.all_modules)
        if count > 0:
            if self.lang == "en":
                text = f"🟢 Inventory Loaded ({count} modules)"
            elif self.lang == "es":
                text = f"🟢 Inventario Cargado ({count} módulos)"
            else:
                text = f"🟢 仓库已加载 ({count} 个模组)"
            self.status_indicator.setStyleSheet("""
                color: #2ecc71; 
                font-weight: bold; 
                font-size: 11px; 
                font-family: 'Segoe UI Emoji', 'Segoe UI', 'Microsoft YaHei';
                background-color: #1e3d25; 
                padding: 4px 10px; 
                min-height: 22px;
                border-radius: 4px; 
                border: 1px solid #27ae60;
            """)
        else:
            if self.lang == "en":
                text = f"🔴 Inventory Not Loaded"
            elif self.lang == "es":
                text = f"🔴 Inventario No Cargado"
            else:
                text = f"🔴 仓库未加载"
            self.status_indicator.setStyleSheet("""
                color: #e74c3c; 
                font-weight: bold; 
                font-size: 11px; 
                font-family: 'Segoe UI Emoji', 'Segoe UI', 'Microsoft YaHei';
                background-color: #3d1e1e; 
                padding: 4px 10px; 
                min-height: 22px;
                border-radius: 4px; 
                border: 1px solid #c0392b;
            """)
        self.status_indicator.setText(text)

    def show_startup_popup(self):
        try:
            popup = StartupInstructionsDialog(self)
            popup.exec()
        except Exception as e:
            print(f"Error showing startup popup: {e}")

    def check_vdata_modification(self):
        vdata_path = self.get_vdata_path()
        if os.path.exists(vdata_path):
            try:
                mtime = os.path.getmtime(vdata_path)
                if mtime != self.last_vdata_mtime:
                    self.last_vdata_mtime = mtime
                    self.on_vdata_changed()
            except Exception as e:
                print(f"Error checking vdata modification: {e}")

    def on_vdata_changed(self):
        print("modules.vdata modified! Reloading inventory...")
        # Re-register file watch path if needed (e.g. if the file was deleted/recreated)
        vdata_path = self.get_vdata_path()
        if hasattr(self, 'watcher'):
            try:
                self.watcher.removePaths(self.watcher.files())
            except Exception:
                pass
            if os.path.exists(vdata_path):
                self.watcher.addPath(vdata_path)
                
        self.load_initial_data()
        self.update_inventory_status_indicator()
        if self.stacked_widget.currentIndex() == 1:
            self.load_inventory_display()

    def position_loading_overlay(self):
        if hasattr(self, 'loading_overlay') and self.loading_overlay.isVisible():
            # Get geometry of results scroll area
            scroll_geom = self.results_scroll.geometry()
            w = self.results_scroll.width()
            h = self.results_scroll.height()
            
            # Central horizontal stripe across the results panel
            stripe_h = 160
            stripe_y = self.results_scroll.y() + (h - stripe_h) // 2
            
            self.loading_overlay.setGeometry(
                self.results_scroll.x(),
                stripe_y,
                w,
                stripe_h
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_loading_overlay()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModuleOptimizerGUI()
    window.show()
    sys.exit(app.exec())
