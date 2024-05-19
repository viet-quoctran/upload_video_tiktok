from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton

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
