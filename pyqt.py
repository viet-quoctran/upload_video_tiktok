import sys
import json
import requests
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLineEdit, QHBoxLayout, QListWidget, QFormLayout,
                             QMessageBox, QTimeEdit, QDialog, QFileDialog, QComboBox)
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtGui import QColor

class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Profile ID')
        self.setLayout(QVBoxLayout())
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Enter new profile ID...")
        self.layout().addWidget(self.input)
        self.button = QPushButton('Update', self)
        self.button.clicked.connect(self.accept)
        self.layout().addWidget(self.button)

    def get_new_id(self):
        return self.input.text()

class CreateGroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Create New Group')
        self.setLayout(QVBoxLayout())
        self.group_name_input = QLineEdit(self)
        self.group_name_input.setPlaceholderText("Enter new group name...")
        self.layout().addWidget(self.group_name_input)
        self.create_button = QPushButton('Create Group', self)
        self.create_button.clicked.connect(self.accept)
        self.layout().addWidget(self.create_button)

    def get_group_name(self):
        return self.group_name_input.text()

class EditGroupDialog(QDialog):
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Group Name')
        self.setLayout(QVBoxLayout())
        self.group_name_input = QLineEdit(self)
        self.group_name_input.setText(current_name)
        self.layout().addWidget(self.group_name_input)
        self.update_button = QPushButton('Update Name', self)
        self.update_button.clicked.connect(self.accept)
        self.layout().addWidget(self.update_button)

    def get_group_name(self):
        return self.group_name_input.text()

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.processes = []
        self.config = self.load_config()
        self.current_group = None
        self.initUI()
        self.update_ui_components()

    def load_config(self):
        try:
            with open('settings.json', 'r') as config_file:
                return json.load(config_file)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Settings", str(e))
            return {}

    def save_config(self):
        try:
            with open('settings.json', 'w') as config_file:
                json.dump(self.config, config_file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving Settings", str(e))

    def initUI(self):
        self.setWindowTitle('Automation Upload Tool')
        self.setGeometry(100, 100, 600, 400)
        main_layout = QVBoxLayout(self)

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

        main_layout.addLayout(group_button_layout)

        form_layout = QFormLayout()
        self.group_selector = QComboBox(self)
        self.group_selector.currentTextChanged.connect(self.on_group_selected)
        form_layout.addRow("Select Group:", self.group_selector)

        self.profile_list = QListWidget(self)
        form_layout.addRow("Profile IDs:", self.profile_list)

        self.profile_input = QLineEdit(self)
        self.profile_input.setPlaceholderText("Enter new profile ID...")
        self.add_profile_btn = QPushButton('Add', self)
        self.add_profile_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.add_profile_btn.clicked.connect(self.add_profile_id)

        profile_buttons = QHBoxLayout()
        profile_buttons.addWidget(self.add_profile_btn)

        self.edit_profile_btn = QPushButton('Edit', self)  # Ensure this button is defined
        self.edit_profile_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.edit_profile_btn.clicked.connect(self.edit_profile_id)
        profile_buttons.addWidget(self.edit_profile_btn)

        self.delete_profile_btn = QPushButton('Delete', self)
        self.delete_profile_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_profile_btn.clicked.connect(self.delete_profile_id)
        profile_buttons.addWidget(self.delete_profile_btn)

        form_layout.addRow("Profile ID:", self.profile_input)
        form_layout.addRow("", profile_buttons)

        self.folder_input = QLineEdit(self)
        self.folder_btn = QPushButton("Browse...", self)
        self.folder_btn.setStyleSheet("background-color: #607D8B; color: white;")
        self.folder_btn.clicked.connect(lambda: self.select_folder('FOLDER_VIDEO_BASE'))
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.folder_btn)
        form_layout.addRow("Folder Path:", folder_layout)

        self.path_main_input = QLineEdit(self)
        self.path_main_btn = QPushButton("Browse...", self)
        self.path_main_btn.setStyleSheet("background-color: #607D8B; color: white;")
        self.path_main_btn.clicked.connect(lambda: self.select_file('PATH_MAIN'))
        path_main_layout = QHBoxLayout()
        path_main_layout.addWidget(self.path_main_input)
        path_main_layout.addWidget(self.path_main_btn)
        form_layout.addRow("Path Main:", path_main_layout)

        self.schedule_time_input = QTimeEdit(self)
        self.schedule_time_input.setDisplayFormat("HH:mm")
        form_layout.addRow("Schedule Time:", self.schedule_time_input)
        self.schedule_time_input.timeChanged.connect(lambda time: self.update_config('SCHEDULE_TIME', time.toString("HH:mm")))

        main_layout.addLayout(form_layout)

        self.start_button = QPushButton("Start", self)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_process)
        main_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_button.clicked.connect(self.stop_process)
        main_layout.addWidget(self.stop_button)

        self.update_group_display()
        if self.current_group:
            self.change_group(self.current_group)
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
                # Initialize PROFILE_ID as an empty dictionary instead of a list
                self.config['groups'][new_group_name] = {
                    "PROFILE_ID": {},
                    "FOLDER_VIDEO_BASE": "",
                    "PATH_MAIN": "",
                    "SCHEDULE_TIME": "00:00",
                    "is_scheduled": False
                }
                self.save_config()
                self.update_group_display()
                self.change_group(new_group_name)
                QMessageBox.information(self, "Success", "New group created.")
                self.group_selector.setCurrentText(new_group_name)  # Ensure new group is selected

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
                self.update_group_display()
                QMessageBox.information(self, "Group Updated", f"Group name updated from '{current_group_name}' to '{new_group_name}'.")

    def delete_group(self):
        current_group_name = self.group_selector.currentText().split(" - ")[0]
        if current_group_name in self.config['groups']:
            if QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the group '{current_group_name}'?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                del self.config['groups'][current_group_name]
                self.save_config()
                self.update_group_display()
                if self.config['groups']:
                    self.current_group = next(iter(self.config['groups']))
                    self.change_group(self.current_group)
                else:
                    self.current_group = None
                QMessageBox.information(self, "Group Deleted", f"Group '{current_group_name}' has been deleted.")
            else:
                return
        else:
            QMessageBox.warning(self, "Group Not Found", "The selected group does not exist.")
    def update_ui_components(self):
        """Enable or disable UI components based on the current group selection."""
        if self.current_group and self.current_group in self.config['groups']:
            # Enable components if a group is selected
            self.profile_list.setEnabled(True)
            self.folder_input.setEnabled(True)
            self.path_main_input.setEnabled(True)
            self.schedule_time_input.setEnabled(True)
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.add_profile_btn.setEnabled(True)
            self.edit_profile_btn.setEnabled(True)
            self.delete_profile_btn.setEnabled(True)
        else:
            # Disable components if no group is selected
            self.profile_list.clear()
            self.folder_input.clear()
            self.path_main_input.clear()
            self.schedule_time_input.clear()
            self.start_button.setDisabled(True)
            self.stop_button.setDisabled(True)
            self.add_profile_btn.setDisabled(True)
            self.edit_profile_btn.setDisabled(True)
            self.delete_profile_btn.setDisabled(True)
    def change_group(self, group):
        if group in self.config['groups']:
            self.current_group = group
            group_config = self.config['groups'][group]
            self.profile_list.clear()
            for profile_id, profile_name in group_config['PROFILE_ID'].items():
                self.profile_list.addItem(f"{profile_name} ({profile_id})")
            self.folder_input.setText(group_config['FOLDER_VIDEO_BASE'])
            self.path_main_input.setText(group_config['PATH_MAIN'])
            schedule_time = QTime.fromString(group_config['SCHEDULE_TIME'], "HH:mm")
            self.schedule_time_input.setTime(schedule_time)

    def update_config(self, key, value):
        if key in ['SCHEDULE_TIME', 'FOLDER_VIDEO_BASE', 'PATH_MAIN']:
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

    def select_file(self, key):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", filter="Python Files (*.py)")
        if file_path:
            self.path_main_input.setText(file_path)
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
                else:
                    QMessageBox.warning(self, "API Error", "Profile ID không có.")
                    return
            else:
                QMessageBox.warning(self, "API Error", "Failed to retrieve profile data.")
                return
        except requests.RequestException as e:
            QMessageBox.critical(self, "API Request Failed", f"Failed to retrieve profile name: {str(e)}")
            return

        display_text = f"{profile_name} ({new_id})"
        self.profile_list.addItem(display_text)
        self.config['groups'][self.current_group]['PROFILE_ID'][new_id] = profile_name
        self.save_config()
        self.profile_input.clear()




    def edit_profile_id(self):
        list_items = self.profile_list.selectedItems()
        if not list_items:
            QMessageBox.warning(self, "Selection Needed", "Please select a profile ID to edit.")
            return

        item = list_items[0]
        old_display_text = item.text()
        old_id = old_display_text.split(" (")[1].rstrip(")")  # Extract ID from display format 'Name (ID)'

        dialog = EditDialog(self)
        if dialog.exec_():
            new_id = dialog.get_new_id()
            if new_id and new_id not in self.config['groups'][self.current_group]['PROFILE_ID']:
                # Fetch new profile info from the GPM Login API
                api_url = f"http://127.0.0.1:19995/api/v3/profiles/{new_id}"
                try:
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        profile_data = response.json()
                        if profile_data['success']:
                            new_profile_name = profile_data['data'].get('name', 'Unknown Profile Name')
                        else:
                            QMessageBox.warning(self, "API Error", "Profile ID không có.")
                            return
                    else:
                        QMessageBox.warning(self, "API Error", "Failed to retrieve profile data.")
                        return
                except requests.RequestException as e:
                    QMessageBox.critical(self, "API Request Failed", f"Failed to retrieve profile name: {str(e)}")
                    return

                # Update the dictionary with new profile info
                self.config['groups'][self.current_group]['PROFILE_ID'].pop(old_id)  # Remove old ID
                self.config['groups'][self.current_group]['PROFILE_ID'][new_id] = new_profile_name  # Add new ID with new name
                new_display_text = f"{new_profile_name} ({new_id})"
                item.setText(new_display_text)  # Update display
                self.save_config()
            else:
                QMessageBox.warning(self, "Duplicate ID", "This profile ID already exists in the list.")

    def delete_profile_id(self):
        list_items = self.profile_list.selectedItems()
        if not list_items:
            return
        for item in list_items:
            display_text = item.text()
            profile_id = display_text.split(" (")[1].rstrip(")")  # Extract ID from display format 'Name (ID)'
            # Remove the profile ID from the dictionary
            self.config['groups'][self.current_group]['PROFILE_ID'].pop(profile_id, None)
            self.profile_list.takeItem(self.profile_list.row(item))
        self.save_config()

    def update_group_display(self):
        current_group_temp = self.current_group 
        self.group_selector.blockSignals(True)
        self.group_selector.clear()
        for group_name, group_info in self.config['groups'].items():
            is_scheduled = group_info.get('is_scheduled', False)
            display_text = f"{group_name} - {'đang hẹn giờ' if is_scheduled else 'chưa hẹn giờ'}"
            self.group_selector.addItem(display_text)
            self.group_selector.setItemData(self.group_selector.count() - 1, QColor('green' if is_scheduled else 'red'), Qt.ForegroundRole)
        self.group_selector.blockSignals(False)  # Cho phép tín hiệu trở lại
        self.group_selector.setCurrentIndex(self.group_selector.findText(current_group_temp))  # Khôi phục lựa chọn hiện tại
        self.current_group = current_group_temp  # Khôi phục giá trị current_group sau khi cập nhật

    def start_process(self):
        print("Attempting to start process...")
        print(f"Current group when starting: {self.current_group}")
        if self.current_group and self.current_group in self.config['groups']:
            self.config['groups'][self.current_group]['is_scheduled'] = True
            self.save_config()
            self.update_group_display()
            path_main = self.config['groups'][self.current_group].get('PATH_MAIN')
            if path_main:
                scheduler_script = 'scheduler.py'
                try:
                    print(f"Starting the scheduler for group {self.current_group}...")
                    process = subprocess.Popen(['python', scheduler_script, self.current_group])
                    self.processes.append(process)
                    QMessageBox.information(self, "Process Started", f"The scheduler has been started successfully for group {self.current_group}.")
                except Exception as e:
                    QMessageBox.critical(self, "Process Failed", str(e))
            else:
                QMessageBox.warning(self, "Configuration Error", "Path to main script is not configured for this group.")
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
        QMessageBox.information(self, "Process Stopped", "All processes have been stopped.")

    def disable_ui_components(self):
        """Disable UI components that should not be accessible without an active group."""
        self.profile_list.setDisabled(True)
        self.folder_input.setDisabled(True)
        self.path_main_input.setDisabled(True)
        self.schedule_time_input.setDisabled(True)
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(True)
        self.add_profile_btn.setDisabled(True)
        self.edit_profile_btn.setDisabled(True)
        self.delete_profile_btn.setDisabled(True)
        self.folder_btn.setDisabled(True)
        self.path_main_btn.setDisabled(True)

    def refresh_profiles(self):
        if self.current_group is None:
            return  # Đảm bảo có nhóm được chọn

        api_url = "http://127.0.0.1:19995/api/v3/profiles"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                profiles_data = response.json().get('data', [])
                for profile in profiles_data:
                    profile_id = profile.get('id')
                    profile_name = profile.get('name')
                    # Kiểm tra và cập nhật nếu có sự khác biệt trong tên
                    if profile_id in self.config['groups'][self.current_group]['PROFILE_ID']:
                        if self.config['groups'][self.current_group]['PROFILE_ID'][profile_id] != profile_name:
                            self.config['groups'][self.current_group]['PROFILE_ID'][profile_id] = profile_name
                            self.update_profile_display(profile_id, profile_name)
                self.save_config()  # Lưu lại cấu hình sau khi cập nhật
        except requests.RequestException as e:
            QMessageBox.critical(self, "API Request Failed", "Failed to refresh profiles: {}".format(str(e)))


    def update_profile_display(self, profile_id, profile_name):
        # Cập nhật hiển thị tên mới trong QListWidget
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            if item.text().endswith("({})".format(profile_id)):
                item.setText("{} ({})".format(profile_name, profile_id))
def main():
    app = QApplication(sys.argv)
    ex = AppWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
