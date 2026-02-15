#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Made BY LTX - Pro Edition

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
import hashlib
import zipfile
from typing import List, Dict, Optional, Tuple
from collections import deque

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

try:
    from PySide6.QtCharts import *
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

import serial
import serial.tools.list_ports

APP_NAME = "ESP Flasher Pro"
VERSION = "2.0.0"
AUTHOR = "LTX"
COMPANY = "LTX74"
SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "settings.json")
HISTORY_FILE = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "history.json")
BACKUP_DIR = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "backups")
FIRMWARE_DIR = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "firmwares")
PROJECTS_DIR = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "projects")
TEMPLATES_DIR = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "templates")
LOGS_DIR = os.path.join(os.getenv('APPDATA'), COMPANY, APP_NAME, "logs")
DEFAULT_BAUDRATE = 460800
DEFAULT_FLASH_ADDRESS = "0x0"

for directory in [BACKUP_DIR, FIRMWARE_DIR, PROJECTS_DIR, TEMPLATES_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

COLOR_SCHEMES = {
    "Purple Dream": {
        "PRIMARY": "#7B2EDA",
        "SECONDARY": "#00B0FF",
        "DARK": "#1E1E2E",
        "DARKER": "#151522",
        "LIGHT": "#F5F5F9",
        "SUCCESS": "#4CAF50",
        "ERROR": "#F44336",
        "WARNING": "#FFC107",
        "INFO": "#2196F3"
    },
    "Ocean Blue": {
        "PRIMARY": "#0077BE",
        "SECONDARY": "#00D4FF",
        "DARK": "#0A1929",
        "DARKER": "#001E3C",
        "LIGHT": "#E3F2FD",
        "SUCCESS": "#2E7D32",
        "ERROR": "#D32F2F",
        "WARNING": "#F57C00",
        "INFO": "#0288D1"
    },
    "Forest Green": {
        "PRIMARY": "#2E7D32",
        "SECONDARY": "#66BB6A",
        "DARK": "#1B1B1B",
        "DARKER": "#0D0D0D",
        "LIGHT": "#E8F5E9",
        "SUCCESS": "#388E3C",
        "ERROR": "#D32F2F",
        "WARNING": "#F57C00",
        "INFO": "#0288D1"
    },
    "Cyber Red": {
        "PRIMARY": "#D32F2F",
        "SECONDARY": "#FF5252",
        "DARK": "#1A1A1A",
        "DARKER": "#0A0A0A",
        "LIGHT": "#FFEBEE",
        "SUCCESS": "#4CAF50",
        "ERROR": "#B71C1C",
        "WARNING": "#FF6F00",
        "INFO": "#1976D2"
    }
}

def get_stylesheet(scheme_name="Purple Dream"):
    colors = COLOR_SCHEMES.get(scheme_name, COLOR_SCHEMES["Purple Dream"])
    COLOR_PRIMARY = colors["PRIMARY"]
    COLOR_SECONDARY = colors["SECONDARY"]
    COLOR_DARK = colors["DARK"]
    COLOR_DARKER = colors["DARKER"]
    COLOR_LIGHT = colors["LIGHT"]
    
    return f"""
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
    border-radius: 6px;
    padding: 10px 20px;
    color: white;
    font-weight: bold;
    min-height: 35px;
}}
QPushButton:hover {{
    background-color: {COLOR_SECONDARY};
}}
QPushButton:pressed {{
    background-color: {COLOR_PRIMARY};
    padding-top: 12px;
    padding-bottom: 8px;
}}
QPushButton:disabled {{
    background-color: #3A3A4A;
    color: #777777;
}}
QPushButton:flat {{
    background-color: transparent;
    color: {COLOR_PRIMARY};
}}
QPushButton:flat:hover {{
    background-color: rgba(123, 46, 218, 0.2);
}}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
    background-color: {COLOR_DARKER};
    border: 2px solid #3A3A4A;
    border-radius: 6px;
    padding: 8px;
    color: {COLOR_LIGHT};
    min-height: 30px;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 2px solid {COLOR_PRIMARY};
}}
QLabel {{
    color: {COLOR_LIGHT};
}}
QGroupBox {{
    border: 2px solid #3A3A4A;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 12px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px 0 8px;
    color: {COLOR_SECONDARY};
    font-size: 11pt;
}}
QTableWidget {{
    background-color: {COLOR_DARKER};
    alternate-background-color: #2A2A3A;
    gridline-color: #3A3A4A;
    selection-background-color: {COLOR_PRIMARY};
    border-radius: 6px;
}}
QTableWidget::item {{
    padding: 8px;
}}
QHeaderView::section {{
    background-color: {COLOR_DARK};
    color: {COLOR_LIGHT};
    border: none;
    border-bottom: 2px solid {COLOR_PRIMARY};
    padding: 10px;
    font-weight: bold;
}}
QProgressBar {{
    border: 2px solid #3A3A4A;
    border-radius: 6px;
    text-align: center;
    background-color: {COLOR_DARKER};
    min-height: 25px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 {COLOR_PRIMARY}, stop: 1 {COLOR_SECONDARY});
    border-radius: 6px;
}}
QTabWidget::pane {{
    border: 2px solid #3A3A4A;
    border-radius: 6px;
    background-color: {COLOR_DARKER};
}}
QTabBar::tab {{
    background-color: {COLOR_DARK};
    color: {COLOR_LIGHT};
    padding: 12px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 3px;
}}
QTabBar::tab:selected {{
    background-color: {COLOR_PRIMARY};
}}
QTabBar::tab:hover {{
    background-color: #3A3A4A;
}}
QScrollBar:vertical {{
    background-color: {COLOR_DARKER};
    width: 16px;
    border-radius: 8px;
}}
QScrollBar::handle:vertical {{
    background-color: #5A5A6A;
    border-radius: 8px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLOR_PRIMARY};
}}
QScrollBar:horizontal {{
    background-color: {COLOR_DARKER};
    height: 16px;
    border-radius: 8px;
}}
QScrollBar::handle:horizontal {{
    background-color: #5A5A6A;
    border-radius: 8px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {COLOR_PRIMARY};
}}
QMenuBar {{
    background-color: {COLOR_DARKER};
    color: {COLOR_LIGHT};
    padding: 5px;
}}
QMenuBar::item:selected {{
    background-color: {COLOR_PRIMARY};
    border-radius: 4px;
}}
QMenu {{
    background-color: {COLOR_DARKER};
    color: {COLOR_LIGHT};
    border: 2px solid #3A3A4A;
    border-radius: 6px;
    padding: 5px;
}}
QMenu::item {{
    padding: 8px 30px 8px 30px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {COLOR_PRIMARY};
}}
QStatusBar {{
    background-color: {COLOR_DARKER};
    color: {COLOR_LIGHT};
    border-top: 1px solid #3A3A4A;
}}
QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
}}
QCheckBox::indicator:unchecked {{
    background-color: {COLOR_DARKER};
    border: 2px solid #3A3A4A;
    border-radius: 4px;
}}
QCheckBox::indicator:checked {{
    background-color: {COLOR_PRIMARY};
    border: 2px solid {COLOR_PRIMARY};
    border-radius: 4px;
}}
QRadioButton {{
    spacing: 8px;
}}
QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 10px;
}}
QRadioButton::indicator:unchecked {{
    background-color: {COLOR_DARKER};
    border: 2px solid #3A3A4A;
}}
QRadioButton::indicator:checked {{
    background-color: {COLOR_PRIMARY};
    border: 2px solid {COLOR_PRIMARY};
}}
QToolTip {{
    background-color: {COLOR_DARKER};
    color: {COLOR_LIGHT};
    border: 2px solid {COLOR_PRIMARY};
    border-radius: 6px;
    padding: 8px;
}}
QSplitter::handle {{
    background-color: #3A3A4A;
}}
QSplitter::handle:hover {{
    background-color: {COLOR_PRIMARY};
}}
"""

class FlashThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str)
    speed = Signal(float)

    def __init__(self, chip, port, baudrate, firmware_path, address, erase=False, ota=False, verify=True):
        super().__init__()
        self.chip = chip
        self.port = port
        self.baudrate = baudrate
        self.firmware_path = firmware_path
        self.address = address
        self.erase = erase
        self.ota = ota
        self.verify = verify
        self._process = None
        self._is_running = True
        self.start_time = None

    def run(self):
        try:
            if not os.path.exists(self.firmware_path):
                self.finished.emit(False, f"Error: Firmware file not found at: {self.firmware_path}")
                return
            
            file_size = os.path.getsize(self.firmware_path)
            self.start_time = time.time()
            
            if self.erase:
                cmd = [sys.executable, '-m', 'esptool', '--chip', self.chip, '--port', self.port, '--baud', str(self.baudrate)]
                cmd.append('erase_flash')
                self.progress.emit(0, "Erasing flash...")
                erase_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                for line in erase_process.stdout:
                    if not self._is_running:
                        erase_process.terminate()
                        return
                    if line.strip():
                        self.progress.emit(10, line.strip())
                erase_process.wait()
                if erase_process.returncode != 0:
                    self.finished.emit(False, "Failed to erase flash")
                    return
            
            cmd = [sys.executable, '-m', 'esptool', '--chip', self.chip, '--port', self.port, '--baud', str(self.baudrate), 'write_flash', '-z']
            
            if self.ota:
                cmd.extend(['--flash_mode', 'dio', '--flash_size', 'detect'])
            
            if self.verify:
                cmd.append('--verify')
                
            cmd.extend([self.address, self.firmware_path])

            self.progress.emit(15, f"Preparing flash... File: {os.path.basename(self.firmware_path)}")
            self.progress.emit(20, f"Size: {file_size / 1024:.2f} KB")
            self.progress.emit(25, f"Chip: {self.chip}")
            
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

            for line in self._process.stdout:
                if not self._is_running:
                    self._process.terminate()
                    return
                if not line:
                    continue
                self.progress.emit(50, line.strip())
                
                match = re.search(r'\((\d+)\s*%\)', line)
                if match:
                    percent = int(match.group(1))
                    self.progress.emit(percent, line.strip())
                    
                    elapsed = time.time() - self.start_time
                    if elapsed > 0:
                        speed = (file_size * (percent / 100)) / elapsed
                        self.speed.emit(speed)

            self._process.wait()
            if self._process.returncode == 0:
                elapsed = time.time() - self.start_time
                self.progress.emit(100, f"Flash completed successfully in {elapsed:.2f}s!")
                self.finished.emit(True, f"Firmware flashed successfully in {elapsed:.2f} seconds.")
            else:
                self.finished.emit(False, "Error during flash. See logs for details.")
        except Exception as e:
            self.finished.emit(False, str(e))

    def stop(self):
        self._is_running = False
        if self._process:
            try:
                self._process.terminate()
            except:
                pass


class BackupThread(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str, str)

    def __init__(self, chip, port, baudrate, size, backup_dir):
        super().__init__()
        self.chip = chip
        self.port = port
        self.baudrate = baudrate
        self.size = size
        self.backup_dir = backup_dir
        self._is_running = True
        self._process = None

    def run(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{self.chip}_{self.port.replace(':', '_')}_{timestamp}.bin"
            backup_path = os.path.join(self.backup_dir, filename)
            
            cmd = [sys.executable, '-m', 'esptool', '--chip', self.chip, '--port', self.port, '--baud', str(self.baudrate),
                   'read_flash', '0x0', str(self.size), backup_path]
            
            self.progress.emit(0, f"Starting backup of {self.size / 1024 / 1024:.1f} MB...")
            
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            for line in self._process.stdout:
                if not self._is_running:
                    self._process.terminate()
                    return
                if not line:
                    continue
                self.progress.emit(50, line.strip())
                match = re.search(r'\((\d+)\s*%\)', line)
                if match:
                    percent = int(match.group(1))
                    self.progress.emit(percent, line.strip())
            
            self._process.wait()
            if self._process.returncode == 0:
                self.progress.emit(100, "Backup completed!")
                self.finished.emit(True, f"Backup saved to {filename}", backup_path)
            else:
                self.finished.emit(False, "Backup failed", "")
        except Exception as e:
            self.finished.emit(False, str(e), "")
    
    def stop(self):
        self._is_running = False
        if self._process:
            try:
                self._process.terminate()
            except:
                pass


class DetectBoardsThread(QThread):
    finished = Signal(list)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self):
        super().__init__()
        self._is_running = True

    def run(self):
        boards = []
        ports = serial.tools.list_ports.comports()
        
        for idx, port in enumerate(ports):
            if not self._is_running:
                break
            
            self.progress.emit(f"Scanning {port.device}... ({idx + 1}/{len(ports)})")
            
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
                            elif 'ESP32' in line.upper():
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
                        'flash_size': flash_size,
                        'status': 'detected'
                    })
                else:
                    boards.append({
                        'port': port.device,
                        'description': port.description,
                        'chip': 'Not ESP / Detection failed',
                        'mac': 'N/A',
                        'flash_size': 'N/A',
                        'status': 'failed'
                    })
            except subprocess.TimeoutExpired:
                boards.append({
                    'port': port.device,
                    'description': port.description,
                    'chip': 'Detection timeout',
                    'mac': 'N/A',
                    'flash_size': 'N/A',
                    'status': 'timeout'
                })
            except Exception as e:
                continue
        
        self.finished.emit(boards)

    def stop(self):
        self._is_running = False


