import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QTextEdit, QMessageBox

class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Backup Application')
        self.setGeometry(100, 100, 400, 400)
        
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
        
        self.backup_button = QPushButton('Start Backup')
        self.backup_button.clicked.connect(self.start_backup)
        layout.addWidget(self.backup_button)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        self.central_widget.setLayout(layout)
        
        self.source_directory = ""
        self.destination_directory = ""
        self.override_all = False
        self.skip_all = False
        
    def select_source_directory(self):
        self.source_directory = QFileDialog.getExistingDirectory(self, 'Select Source Directory')
        self.source_label.setText(f'Source directory: {self.source_directory}')
        
    def select_destination_directory(self):
        self.destination_directory = QFileDialog.getExistingDirectory(self, 'Select Destination Directory')
        self.destination_label.setText(f'Destination directory: {self.destination_directory}')
        
    def start_backup(self):
        if self.source_directory and self.destination_directory:
            python_source_directory = self.normalize_path(self.source_directory)
            python_destination_directory = self.normalize_path(self.destination_directory)
            self.copy_new_and_modified_files(python_source_directory, python_destination_directory)
        else:
            self.output_text.append("Please select both source and destination directories.")
            
    def normalize_path(self, path):
        return os.path.normpath(path)
    
    def copy_new_and_modified_files(self, src, dst):
        self.override_all = False
        self.skip_all = False
        # Walk through the source directory
        for root, _, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                # Determine the corresponding destination file path
                dst_file = os.path.join(dst, os.path.relpath(src_file, src))
                
                # Create target directories if they don't exist
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                
                # Copy the file if it doesn't exist in the destination or is newer
                if not os.path.exists(dst_file) or os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                    if os.path.exists(dst_file):
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
                    self.output_text.append(f"Copied {src_file} to {dst_file}")
    
    def ask_override(self, filename):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('File Overwrite Confirmation')
        msg_box.setText(f'The file "{filename}" has been modified. Do you want to overwrite it?')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.YesToAll | QMessageBox.NoToAll)
        msg_box.setDefaultButton(QMessageBox.Yes)
        return msg_box.exec_()

if __name__ == '__main__':
    app = QApplication([])
    window = BackupApp()
    window.show()
    app.exec_()
