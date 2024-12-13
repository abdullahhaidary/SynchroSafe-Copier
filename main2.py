import os
import shutil
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QTextEdit, QMessageBox
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QTextCharFormat, QColor, QIcon

class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Backup Application')
        self.setGeometry(100, 100, 500, 600)  # Adjusted height to accommodate new button
        self.setWindowIcon(QIcon('icon.png'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.source_label = QLabel('Select source directory:')
        layout.addWidget(self.source_label)

        self.source_button = QPushButton('Browse...')
        self.source_button.clicked.connect(self.select_source_directory)
        layout.addWidget(self.source_button)

        self.destination_label = QLabel('Select destination directory:')
        layout.addWidget(self.destination_label)

        self.destination_button = QPushButton('Browse...')
        self.destination_button.clicked.connect(self.select_destination_directory)
        layout.addWidget(self.destination_button)

        self.check_button = QPushButton('Check Files')
        self.check_button.clicked.connect(self.check_files)
        layout.addWidget(self.check_button)

        self.backup_button = QPushButton('Start Backup')
        self.backup_button.clicked.connect(self.start_backup)
        layout.addWidget(self.backup_button)

        self.clear_button = QPushButton('Clear Output')
        self.clear_button.clicked.connect(self.clear_output)
        layout.addWidget(self.clear_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.central_widget.setLayout(layout)

        self.source_directory = ""
        self.destination_directory = ""
        self.override_all = False
        self.skip_all = False

        # Initialize QSettings
        self.settings = QSettings('MyCompany', 'BackupApp')
        self.load_settings()

    def load_settings(self):
        self.source_directory = self.settings.value('source_directory', "")
        self.destination_directory = self.settings.value('destination_directory', "")
        self.source_label.setText(f'Source directory: {self.source_directory}')
        self.destination_label.setText(f'Destination directory: {self.destination_directory}')

    def save_settings(self):
        self.settings.setValue('source_directory', self.source_directory)
        self.settings.setValue('destination_directory', self.destination_directory)

    def select_source_directory(self):
        self.source_directory = QFileDialog.getExistingDirectory(self, 'Select Source Directory')
        self.source_label.setText(f'Source directory: {self.source_directory}')
        self.save_settings()

    def select_destination_directory(self):
        self.destination_directory = QFileDialog.getExistingDirectory(self, 'Select Destination Directory')
        self.destination_label.setText(f'Destination directory: {self.destination_directory}')
        self.save_settings()

    def start_backup(self):
        if self.source_directory and self.destination_directory:
            python_source_directory = self.normalize_path(self.source_directory)
            python_destination_directory = self.normalize_path(self.destination_directory)
            try:
                self.copy_new_and_modified_files(python_source_directory, python_destination_directory)
            except Exception as e:
                self.log_to_output(f"Error during backup: {str(e)}", QColor("red"))
                self.log_to_output("Detailed Traceback:\n" + traceback.format_exc(), QColor("red"))
        else:
            self.output_text.append("Please select both source and destination directories.")

    def check_files(self):
        if self.source_directory and self.destination_directory:
            python_source_directory = self.normalize_path(self.source_directory)
            python_destination_directory = self.normalize_path(self.destination_directory)
            try:
                self.check_new_and_modified_files(python_source_directory, python_destination_directory)
            except Exception as e:
                self.log_to_output(f"Error checking files: {str(e)}", QColor("red"))
                self.log_to_output("Detailed Traceback:\n" + traceback.format_exc(), QColor("red"))
        else:
            self.output_text.append("Please select both source and destination directories.")

    def normalize_path(self, path):
        return os.path.normpath(path)

    def check_new_and_modified_files(self, src, dst):
        try:
            for root, _, files in os.walk(src):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst, os.path.relpath(src_file, src))
                    if not os.path.exists(dst_file):
                        self.log_to_output(f"New file: {src_file}", QColor("green"))
                    elif os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                        self.log_to_output(f"Modified file: {src_file}", QColor("red"))
        except Exception as e:
            self.log_to_output(f"Error checking files: {str(e)}", QColor("red"))

    def copy_new_and_modified_files(self, src, dst):
        self.override_all = False
        self.skip_all = False
        try:
            # Walk through the source directory
            for root, _, files in os.walk(src):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst, os.path.relpath(src_file, src))

                    # Create target directories if they don't exist
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                    # Copy the file if it doesn't exist in the destination or is newer
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
                        self.log_to_output(f"Copied {src_file} to {dst_file}", QColor("green"))
                    elif os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                        if self.skip_all:
                            continue
                        if not self.override_all:
                            reply = self.ask_override(file)
                            if reply == QMessageBox.Yes:
                                pass
                            elif reply == QMessageBox.No:
                                continue
                            elif reply == QMessageBox.YesToAll:
                                self.override_all = True
                            elif reply == QMessageBox.NoToAll:
                                self.skip_all = True
                                continue
                        shutil.copy2(src_file, dst_file)
                        self.log_to_output(f"Overwritten {src_file} to {dst_file}", QColor("red"))
        except Exception as e:
            self.log_to_output(f"Error during backup: {str(e)}", QColor("red"))
            self.log_to_output("Detailed Traceback:\n" + traceback.format_exc(), QColor("red"))

    def ask_override(self, filename):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('File Overwrite Confirmation')
        msg_box.setText(f'The file "{filename}" has been modified. Do you want to overwrite it?')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.YesToAll | QMessageBox.NoToAll)
        msg_box.setDefaultButton(QMessageBox.Yes)
        return msg_box.exec_()

    def log_to_output(self, message, color):
        format = QTextCharFormat()
        format.setForeground(color)
        self.output_text.setCurrentCharFormat(format)
        self.output_text.append(message)

    def clear_output(self):
        self.output_text.clear()

if __name__ == '__main__':
    app = QApplication([])
    window = BackupApp()
    window.show()
    app.exec_()
