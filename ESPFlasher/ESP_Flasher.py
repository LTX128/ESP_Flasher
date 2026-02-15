#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Made BY LTX

import sys
import os
import json
import subprocess
import threading
import time
import datetime
import shutil
import glob
import re
from typing import List, Dict, Optional, Tuple

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSpinBox, QCheckBox, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QGroupBox, QSplitter, QStackedWidget,
    QListWidget, QListWidgetItem, QLineEdit, QPlainTextEdit,
    QMenu, QToolBar, QStatusBar, QDialog, QDialogButtonBox,
    QFormLayout, QTabWidget, QRadioButton, QButtonGroup,
    QFrame, QScrollArea, QSizePolicy, QAbstractItemView, QTreeWidget, QTreeWidgetItem,
    QInputDialog
)
from PySide6.QtCore import (
    Qt, QThread, Signal, Slot, QTimer, QPropertyAnimation,
    QEasingCurve, QPoint, QSize, QRect, QSettings, QByteArray,
    QMutex, QWaitCondition, QIODevice, QDateTime
)
from PySide6.QtGui import (
    QIcon, QPixmap, QFont, QColor, QPalette, QBrush,
    QLinearGradient, QPainter, QPen, QAction, QDragEnterEvent,
    QDropEvent, QTextCursor, QTextCharFormat, QSyntaxHighlighter,
    QFontDatabase, QMovie
)

import serial
import serial.tools.list_ports

APP_NAME = "ESP Flasher"
VERSION = "1.0.0"
AUTHOR = "LTX"
COMPANY = "LTX74"
SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "settings.json")
HISTORY_FILE = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "history.json")
BACKUP_DIR = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "backups")
FIRMWARE_DIR = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "firmwares")
DEFAULT_BAUDRATE = 460800
DEFAULT_FLASH_ADDRESS = "0x0"

COLOR_PRIMARY = "#7B2EDA"
COLOR_SECONDARY = "#00B0FF"
COLOR_DARK = "#1E1E2E"
COLOR_DARKER = "#151522"
COLOR_LIGHT = "#F5F5F9"
COLOR_SUCCESS = "#4CAF50"
COLOR_ERROR = "#F44336"
COLOR_WARNING = "#FFC107"
COLOR_INFO = "#2196F3"

STYLE_SHEET = f"""
QMainWindow, QDialog {{
    background-color: {COLOR_DARK};
    color: {COLOR_LIGHT};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 10pt;
}}
QWidget {{
    background-color: transparent;
    color: {COLOR_LIGHT};
}}
QPushButton {{
    background-color: {COLOR_PRIMARY};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    color: white;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: #9B4DED;
}}
QPushButton:pressed {{
    background-color: #5A1FA0;
}}
QPushButton:flat {{
    background-color: transparent;
    color: {COLOR_PRIMARY};
}}
QPushButton:flat:hover {{
    background-color: rgba(123, 46, 218, 0.1);
}}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
    background-color: {COLOR_DARKER};
    border: 1px solid #3A3A4A;
    border-radius: 4px;
    padding: 6px;
    color: {COLOR_LIGHT};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {COLOR_PRIMARY};
}}
QLabel {{
    color: {COLOR_LIGHT};
}}
QGroupBox {{
    border: 1px solid #3A3A4A;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: {COLOR_SECONDARY};
}}
QTableWidget {{
    background-color: {COLOR_DARKER};
    alternate-background-color: #2A2A3A;
    gridline-color: #3A3A4A;
    selection-background-color: {COLOR_PRIMARY};
}}
QTableWidget::item {{
    padding: 5px;
}}
QHeaderView::section {{
    background-color: {COLOR_DARK};
    color: {COLOR_LIGHT};
    border: none;
    border-bottom: 1px solid #3A3A4A;
    padding: 8px;
}}
QProgressBar {{
    border: 1px solid #3A3A4A;
    border-radius: 4px;
    text-align: center;
    background-color: {COLOR_DARKER};
}}
QProgressBar::chunk {{
    background-color: {COLOR_PRIMARY};
    border-radius: 4px;
}}
QTabWidget::pane {{
    border: 1px solid #3A3A4A;
    border-radius: 4px;
    background-color: {COLOR_DARKER};
}}
QTabBar::tab {{
    background-color: {COLOR_DARK};
    color: {COLOR_LIGHT};
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {COLOR_PRIMARY};
}}
QTabBar::tab:hover {{
    background-color: #3A3A4A;
}}
QScrollBar:vertical {{
    background-color: {COLOR_DARKER};
    width: 14px;
    border-radius: 7px;
}}
QScrollBar::handle:vertical {{
    background-color: #5A5A6A;
    border-radius: 7px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLOR_PRIMARY};
}}
QScrollBar:horizontal {{
    background-color: {COLOR_DARKER};
    height: 14px;
    border-radius: 7px;
}}
QScrollBar::handle:horizontal {{
    background-color: #5A5A6A;
    border-radius: 7px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {COLOR_PRIMARY};
}}
QMenuBar {{
    background-color: {COLOR_DARKER};
    color: {COLOR_LIGHT};
}}
QMenuBar::item:selected {{
    background-color: {COLOR_PRIMARY};
}}
QMenu {{
    background-color: {COLOR_DARKER};
    color: {COLOR_LIGHT};
    border: 1px solid #3A3A4A;
}}
QMenu::item:selected {{
    background-color: {COLOR_PRIMARY};
}}
QStatusBar {{
    background-color: {COLOR_DARKER};
    color: {COLOR_LIGHT};
}}
QCheckBox {{
    spacing: 5px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}
QCheckBox::indicator:unchecked {{
    background-color: {COLOR_DARKER};
    border: 1px solid #3A3A4A;
    border-radius: 3px;
}}
QCheckBox::indicator:checked {{
    background-color: {COLOR_PRIMARY};
    border: 1px solid {COLOR_PRIMARY};
    border-radius: 3px;
    image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpolygon points='10.5,2.5 4.5,8.5 1.5,5.5 0.5,6.5 4.5,10.5 11.5,3.5' fill='white'/%3E%3C/svg%3E");
}}
QRadioButton {{
    spacing: 5px;
}}
QRadioButton::indicator {{
    width: 18px;
    height: 18px;
}}
QRadioButton::indicator:unchecked {{
    background-color: {COLOR_DARKER};
    border: 1px solid #3A3A4A;
    border-radius: 9px;
}}
QRadioButton::indicator:checked {{
    background-color: {COLOR_PRIMARY};
    border: 1px solid {COLOR_PRIMARY};
    border-radius: 9px;
    image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'%3E%3Ccircle cx='5' cy='5' r='3' fill='white'/%3E%3C/svg%3E");
}}
QSplitter::handle {{
    background-color: #3A3A4A;
}}
"""