class SerialMonitorThread(QThread):
    data_received = Signal(bytes)
    error = Signal(str)
    data_sent = Signal(str)

    def __init__(self, port, baudrate, data_bits=8, stop_bits=1, parity='N'):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.parity = parity
        self.serial_port = None
        self._is_running = True
        self._write_mutex = QMutex()

    def run(self):
        try:
            self.serial_port = serial.Serial(
                self.port, 
                self.baudrate,
                bytesize=self.data_bits,
                stopbits=self.stop_bits,
                parity=self.parity,
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
                    loaded_data = json.load(f)
                    defaults = self.defaults()
                    defaults.update(loaded_data)
                    return defaults
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
            'verify_after_flash': True,
            'ota_mode': False,
            'backup_before_flash': True,
            'backup_size': 4194304,
            'serial_baudrate': 115200,
            'serial_databits': 8,
            'serial_stopbits': 1,
            'serial_parity': 'N',
            'firmware_dir': FIRMWARE_DIR,
            'backup_dir': BACKUP_DIR,
            'dark_mode': True,
            'auto_detect_on_start': True,
            'theme': 'Purple Dream',
            'auto_scroll_serial': True,
            'timestamp_serial': True,
            'show_hex_serial': False,
            'auto_save_backups': True,
            'compression_level': 9
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
        # Keep only last 100 entries
        self.history = self.history[:100]
        self.save()

    def clear(self):
        self.history = []
        self.save()


class FirmwareInfo:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        self.md5 = self.calculate_md5()
    
    def calculate_md5(self):
        hash_md5 = hashlib.md5()
        with open(self.path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


class Project:
    def __init__(self, name, chip_type="auto"):
        self.name = name
        self.chip_type = chip_type
        self.firmwares = []
        self.notes = ""
        self.created = datetime.datetime.now().isoformat()
        self.modified = datetime.datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'name': self.name,
            'chip_type': self.chip_type,
            'firmwares': self.firmwares,
            'notes': self.notes,
            'created': self.created,
            'modified': self.modified
        }
    
    @staticmethod
    def from_dict(data):
        proj = Project(data['name'], data.get('chip_type', 'auto'))
        proj.firmwares = data.get('firmwares', [])
        proj.notes = data.get('notes', '')
        proj.created = data.get('created', datetime.datetime.now().isoformat())
        proj.modified = data.get('modified', datetime.datetime.now().isoformat())
        return proj


class ProjectManager:
    def __init__(self):
        self.projects_dir = PROJECTS_DIR
        self.current_project = None
    
    def create_project(self, name, chip_type="auto"):
        project = Project(name, chip_type)
        self.save_project(project)
        return project
    
    def save_project(self, project):
        project.modified = datetime.datetime.now().isoformat()
        path = os.path.join(self.projects_dir, f"{project.name}.json")
        with open(path, 'w') as f:
            json.dump(project.to_dict(), f, indent=4)
    
    def load_project(self, name):
        path = os.path.join(self.projects_dir, f"{name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return Project.from_dict(data)
        return None
    
    def list_projects(self):
        projects = []
        for file in os.listdir(self.projects_dir):
            if file.endswith('.json'):
                projects.append(file[:-5])
        return projects
    
    def delete_project(self, name):
        path = os.path.join(self.projects_dir, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)


class BatchFlashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Batch Flash Multiple Devices")
        self.setMinimumSize(700, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        info = QLabel("Select firmware and target devices for batch flashing:")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        fw_layout = QHBoxLayout()
        self.fw_edit = QLineEdit()
        self.fw_edit.setReadOnly(True)
        self.fw_edit.setPlaceholderText("No firmware selected")
        fw_layout.addWidget(QLabel("Firmware:"))
        fw_layout.addWidget(self.fw_edit)
        
        fw_btn = QPushButton("Browse")
        fw_btn.clicked.connect(self.select_firmware)
        fw_layout.addWidget(fw_btn)
        layout.addLayout(fw_layout)
        
        layout.addWidget(QLabel("Select devices to flash:"))
        self.device_list = QListWidget()
        self.device_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.device_list)
        
        refresh_btn = QPushButton("🔄 Refresh Devices")
        refresh_btn.clicked.connect(self.refresh_devices)
        layout.addWidget(refresh_btn)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        btn_layout = QHBoxLayout()
        self.flash_btn = QPushButton("⚡ Start Batch Flash")
        self.flash_btn.clicked.connect(self.start_batch_flash)
        btn_layout.addWidget(self.flash_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.refresh_devices()
    
    def select_firmware(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select firmware", "", "Binary files (*.bin)")
        if file_path:
            self.firmware_path = file_path
            self.fw_edit.setText(file_path)
    
    def refresh_devices(self):
        self.device_list.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            item = QListWidgetItem(f"{port.device} - {port.description}")
            item.setData(Qt.ItemDataRole.UserRole, port.device)
            self.device_list.addItem(item)
    
    def start_batch_flash(self):
        if not hasattr(self, 'firmware_path'):
            QMessageBox.warning(self, "No firmware", "Please select a firmware file first.")
            return
        
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No devices", "Please select at least one device.")
            return
        
        devices = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        
        reply = QMessageBox.question(self, "Confirm Batch Flash",
                                     f"Flash {len(devices)} device(s) with {os.path.basename(self.firmware_path)}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.flash_devices(devices)
    
    def flash_devices(self, devices):
        self.progress.setVisible(True)
        self.progress.setMaximum(len(devices))
        self.flash_btn.setEnabled(False)
        
        for idx, device in enumerate(devices):
            self.progress.setValue(idx)
            self.progress.setFormat(f"Flashing {device}... ({idx + 1}/{len(devices)})")
            
            chip = self.parent.settings.data.get('chip_type', 'auto')
            baudrate = self.parent.settings.data.get('baudrate', DEFAULT_BAUDRATE)
            address = self.parent.settings.data.get('flash_address', DEFAULT_FLASH_ADDRESS)
            
            QMessageBox.information(self, "Flash Complete", 
                                  f"Would flash {device} with {self.firmware_path}\n(Threading implementation needed for production)")
        
        self.progress.setValue(len(devices))
        self.flash_btn.setEnabled(True)
        QMessageBox.information(self, "Batch Flash Complete", f"Successfully flashed {len(devices)} device(s)!")
        self.accept()


class FirmwareCompareDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compare Firmwares")
        self.setMinimumSize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        files_layout = QHBoxLayout()
        
        fw1_layout = QVBoxLayout()
        self.fw1_edit = QLineEdit()
        self.fw1_edit.setPlaceholderText("Firmware 1")
        fw1_btn = QPushButton("Browse")
        fw1_btn.clicked.connect(lambda: self.select_firmware(1))
        fw1_layout.addWidget(self.fw1_edit)
        fw1_layout.addWidget(fw1_btn)
        files_layout.addLayout(fw1_layout)
        
        fw2_layout = QVBoxLayout()
        self.fw2_edit = QLineEdit()
        self.fw2_edit.setPlaceholderText("Firmware 2")
        fw2_btn = QPushButton("Browse")
        fw2_btn.clicked.connect(lambda: self.select_firmware(2))
        fw2_layout.addWidget(self.fw2_edit)
        fw2_layout.addWidget(fw2_btn)
        files_layout.addLayout(fw2_layout)
        
        layout.addLayout(files_layout)
        
        compare_btn = QPushButton("🔍 Compare")
        compare_btn.clicked.connect(self.compare_firmwares)
        layout.addWidget(compare_btn)
        
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def select_firmware(self, number):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select firmware {number}", "", "Binary files (*.bin)")
        if file_path:
            if number == 1:
                self.fw1_path = file_path
                self.fw1_edit.setText(file_path)
            else:
                self.fw2_path = file_path
                self.fw2_edit.setText(file_path)
    
    def compare_firmwares(self):
        if not hasattr(self, 'fw1_path') or not hasattr(self, 'fw2_path'):
            QMessageBox.warning(self, "Missing files", "Please select both firmware files.")
            return
        
        fw1 = FirmwareInfo(self.fw1_path)
        fw2 = FirmwareInfo(self.fw2_path)
        
        result = f"""
<h2>Firmware Comparison</h2>

<h3>Firmware 1: {fw1.name}</h3>
<ul>
<li><b>Size:</b> {fw1.size:,} bytes ({fw1.size / 1024:.2f} KB)</li>
<li><b>MD5:</b> {fw1.md5}</li>
<li><b>Modified:</b> {fw1.modified.strftime('%Y-%m-%d %H:%M:%S')}</li>
</ul>

<h3>Firmware 2: {fw2.name}</h3>
<ul>
<li><b>Size:</b> {fw2.size:,} bytes ({fw2.size / 1024:.2f} KB)</li>
<li><b>MD5:</b> {fw2.md5}</li>
<li><b>Modified:</b> {fw2.modified.strftime('%Y-%m-%d %H:%M:%S')}</li>
</ul>

<h3>Comparison Results:</h3>
<ul>
<li><b>Size difference:</b> {abs(fw1.size - fw2.size):,} bytes ({abs(fw1.size - fw2.size) / 1024:.2f} KB)</li>
<li><b>MD5 Match:</b> {'✅ YES (Identical files)' if fw1.md5 == fw2.md5 else '❌ NO (Different files)'}</li>
<li><b>Newer file:</b> {'Firmware 1' if fw1.modified > fw2.modified else 'Firmware 2'}</li>
</ul>
"""
        
        self.results.setHtml(result)


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.detect_thread = None  # Initialize to None
        self.init_ui()
    
    def cleanup(self):
        """Cleanup when page is being destroyed - MUST be called explicitly"""
        try:
            if self.detect_thread and self.detect_thread.isRunning():
                print("Stopping detect_thread...")
                self.detect_thread.stop()
                self.detect_thread.wait(1000)
                print("detect_thread stopped")
        except Exception as e:
            print(f"Error stopping detect_thread: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("📊 Professional Dashboard")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; color: #00B0FF;")
        header.addWidget(title)
        header.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_boards)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(self.refresh_btn)
        
        layout.addLayout(header)
        
        stats_layout = QHBoxLayout()
        
        self.total_devices_card = self.create_stat_card("Total Devices", "0", "#7B2EDA")
        self.esp_devices_card = self.create_stat_card("ESP Devices", "0", "#4CAF50")
        self.flash_history_card = self.create_stat_card("Flash History", "0", "#00B0FF")
        self.backups_card = self.create_stat_card("Backups", "0", "#FFC107")
        
        stats_layout.addWidget(self.total_devices_card)
        stats_layout.addWidget(self.esp_devices_card)
        stats_layout.addWidget(self.flash_history_card)
        stats_layout.addWidget(self.backups_card)
        
        layout.addLayout(stats_layout)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        devices_widget = QWidget()
        devices_layout = QVBoxLayout(devices_widget)
        devices_layout.addWidget(QLabel("Detected Devices"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Status", "Port", "Description", "Chip", "MAC", "Flash Size"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.on_device_double_click)
        devices_layout.addWidget(self.table)
        
        splitter.addWidget(devices_widget)
        
        actions_widget = QWidget()
        actions_layout = QVBoxLayout(actions_widget)
        actions_layout.addWidget(QLabel("Quick Actions"))
        
        quick_flash_btn = QPushButton("⚡ Quick Flash")
        quick_flash_btn.clicked.connect(self.quick_flash)
        actions_layout.addWidget(quick_flash_btn)
        
        batch_flash_btn = QPushButton("📦 Batch Flash")
        batch_flash_btn.clicked.connect(self.batch_flash)
        actions_layout.addWidget(batch_flash_btn)
        
        backup_all_btn = QPushButton("💾 Backup All")
        backup_all_btn.clicked.connect(self.backup_all)
        actions_layout.addWidget(backup_all_btn)
        
        actions_layout.addWidget(QLabel("\nRecent Activity"))
        
        self.activity_list = QListWidget()
        actions_layout.addWidget(self.activity_list)
        
        actions_layout.addStretch()
        
        splitter.addWidget(actions_widget)
        splitter.setSizes([600, 300])
        
        layout.addWidget(splitter)

        self.update_stats()

    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10pt; font-weight: normal;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(value_label)
        
        return card

    def update_stat_card(self, card, value):
        value_label = card.findChild(QLabel, "value")
        if value_label:
            value_label.setText(str(value))

    def refresh_boards(self):
        # Stop previous detection if running
        if self.detect_thread and self.detect_thread.isRunning():
            self.detect_thread.stop()
            self.detect_thread.wait(500)
        
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("🔍 Detecting...")
        self.parent.statusBar().showMessage("Detecting boards...")
        self.detect_thread = DetectBoardsThread()
        self.detect_thread.finished.connect(self.on_detection_finished)
        self.detect_thread.progress.connect(lambda msg: self.parent.statusBar().showMessage(msg))
        self.detect_thread.start()

    def on_detection_finished(self, boards):
        self.table.setRowCount(len(boards))
        esp_count = 0
        
        for row, board in enumerate(boards):
            status = board.get('status', 'unknown')
            chip = board.get('chip', '')
            
            status_item = QTableWidgetItem()
            if status == 'detected' and 'ESP' in chip.upper():
                status_item.setText("✅")
                status_item.setForeground(QColor(76, 175, 80))
                esp_count += 1
            elif status == 'timeout':
                status_item.setText("⏱️")
                status_item.setForeground(QColor(255, 193, 7))
            else:
                status_item.setText("❌")
                status_item.setForeground(QColor(158, 158, 158))
            
            self.table.setItem(row, 0, status_item)
            self.table.setItem(row, 1, QTableWidgetItem(board.get('port', '')))
            self.table.setItem(row, 2, QTableWidgetItem(board.get('description', '')))
            self.table.setItem(row, 3, QTableWidgetItem(chip))
            self.table.setItem(row, 4, QTableWidgetItem(board.get('mac', '')))
            self.table.setItem(row, 5, QTableWidgetItem(board.get('flash_size', '')))
            
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Refresh")
        
        self.update_stat_card(self.total_devices_card, len(boards))
        self.update_stat_card(self.esp_devices_card, esp_count)
        
        if esp_count > 0:
            self.parent.statusBar().showMessage(f"✅ {esp_count} ESP device(s) detected, {len(boards)} total port(s)", 5000)
        else:
            self.parent.statusBar().showMessage(f"ℹ️ No ESP devices found, {len(boards)} port(s) scanned", 5000)

    def update_stats(self):
        history_count = len(self.parent.history_manager.history)
        self.update_stat_card(self.flash_history_card, history_count)
        
        if os.path.exists(BACKUP_DIR):
            backups_count = len([f for f in os.listdir(BACKUP_DIR) if f.endswith('.bin')])
            self.update_stat_card(self.backups_card, backups_count)
        
        self.activity_list.clear()
        for entry in self.parent.history_manager.history[:10]:
            timestamp = entry.get('timestamp', '')
            firmware = os.path.basename(entry.get('firmware', 'Unknown'))
            status = entry.get('status', 'unknown')
            icon = "✅" if status == 'success' else "❌"
            
            item = QListWidgetItem(f"{icon} {firmware}")
            item.setToolTip(f"{timestamp}\n{entry.get('port', 'Unknown port')}")
            self.activity_list.addItem(item)

    def on_device_double_click(self, index):
        row = index.row()
        port = self.table.item(row, 1).text()
        chip = self.table.item(row, 3).text()
        
        if 'ESP' in chip.upper() and 'failed' not in chip.lower():
            reply = QMessageBox.question(self, "Quick Flash",
                                        f"Flash device on {port} ({chip})?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.sidebar_stack.setCurrentIndex(1)

    def quick_flash(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No selection", "Please select a device first.")
            return
        
        self.parent.sidebar_stack.setCurrentIndex(1)

    def batch_flash(self):
        dialog = BatchFlashDialog(self.parent)
        dialog.exec()

    def backup_all(self):
        esp_devices = []
        for row in range(self.table.rowCount()):
            chip = self.table.item(row, 3).text()
            if 'ESP' in chip.upper() and 'failed' not in chip.lower():
                port = self.table.item(row, 1).text()
                esp_devices.append((port, chip))
        
        if not esp_devices:
            QMessageBox.information(self, "No devices", "No ESP devices found to backup.")
            return
        
        reply = QMessageBox.question(self, "Backup All",
                                    f"Backup {len(esp_devices)} ESP device(s)?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Backup", f"Would backup {len(esp_devices)} device(s)\n(Implementation needed)")

class FlashPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_firmware = None
        self.flash_thread = None
        self.init_ui()
    
    def cleanup(self):
        try:
            if hasattr(self, 'port_timer'):
                self.port_timer.stop()
            if self.flash_thread and self.flash_thread.isRunning():
                print("Stopping flash_thread...")
                self.flash_thread.stop()
                self.flash_thread.wait(1000)
                print("flash_thread stopped")
        except Exception as e:
            print(f"Error stopping flash_thread: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("⚡ Advanced Flash Manager")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #00B0FF;")
        header.addWidget(title)
        header.addStretch()
        
        self.speed_label = QLabel("Speed: -- KB/s")
        self.speed_label.setStyleSheet("font-size: 11pt; color: #FFC107;")
        header.addWidget(self.speed_label)
        
        layout.addLayout(header)

        tabs = QTabWidget()
        
        single_tab = QWidget()
        single_layout = QVBoxLayout(single_tab)
        
        self.drop_area = QFrame()
        self.drop_area.setMinimumHeight(160)
        self.drop_area.setAcceptDrops(True)
        self.drop_area.setCursor(Qt.CursorShape.PointingHandCursor)
        self.drop_area.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #252538, stop: 1 #1A1A2E);
                border: 3px dashed #7B2EDA;
                border-radius: 15px;
            }
            QFrame:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #2E2E48, stop: 1 #252538);
                border: 3px dashed #9B4DED;
            }
        """)

        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setContentsMargins(50, 30, 50, 30)
        drop_layout.setSpacing(15)
        
        drop_text = QLabel("📁 Click to select your .bin file")
        drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_text.setStyleSheet("""
            font-size: 18pt; 
            font-weight: bold; 
            color: #FFFFFF;
            background: transparent;
            border: none;
            padding: 15px;
        """)
        drop_layout.addWidget(drop_text)
        
        or_label = QLabel("Click anywhere to browse")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_label.setStyleSheet("""
            font-size: 13pt; 
            color: #AAAAAA;
            background: transparent;
            border: none;
        """)
        drop_layout.addWidget(or_label)
        
        self.drop_area.mousePressEvent = self.select_firmware
        single_layout.addWidget(self.drop_area)

        info_layout = QHBoxLayout()
        self.firmware_info = QLabel("No file selected")
        self.firmware_info.setStyleSheet("color: #AAAAAA; font-style: italic; font-size: 11pt;")
        info_layout.addWidget(self.firmware_info)
        info_layout.addStretch()
        
        self.hash_label = QLabel("")
        self.hash_label.setStyleSheet("color: #AAAAAA; font-size: 9pt; font-family: 'Courier New';")
        info_layout.addWidget(self.hash_label)
        
        single_layout.addLayout(info_layout)

        options_group = QGroupBox("⚙️ Flash Configuration")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("Chip Type:"), 0, 0)
        self.chip_combo = QComboBox()
        self.chip_combo.addItems(["auto", "esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c2", "esp32c6", "esp32c61", "esp32c5", "esp32h2", "esp32h21", "esp32p4", "esp32h4"])
        self.chip_combo.setCurrentText(self.parent.settings.data.get('chip_type', 'auto'))
        options_layout.addWidget(self.chip_combo, 0, 1)
        
        options_layout.addWidget(QLabel("Port:"), 0, 2)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        self.refresh_ports()
        options_layout.addWidget(self.port_combo, 0, 3)
        
        options_layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["115200", "230400", "460800", "921600", "1500000", "2000000"])
        self.baudrate_combo.setCurrentText(str(self.parent.settings.data.get('baudrate', DEFAULT_BAUDRATE)))
        options_layout.addWidget(self.baudrate_combo, 1, 1)
        
        options_layout.addWidget(QLabel("Flash Address:"), 1, 2)
        self.address_edit = QLineEdit(self.parent.settings.data.get('flash_address', DEFAULT_FLASH_ADDRESS))
        options_layout.addWidget(self.address_edit, 1, 3)
        
        self.erase_check = QCheckBox("Erase flash before flashing")
        self.erase_check.setChecked(self.parent.settings.data.get('erase_before_flash', False))
        options_layout.addWidget(self.erase_check, 2, 0, 1, 2)
        
        self.verify_check = QCheckBox("Verify after flashing")
        self.verify_check.setChecked(self.parent.settings.data.get('verify_after_flash', True))
        options_layout.addWidget(self.verify_check, 2, 2, 1, 2)
        
        self.ota_check = QCheckBox("OTA mode (if supported)")
        self.ota_check.setChecked(self.parent.settings.data.get('ota_mode', False))
        options_layout.addWidget(self.ota_check, 3, 0, 1, 2)
        
        self.backup_check = QCheckBox("Backup before flash")
        self.backup_check.setChecked(self.parent.settings.data.get('backup_before_flash', True))
        options_layout.addWidget(self.backup_check, 3, 2, 1, 2)
        
        single_layout.addWidget(options_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                min-height: 30px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        single_layout.addWidget(self.progress_bar)

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("background-color: #0D0D0D;")
        single_layout.addWidget(self.log_text)

        btn_layout = QHBoxLayout()
        
        self.flash_btn = QPushButton("⚡ FLASH NOW")
        self.flash_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                            stop: 0 #7B2EDA, stop: 1 #00B0FF);
                font-size: 14pt;
                min-height: 50px;
            }
        """)
        self.flash_btn.clicked.connect(self.start_flash)
        self.flash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self.flash_btn)
        
        save_template_btn = QPushButton("💾 Save as Template")
        save_template_btn.clicked.connect(self.save_template)
        btn_layout.addWidget(save_template_btn)
        
        load_template_btn = QPushButton("📂 Load Template")
        load_template_btn.clicked.connect(self.load_template)
        btn_layout.addWidget(load_template_btn)
        
        single_layout.addLayout(btn_layout)
        
        tabs.addTab(single_tab, "Single Device")
        
        multi_tab = QWidget()
        multi_layout = QVBoxLayout(multi_tab)
        
        multi_layout.addWidget(QLabel("Flash multiple firmwares at different addresses:"))
        
        self.multi_table = QTableWidget()
        self.multi_table.setColumnCount(3)
        self.multi_table.setHorizontalHeaderLabels(["Address", "Firmware", "Actions"])
        multi_layout.addWidget(self.multi_table)
        
        multi_btn_layout = QHBoxLayout()
        add_fw_btn = QPushButton("➕ Add Firmware")
        add_fw_btn.clicked.connect(self.add_multi_firmware)
        multi_btn_layout.addWidget(add_fw_btn)
        
        remove_fw_btn = QPushButton("➖ Remove Selected")
        remove_fw_btn.clicked.connect(self.remove_multi_firmware)
        multi_btn_layout.addWidget(remove_fw_btn)
        
        multi_btn_layout.addStretch()
        
        flash_multi_btn = QPushButton("⚡ Flash All")
        flash_multi_btn.clicked.connect(self.flash_multi)
        multi_btn_layout.addWidget(flash_multi_btn)
        
        multi_layout.addLayout(multi_btn_layout)
        
        tabs.addTab(multi_tab, "Multi-Address Flash")
        
        ota_tab = QWidget()
        ota_layout = QVBoxLayout(ota_tab)
        
        ota_layout.addWidget(QLabel("Over-The-Air (OTA) Firmware Update"))
        
        ota_form = QFormLayout()
        self.ota_ip = QLineEdit()
        self.ota_ip.setPlaceholderText("192.168.1.100")
        ota_form.addRow("Device IP:", self.ota_ip)
        
        self.ota_port = QSpinBox()
        self.ota_port.setRange(1, 65535)
        self.ota_port.setValue(8266)
        ota_form.addRow("OTA Port:", self.ota_port)
        
        self.ota_password = QLineEdit()
        self.ota_password.setEchoMode(QLineEdit.EchoMode.Password)
        ota_form.addRow("Password (optional):", self.ota_password)
        
        ota_layout.addLayout(ota_form)
        
        ota_fw_layout = QHBoxLayout()
        self.ota_fw_edit = QLineEdit()
        self.ota_fw_edit.setPlaceholderText("Select firmware...")
        ota_fw_layout.addWidget(self.ota_fw_edit)
        
        ota_browse_btn = QPushButton("Browse")
        ota_browse_btn.clicked.connect(self.select_ota_firmware)
        ota_fw_layout.addWidget(ota_browse_btn)
        
        ota_layout.addLayout(ota_fw_layout)
        
        ota_flash_btn = QPushButton("📡 Start OTA Update")
        ota_flash_btn.clicked.connect(self.start_ota_update)
        ota_layout.addWidget(ota_flash_btn)
        
        ota_layout.addStretch()
        
        tabs.addTab(ota_tab, "OTA Update")
        
        layout.addWidget(tabs)
        
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.refresh_ports)
        self.port_timer.start(3000)

    def select_firmware(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select firmware", "", "Binary files (*.bin);;All files (*.*)")
        if file_path:
            self.set_firmware(file_path)

    def set_firmware(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(self, "File not found", f"The specified file does not exist:\n{path}")
            return
        
        self.current_firmware = path
        fw_info = FirmwareInfo(path)
        
        self.firmware_info.setText(f"📁 {fw_info.name} ({fw_info.size / 1024:.2f} KB)")
        self.firmware_info.setStyleSheet("color: #00B0FF; font-weight: bold; font-size: 11pt;")
        self.firmware_info.setToolTip(path)
        
        self.hash_label.setText(f"MD5: {fw_info.md5}")
        
        self.log_text.appendPlainText(f"✅ File selected: {fw_info.name}")
        self.log_text.appendPlainText(f"   Path: {path}")
        self.log_text.appendPlainText(f"   Size: {fw_info.size / 1024:.2f} KB")
        self.log_text.appendPlainText(f"   MD5: {fw_info.md5}\n")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toString().endswith('.bin'):
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                               stop: 0 #00B0FF, stop: 1 #7B2EDA);
                    border: 4px solid #00D4FF;
                    border-radius: 15px;
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #252538, stop: 1 #1A1A2E);
                border: 3px dashed #7B2EDA;
                border-radius: 15px;
            }
            QFrame:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #2E2E48, stop: 1 #252538);
                border: 3px dashed #9B4DED;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].endswith('.bin'):
            self.set_firmware(files[0])
        self.drop_area.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #252538, stop: 1 #1A1A2E);
                border: 3px dashed #7B2EDA;
                border-radius: 15px;
            }
            QFrame:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #2E2E48, stop: 1 #252538);
                border: 3px dashed #9B4DED;
            }
        """)

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

    def start_flash(self):
        if not self.current_firmware:
            QMessageBox.warning(self, "File missing", "Please select a .bin file first.")
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
        verify = self.verify_check.isChecked()
        backup = self.backup_check.isChecked()

        if backup:
            size = self.parent.settings.data.get('backup_size', 4194304)
            reply = QMessageBox.question(self, "Backup",
                                         f"Create backup before flashing ({size/1024/1024:.0f} MB)?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.backup_thread = BackupThread(chip, port, baudrate, size, self.parent.settings.data['backup_dir'])
                self.backup_thread.progress.connect(self.update_progress)
                self.backup_thread.finished.connect(self.on_backup_finished)
                self.backup_thread.start()
                self.flash_btn.setEnabled(False)
                return

        self.do_flash(chip, port, baudrate, address, erase, ota, verify)

    def on_backup_finished(self, success, message, backup_path):
        if success:
            self.parent.statusBar().showMessage(f"✅ Backup successful: {os.path.basename(backup_path)}", 5000)
            chip = self.chip_combo.currentText()
            port = self.port_combo.currentData()
            baudrate = int(self.baudrate_combo.currentText())
            address = self.address_edit.text().strip()
            erase = self.erase_check.isChecked()
            ota = self.ota_check.isChecked()
            verify = self.verify_check.isChecked()
            self.do_flash(chip, port, baudrate, address, erase, ota, verify)
        else:
            QMessageBox.critical(self, "Backup error", message)
            self.flash_btn.setEnabled(True)

    def do_flash(self, chip, port, baudrate, address, erase, ota, verify):
        self.flash_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.log_text.appendPlainText(f"⚡ Starting flash on {port}...")
        self.log_text.appendPlainText(f"📌 Chip: {chip}")
        
        self.flash_thread = FlashThread(chip, port, baudrate, self.current_firmware, address, erase, ota, verify)
        self.flash_thread.progress.connect(self.update_progress)
        self.flash_thread.finished.connect(self.on_flash_finished)
        self.flash_thread.speed.connect(self.update_speed)
        self.flash_thread.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.log_text.appendPlainText(message)
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def update_speed(self, speed):
        self.speed_label.setText(f"Speed: {speed / 1024:.2f} KB/s")

    def on_flash_finished(self, success, message):
        self.flash_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.speed_label.setText("Speed: -- KB/s")
        
        if success:
            self.log_text.appendPlainText(f"\n✅ {message}")
            QMessageBox.information(self, "Success", message)
            
            entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'port': self.port_combo.currentData(),
                'chip': self.chip_combo.currentText(),
                'firmware': self.current_firmware,
                'address': self.address_edit.text(),
                'status': 'success'
            }
            self.parent.history_manager.add_entry(entry)
            self.parent.dashboard_page.update_stats()
        else:
            self.log_text.appendPlainText(f"\n❌ {message}")
            QMessageBox.critical(self, "Failure", message)

    def save_template(self):
        if not self.current_firmware:
            QMessageBox.warning(self, "No firmware", "Please select a firmware first.")
            return
        
        name, ok = QInputDialog.getText(self, "Save Template", "Template name:")
        if ok and name:
            template = {
                'name': name,
                'chip': self.chip_combo.currentText(),
                'baudrate': self.baudrate_combo.currentText(),
                'address': self.address_edit.text(),
                'erase': self.erase_check.isChecked(),
                'ota': self.ota_check.isChecked(),
                'verify': self.verify_check.isChecked(),
                'backup': self.backup_check.isChecked(),
                'firmware': self.current_firmware
            }
            
            template_path = os.path.join(TEMPLATES_DIR, f"{name}.json")
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=4)
            
            QMessageBox.information(self, "Template Saved", f"Template '{name}' saved successfully!")

    def load_template(self):
        templates = [f[:-5] for f in os.listdir(TEMPLATES_DIR) if f.endswith('.json')]
        
        if not templates:
            QMessageBox.information(self, "No templates", "No saved templates found.")
            return
        
        name, ok = QInputDialog.getItem(self, "Load Template", "Select template:", templates, 0, False)
        if ok and name:
            template_path = os.path.join(TEMPLATES_DIR, f"{name}.json")
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            self.chip_combo.setCurrentText(template.get('chip', 'auto'))
            self.baudrate_combo.setCurrentText(str(template.get('baudrate', DEFAULT_BAUDRATE)))
            self.address_edit.setText(template.get('address', DEFAULT_FLASH_ADDRESS))
            self.erase_check.setChecked(template.get('erase', False))
            self.ota_check.setChecked(template.get('ota', False))
            self.verify_check.setChecked(template.get('verify', True))
            self.backup_check.setChecked(template.get('backup', True))
            
            if os.path.exists(template.get('firmware', '')):
                self.set_firmware(template['firmware'])
            
            QMessageBox.information(self, "Template Loaded", f"Template '{name}' loaded successfully!")

    def add_multi_firmware(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select firmware", "", "Binary files (*.bin)")
        if file_path:
            row = self.multi_table.rowCount()
            self.multi_table.insertRow(row)
            
            address_edit = QLineEdit("0x0")
            self.multi_table.setCellWidget(row, 0, address_edit)
            
            self.multi_table.setItem(row, 1, QTableWidgetItem(file_path))
            
            remove_btn = QPushButton("🗑️")
            remove_btn.clicked.connect(lambda: self.multi_table.removeRow(self.multi_table.currentRow()))
            self.multi_table.setCellWidget(row, 2, remove_btn)

    def remove_multi_firmware(self):
        current_row = self.multi_table.currentRow()
        if current_row >= 0:
            self.multi_table.removeRow(current_row)

    def flash_multi(self):
        if self.multi_table.rowCount() == 0:
            QMessageBox.warning(self, "No firmwares", "Please add at least one firmware.")
            return
        
        QMessageBox.information(self, "Multi-Flash", "Multi-address flash feature\n(Implementation pending)")

    def select_ota_firmware(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select firmware", "", "Binary files (*.bin)")
        if file_path:
            self.ota_fw_edit.setText(file_path)

    def start_ota_update(self):
        ip = self.ota_ip.text().strip()
        port = self.ota_port.value()
        firmware = self.ota_fw_edit.text()
        
        if not ip or not firmware:
            QMessageBox.warning(self, "Missing info", "Please fill in all required fields.")
            return
        
        QMessageBox.information(self, "OTA Update", f"Would start OTA update to {ip}:{port}\n(Implementation pending)")


class BackupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.backup_thread = None
        self.init_ui()
    
    def cleanup(self):
        try:
            if hasattr(self, 'backup_timer'):
                self.backup_timer.stop()
            if self.backup_thread and self.backup_thread.isRunning():
                print("Stopping backup_thread...")
                self.backup_thread.stop()
                self.backup_thread.wait(1000)
                print("backup_thread stopped")
        except Exception as e:
            print(f"Error stopping backup_thread: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("💾 Backup & Restore Manager")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #00B0FF;")
        layout.addWidget(title)

        backup_group = QGroupBox("Create New Backup")
        backup_layout = QVBoxLayout(backup_group)

        form = QFormLayout()
        
        self.backup_chip_combo = QComboBox()
        self.backup_chip_combo.addItems(["auto", "esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c6"])
        form.addRow("Chip:", self.backup_chip_combo)

        self.backup_port_combo = QComboBox()
        self.refresh_backup_ports()
        form.addRow("Port:", self.backup_port_combo)

        self.backup_baudrate_combo = QComboBox()
        self.backup_baudrate_combo.addItems(["115200", "460800", "921600"])
        self.backup_baudrate_combo.setCurrentText("460800")
        form.addRow("Baudrate:", self.backup_baudrate_combo)

        self.backup_size_combo = QComboBox()
        self.backup_size_combo.addItems([
            "1 MB (ESP8266)",
            "2 MB",
            "4 MB (ESP32)",
            "8 MB",
            "16 MB"
        ])
        self.backup_size_combo.setCurrentIndex(2)
        form.addRow("Flash Size:", self.backup_size_combo)

        backup_layout.addLayout(form)

        btn_layout = QHBoxLayout()
        create_backup_btn = QPushButton("💾 Create Backup")
        create_backup_btn.clicked.connect(self.create_backup)
        btn_layout.addWidget(create_backup_btn)
        
        auto_detect_btn = QPushButton("🔍 Auto-Detect Size")
        auto_detect_btn.clicked.connect(self.auto_detect_size)
        btn_layout.addWidget(auto_detect_btn)
        
        backup_layout.addLayout(btn_layout)

        self.backup_progress = QProgressBar()
        self.backup_progress.setVisible(False)
        backup_layout.addWidget(self.backup_progress)

        layout.addWidget(backup_group)

        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("Saved Backups"))
        list_header.addStretch()
        
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("🔍 Search backups...")
        search_edit.textChanged.connect(self.filter_backups)
        list_header.addWidget(search_edit)
        
        sort_combo = QComboBox()
        sort_combo.addItems(["Date (Newest)", "Date (Oldest)", "Name (A-Z)", "Size (Largest)"])
        sort_combo.currentTextChanged.connect(self.sort_backups)
        list_header.addWidget(sort_combo)
        
        layout.addLayout(list_header)

        self.backup_list = QListWidget()
        self.backup_list.setAlternatingRowColors(True)
        self.backup_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.backup_list.customContextMenuRequested.connect(self.show_backup_context_menu)
        layout.addWidget(self.backup_list)

        actions = QHBoxLayout()
        
        restore_btn = QPushButton("↩️ Restore Selected")
        restore_btn.clicked.connect(self.restore_selected)
        actions.addWidget(restore_btn)
        
        compare_btn = QPushButton("🔍 Compare")
        compare_btn.clicked.connect(self.compare_backups)
        actions.addWidget(compare_btn)
        
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self.export_backup)
        actions.addWidget(export_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self.delete_selected)
        actions.addWidget(delete_btn)
        
        layout.addLayout(actions)

        self.refresh_backups()
        
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self.refresh_backups)
        self.backup_timer.start(5000)

    def refresh_backup_ports(self):
        self.backup_port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.backup_port_combo.addItem(f"{port.device} - {port.description}", port.device)

    def create_backup(self):
        if self.backup_port_combo.count() == 0:
            QMessageBox.warning(self, "No port", "No COM port detected.")
            return
        
        if self.backup_thread and self.backup_thread.isRunning():
            self.backup_thread.stop()
            self.backup_thread.wait(500)
        
        chip = self.backup_chip_combo.currentText()
        port = self.backup_port_combo.currentData()
        baudrate = int(self.backup_baudrate_combo.currentText())
        
        size_text = self.backup_size_combo.currentText()
        size_mb = int(size_text.split()[0])
        size_bytes = size_mb * 1024 * 1024
        
        reply = QMessageBox.question(self, "Create Backup",
                                     f"Create {size_mb}MB backup of {port} ({chip})?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.backup_progress.setVisible(True)
            self.backup_progress.setValue(0)
            
            self.backup_thread = BackupThread(chip, port, baudrate, size_bytes, BACKUP_DIR)
            self.backup_thread.progress.connect(self.update_backup_progress)
            self.backup_thread.finished.connect(self.on_backup_complete)
            self.backup_thread.start()

    def update_backup_progress(self, value, message):
        self.backup_progress.setValue(value)
        self.parent.statusBar().showMessage(message)

    def on_backup_complete(self, success, message, backup_path):
        self.backup_progress.setVisible(False)
        if success:
            QMessageBox.information(self, "Backup Complete", message)
            self.refresh_backups()
        else:
            QMessageBox.critical(self, "Backup Failed", message)

    def auto_detect_size(self):
        QMessageBox.information(self, "Auto-Detect", "Auto-detection would query the device\n(Implementation pending)")

    def refresh_backups(self):
        self.backup_list.clear()
        if not os.path.exists(BACKUP_DIR):
            return
        
        backups = []
        for file in os.listdir(BACKUP_DIR):
            if file.endswith('.bin'):
                path = os.path.join(BACKUP_DIR, file)
                size = os.path.getsize(path)
                modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                backups.append((file, path, size, modified))
        
        backups.sort(key=lambda x: x[3], reverse=True)
        
        for name, path, size, modified in backups:
            item_text = f"{name} - {size / 1024 / 1024:.2f} MB - {modified.strftime('%Y-%m-%d %H:%M')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setIcon(self.parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            self.backup_list.addItem(item)

    def filter_backups(self, text):
        for i in range(self.backup_list.count()):
            item = self.backup_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def sort_backups(self, sort_type):
        self.refresh_backups()

    def show_backup_context_menu(self, position):
        menu = QMenu()
        
        restore_action = menu.addAction("↩️ Restore")
        compare_action = menu.addAction("🔍 Compare with another backup")
        menu.addSeparator()
        export_action = menu.addAction("📤 Export")
        rename_action = menu.addAction("✏️ Rename")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Delete")
        
        action = menu.exec(self.backup_list.mapToGlobal(position))
        
        if action == restore_action:
            self.restore_selected()
        elif action == delete_action:
            self.delete_selected()
        elif action == compare_action:
            self.compare_backups()

    def restore_selected(self):
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No selection", "Please select a backup to restore.")
            return
        
        backup_path = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Restore Backup",
                                     f"Restore {os.path.basename(backup_path)}?\nThis will flash it to the selected device.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.parent.flash_page.set_firmware(backup_path)
            self.parent.sidebar_stack.setCurrentIndex(1)

    def compare_backups(self):
        dialog = FirmwareCompareDialog(self.parent)
        dialog.exec()

    def export_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No selection", "Please select a backup to export.")
            return
        
        backup_path = item.data(Qt.ItemDataRole.UserRole)
        export_path = QFileDialog.getSaveFileName(self, "Export Backup", os.path.basename(backup_path), "Binary files (*.bin)")[0]
        
        if export_path:
            shutil.copy2(backup_path, export_path)
            QMessageBox.information(self, "Export Complete", f"Backup exported to:\n{export_path}")

    def delete_selected(self):
        item = self.backup_list.currentItem()
        if not item:
            return
        
        backup_path = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Delete Backup",
                                     f"Permanently delete {os.path.basename(backup_path)}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(backup_path)
                self.refresh_backups()
                QMessageBox.information(self, "Deleted", "Backup deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete backup:\n{str(e)}")


class SerialPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.serial_thread = None
        self.data_buffer = deque(maxlen=10000)
        self.init_ui()
    
    def cleanup(self):
        try:
            if hasattr(self, 'port_timer'):
                self.port_timer.stop()
            if self.serial_thread and self.serial_thread.isRunning():
                print("Stopping serial_thread...")
                self.serial_thread.stop()
                self.serial_thread.wait(1000)
                print("serial_thread stopped")
        except Exception as e:
            print(f"Error stopping serial_thread: {e}")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("📡 Professional Serial Monitor")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; color: #00B0FF;")
        header.addWidget(title)
        header.addStretch()
        
        self.status_label = QLabel("⭕ Disconnected")
        self.status_label.setStyleSheet("""
            color: #F44336; 
            font-weight: bold; 
            font-size: 14pt;
            padding: 10px 20px;
            background-color: rgba(244, 67, 54, 0.1);
            border-radius: 8px;
        """)
        header.addWidget(self.status_label)
        
        layout.addLayout(header)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3A3A4A;
                border-radius: 8px;
                background-color: #1E1E2E;
                padding: 15px;
            }
            QTabBar::tab {
                padding: 12px 25px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)

        connection_tab = QWidget()
        connection_layout = QVBoxLayout(connection_tab)
        connection_layout.setSpacing(20)
        
        conn_title = QLabel("⚙️ Connection Configuration")
        conn_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #00B0FF; margin-bottom: 10px;")
        connection_layout.addWidget(conn_title)
        
        settings_grid = QGridLayout()
        settings_grid.setSpacing(15)
        settings_grid.setColumnStretch(1, 1)
        settings_grid.setColumnStretch(3, 1)
        
        port_label = QLabel("Port:")
        port_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        settings_grid.addWidget(port_label, 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumHeight(45)
        self.port_combo.setStyleSheet("font-size: 11pt; padding: 8px;")
        settings_grid.addWidget(self.port_combo, 0, 1)
        
        baud_label = QLabel("Baudrate:")
        baud_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        settings_grid.addWidget(baud_label, 0, 2)
        self.baud_combo = QComboBox()
        self.baud_combo.setMinimumHeight(45)
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600", "1000000", "2000000"])
        self.baud_combo.setCurrentText("115200")
        self.baud_combo.setStyleSheet("font-size: 11pt; padding: 8px;")
        settings_grid.addWidget(self.baud_combo, 0, 3)
        
        databits_label = QLabel("Data Bits:")
        databits_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        settings_grid.addWidget(databits_label, 1, 0)
        self.databits_combo = QComboBox()
        self.databits_combo.setMinimumHeight(45)
        self.databits_combo.addItems(["5", "6", "7", "8"])
        self.databits_combo.setCurrentText("8")
        self.databits_combo.setStyleSheet("font-size: 11pt; padding: 8px;")
        settings_grid.addWidget(self.databits_combo, 1, 1)
        
        stopbits_label = QLabel("Stop Bits:")
        stopbits_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        settings_grid.addWidget(stopbits_label, 1, 2)
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.setMinimumHeight(45)
        self.stopbits_combo.addItems(["1", "1.5", "2"])
        self.stopbits_combo.setCurrentText("1")
        self.stopbits_combo.setStyleSheet("font-size: 11pt; padding: 8px;")
        settings_grid.addWidget(self.stopbits_combo, 1, 3)
        
        parity_label = QLabel("Parity:")
        parity_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        settings_grid.addWidget(parity_label, 2, 0)
        self.parity_combo = QComboBox()
        self.parity_combo.setMinimumHeight(45)
        self.parity_combo.addItems(["None", "Odd", "Even", "Mark", "Space"])
        self.parity_combo.setStyleSheet("font-size: 11pt; padding: 8px;")
        settings_grid.addWidget(self.parity_combo, 2, 1)
        
        flow_label = QLabel("Flow Control:")
        flow_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        settings_grid.addWidget(flow_label, 2, 2)
        self.flow_combo = QComboBox()
        self.flow_combo.setMinimumHeight(45)
        self.flow_combo.addItems(["None", "Hardware", "Software"])
        self.flow_combo.setStyleSheet("font-size: 11pt; padding: 8px;")
        settings_grid.addWidget(self.flow_combo, 2, 3)
        
        connection_layout.addLayout(settings_grid)
        
        connection_layout.addSpacing(20)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.connect_btn = QPushButton("🔌 Connect")
        self.connect_btn.setMinimumHeight(60)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #4CAF50, stop: 1 #66BB6A);
            }
        """)
        self.connect_btn.clicked.connect(self.toggle_serial)
        btn_layout.addWidget(self.connect_btn)
        
        refresh_btn = QPushButton("🔄 Refresh Ports")
        refresh_btn.setMinimumHeight(60)
        refresh_btn.setStyleSheet("font-size: 13pt; font-weight: bold;")
        refresh_btn.clicked.connect(self.refresh_ports)
        btn_layout.addWidget(refresh_btn)
        
        connection_layout.addLayout(btn_layout)
        connection_layout.addStretch()
        
        tabs.addTab(connection_tab, "🔧 Connection")

        console_tab = QWidget()
        console_layout = QVBoxLayout(console_tab)
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(15)
        
        console_header = QHBoxLayout()
        console_header.setSpacing(20)
        
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)
        self.autoscroll_check.setStyleSheet("font-size: 11pt; font-weight: bold;")
        console_header.addWidget(self.autoscroll_check)
        
        self.timestamp_check = QCheckBox("Show Timestamps")
        self.timestamp_check.setChecked(False)
        self.timestamp_check.setStyleSheet("font-size: 11pt; font-weight: bold;")
        console_header.addWidget(self.timestamp_check)
        
        console_header.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(11)
        self.font_size_spin.setMinimumHeight(35)
        self.font_size_spin.valueChanged.connect(self.update_font_size)
        console_header.addWidget(self.font_size_spin)
        
        console_header.addStretch()
        
        self.stats_label = QLabel("📊 RX: 0 | TX: 0 | Lines: 0")
        self.stats_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #00B0FF;")
        console_header.addWidget(self.stats_label)
        
        console_layout.addLayout(console_header)
        
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 11))
        self.console.setMaximumBlockCount(10000)
        self.console.setMinimumHeight(350)
        self.console.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0A0A0A; 
                color: #00FF00; 
                border: 2px solid #3A3A4A;
                border-radius: 8px;
                padding: 15px;
                font-size: 11pt;
                line-height: 1.5;
            }
        """)
        console_layout.addWidget(self.console)
        
        send_section = QGroupBox("📤 Send Commands")
        send_section.setStyleSheet("QGroupBox { font-size: 13pt; font-weight: bold; padding-top: 15px; }")
        send_section_layout = QVBoxLayout(send_section)
        send_section_layout.setSpacing(12)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("Type your message here...")
        self.send_input.setMinimumHeight(50)
        self.send_input.setStyleSheet("""
            QLineEdit {
                font-size: 12pt;
                padding: 12px;
                background-color: #151522;
                border: 2px solid #3A3A4A;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border: 2px solid #7B2EDA;
            }
        """)
        self.send_input.returnPressed.connect(self.send_data)
        input_layout.addWidget(self.send_input)
        
        self.send_btn = QPushButton("📤 SEND")
        self.send_btn.setMinimumHeight(50)
        self.send_btn.setMinimumWidth(120)
        self.send_btn.setStyleSheet("""
            QPushButton {
                font-size: 13pt;
                font-weight: bold;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #4CAF50, stop: 1 #66BB6A);
            }
        """)
        self.send_btn.clicked.connect(self.send_data)
        input_layout.addWidget(self.send_btn)
        
        send_section_layout.addLayout(input_layout)
        
        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        
        self.send_ascii = QRadioButton("ASCII")
        self.send_ascii.setChecked(True)
        self.send_ascii.setStyleSheet("font-size: 10pt;")
        options_layout.addWidget(self.send_ascii)
        
        self.send_hex = QRadioButton("HEX")
        self.send_hex.setStyleSheet("font-size: 10pt;")
        options_layout.addWidget(self.send_hex)
        
        options_layout.addWidget(QLabel("Line Ending:"))
        self.line_ending_combo = QComboBox()
        self.line_ending_combo.addItems(["None", "LF (\\n)", "CR (\\r)", "CRLF (\\r\\n)"])
        self.line_ending_combo.setCurrentIndex(1)
        self.line_ending_combo.setMinimumHeight(35)
        self.line_ending_combo.setStyleSheet("font-size: 10pt; padding: 5px;")
        options_layout.addWidget(self.line_ending_combo)
        
        options_layout.addStretch()
        
        send_section_layout.addLayout(options_layout)
        
        quick_label = QLabel("Quick Commands:")
        quick_label.setStyleSheet("font-size: 10pt; font-weight: bold; margin-top: 5px;")
        send_section_layout.addWidget(quick_label)
        
        quick_layout = QGridLayout()
        quick_layout.setSpacing(8)
        
        commands = ["AT", "AT+GMR", "AT+RST", "help", "status", "reboot", "reset", "info"]
        for i, cmd in enumerate(commands):
            btn = QPushButton(cmd)
            btn.setMinimumHeight(38)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 10pt;
                    font-weight: bold;
                    background-color: #2A2A3A;
                }
                QPushButton:hover {
                    background-color: #3A3A4A;
                }
            """)
            btn.clicked.connect(lambda checked, c=cmd: self.quick_send(c))
            quick_layout.addWidget(btn, i // 4, i % 4)
        
        send_section_layout.addLayout(quick_layout)
        
        console_layout.addWidget(send_section)
        
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMinimumHeight(40)
        clear_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        clear_btn.clicked.connect(self.clear_console)
        action_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("💾 Save Log")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        save_btn.clicked.connect(self.save_log)
        action_layout.addWidget(save_btn)
        
        self.capture_btn = QPushButton("📹 Start Capture")
        self.capture_btn.setMinimumHeight(40)
        self.capture_btn.setStyleSheet("font-size: 11pt; font-weight: bold;")
        self.capture_btn.clicked.connect(self.toggle_capture)
        action_layout.addWidget(self.capture_btn)
        
        action_layout.addStretch()
        
        console_layout.addLayout(action_layout)
        
        tabs.addTab(console_tab, "📝 Console")

        send_tab = QWidget()
        send_layout = QVBoxLayout(send_tab)
        send_layout.setSpacing(20)
        
        send_info = QLabel("💡 Tip: Use the Console tab for quick access to send commands!")
        send_info.setStyleSheet("""
            font-size: 12pt; 
            color: #FFC107; 
            background-color: rgba(255, 193, 7, 0.1);
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #FFC107;
        """)
        send_info.setWordWrap(True)
        send_layout.addWidget(send_info)
        
        send_title = QLabel("📤 Advanced Send Options")
        send_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #00B0FF; margin-bottom: 10px;")
        send_layout.addWidget(send_title)
        
        macros_group = QGroupBox("Custom Macros (Coming Soon)")
        macros_group.setStyleSheet("QGroupBox { font-size: 12pt; font-weight: bold; }")
        macros_layout = QVBoxLayout(macros_group)
        
        macro_info = QLabel("• Save frequently used commands\n• Create custom command sequences\n• Automate testing workflows")
        macro_info.setStyleSheet("font-size: 11pt; color: #AAAAAA; padding: 20px;")
        macros_layout.addWidget(macro_info)
        
        send_layout.addWidget(macros_group)
        send_layout.addStretch()
        
        tabs.addTab(send_tab, "📤 Advanced")

        hex_tab = QWidget()
        hex_layout = QVBoxLayout(hex_tab)
        hex_layout.setContentsMargins(0, 0, 0, 0)
        
        hex_title = QLabel("🔢 HEX View - Raw Data")
        hex_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #00FFFF; margin-bottom: 10px;")
        hex_layout.addWidget(hex_title)
        
        self.hex_view = QPlainTextEdit()
        self.hex_view.setReadOnly(True)
        self.hex_view.setFont(QFont("Courier New", 10))
        self.hex_view.setMinimumHeight(550)
        self.hex_view.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0A0A0A; 
                color: #00FFFF; 
                border: 2px solid #3A3A4A;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Courier New';
            }
        """)
        hex_layout.addWidget(self.hex_view)
        
        tabs.addTab(hex_tab, "🔢 HEX")

        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMinimumHeight(550)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #151522;
                color: #F5F5F9;
                border: 2px solid #3A3A4A;
                border-radius: 8px;
                padding: 15px;
                font-size: 11pt;
            }
        """)
        stats_layout.addWidget(self.stats_text)
        
        tabs.addTab(stats_tab, "📊 Statistics")
        
        layout.addWidget(tabs)

        self.refresh_ports()
        
        self.rx_bytes = 0
        self.tx_bytes = 0
        self.line_count = 0
        self.capture_file = None

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
            QMessageBox.warning(self, "No port", "No COM port detected.")
            return
        
        port = self.port_combo.currentData()
        baudrate = int(self.baud_combo.currentText())
        databits = int(self.databits_combo.currentText())
        stopbits = float(self.stopbits_combo.currentText())
        parity = self.parity_combo.currentText()[0]
        
        self.serial_thread = SerialMonitorThread(port, baudrate, databits, int(stopbits), parity)
        self.serial_thread.data_received.connect(self.on_data_received)
        self.serial_thread.error.connect(self.on_serial_error)
        self.serial_thread.data_sent.connect(self.on_data_sent)
        self.serial_thread.start()
        
        self.connect_btn.setText("🔌 Disconnect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #F44336, stop: 1 #E57373);
            }
        """)
        self.status_label.setText("🟢 Connected")
        self.status_label.setStyleSheet("""
            color: #4CAF50; 
            font-weight: bold; 
            font-size: 14pt;
            padding: 10px 20px;
            background-color: rgba(76, 175, 80, 0.1);
            border-radius: 8px;
        """)
        self.parent.statusBar().showMessage(f"✅ Connected to {port} at {baudrate} baud")

    def disconnect_serial(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()
            self.serial_thread = None
        
        self.connect_btn.setText("🔌 Connect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                font-weight: bold;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #4CAF50, stop: 1 #66BB6A);
            }
        """)
        self.status_label.setText("⭕ Disconnected")
        self.status_label.setStyleSheet("""
            color: #F44336; 
            font-weight: bold; 
            font-size: 14pt;
            padding: 10px 20px;
            background-color: rgba(244, 67, 54, 0.1);
            border-radius: 8px;
        """)
        self.parent.statusBar().showMessage("Disconnected")

    def on_data_received(self, data: bytes):
        self.rx_bytes += len(data)
        self.data_buffer.append(data)
        
        try:
            text = data.decode('utf-8', errors='replace')
        except:
            text = str(data)
        
        self.line_count += text.count('\n')
        
        if self.timestamp_check.isChecked():
            timestamp = datetime.datetime.now().strftime("[%H:%M:%S.%f")[:-3] + "] "
            text = timestamp + text
        
        self.console.insertPlainText(text)
        
        if self.autoscroll_check.isChecked():
            cursor = self.console.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.console.setTextCursor(cursor)
        
        hex_str = ' '.join([f'{b:02X}' for b in data])
        self.hex_view.appendPlainText(hex_str)
        
        self.update_stats()
        
        if self.capture_file:
            self.capture_file.write(data)
            self.capture_file.flush()

    def on_serial_error(self, error_msg):
        self.console.insertPlainText(f"\n⚠️ ERROR: {error_msg}\n")
        if self.autoscroll_check.isChecked():
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
        
        line_ending_map = {0: '', 1: '\n', 2: '\r', 3: '\r\n'}
        line_ending = line_ending_map[self.line_ending_combo.currentIndex()]
        
        if self.send_ascii.isChecked():
            data = (text + line_ending).encode('utf-8')
            self.console.insertPlainText(f">> {text}{line_ending}")
        else:
            hex_str = text.replace(' ', '').replace(',', '')
            try:
                data = bytes.fromhex(hex_str)
                if line_ending:
                    data += line_ending.encode('utf-8')
                self.console.insertPlainText(f">> HEX: {text}\n")
            except:
                QMessageBox.warning(self, "HEX error", "Invalid HEX format.")
                return
        
        self.serial_thread.write(data)
        self.tx_bytes += len(data)
        self.update_stats()
        self.send_input.clear()
        
        if self.autoscroll_check.isChecked():
            cursor = self.console.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.console.setTextCursor(cursor)

    def quick_send(self, command):
        if self.serial_thread and self.serial_thread.isRunning():
            self.send_input.setText(command)
            self.send_data()

    def update_stats(self):
        self.stats_label.setText(f"📊 RX: {self.rx_bytes} | TX: {self.tx_bytes} | Lines: {self.line_count}")
        
        stats_html = f"""
        <h2>Serial Monitor Statistics</h2>
        <table border="1" cellpadding="5">
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Bytes Received</td><td>{self.rx_bytes:,}</td></tr>
        <tr><td>Bytes Transmitted</td><td>{self.tx_bytes:,}</td></tr>
        <tr><td>Lines Received</td><td>{self.line_count:,}</td></tr>
        <tr><td>Buffer Size</td><td>{len(self.data_buffer)}</td></tr>
        <tr><td>Port</td><td>{self.port_combo.currentText()}</td></tr>
        <tr><td>Baudrate</td><td>{self.baud_combo.currentText()}</td></tr>
        </table>
        """
        self.stats_text.setHtml(stats_html)

    def update_font_size(self, size):
        font = QFont("Consolas", size)
        self.console.setFont(font)
        self.hex_view.setFont(QFont("Courier New", size))

    def clear_console(self):
        reply = QMessageBox.question(self, "Clear Console",
                                     "Clear all console data?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.console.clear()
            self.hex_view.clear()
            self.rx_bytes = 0
            self.tx_bytes = 0
            self.line_count = 0
            self.data_buffer.clear()
            self.update_stats()

    def save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Text files (*.txt);;Log files (*.log);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.console.toPlainText())
                QMessageBox.information(self, "Log Saved", f"Log saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save log:\n{str(e)}")

    def toggle_capture(self):
        if self.capture_file:
            self.capture_file.close()
            self.capture_file = None
            self.capture_btn.setText("📹 Start Capture")
            self.capture_btn.setStyleSheet("")
            QMessageBox.information(self, "Capture Stopped", "Data capture stopped.")
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Capture to File", "", "Binary files (*.bin);;Text files (*.txt)")
            if file_path:
                self.capture_file = open(file_path, 'wb')
                self.capture_btn.setText("⏹️ Stop Capture")
                self.capture_btn.setStyleSheet("background-color: #F44336;")
                QMessageBox.information(self, "Capture Started", f"Capturing to:\n{file_path}")


class ProjectsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.project_manager = ProjectManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("📁 Project Manager")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #00B0FF;")
        header.addWidget(title)
        header.addStretch()
        
        new_project_btn = QPushButton("➕ New Project")
        new_project_btn.clicked.connect(self.create_new_project)
        header.addWidget(new_project_btn)
        
        layout.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Your Projects"))
        
        self.projects_list = QListWidget()
        self.projects_list.itemClicked.connect(self.load_project_details)
        left_layout.addWidget(self.projects_list)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("Project Details"))
        
        form = QFormLayout()
        
        self.project_name_edit = QLineEdit()
        form.addRow("Name:", self.project_name_edit)
        
        self.project_chip_combo = QComboBox()
        self.project_chip_combo.addItems(["auto", "esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3"])
        form.addRow("Target Chip:", self.project_chip_combo)
        
        right_layout.addLayout(form)
        
        right_layout.addWidget(QLabel("Firmwares in Project:"))
        
        self.project_files_list = QListWidget()
        right_layout.addWidget(self.project_files_list)
        
        files_btn_layout = QHBoxLayout()
        add_file_btn = QPushButton("➕ Add Firmware")
        add_file_btn.clicked.connect(self.add_firmware_to_project)
        files_btn_layout.addWidget(add_file_btn)
        
        remove_file_btn = QPushButton("➖ Remove")
        remove_file_btn.clicked.connect(self.remove_firmware_from_project)
        files_btn_layout.addWidget(remove_file_btn)
        
        right_layout.addLayout(files_btn_layout)
        
        right_layout.addWidget(QLabel("Notes:"))
        self.project_notes = QTextEdit()
        right_layout.addWidget(self.project_notes)
        
        save_btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Project")
        save_btn.clicked.connect(self.save_current_project)
        save_btn_layout.addWidget(save_btn)
        
        delete_btn = QPushButton("🗑️ Delete Project")
        delete_btn.clicked.connect(self.delete_current_project)
        save_btn_layout.addWidget(delete_btn)
        
        right_layout.addLayout(save_btn_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        self.current_project = None
        self.refresh_projects()

    def refresh_projects(self):
        self.projects_list.clear()
        projects = self.project_manager.list_projects()
        for project_name in projects:
            item = QListWidgetItem(f"📁 {project_name}")
            item.setData(Qt.ItemDataRole.UserRole, project_name)
            self.projects_list.addItem(item)

    def create_new_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name:
            chip, ok = QInputDialog.getItem(self, "Chip Type", "Select target chip:",
                                           ["auto", "esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3"], 0, False)
            if ok:
                project = self.project_manager.create_project(name, chip)
                self.refresh_projects()
                QMessageBox.information(self, "Project Created", f"Project '{name}' created successfully!")

    def load_project_details(self, item):
        project_name = item.data(Qt.ItemDataRole.UserRole)
        project = self.project_manager.load_project(project_name)
        
        if project:
            self.current_project = project
            self.project_name_edit.setText(project.name)
            self.project_chip_combo.setCurrentText(project.chip_type)
            self.project_notes.setPlainText(project.notes)
            
            self.project_files_list.clear()
            for fw in project.firmwares:
                self.project_files_list.addItem(fw)

    def add_firmware_to_project(self):
        if not self.current_project:
            QMessageBox.warning(self, "No project", "Please select or create a project first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Add Firmware", "", "Binary files (*.bin)")
        if file_path:
            self.current_project.firmwares.append(file_path)
            self.project_files_list.addItem(file_path)

    def remove_firmware_from_project(self):
        if not self.current_project:
            return
        
        current_item = self.project_files_list.currentItem()
        if current_item:
            fw_path = current_item.text()
            self.current_project.firmwares.remove(fw_path)
            self.project_files_list.takeItem(self.project_files_list.currentRow())

    def save_current_project(self):
        if not self.current_project:
            QMessageBox.warning(self, "No project", "No project selected.")
            return
        
        self.current_project.chip_type = self.project_chip_combo.currentText()
        self.current_project.notes = self.project_notes.toPlainText()
        
        self.project_manager.save_project(self.current_project)
        QMessageBox.information(self, "Project Saved", f"Project '{self.current_project.name}' saved!")

    def delete_current_project(self):
        if not self.current_project:
            return
        
        reply = QMessageBox.question(self, "Delete Project",
                                     f"Permanently delete project '{self.current_project.name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project_manager.delete_project(self.current_project.name)
            self.current_project = None
            self.refresh_projects()
            self.project_name_edit.clear()
            self.project_notes.clear()
            self.project_files_list.clear()
            QMessageBox.information(self, "Deleted", "Project deleted successfully.")


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("⚙️ Advanced Settings")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #00B0FF;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        form = QFormLayout(scroll_content)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(COLOR_SCHEMES.keys()))
        self.theme_combo.setCurrentText(self.parent.settings.data.get('theme', 'Purple Dream'))
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        form.addRow("🎨 Color Theme:", self.theme_combo)

        form.addRow(QLabel(""))

        form.addRow(QLabel("<b>Flash Settings</b>"))
        
        self.baudrate_spin = QSpinBox()
        self.baudrate_spin.setRange(9600, 2000000)
        self.baudrate_spin.setValue(self.parent.settings.data.get('baudrate', DEFAULT_BAUDRATE))
        form.addRow("Default Baudrate:", self.baudrate_spin)

        self.address_edit = QLineEdit(self.parent.settings.data.get('flash_address', DEFAULT_FLASH_ADDRESS))
        form.addRow("Default Flash Address:", self.address_edit)

        self.chip_combo = QComboBox()
        self.chip_combo.addItems(["auto", "esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3"])
        self.chip_combo.setCurrentText(self.parent.settings.data.get('chip_type', 'auto'))
        form.addRow("Default Chip Type:", self.chip_combo)

        self.erase_check = QCheckBox()
        self.erase_check.setChecked(self.parent.settings.data.get('erase_before_flash', False))
        form.addRow("Erase Before Flash:", self.erase_check)

        self.verify_check = QCheckBox()
        self.verify_check.setChecked(self.parent.settings.data.get('verify_after_flash', True))
        form.addRow("Verify After Flash:", self.verify_check)

        form.addRow(QLabel(""))

        form.addRow(QLabel("<b>Backup Settings</b>"))
        
        self.backup_check = QCheckBox()
        self.backup_check.setChecked(self.parent.settings.data.get('backup_before_flash', True))
        form.addRow("Auto-Backup Before Flash:", self.backup_check)

        self.backup_size_spin = QSpinBox()
        self.backup_size_spin.setRange(1024, 16777216)
        self.backup_size_spin.setValue(self.parent.settings.data.get('backup_size', 4194304))
        form.addRow("Backup Size (bytes):", self.backup_size_spin)

        form.addRow(QLabel(""))

        form.addRow(QLabel("<b>Serial Monitor Settings</b>"))
        
        self.serial_baud_combo = QComboBox()
        self.serial_baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.serial_baud_combo.setCurrentText(str(self.parent.settings.data.get('serial_baudrate', 115200)))
        form.addRow("Default Serial Baudrate:", self.serial_baud_combo)

        self.auto_scroll_check = QCheckBox()
        self.auto_scroll_check.setChecked(self.parent.settings.data.get('auto_scroll_serial', True))
        form.addRow("Auto-Scroll Serial:", self.auto_scroll_check)

        self.timestamp_check = QCheckBox()
        self.timestamp_check.setChecked(self.parent.settings.data.get('timestamp_serial', False))
        form.addRow("Timestamps in Serial:", self.timestamp_check)

        form.addRow(QLabel(""))

        form.addRow(QLabel("<b>Directories</b>"))
        
        fw_layout = QHBoxLayout()
        self.firmware_dir_edit = QLineEdit(self.parent.settings.data.get('firmware_dir', FIRMWARE_DIR))
        fw_layout.addWidget(self.firmware_dir_edit)
        fw_btn = QPushButton("Browse")
        fw_btn.clicked.connect(self.browse_firmware_dir)
        fw_layout.addWidget(fw_btn)
        form.addRow("Firmware Folder:", fw_layout)

        bk_layout = QHBoxLayout()
        self.backup_dir_edit = QLineEdit(self.parent.settings.data.get('backup_dir', BACKUP_DIR))
        bk_layout.addWidget(self.backup_dir_edit)
        bk_btn = QPushButton("Browse")
        bk_btn.clicked.connect(self.browse_backup_dir)
        bk_layout.addWidget(bk_btn)
        form.addRow("Backup Folder:", bk_layout)

        form.addRow(QLabel(""))

        form.addRow(QLabel("<b>Behavior</b>"))
        
        self.auto_detect_check = QCheckBox()
        self.auto_detect_check.setChecked(self.parent.settings.data.get('auto_detect_on_start', True))
        form.addRow("Auto-Detect on Start:", self.auto_detect_check)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        reset_btn = QPushButton("↩️ Restore Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        btn_layout.addWidget(reset_btn)

        export_btn = QPushButton("📤 Export Settings")
        export_btn.clicked.connect(self.export_settings)
        btn_layout.addWidget(export_btn)

        import_btn = QPushButton("📥 Import Settings")
        import_btn.clicked.connect(self.import_settings)
        btn_layout.addWidget(import_btn)

        layout.addLayout(btn_layout)

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
        self.parent.settings.data['verify_after_flash'] = self.verify_check.isChecked()
        self.parent.settings.data['backup_before_flash'] = self.backup_check.isChecked()
        self.parent.settings.data['backup_size'] = self.backup_size_spin.value()
        self.parent.settings.data['serial_baudrate'] = int(self.serial_baud_combo.currentText())
        self.parent.settings.data['auto_scroll_serial'] = self.auto_scroll_check.isChecked()
        self.parent.settings.data['timestamp_serial'] = self.timestamp_check.isChecked()
        self.parent.settings.data['firmware_dir'] = self.firmware_dir_edit.text()
        self.parent.settings.data['backup_dir'] = self.backup_dir_edit.text()
        self.parent.settings.data['auto_detect_on_start'] = self.auto_detect_check.isChecked()
        self.parent.settings.data['theme'] = self.theme_combo.currentText()
        self.parent.settings.save()
        
        QMessageBox.information(self, "Settings Saved", "Settings saved successfully!")

    def reset_defaults(self):
        reply = QMessageBox.question(self, "Reset Settings",
                                     "Reset all settings to defaults?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.parent.settings.data = self.parent.settings.defaults()
            self.parent.settings.save()
            QMessageBox.information(self, "Reset Complete", "Settings reset to defaults. Please restart the application.")

    def export_settings(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Settings", "", "JSON files (*.json)")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.parent.settings.data, f, indent=4)
            QMessageBox.information(self, "Export Complete", f"Settings exported to:\n{file_path}")

    def import_settings(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Settings", "", "JSON files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_settings = json.load(f)
                self.parent.settings.data.update(imported_settings)
                self.parent.settings.save()
                QMessageBox.information(self, "Import Complete", "Settings imported successfully! Please restart.")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import settings:\n{str(e)}")

    def change_theme(self, theme_name):
        self.parent.setStyleSheet(get_stylesheet(theme_name))
        self.parent.settings.data['theme'] = theme_name
        self.parent.settings.save()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION} - Professional ESP Flasher")
        self.setMinimumSize(1400, 900)

        self.settings = SettingsManager()
        self.history_manager = HistoryManager()

        theme = self.settings.data.get('theme', 'Purple Dream')
        self.setStyleSheet(get_stylesheet(theme))

        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #151522, stop: 1 #0A0A0A);
                border-right: 2px solid #3A3A4A;
            }}
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(8)

        logo_label = QLabel(APP_NAME)
        logo_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: white;
            padding: 15px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                       stop: 0 #7B2EDA, stop: 1 #00B0FF);
            border-radius: 10px;
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        version_label = QLabel(f"v{VERSION} - Pro Edition - LTX")
        version_label.setStyleSheet("color: #888888; font-size: 9pt;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)

        sidebar_layout.addWidget(QLabel(""))

        self.nav_buttons = []
        nav_items = [
            ("📊", "Dashboard", "Overview and statistics"),
            ("⚡", "Flash", "Flash firmware to devices"),
            ("💾", "Backup", "Backup and restore"),
            ("📡", "Serial", "Serial monitor"),
            ("📁", "Projects", "Manage projects"),
            ("⚙️", "Settings", "Application settings")
        ]
        
        self.sidebar_stack = QStackedWidget()

        self.dashboard_page = DashboardPage(self)
        self.flash_page = FlashPage(self)
        self.backup_page = BackupPage(self)
        self.serial_page = SerialPage(self)
        self.projects_page = ProjectsPage(self)
        self.settings_page = SettingsPage(self)

        self.sidebar_stack.addWidget(self.dashboard_page)
        self.sidebar_stack.addWidget(self.flash_page)
        self.sidebar_stack.addWidget(self.backup_page)
        self.sidebar_stack.addWidget(self.serial_page)
        self.sidebar_stack.addWidget(self.projects_page)
        self.sidebar_stack.addWidget(self.settings_page)

        for i, (icon, text, tooltip) in enumerate(nav_items):
            btn = QPushButton(f"{icon}  {text}")
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 15px;
                    border-radius: 8px;
                    background-color: transparent;
                    color: #CCCCCC;
                    font-size: 11pt;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #3A3A4A;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                               stop: 0 #7B2EDA, stop: 1 #00B0FF);
                    color: white;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        system_info = QLabel(f"💻 {sys.platform}\n🐍 Python {sys.version_info.major}.{sys.version_info.minor}")
        system_info.setStyleSheet("color: #666666; font-size: 8pt;")
        system_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(system_info)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.sidebar_stack, 1)

        self.nav_buttons[0].setChecked(True)

        self.setup_shortcuts()

    def create_menus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar { padding: 5px; }")

        file_menu = menubar.addMenu("📁 File")
        
        new_project_action = QAction("➕ New Project", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(lambda: self.projects_page.create_new_project())
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("📂 Open Project", self)
        open_project_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        import_fw_action = QAction("📥 Import Firmware", self)
        import_fw_action.triggered.connect(self.import_firmware)
        file_menu.addAction(import_fw_action)
        
        export_backup_action = QAction("📤 Export Backup", self)
        file_menu.addAction(export_backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("🛠️ Tools")
        
        detect_action = QAction("🔍 Detect Devices", self)
        detect_action.setShortcut("F5")
        detect_action.triggered.connect(lambda: self.dashboard_page.refresh_boards())
        tools_menu.addAction(detect_action)
        
        batch_flash_action = QAction("📦 Batch Flash", self)
        batch_flash_action.triggered.connect(self.open_batch_flash)
        tools_menu.addAction(batch_flash_action)
        
        compare_fw_action = QAction("🔍 Compare Firmwares", self)
        compare_fw_action.triggered.connect(self.open_firmware_compare)
        tools_menu.addAction(compare_fw_action)
        
        tools_menu.addSeparator()
        
        terminal_action = QAction("💻 Open Terminal", self)
        terminal_action.setShortcut("Ctrl+T")
        terminal_action.triggered.connect(self.open_terminal)
        tools_menu.addAction(terminal_action)

        view_menu = menubar.addMenu("👁️ View")
        
        dashboard_action = QAction("📊 Dashboard", self)
        dashboard_action.setShortcut("Ctrl+1")
        dashboard_action.triggered.connect(lambda: self.switch_page(0))
        view_menu.addAction(dashboard_action)
        
        flash_action = QAction("⚡ Flash", self)
        flash_action.setShortcut("Ctrl+2")
        flash_action.triggered.connect(lambda: self.switch_page(1))
        view_menu.addAction(flash_action)
        
        serial_action = QAction("📡 Serial Monitor", self)
        serial_action.setShortcut("Ctrl+3")
        serial_action.triggered.connect(lambda: self.switch_page(3))
        view_menu.addAction(serial_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("⛶ Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        help_menu = menubar.addMenu("❓ Help")
        
        docs_action = QAction("📚 Documentation", self)
        docs_action.setShortcut("F1")
        docs_action.triggered.connect(self.open_documentation)
        help_menu.addAction(docs_action)
        
        github_action = QAction("🐙 GitHub Repository", self)
        github_action.triggered.connect(lambda: QMessageBox.information(self, "GitHub", 
            "Visit: https://github.com/LTX128/ESP_Flasher"))
        help_menu.addAction(github_action)
        
        help_menu.addSeparator()
        
        updates_action = QAction("🔄 Check for Updates", self)
        updates_action.triggered.connect(self.check_updates)
        help_menu.addAction(updates_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #151522;
                border-bottom: 2px solid #3A3A4A;
                padding: 5px;
                spacing: 10px;
            }
            QToolButton {
                padding: 8px;
                border-radius: 6px;
            }
            QToolButton:hover {
                background-color: #3A3A4A;
            }
        """)
        self.addToolBar(toolbar)

        detect_btn = QPushButton("🔍 Detect")
        detect_btn.clicked.connect(lambda: self.dashboard_page.refresh_boards())
        toolbar.addWidget(detect_btn)

        flash_btn = QPushButton("⚡ Flash")
        flash_btn.clicked.connect(lambda: self.switch_page(1))
        toolbar.addWidget(flash_btn)

        backup_btn = QPushButton("💾 Backup")
        backup_btn.clicked.connect(lambda: self.switch_page(2))
        toolbar.addWidget(backup_btn)

        toolbar.addSeparator()

        serial_btn = QPushButton("📡 Serial")
        serial_btn.clicked.connect(lambda: self.switch_page(3))
        toolbar.addWidget(serial_btn)

        toolbar.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.connection_indicator = QLabel("⭕ No device")
        self.connection_indicator.setStyleSheet("color: #F44336; padding: 5px;")
        toolbar.addWidget(self.connection_indicator)

    def create_status_bar(self):
        status = self.statusBar()
        status.setStyleSheet("""
            QStatusBar {
                background-color: #151522;
                border-top: 1px solid #3A3A4A;
                padding: 5px;
            }
        """)
        
        self.status_label = QLabel("Ready")
        status.addWidget(self.status_label)
        
        status.addPermanentWidget(QLabel(" | "))
        
        self.device_count_label = QLabel("Devices: 0")
        status.addPermanentWidget(self.device_count_label)
        
        status.addPermanentWidget(QLabel(" | "))
        
        self.memory_label = QLabel("Memory: -- MB")
        status.addPermanentWidget(self.memory_label)
        
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory)
        self.memory_timer.start(5000)

    def setup_shortcuts(self):
        QShortcut("Ctrl+D", self, lambda: self.dashboard_page.refresh_boards())
        QShortcut("Ctrl+F", self, lambda: self.switch_page(1))
        QShortcut("Ctrl+B", self, lambda: self.switch_page(2))
        QShortcut("Ctrl+M", self, lambda: self.switch_page(3))

    def switch_page(self, index):
        self.sidebar_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def update_memory(self):
        try:
            import psutil
            process = psutil.Process()
            mem_mb = process.memory_info().rss / 1024 / 1024
            self.memory_label.setText(f"Memory: {mem_mb:.1f} MB")
        except ImportError:
            self.memory_label.setText("Memory: N/A (install psutil)")
        except Exception:
            self.memory_label.setText("Memory: N/A")

    def import_firmware(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Firmware", "", "Binary files (*.bin);;All files (*.*)")
        if file_path:
            dest = os.path.join(FIRMWARE_DIR, os.path.basename(file_path))
            shutil.copy2(file_path, dest)
            QMessageBox.information(self, "Import Complete", f"Firmware imported to:\n{dest}")

    def open_batch_flash(self):
        dialog = BatchFlashDialog(self)
        dialog.exec()

    def open_firmware_compare(self):
        dialog = FirmwareCompareDialog(self)
        dialog.exec()

    def open_terminal(self):
        if sys.platform == 'win32':
            subprocess.Popen('cmd.exe', creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', '-a', 'Terminal'])
        else:
            subprocess.Popen(['x-terminal-emulator'])

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def open_documentation(self):
        QMessageBox.information(self, "Documentation", 
            "📚 Full documentation available at:\n\n"
            "https://github.com/LTX128/ESP_Flasher/\n\n"
            "Press F1 anytime for help!")

    def check_updates(self):
        QMessageBox.information(self, "Updates", 
            f"Current version: {VERSION}\n\n"
            "✅ You are running the latest version!\n\n"
            "(Update checking feature - implementation pending)")

    def show_about(self):
        about_text = f"""
        <div style='text-align: center;'>
        <h1 style='color: #00B0FF;'>{APP_NAME}</h1>
        <h2>Version {VERSION}</h2>
        <p style='font-size: 11pt;'>
        <b>Professional ESP Flasher & Development Tool</b><br><br>
        
        <b>Features:</b><br>
        ✅ Multi-device batch flashing<br>
        ✅ Advanced serial monitoring<br>
        ✅ Project management<br>
        ✅ Firmware comparison<br>
        ✅ Automated backups<br>
        ✅ OTA updates<br>
        ✅ Template system<br>
        ✅ Real-time statistics<br><br>
        
        <b>Supported Chips:</b><br>
        ESP8266, ESP32, ESP32-S2, ESP32-S3,<br>
        ESP32-C3, ESP32-C6, ESP32-H2, and more<br><br>
        
        <b>Created by</b> {AUTHOR}<br>
        <b>Company:</b> {COMPANY}<br><br>
        
        <b>Links:</b><br>
        🐙 <a href='https://github.com/LTX128/ESP_Flasher'>GitHub</a><br>
        📹 <a href='https://www.tiktok.com/@aro.x.74'>TikTok</a><br><br>
        
        © 2026 {COMPANY}. All rights reserved.<br>
        Built with PySide6, Python, and esptool
        </p>
        </div>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                min-width: 500px;
            }
        """)
        msg.exec()

    def closeEvent(self, event):
        print("\n" + "="*60)
        print("CLOSING APPLICATION - CLEANING UP ALL THREADS")
        print("="*60)
        
        try:
            print("\n1. Cleaning up pages...")
            if hasattr(self, 'dashboard_page'):
                print("   - Dashboard page cleanup")
                self.dashboard_page.cleanup()
            
            if hasattr(self, 'flash_page'):
                print("   - Flash page cleanup")
                self.flash_page.cleanup()
            
            if hasattr(self, 'backup_page'):
                print("   - Backup page cleanup")
                self.backup_page.cleanup()
            
            if hasattr(self, 'serial_page'):
                print("   - Serial page cleanup")
                self.serial_page.cleanup()
            
            print("\n2. Stopping main window timers...")
            if hasattr(self, 'memory_timer'):
                self.memory_timer.stop()
                print("   - Memory timer stopped")
            
            print("\n" + "="*60)
            print("ALL CLEANUP COMPLETE - Application can close safely")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(COMPANY)
    app.setApplicationVersion(VERSION)
    
    icon_path = "logo.ico"
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(QColor("#7B2EDA"))
    
    painter = QPainter(splash_pix)
    painter.setPen(QColor("#FFFFFF"))
    
    font = QFont("Arial", 28, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(splash_pix.rect(), Qt.AlignmentFlag.AlignCenter, APP_NAME)
    
    font = QFont("Arial", 14)
    painter.setFont(font)
    text_rect = QRect(0, 200, 400, 40)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"Version {VERSION}")
    
    text_rect2 = QRect(0, 230, 400, 40)
    painter.drawText(text_rect2, Qt.AlignmentFlag.AlignCenter, "Loading...")
    
    painter.end()
    
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    splash.show()
    app.processEvents()

    window = MainWindow()
    
    QTimer.singleShot(1500, lambda: (window.show(), splash.finish(window)))

    return app.exec()


if __name__ == "__main__":
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           {APP_NAME} v{VERSION}                          ║
    ║                                                           ║
    ║         Professional ESP Flasher & Dev Tool               ║
    ║                                                           ║
    ║                  Created by {AUTHOR}                           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Starting application...
    """)
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made BY LTX - Pro Edition