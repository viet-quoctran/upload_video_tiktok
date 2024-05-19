import sys
import json
import requests
import subprocess
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLineEdit, QHBoxLayout, QFormLayout,
                             QMessageBox, QTimeEdit, QDialog, QFileDialog, QComboBox, QSpinBox, QGroupBox,
                             QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,QLabel)
from PyQt5.QtCore import QTime, Qt, QFileSystemWatcher
from PyQt5.QtGui import QColor
from display.config_manager import ConfigManager
from display.dialogs import EditDialog, CreateGroupDialog, EditGroupDialog

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.processes = []
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.current_group = None if not self.config['groups'] else list(self.config['groups'].keys())[0]
        self.max_concurrent_profiles = 10
        self.initUI()
        self.update_ui_components()
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.directoryChanged.connect(self.update_video_counts)

    def save_config(self):
        self.config_manager.save_config()

    def initUI(self):
        self.setWindowTitle('Automation Upload Tool')
        self.setGeometry(100, 100, 800, 600)
        main_layout = QVBoxLayout(self)

        # Group management section
        group_box = QGroupBox("Group Management")
        group_layout = QVBoxLayout()

        group_button_layout = QHBoxLayout()
        self.create_group_btn = QPushButton("Create New Group", self)
        self.create_group_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.create_group_btn.clicked.connect(self.create_new_group)
        group_button_layout.addWidget(self.create_group_btn)

        self.edit_group_btn = QPushButton("Edit Group Name", self)
        self.edit_group_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.edit_group_btn.clicked.connect(self.edit_group_name)
        group_button_layout.addWidget(self.edit_group_btn)

        self.delete_group_btn = QPushButton("Delete Group", self)
        self.delete_group_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_group_btn.clicked.connect(self.delete_group)
        group_button_layout.addWidget(self.delete_group_btn)

        self.refresh_btn = QPushButton("Refresh Profiles", self)
        self.refresh_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.refresh_btn.clicked.connect(self.refresh_profiles)
        group_button_layout.addWidget(self.refresh_btn)

        group_layout.addLayout(group_button_layout)

        self.group_selector = QComboBox(self)
        self.group_selector.currentTextChanged.connect(self.on_group_selected)
        group_layout.addWidget(self.group_selector)

        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        # Profile management section
        profile_box = QGroupBox("Profile Management")
        profile_layout = QVBoxLayout()

        # Search bar
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search profile by name...")
        self.search_input.textChanged.connect(self.filter_profiles)
        profile_layout.addWidget(self.search_input)

        # Profile input and add button
        profile_input_layout = QHBoxLayout()
        self.profile_input = QLineEdit(self)
        self.profile_input.setPlaceholderText("Enter new profile ID...")
        self.add_profile_btn = QPushButton('Add', self)
        self.add_profile_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.add_profile_btn.clicked.connect(self.add_profile_id)
        profile_input_layout.addWidget(self.profile_input)
        profile_input_layout.addWidget(self.add_profile_btn)
        profile_layout.addLayout(profile_input_layout)

        # Profile table
        self.profile_table = QTableWidget(self)
        self.profile_table.setColumnCount(6)
        self.profile_table.setHorizontalHeaderLabels(['ID', 'Name', 'Uploaded', 'Remaining', 'Error', 'Actions'])
        
        # Tô màu cho hàng tiêu đề
        header = self.profile_table.horizontalHeader()
        header.setStyleSheet("::section {background-color: #f0f0f0; color: #000000; font-weight: bold;}")

        # Thiết lập độ rộng cột
        self.profile_table.horizontalHeader().setStretchLastSection(True)
        self.profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.profile_table.setColumnWidth(0, 150)  # ID column
        self.profile_table.setColumnWidth(1, 200)  # Name column
        self.profile_table.setColumnWidth(2, 80)   # Uploaded column
        self.profile_table.setColumnWidth(3, 80)   # Remaining column
        self.profile_table.setColumnWidth(4, 80)   # Error column
        self.profile_table.setColumnWidth(5, 150)  # Actions column

        profile_layout.addWidget(self.profile_table)

        profile_box.setLayout(profile_layout)
        main_layout.addWidget(profile_box)

        # Settings section
        settings_box = QGroupBox("Settings")
        settings_layout = QFormLayout()

        # Folder Video Path
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self)
        self.folder_btn = QPushButton("Browse...", self)
        self.folder_btn.setStyleSheet("background-color: #607D8B; color: white;")
        self.folder_btn.clicked.connect(lambda: self.select_folder('FOLDER_VIDEO_BASE'))
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.folder_btn)
        settings_layout.addRow("Folder Video Path:", folder_layout)

        # Schedule Time and Max Concurrent Profiles in one row
        schedule_layout = QHBoxLayout()
        self.schedule_time_input = QTimeEdit(self)
        self.schedule_time_input.setDisplayFormat("HH:mm")
        self.schedule_time_input.timeChanged.connect(lambda time: self.update_config('SCHEDULE_TIME', time.toString("HH:mm")))
        schedule_layout.addWidget(QLabel("Schedule Time:"))
        schedule_layout.addWidget(self.schedule_time_input)

        self.profile_spin_box = QSpinBox(self)
        self.profile_spin_box.setMinimum(1)
        self.profile_spin_box.setMaximum(50)  # Default maximum, will be updated per group
        self.profile_spin_box.valueChanged.connect(lambda value: self.update_config('MAX_CONCURRENT_PROFILES', value))
        schedule_layout.addWidget(QLabel("Max Concurrent Profiles:"))
        schedule_layout.addWidget(self.profile_spin_box)

        settings_layout.addRow(schedule_layout)
        settings_box.setLayout(settings_layout)
        main_layout.addWidget(settings_box)

        # Start and Stop buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start", self)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_process)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_button.clicked.connect(self.stop_process)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.update_group_display()
        if self.current_group:
            self.change_group(self.current_group)


    def update_max_concurrent_profiles(self, value):
        self.max_concurrent_profiles = value
        print(f"Updated max concurrent profiles to: {self.max_concurrent_profiles}")

    def on_group_selected(self):
        selected_text = self.group_selector.currentText()
        if selected_text:
            group_name = selected_text.split(" - ")[0]
            self.current_group = group_name
            self.change_group(group_name)
            self.update_ui_components()
        else:
            self.current_group = None
            self.disable_ui_components()

    def create_new_group(self):
        dialog = CreateGroupDialog(self)
        if dialog.exec_():
            new_group_name = dialog.get_group_name()
            if new_group_name:
                if new_group_name in self.config['groups']:
                    QMessageBox.warning(self, "Error", "A group with this name already exists.")
                    return

                # Automatically determine the path to main.py relative to the current file
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Adjust to go up one level
                main_py_path = os.path.join(base_dir, 'main.py')

                if not os.path.exists(main_py_path):
                    QMessageBox.critical(self, "Error", "main.py not found at expected location.")
                    return

                # Initialize PROFILE_ID as an empty dictionary instead of a list
                self.config['groups'][new_group_name] = {
                    "PROFILE_ID": {},
                    "FOLDER_VIDEO_BASE": "",
                    "PATH_MAIN": main_py_path,
                    "SCHEDULE_TIME": "00:00",
                    "MAX_CONCURRENT_PROFILES": self.max_concurrent_profiles,
                    "videos_error": 0,  # Initialize videos_error
                    "is_scheduled": False
                }
                self.save_config()
                self.update_group_display()
                self.change_group(new_group_name)
                self.group_selector.setCurrentText(f"{new_group_name} - chưa hẹn giờ")  # Ensure new group is selected
                self.update_ui_components()  # Add this line to update UI components
                QMessageBox.information(self, "Success", "New group created.")



    def edit_group_name(self):
        current_group_name = self.group_selector.currentText().split(" - ")[0]
        dialog = EditGroupDialog(current_group_name, self)
        if dialog.exec_():
            new_group_name = dialog.get_group_name()
            if new_group_name and new_group_name != current_group_name:
                if new_group_name in self.config['groups']:
                    QMessageBox.warning(self, "Error", "A group with this name already exists.")
                    return
                self.config['groups'][new_group_name] = self.config['groups'].pop(current_group_name)
                self.config['groups'][new_group_name]['is_scheduled'] = False
                self.save_config()
                self.current_group = new_group_name  # Cập nhật self.current_group với tên mới
                self.update_group_display()
                self.change_group(new_group_name)  # Đảm bảo UI cập nhật theo nhóm mới
                QMessageBox.information(self, "Group Updated", f"Group name updated from '{current_group_name}' to '{new_group_name}'.")

    def delete_group(self):
        current_group_name = self.group_selector.currentText().split(" - ")[0]
        if current_group_name in self.config['groups']:
            if QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the group '{current_group_name}'?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                del self.config['groups'][current_group_name]
                self.save_config()
                # Clear all profile and settings information if no groups are left
                if not self.config['groups']:
                    self.current_group = None
                    self.profile_table.clearContents()
                    self.profile_table.setRowCount(0)
                    self.folder_input.clear()
                    self.schedule_time_input.clear()
                    self.start_button.setDisabled(True)
                    self.stop_button.setDisabled(True)
                    self.add_profile_btn.setDisabled(True)
                    self.profile_input.setDisabled(True)
                    self.update_settings_enabled(False)
                    self.group_selector.clear()  # Clear the ComboBox
                    QMessageBox.information(self, "Group Deleted", f"Group '{current_group_name}' has been deleted. All related profiles and settings have been cleared.")
                else:
                    # Update current_group to ensure it's not the deleted group
                    self.current_group = next(iter(self.config['groups']))
                    self.update_group_display()
                    if self.current_group:
                        self.change_group(self.current_group)
                    QMessageBox.information(self, "Group Deleted", f"Group '{current_group_name}' has been deleted.")
            else:
                return
        else:
            QMessageBox.warning(self, "Group Not Found", "The selected group does not exist.")



    def update_ui_components(self):
        """Enable or disable UI components based on the current group selection."""
        if self.current_group and self.current_group in self.config['groups']:
            # Enable components if a group is selected
            self.profile_table.setEnabled(True)
            self.folder_input.setEnabled(True)
            self.schedule_time_input.setEnabled(True)
            self.start_button.setEnabled(not self.config['groups'][self.current_group]['is_scheduled'])
            self.start_button.setStyleSheet("background-color: grey; color: white;" if self.config['groups'][self.current_group]['is_scheduled'] else "background-color: #4CAF50; color: white;")
            self.stop_button.setEnabled(self.config['groups'][self.current_group]['is_scheduled'])
            self.add_profile_btn.setEnabled(True)
            self.profile_input.setEnabled(True)
            self.update_video_counts()  # Add this line to ensure video counts are updated
            self.update_settings_enabled(not self.config['groups'][self.current_group]['is_scheduled'])
        else:
            # Disable components if no group is selected
            self.profile_table.setDisabled(True)
            self.profile_table.clearContents()
            self.profile_table.setRowCount(0)
            self.folder_input.clear()
            self.schedule_time_input.clear()
            self.start_button.setDisabled(True)
            self.stop_button.setDisabled(True)
            self.add_profile_btn.setDisabled(True)
            self.profile_input.setDisabled(True)
            self.update_settings_enabled(False)

    def update_settings_enabled(self, enabled):
        """Enable or disable settings input fields."""
        self.folder_input.setEnabled(enabled)
        self.folder_btn.setEnabled(enabled)
        self.schedule_time_input.setEnabled(enabled)
        self.profile_spin_box.setEnabled(enabled)

    def change_group(self, group):
        if group in self.config['groups']:
            self.current_group = group
            group_config = self.config['groups'][group]
            self.profile_table.setRowCount(0)
            for profile_id, profile_info in group_config['PROFILE_ID'].items():
                self.add_profile_item(profile_id, profile_info['name'], profile_info.get('videos_uploaded', 0), profile_info.get('videos_remaining', 0), profile_info.get('videos_error', 0))
            self.folder_input.setText(group_config['FOLDER_VIDEO_BASE'])
            schedule_time = QTime.fromString(group_config['SCHEDULE_TIME'], "HH:mm")
            self.schedule_time_input.setTime(schedule_time)
            max_profiles = len(group_config['PROFILE_ID'])
            self.profile_spin_box.setMaximum(max_profiles if max_profiles > 0 else 1)
            self.profile_spin_box.setValue(group_config['MAX_CONCURRENT_PROFILES'])
            self.update_video_counts()  # Cập nhật số lượng video khi nhóm thay đổi

    def add_profile_item(self, profile_id, profile_name, uploaded_videos, remaining_videos, error_videos):
        row_position = self.profile_table.rowCount()
        self.profile_table.insertRow(row_position)

        self.profile_table.setItem(row_position, 0, QTableWidgetItem(profile_id))
        self.profile_table.setItem(row_position, 1, QTableWidgetItem(profile_name))
        self.profile_table.setItem(row_position, 2, QTableWidgetItem(str(uploaded_videos)))
        self.profile_table.setItem(row_position, 3, QTableWidgetItem(str(remaining_videos)))
        self.profile_table.setItem(row_position, 4, QTableWidgetItem(str(error_videos)))

        action_layout = QHBoxLayout()

        edit_button = QPushButton('Edit')
        edit_button.setStyleSheet("background-color: #2196F3; color: white; height: 25px; width: 50px;")
        edit_button.clicked.connect(lambda _, pid=profile_id: self.edit_profile_id(pid))
        action_layout.addWidget(edit_button)

        delete_button = QPushButton('Delete')
        delete_button.setStyleSheet("background-color: #f44336; color: white; height: 25px; width: 50px;")
        delete_button.clicked.connect(lambda _, pid=profile_id: self.delete_profile_id(pid))
        action_layout.addWidget(delete_button)

        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        self.profile_table.setCellWidget(row_position, 5, action_widget)

    def toggle_all_checkboxes(self, state):
        for index in range(self.profile_list.count()):
            item = self.profile_list.item(index)
            widget = self.profile_list.itemWidget(item)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(state == Qt.Checked)

    def update_config(self, key, value):
        if key in ['SCHEDULE_TIME', 'FOLDER_VIDEO_BASE', 'PATH_MAIN', 'MAX_CONCURRENT_PROFILES']:
            self.config['groups'][self.current_group][key] = value
        elif key == 'PROFILE_ID':
            if value not in self.config['groups'][self.current_group][key]:
                self.config['groups'][self.current_group][key].append(value)
        self.save_config()

    def select_folder(self, key):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_input.setText(folder_path)
            self.update_config(key, folder_path)
            self.file_watcher.addPath(folder_path)
            self.update_video_counts()  # Cập nhật số lượng video khi thư mục thay đổi

    def select_file(self, key):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", filter="Python Files (*.py)")
        if file_path:
            self.update_config(key, file_path)

    def add_profile_id(self):
        new_id = self.profile_input.text().strip()
        if not new_id:
            QMessageBox.warning(self, "Invalid Input", "Profile ID cannot be empty.")
            return

        if new_id in self.config['groups'][self.current_group]['PROFILE_ID']:
            QMessageBox.warning(self, "Duplicate ID", "This profile ID already exists in the list.")
            return

        api_url = f"http://127.0.0.1:19995/api/v3/profiles/{new_id}"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                profile_data = response.json()
                if profile_data['success']:
                    profile_name = profile_data['data'].get('name', 'Unknown Profile Name')
                    videos_uploaded = profile_data['data'].get('videos_uploaded', 0)
                    videos_remaining = profile_data['data'].get('videos_remaining', 0)
                    videos_error = profile_data['data'].get('videos_error', 0)
                else:
                    QMessageBox.warning(self, "API Error", "Profile ID không có.")
                    return
            else:
                QMessageBox.warning(self, "API Error", "Failed to retrieve profile data.")
                return
        except requests.RequestException as e:
            QMessageBox.critical(self, "API Request Failed", f"Failed to retrieve profile name: {str(e)}")
            return

        self.config['groups'][self.current_group]['PROFILE_ID'][new_id] = {
            "name": profile_name,
            "videos_uploaded": videos_uploaded,
            "videos_remaining": videos_remaining,
            "videos_error": videos_error
        }
        self.save_config()
        self.profile_input.clear()
        self.add_profile_item(new_id, profile_name, videos_uploaded, videos_remaining, videos_error)
        self.update_video_counts()  # Cập nhật ngay lập tức số lượng video

    def edit_profile_id(self, profile_id):
        dialog = EditDialog(self)
        if dialog.exec_():
            new_id = dialog.get_new_id()
            if new_id and new_id != profile_id:
                if new_id in self.config['groups'][self.current_group]['PROFILE_ID']:
                    QMessageBox.warning(self, "Duplicate ID", "This profile ID already exists in the list.")
                    return

                api_url = f"http://127.0.0.1:19995/api/v3/profiles/{new_id}"
                try:
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        profile_data = response.json()
                        if profile_data['success']:
                            new_profile_name = profile_data['data'].get('name', 'Unknown Profile Name')
                            videos_uploaded = profile_data['data'].get('videos_uploaded', 0)
                            videos_remaining = profile_data['data'].get('videos_remaining', 0)
                            videos_error = profile_data['data'].get('videos_error', 0)
                        else:
                            QMessageBox.warning(self, "API Error", "Profile ID không có.")
                            return
                    else:
                        QMessageBox.warning(self, "API Error", "Failed to retrieve profile data.")
                        return
                except requests.RequestException as e:
                    QMessageBox.critical(self, "API Request Failed", f"Failed to retrieve profile name: {str(e)}")
                    return

                self.config['groups'][self.current_group]['PROFILE_ID'][new_id] = {
                    "name": new_profile_name,
                    "videos_uploaded": videos_uploaded,
                    "videos_remaining": videos_remaining,
                    "videos_error": videos_error
                }
                del self.config['groups'][self.current_group]['PROFILE_ID'][profile_id]
                self.save_config()
                self.update_profile_display(new_id, new_profile_name, videos_uploaded, videos_remaining, videos_error)
                self.update_video_counts()  # Cập nhật ngay lập tức số lượng video

    def delete_profile_id(self, profile_id):
        if QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the profile '{profile_id}'?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if profile_id in self.config['groups'][self.current_group]['PROFILE_ID']:
                del self.config['groups'][self.current_group]['PROFILE_ID'][profile_id]
                self.save_config()
                self.update_profile_display(profile_id, "", "", "", "")
                self.update_video_counts()  # Cập nhật ngay lập tức số lượng video

    def update_group_display(self):
        self.group_selector.blockSignals(True)
        self.group_selector.clear()
        for group_name, group_info in self.config['groups'].items():
            is_scheduled = group_info.get('is_scheduled', False)
            display_text = f"{group_name} - {'đang hẹn giờ' if is_scheduled else 'chưa hẹn giờ'}"
            self.group_selector.addItem(display_text)
            self.group_selector.setItemData(self.group_selector.count() - 1, QColor('green' if is_scheduled else 'red'), Qt.ForegroundRole)
        self.group_selector.blockSignals(False)
        if self.current_group:
            is_scheduled = self.config['groups'][self.current_group].get('is_scheduled', False)
            self.group_selector.setCurrentText(f"{self.current_group} - {'đang hẹn giờ' if is_scheduled else 'chưa hẹn giờ'}")
        else:
            self.disable_ui_components()

    def start_process(self):
        print("Attempting to start process...")
        print(f"Current group when starting: {self.current_group}")
        if self.current_group and self.current_group in self.config['groups']:
            if not self.config['groups'][self.current_group]['PROFILE_ID']:
                QMessageBox.warning(self, "No Profiles", "There are no profiles in the current group.")
                return

            self.config['groups'][self.current_group]['is_scheduled'] = True
            self.save_config()
            self.update_group_display()
            path_main = self.config['groups'][self.current_group].get('FOLDER_VIDEO_BASE')
            if path_main:
                scheduler_script = 'scheduler.py'
                try:
                    print(f"Starting the scheduler for group {self.current_group}...")
                    process = subprocess.Popen(['python', scheduler_script, self.current_group])
                    self.processes.append(process)
                    self.start_button.setEnabled(False)
                    self.start_button.setStyleSheet("background-color: grey; color: white;")
                    self.stop_button.setEnabled(True)
                    self.update_settings_enabled(False)  # Disable settings input fields when process starts
                    QMessageBox.information(self, "Process Started", f"The scheduler has been started successfully for group {self.current_group}.")
                except Exception as e:
                    QMessageBox.critical(self, "Process Failed", str(e))
            else:
                QMessageBox.warning(self, "Configuration Error", "Folder video Path is not configured for this group.")
        else:
            QMessageBox.warning(self, "No Group Selected", "Please select a group before starting the process.")

    def stop_process(self):
        if self.current_group and self.current_group in self.config['groups']:
            self.config['groups'][self.current_group]['is_scheduled'] = False
            self.save_config()
            self.update_group_display()
        for process in self.processes:
            process.terminate()
        self.processes.clear()
        self.start_button.setEnabled(True)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.stop_button.setEnabled(False)
        self.update_settings_enabled(True)  # Enable settings input fields when process stops
        QMessageBox.information(self, "Process Stopped", "All processes have been stopped.")

    def disable_ui_components(self):
        """Disable UI components that should not be accessible without an active group."""
        self.profile_table.setDisabled(True)
        self.folder_input.setDisabled(True)
        self.schedule_time_input.setDisabled(True)
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(True)
        self.add_profile_btn.setDisabled(True)
        self.profile_input.setDisabled(True)
        self.update_settings_enabled(False)

    def refresh_profiles(self):
        if self.current_group is None:
            return

        api_url = "http://127.0.0.1:19995/api/v3/profiles"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                profiles_data = response.json().get('data', [])
                for profile in profiles_data:
                    profile_id = profile.get('id')
                    profile_name = profile.get('name')
                    videos_uploaded = profile.get('videos_uploaded', 0)
                    videos_remaining = profile.get('videos_remaining', 0)
                    videos_error = profile.get('videos_error', 0)
                    if profile_id in self.config['groups'][self.current_group]['PROFILE_ID']:
                        profile_info = self.config['groups'][self.current_group]['PROFILE_ID'][profile_id]
                        if (profile_info['name'] != profile_name or
                            profile_info['videos_uploaded'] != videos_uploaded or
                            profile_info['videos_remaining'] != videos_remaining or
                            profile_info['videos_error'] != videos_error):
                            profile_info['name'] = profile_name
                            profile_info['videos_uploaded'] = videos_uploaded
                            profile_info['videos_remaining'] = videos_remaining
                            profile_info['videos_error'] = videos_error
                            self.update_profile_display(profile_id, profile_name, videos_uploaded, videos_remaining, videos_error)
                self.save_config()
                self.update_video_counts()
            else:
                QMessageBox.warning(self, "API Error", "Failed to retrieve profiles.")
        except requests.RequestException as e:
            QMessageBox.critical(self, "API Request Failed", f"Failed to refresh profiles: {str(e)}")

    def update_profile_display(self, profile_id, profile_name, uploaded_videos, remaining_videos, error_videos):
        for row in range(self.profile_table.rowCount()):
            if self.profile_table.item(row, 0).text() == profile_id:
                self.profile_table.setItem(row, 1, QTableWidgetItem(profile_name))
                self.profile_table.setItem(row, 2, QTableWidgetItem(str(uploaded_videos)))
                self.profile_table.setItem(row, 3, QTableWidgetItem(str(remaining_videos)))
                self.profile_table.setItem(row, 4, QTableWidgetItem(str(error_videos)))
                break

    def update_video_counts(self):
        if self.current_group and self.current_group in self.config['groups']:
            video_folder = self.config['groups'][self.current_group].get('FOLDER_VIDEO_BASE', "")
            for profile_id in self.config['groups'][self.current_group]['PROFILE_ID']:
                profile_video_path = os.path.join(video_folder, profile_id)
                if os.path.exists(profile_video_path):
                    uploaded_videos = len([f for f in os.listdir(profile_video_path) if f.endswith('_done.mp4')])
                    total_videos = len([f for f in os.listdir(profile_video_path) if f.endswith('.mp4')])
                    error_videos = len([f for f in os.listdir(profile_video_path) if f.endswith('_error.mp4')])
                    remaining_videos = total_videos - uploaded_videos - error_videos
                else:
                    uploaded_videos = 0
                    remaining_videos = 0
                    error_videos = 0
                
                self.config['groups'][self.current_group]['PROFILE_ID'][profile_id]['videos_uploaded'] = uploaded_videos
                self.config['groups'][self.current_group]['PROFILE_ID'][profile_id]['videos_remaining'] = remaining_videos
                self.config['groups'][self.current_group]['PROFILE_ID'][profile_id]['videos_error'] = error_videos
                self.save_config()
                
                self.update_profile_display(profile_id, self.config['groups'][self.current_group]['PROFILE_ID'][profile_id]['name'], uploaded_videos, remaining_videos, error_videos)

    def filter_profiles(self, search_text):
        search_text = search_text.lower()
        for row in range(self.profile_table.rowCount()):
            profile_name = self.profile_table.item(row, 1).text().lower()
            self.profile_table.setRowHidden(row, search_text not in profile_name)