class DetectBoardsThread(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._is_running = True

    def run(self):
        boards = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if not self._is_running:
                break
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'esptool', '--port', port.device, 'flash_id'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    output = result.stdout + result.stderr
                    chip_type = 'Unknown'
                    mac = 'N/A'
                    flash_size = 'N/A'
                    
                    for line in output.splitlines():
                        if 'Chip is' in line or 'Detecting chip type' in line:
                            if 'ESP32' in line.upper():
                                if 'ESP32-S2' in line.upper():
                                    chip_type = 'ESP32-S2'
                                elif 'ESP32-S3' in line.upper():
                                    chip_type = 'ESP32-S3'
                                elif 'ESP32-C3' in line.upper():
                                    chip_type = 'ESP32-C3'
                                elif 'ESP32-C6' in line.upper():
                                    chip_type = 'ESP32-C6'
                                elif 'ESP32-H2' in line.upper():
                                    chip_type = 'ESP32-H2'
                                else:
                                    chip_type = 'ESP32'
                            elif 'ESP8266' in line.upper():
                                chip_type = 'ESP8266'
                        elif 'MAC:' in line:
                            mac = line.split('MAC:')[-1].strip()
                        elif 'Detected flash size:' in line:
                            flash_size = line.split('Detected flash size:')[-1].strip()
                    
                    boards.append({
                        'port': port.device,
                        'description': port.description,
                        'chip': chip_type,
                        'mac': mac,
                        'flash_size': flash_size
                    })
                else:
                    boards.append({
                        'port': port.device,
                        'description': port.description,
                        'chip': 'Not ESP / Detection failed',
                        'mac': 'N/A',
                        'flash_size': 'N/A'
                    })
            except subprocess.TimeoutExpired:
                boards.append({
                    'port': port.device,
                    'description': port.description,
                    'chip': 'Detection timeout',
                    'mac': 'N/A',
                    'flash_size': 'N/A'
                })
            except Exception as e:
                continue
        self.finished.emit(boards)

    def stop(self):
        self._is_running = False


class FlashThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, chip, port, baudrate, firmware_path, address, erase=False, ota=False):
        super().__init__()
        self.chip = chip
        self.port = port
        self.baudrate = baudrate
        self.firmware_path = firmware_path
        self.address = address
        self.erase = erase
        self.ota = ota
        self._process = None

    def run(self):
        try:
            if not os.path.exists(self.firmware_path):
                self.finished.emit(False, f"Error: Firmware file not found at: {self.firmware_path}")
                return

            cmd = [sys.executable, '-m', 'esptool', '--chip', self.chip, '--port', self.port, '--baud', str(self.baudrate), 'write_flash']
            if self.erase:
                cmd.append('--erase-all')
            cmd.append('-z')
            if self.ota:
                cmd.extend(['--flash_mode', 'dio', '--flash_size', 'detect'])
            cmd.extend([self.address, self.firmware_path])

            self.progress.emit(0, f"Preparing flash... File: {os.path.basename(self.firmware_path)}")
            self.progress.emit(5, f"Full path: {self.firmware_path}")
            self.progress.emit(10, f"Chip: {self.chip}")
            self.progress.emit(15, f"Command: {' '.join(cmd)}")
            
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in self._process.stdout:
                if not line:
                    continue
                self.progress.emit(50, line.strip())
                match = re.search(r'\((\d+)\s*%\)', line)
                if match:
                    percent = int(match.group(1))
                    self.progress.emit(percent, line.strip())

            self._process.wait()
            if self._process.returncode == 0:
                self.progress.emit(100, "Flash completed successfully!")
                self.finished.emit(True, "Firmware flashed successfully.")
            else:
                self.finished.emit(False, "Error during flash. See logs for details.")
        except Exception as e:
            self.finished.emit(False, str(e))

    def stop(self):
        if self._process:
            self._process.terminate()


class BackupThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str, str)

    def __init__(self, port, baudrate, size, output_dir):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.size = size
        self.output_dir = output_dir

    def run(self):
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.output_dir, f"backup_{timestamp}.bin")

            cmd = ['esptool', '--port', self.port, '--baud', str(self.baudrate),
                   'read_flash', '0x0', str(self.size), backup_file]
            self.progress.emit(0, "Starting backup...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.progress.emit(50, line.strip())
            process.wait()
            if process.returncode == 0:
                self.progress.emit(100, "Backup finished.")
                self.finished.emit(True, "Backup successful.", backup_file)
            else:
                self.finished.emit(False, "Error during backup.", "")
        except Exception as e:
            self.finished.emit(False, str(e), "")


class SerialMonitorThread(QThread):
    data_received = Signal(bytes)
    error = Signal(str)
    data_sent = Signal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self._is_running = True
        self._write_mutex = QMutex()

    def run(self):
        try:
            self.serial_port = serial.Serial(
                self.port, 
                self.baudrate, 
                timeout=1,
                write_timeout=2
            )
            self.msleep(100)
            
            while self._is_running:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.data_received.emit(data)
                else:
                    self.msleep(10)
        except Exception as e:
            self.error.emit(f"Serial error: {str(e)}")
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

    def stop(self):
        self._is_running = False
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except:
                pass

    def write(self, data: bytes):
        self._write_mutex.lock()
        try:
            if self.serial_port and self.serial_port.is_open:
                written = self.serial_port.write(data)
                self.serial_port.flush()
                self.data_sent.emit(f"Sent {written} bytes")
                return True
            else:
                self.error.emit("Serial port is not open")
                return False
        except Exception as e:
            self.error.emit(f"Error sending data: {str(e)}")
            return False
        finally:
            self._write_mutex.unlock()

class SettingsManager:
    def __init__(self):
        self.settings_file = SETTINGS_FILE
        self.data = self.load()

    def load(self) -> dict:
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                return self.defaults()
        return self.defaults()

    def save(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def defaults(self) -> dict:
        return {
            'baudrate': DEFAULT_BAUDRATE,
            'flash_address': DEFAULT_FLASH_ADDRESS,
            'chip_type': 'auto',
            'erase_before_flash': False,
            'ota_mode': False,
            'backup_before_flash': True,
            'backup_size': 4194304,
            'serial_baudrate': 115200,
            'firmware_dir': FIRMWARE_DIR,
            'backup_dir': BACKUP_DIR,
            'dark_mode': True,
            'auto_detect_on_start': True,
            'theme_primary': COLOR_PRIMARY,
            'theme_secondary': COLOR_SECONDARY
        }


class HistoryManager:
    def __init__(self):
        self.history_file = HISTORY_FILE
        self.history = self.load()

    def load(self) -> list:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def add_entry(self, entry: dict):
        self.history.insert(0, entry)
        if len(self.history) > 100:
            self.history = self.history[:100]
        self.save()

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📊 Dashboard")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #00B0FF;")
        layout.addWidget(title)

        subtitle = QLabel("Boards detected automatically")
        subtitle.setStyleSheet("font-size: 10pt; color: #AAAAAA;")
        layout.addWidget(subtitle)

        toolbar = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_boards)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Port", "Description", "Chip", "MAC", "Flash Size"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        QTimer.singleShot(100, self.refresh_boards)

    def refresh_boards(self):
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("🔍 Detecting...")
        self.parent.statusBar().showMessage("Detecting boards...")
        self.detect_thread = DetectBoardsThread()
        self.detect_thread.finished.connect(self.on_detection_finished)
        self.detect_thread.error.connect(self.on_detection_error)
        self.detect_thread.start()

    def on_detection_finished(self, boards):
        self.table.setRowCount(len(boards))
        esp_count = 0
        for row, board in enumerate(boards):
            chip = board.get('chip', '')
            
            if 'ESP' in chip.upper() and 'failed' not in chip.lower() and 'timeout' not in chip.lower():
                color = QColor(76, 175, 80)
                esp_count += 1
            elif 'timeout' in chip.lower():
                color = QColor(255, 193, 7)
            elif 'failed' in chip.lower() or 'Not ESP' in chip:
                color = QColor(158, 158, 158)
            else:
                color = QColor(255, 255, 255)
            
            port_item = QTableWidgetItem(board.get('port', ''))
            port_item.setForeground(color)
            self.table.setItem(row, 0, port_item)
            
            desc_item = QTableWidgetItem(board.get('description', ''))
            desc_item.setForeground(color)
            self.table.setItem(row, 1, desc_item)
            
            chip_item = QTableWidgetItem(chip)
            chip_item.setForeground(color)
            self.table.setItem(row, 2, chip_item)
            
            mac_item = QTableWidgetItem(board.get('mac', ''))
            mac_item.setForeground(color)
            self.table.setItem(row, 3, mac_item)
            
            flash_item = QTableWidgetItem(board.get('flash_size', ''))
            flash_item.setForeground(color)
            self.table.setItem(row, 4, flash_item)
            
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh")
        
        if esp_count > 0:
            self.parent.statusBar().showMessage(f"Detection finished: {esp_count} ESP board(s) detected, {len(boards)} total port(s)")
        else:
            self.parent.statusBar().showMessage(f"Detection finished: No ESP boards found, {len(boards)} port(s) scanned")

    def on_detection_error(self, error_msg):
        QMessageBox.warning(self, "Detection error", error_msg)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh")
        self.parent.statusBar().showMessage("Error during detection.")


class FlashPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_firmware = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("⚡ Flash firmware")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #00B0FF;")
        layout.addWidget(title)

        self.drop_area = QFrame()
        self.drop_area.setFrameShape(QFrame.Shape.Box)
        self.drop_area.setLineWidth(2)
        self.drop_area.setStyleSheet("border: 2px dashed #7B2EDA; border-radius: 10px; background-color: #1E1E2E;")
        self.drop_area.setMinimumHeight(120)
        self.drop_area.setAcceptDrops(True)

        drop_layout = QVBoxLayout(self.drop_area)
        drop_label = QLabel("Drag and drop your .bin file here\nor click to select")
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_label.setStyleSheet("font-size: 12pt; color: #AAAAAA;")
        drop_layout.addWidget(drop_label)
        self.drop_area.mousePressEvent = self.select_firmware
        layout.addWidget(self.drop_area)

        self.firmware_info = QLabel("No file selected")
        self.firmware_info.setStyleSheet("color: #AAAAAA; font-style: italic;")
        layout.addWidget(self.firmware_info)

        options_group = QGroupBox("Flash options")
        options_layout = QFormLayout(options_group)

        self.chip_combo = QComboBox()
        self.chip_combo.addItems(["auto", "esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c2", "esp32c6", "esp32c61", "esp32c5", "esp32h2", "esp32h21", "esp32p4", "esp32h4"])
        self.chip_combo.setCurrentText(self.parent.settings.data.get('chip_type', 'auto'))
        options_layout.addRow("Chip type:", self.chip_combo)

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        self.refresh_ports()
        options_layout.addRow("Port:", self.port_combo)

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["115200", "230400", "460800", "921600", "1500000"])
        self.baudrate_combo.setCurrentText(str(self.parent.settings.data.get('baudrate', DEFAULT_BAUDRATE)))
        options_layout.addRow("Baudrate:", self.baudrate_combo)

        self.address_edit = QLineEdit(self.parent.settings.data.get('flash_address', DEFAULT_FLASH_ADDRESS))
        options_layout.addRow("Flash address:", self.address_edit)

        self.erase_check = QCheckBox("Erase all memory before flash")
        self.erase_check.setChecked(self.parent.settings.data.get('erase_before_flash', False))
        options_layout.addRow("", self.erase_check)

        self.ota_check = QCheckBox("OTA mode (if supported)")
        self.ota_check.setChecked(self.parent.settings.data.get('ota_mode', False))
        options_layout.addRow("", self.ota_check)

        self.backup_check = QCheckBox("Backup current firmware before flash")
        self.backup_check.setChecked(self.parent.settings.data.get('backup_before_flash', True))
        options_layout.addRow("", self.backup_check)

        layout.addWidget(options_group)

        self.flash_btn = QPushButton("🚀 Start flash")
        self.flash_btn.setMinimumHeight(40)
        self.flash_btn.setStyleSheet(f"background-color: {COLOR_SUCCESS}; font-size: 12pt;")
        self.flash_btn.clicked.connect(self.start_flash)
        self.flash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.flash_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(1000)
        self.log_text.setStyleSheet("font-family: 'Consolas', monospace;")
        layout.addWidget(QLabel("📝 Logs:"))
        layout.addWidget(self.log_text)

        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.refresh_ports)
        self.port_timer.start(2000)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toString().endswith('.bin'):
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("border: 2px dashed #00B0FF; border-radius: 10px; background-color: #2A2A3A;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet("border: 2px dashed #7B2EDA; border-radius: 10px; background-color: #1E1E2E;")

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].endswith('.bin'):
            self.set_firmware(files[0])
        self.drop_area.setStyleSheet("border: 2px dashed #7B2EDA; border-radius: 10px; background-color: #1E1E2E;")

    def select_firmware(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select firmware", "", "Binary files (*.bin)")
        if file_path:
            self.set_firmware(file_path)

    def set_firmware(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(self, "File not found", f"The specified file does not exist:\n{path}")
            return
        self.current_firmware = path
        file_size = self.human_size(os.path.getsize(path))
        self.firmware_info.setText(f"📁 {os.path.basename(path)} ({file_size})")
        self.firmware_info.setStyleSheet("color: #00B0FF; font-weight: bold;")
        self.firmware_info.setToolTip(path)
        self.log_text.appendPlainText(f"✅ File selected: {os.path.basename(path)}")
        self.log_text.appendPlainText(f"   Path: {path}")
        self.log_text.appendPlainText(f"   Size: {file_size}\n")

    def human_size(self, size):
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}", port.device)
        index = self.port_combo.findText(current, Qt.MatchFlag.MatchContains)
        if index >= 0:
            self.port_combo.setCurrentIndex(index)

    def start_flash(self):
        if not self.current_firmware:
            QMessageBox.warning(self, "File missing", "Please select a .bin file.")
            return
        if self.port_combo.count() == 0:
            QMessageBox.warning(self, "Port missing", "No COM port detected.")
            return

        chip = self.chip_combo.currentText()
        port = self.port_combo.currentData()
        baudrate = int(self.baudrate_combo.currentText())
        address = self.address_edit.text().strip()
        erase = self.erase_check.isChecked()
        ota = self.ota_check.isChecked()
        backup = self.backup_check.isChecked()

        if backup:
            size = self.parent.settings.data.get('backup_size', 4194304)
            reply = QMessageBox.question(self, "Backup",
                                         f"Do you want to backup the current firmware (size {size/1024/1024:.0f} MB)?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.backup_thread = BackupThread(port, baudrate, size, self.parent.settings.data['backup_dir'])
                self.backup_thread.progress.connect(self.update_progress)
                self.backup_thread.finished.connect(self.on_backup_finished)
                self.backup_thread.start()
                self.flash_btn.setEnabled(False)
                return

        self.do_flash(chip, port, baudrate, address, erase, ota)

    def on_backup_finished(self, success, message, backup_path):
        if success:
            self.parent.statusBar().showMessage(f"Backup successful: {backup_path}")
            chip = self.chip_combo.currentText()
            port = self.port_combo.currentData()
            baudrate = int(self.baudrate_combo.currentText())
            address = self.address_edit.text().strip()
            erase = self.erase_check.isChecked()
            ota = self.ota_check.isChecked()
            self.do_flash(chip, port, baudrate, address, erase, ota)
        else:
            QMessageBox.critical(self, "Backup error", message)
            self.flash_btn.setEnabled(True)

    def do_flash(self, chip, port, baudrate, address, erase, ota):
        self.flash_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.log_text.appendPlainText(f"Starting flash on {port}...")
        self.log_text.appendPlainText(f"Chip type: {chip}")
        self.flash_thread = FlashThread(chip, port, baudrate, self.current_firmware, address, erase, ota)
        self.flash_thread.progress.connect(self.update_progress)
        self.flash_thread.finished.connect(self.on_flash_finished)
        self.flash_thread.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.log_text.appendPlainText(message)
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def on_flash_finished(self, success, message):
        self.flash_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.log_text.appendPlainText("✅ " + message)
            QMessageBox.information(self, "Success", message)
            entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'port': self.port_combo.currentData(),
                'firmware': self.current_firmware,
                'address': self.address_edit.text(),
                'status': 'success'
            }
            self.parent.history_manager.add_entry(entry)
        else:
            self.log_text.appendPlainText("❌ " + message)
            QMessageBox.critical(self, "Failure", message)
            entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'port': self.port_combo.currentData(),
                'firmware': self.current_firmware,
                'address': self.address_edit.text(),
                'status': 'failed'
            }
            self.parent.history_manager.add_entry(entry)


class BackupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("💾 Backups")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #00B0FF;")
        layout.addWidget(title)

        self.backup_list = QListWidget()
        self.backup_list.setIconSize(QSize(32, 32))
        self.backup_list.itemDoubleClicked.connect(self.restore_backup)
        layout.addWidget(QLabel("Available backups (double-click to restore):"))
        layout.addWidget(self.backup_list)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_backups)
        btn_layout.addWidget(self.refresh_btn)

        self.restore_btn = QPushButton("♻️ Restore selected")
        self.restore_btn.clicked.connect(self.restore_selected)
        btn_layout.addWidget(self.restore_btn)

        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        self.refresh_backups()

    def refresh_backups(self):
        self.backup_list.clear()
        backup_dir = self.parent.settings.data.get('backup_dir', BACKUP_DIR)
        if os.path.exists(backup_dir):
            for file in sorted(glob.glob(os.path.join(backup_dir, "*.bin")), reverse=True):
                size = os.path.getsize(file)
                mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file))
                item = QListWidgetItem(f"{os.path.basename(file)} ({mod_time.strftime('%Y-%m-%d %H:%M')}) - {self.human_size(size)}")
                item.setData(Qt.UserRole, file)
                self.backup_list.addItem(item)

    def human_size(self, size):
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def restore_selected(self):
        item = self.backup_list.currentItem()
        if item:
            self.restore_backup(item)

    def restore_backup(self, item):
        backup_path = item.data(Qt.UserRole)
        if not backup_path:
            return
        ports = serial.tools.list_ports.comports()
        if not ports:
            QMessageBox.warning(self, "No port", "No COM port detected.")
            return
        port_list = [f"{p.device} - {p.description}" for p in ports]
        port, ok = QInputDialog.getItem(self, "Restore", "Choose target port:", port_list, 0, False)
        if not ok:
            return
        port_device = ports[port_list.index(port)].device

        self.parent.flash_page.current_firmware = backup_path
        self.parent.flash_page.firmware_info.setText(f"📁 {os.path.basename(backup_path)} (restore)")
        self.parent.sidebar_stack.setCurrentIndex(1)
        index = self.parent.flash_page.port_combo.findText(port, Qt.MatchFlag.MatchContains)
        if index >= 0:
            self.parent.flash_page.port_combo.setCurrentIndex(index)

    def delete_selected(self):
        item = self.backup_list.currentItem()
        if item:
            backup_path = item.data(Qt.UserRole)
            reply = QMessageBox.question(self, "Confirmation",
                                         f"Permanently delete {os.path.basename(backup_path)}?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    os.remove(backup_path)
                    self.refresh_backups()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))


class SerialPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.serial_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📡 Serial monitor")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #00B0FF;")
        layout.addWidget(title)

        ctrl_layout = QHBoxLayout()

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        ctrl_layout.addWidget(QLabel("Port:"))
        ctrl_layout.addWidget(self.port_combo)

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.baud_combo.setCurrentText(str(self.parent.settings.data.get('serial_baudrate', 115200)))
        ctrl_layout.addWidget(QLabel("Baudrate:"))
        ctrl_layout.addWidget(self.baud_combo)

        self.connect_btn = QPushButton("🔌 Connect")
        self.connect_btn.clicked.connect(self.toggle_serial)
        self.connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ctrl_layout.addWidget(self.connect_btn)

        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_console)
        ctrl_layout.addWidget(self.clear_btn)

        self.export_btn = QPushButton("💾 Export")
        self.export_btn.clicked.connect(self.export_logs)
        ctrl_layout.addWidget(self.export_btn)

        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.console.setMaximumBlockCount(10000)
        layout.addWidget(self.console)

        send_layout = QHBoxLayout()
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("Type a message to send...")
        self.send_input.returnPressed.connect(self.send_data)
        send_layout.addWidget(self.send_input)

        self.send_btn = QPushButton("📤 Send")
        self.send_btn.clicked.connect(self.send_data)
        send_layout.addWidget(self.send_btn)

        self.send_ascii = QRadioButton("ASCII")
        self.send_ascii.setChecked(True)
        self.send_hex = QRadioButton("HEX")
        send_layout.addWidget(self.send_ascii)
        send_layout.addWidget(self.send_hex)
        
        send_layout.addWidget(QLabel("Line ending:"))
        self.line_ending_combo = QComboBox()
        self.line_ending_combo.addItems(["\\n (LF)", "\\r\\n (CRLF)", "\\r (CR)", "None"])
        self.line_ending_combo.setCurrentIndex(0)
        send_layout.addWidget(self.line_ending_combo)

        layout.addLayout(send_layout)

        self.refresh_ports()
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.refresh_ports)
        self.port_timer.start(2000)

    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}", port.device)
        if current:
            index = self.port_combo.findText(current, Qt.MatchFlag.MatchContains)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)

    def toggle_serial(self):
        if self.serial_thread and self.serial_thread.isRunning():
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        if self.port_combo.count() == 0:
            QMessageBox.warning(self, "Port missing", "No COM port detected.")
            return
        port = self.port_combo.currentData()
        baudrate = int(self.baud_combo.currentText())
        self.serial_thread = SerialMonitorThread(port, baudrate)
        self.serial_thread.data_received.connect(self.on_data_received)
        self.serial_thread.error.connect(self.on_serial_error)
        self.serial_thread.data_sent.connect(self.on_data_sent)
        self.serial_thread.start()
        self.connect_btn.setText("🔌 Disconnect")
        self.connect_btn.setStyleSheet(f"background-color: {COLOR_ERROR};")
        self.parent.statusBar().showMessage(f"Connected to {port} at {baudrate} baud")

    def disconnect_serial(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()
            self.serial_thread = None
        self.connect_btn.setText("🔌 Connect")
        self.connect_btn.setStyleSheet("")
        self.parent.statusBar().showMessage("Disconnected")

    def on_data_received(self, data: bytes):
        try:
            text = data.decode('utf-8', errors='replace')
        except:
            text = str(data)
        self.console.insertPlainText(text)
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console.setTextCursor(cursor)

    def on_serial_error(self, error_msg):
        self.console.insertPlainText(f"\n⚠️ ERROR: {error_msg}\n")
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console.setTextCursor(cursor)
    
    def on_data_sent(self, message):
        self.parent.statusBar().showMessage(message, 2000)

    def send_data(self):
        if not self.serial_thread or not self.serial_thread.isRunning():
            QMessageBox.warning(self, "Not connected", "Connect to a port first.")
            return
        text = self.send_input.text()
        if not text:
            return
        
        line_ending_index = self.line_ending_combo.currentIndex()
        line_endings = ['\n', '\r\n', '\r', '']
        line_ending = line_endings[line_ending_index]
        
        if self.send_ascii.isChecked():
            data = (text + line_ending).encode('utf-8')
            self.console.insertPlainText(f">> {text}{line_ending}")
        else:
            hex_str = text.replace(' ', '')
            try:
                data = bytes.fromhex(hex_str)
                if line_ending:
                    data += line_ending.encode('utf-8')
                self.console.insertPlainText(f">> HEX: {text}\n")
            except:
                QMessageBox.warning(self, "HEX error", "Invalid HEX format. Use hex pairs (e.g. 41 42 43).")
                return
        
        self.serial_thread.write(data)
        self.send_input.clear()
        
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console.setTextCursor(cursor)

    def clear_console(self):
        self.console.clear()

    def export_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export logs", "", "Text files (*.txt);;Log files (*.log)")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.console.toPlainText())
                QMessageBox.information(self, "Export successful", f"Logs exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export error", str(e))


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #00B0FF;")
        layout.addWidget(title)

        form = QFormLayout()

        self.baudrate_spin = QSpinBox()
        self.baudrate_spin.setRange(9600, 921600)
        self.baudrate_spin.setValue(self.parent.settings.data.get('baudrate', DEFAULT_BAUDRATE))
        form.addRow("Default baudrate:", self.baudrate_spin)

        self.address_edit = QLineEdit(self.parent.settings.data.get('flash_address', DEFAULT_FLASH_ADDRESS))
        form.addRow("Default flash address:", self.address_edit)

        self.chip_combo = QComboBox()
        self.chip_combo.addItems(["auto", "esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c2", "esp32c6", "esp32c61", "esp32c5", "esp32h2", "esp32h21", "esp32p4", "esp32h4"])
        self.chip_combo.setCurrentText(self.parent.settings.data.get('chip_type', 'auto'))
        form.addRow("Default chip type:", self.chip_combo)

        self.erase_check = QCheckBox()
        self.erase_check.setChecked(self.parent.settings.data.get('erase_before_flash', False))
        form.addRow("Erase before flash:", self.erase_check)

        self.ota_check = QCheckBox()
        self.ota_check.setChecked(self.parent.settings.data.get('ota_mode', False))
        form.addRow("OTA mode by default:", self.ota_check)

        self.backup_check = QCheckBox()
        self.backup_check.setChecked(self.parent.settings.data.get('backup_before_flash', True))
        form.addRow("Backup before flash:", self.backup_check)

        self.backup_size_spin = QSpinBox()
        self.backup_size_spin.setRange(1024, 16777216)
        self.backup_size_spin.setValue(self.parent.settings.data.get('backup_size', 4194304))
        form.addRow("Backup size (bytes):", self.backup_size_spin)

        self.serial_baud_combo = QComboBox()
        self.serial_baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.serial_baud_combo.setCurrentText(str(self.parent.settings.data.get('serial_baudrate', 115200)))
        form.addRow("Default serial baudrate:", self.serial_baud_combo)

        fw_layout = QHBoxLayout()
        self.firmware_dir_edit = QLineEdit(self.parent.settings.data.get('firmware_dir', FIRMWARE_DIR))
        fw_layout.addWidget(self.firmware_dir_edit)
        fw_btn = QPushButton("Browse")
        fw_btn.clicked.connect(self.browse_firmware_dir)
        fw_layout.addWidget(fw_btn)
        form.addRow("Firmware folder:", fw_layout)

        bk_layout = QHBoxLayout()
        self.backup_dir_edit = QLineEdit(self.parent.settings.data.get('backup_dir', BACKUP_DIR))
        bk_layout.addWidget(self.backup_dir_edit)
        bk_btn = QPushButton("Browse")
        bk_btn.clicked.connect(self.browse_backup_dir)
        bk_layout.addWidget(bk_btn)
        form.addRow("Backup folder:", bk_layout)

        self.auto_detect_check = QCheckBox()
        self.auto_detect_check.setChecked(self.parent.settings.data.get('auto_detect_on_start', True))
        form.addRow("Auto detect on start:", self.auto_detect_check)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        reset_btn = QPushButton("↩️ Restore defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def browse_firmware_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select firmware folder", self.firmware_dir_edit.text())
        if dir_path:
            self.firmware_dir_edit.setText(dir_path)

    def browse_backup_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select backup folder", self.backup_dir_edit.text())
        if dir_path:
            self.backup_dir_edit.setText(dir_path)

    def save_settings(self):
        self.parent.settings.data['baudrate'] = self.baudrate_spin.value()
        self.parent.settings.data['flash_address'] = self.address_edit.text()
        self.parent.settings.data['chip_type'] = self.chip_combo.currentText()
        self.parent.settings.data['erase_before_flash'] = self.erase_check.isChecked()
        self.parent.settings.data['ota_mode'] = self.ota_check.isChecked()
        self.parent.settings.data['backup_before_flash'] = self.backup_check.isChecked()
        self.parent.settings.data['backup_size'] = self.backup_size_spin.value()
        self.parent.settings.data['serial_baudrate'] = int(self.serial_baud_combo.currentText())
        self.parent.settings.data['firmware_dir'] = self.firmware_dir_edit.text()
        self.parent.settings.data['backup_dir'] = self.backup_dir_edit.text()
        self.parent.settings.data['auto_detect_on_start'] = self.auto_detect_check.isChecked()
        self.parent.settings.save()
        QMessageBox.information(self, "Settings", "Settings saved.")

    def reset_defaults(self):
        self.parent.settings.data = self.parent.settings.defaults()
        self.baudrate_spin.setValue(self.parent.settings.data['baudrate'])
        self.address_edit.setText(self.parent.settings.data['flash_address'])
        self.chip_combo.setCurrentText(self.parent.settings.data['chip_type'])
        self.erase_check.setChecked(self.parent.settings.data['erase_before_flash'])
        self.ota_check.setChecked(self.parent.settings.data['ota_mode'])
        self.backup_check.setChecked(self.parent.settings.data['backup_before_flash'])
        self.backup_size_spin.setValue(self.parent.settings.data['backup_size'])
        self.serial_baud_combo.setCurrentText(str(self.parent.settings.data['serial_baudrate']))
        self.firmware_dir_edit.setText(self.parent.settings.data['firmware_dir'])
        self.backup_dir_edit.setText(self.parent.settings.data['backup_dir'])
        self.auto_detect_check.setChecked(self.parent.settings.data['auto_detect_on_start'])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(1200, 800)

        self.settings = SettingsManager()
        self.history_manager = HistoryManager()

        self.setStyleSheet(STYLE_SHEET)

        self.create_menus()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet(f"background-color: {COLOR_DARKER}; border-right: 1px solid #3A3A4A;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)

        logo_label = QLabel(APP_NAME)
        logo_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #00B0FF; padding: 10px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        self.nav_buttons = []
        nav_items = [
            ("📊", "Dashboard"),
            ("⚡", "Flash"),
            ("💾", "Backup"),
            ("📡", "Serial"),
            ("⚙️", "Settings")
        ]
        self.sidebar_stack = QStackedWidget()

        self.dashboard_page = DashboardPage(self)
        self.flash_page = FlashPage(self)
        self.backup_page = BackupPage(self)
        self.serial_page = SerialPage(self)
        self.settings_page = SettingsPage(self)

        self.sidebar_stack.addWidget(self.dashboard_page)
        self.sidebar_stack.addWidget(self.flash_page)
        self.sidebar_stack.addWidget(self.backup_page)
        self.sidebar_stack.addWidget(self.serial_page)
        self.sidebar_stack.addWidget(self.settings_page)

        for i, (icon, text) in enumerate(nav_items):
            btn = QPushButton(f"{icon}  {text}")
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: transparent;
                    color: #CCCCCC;
                }
                QPushButton:hover {
                    background-color: #3A3A4A;
                }
                QPushButton:checked {
                    background-color: #7B2EDA;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.sidebar_stack, 1)

        self.statusBar().showMessage("Ready")

        self.nav_buttons[0].setChecked(True)

        self.anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Quit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("Tools")
        detect_action = QAction("Detect boards", self)
        detect_action.triggered.connect(lambda: self.dashboard_page.refresh_boards())
        tools_menu.addAction(detect_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def switch_page(self, index):
        self.sidebar_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def show_about(self):
        QMessageBox.about(self, "About",
                          f"<b>{APP_NAME} v{VERSION}</b><br><br>"
                          "<b>https://www.tiktok.com/@aro.x.74    /    https://github.com/ESP_Flasher</b><br><br>"
                          "Professional application for flashing firmwares on ESP chips (ESP8266, ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2, and more).<br><br>"
                          "© 2026 LTX. All rights reserved.")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QSplashScreen
    from PySide6.QtGui import QPixmap, QIcon
    from PySide6.QtCore import Qt, QTimer

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.ico"))
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(COMPANY)
    app.setOrganizationDomain(COMPANY)
    app.setApplicationVersion(VERSION)
    
    splash_pix = QPixmap("logo.png")
    splash_pix = splash_pix.scaled(
        400, 400,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()
    app.processEvents()

    window = MainWindow()

    def show_main():
        window.show()
        splash.finish(window)

    QTimer.singleShot(2000, show_main)

    sys.exit(app.exec())

# Made BY LTX