#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import (QDir, Qt)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QApplication,
                             QPushButton, QFileDialog, QAction, QDialogButtonBox, QMessageBox)

import HelpForm
import ValidateCSV


# TODO:
# 1. non-native dialogs is used to cope with my arch/gnome setup.
# - leave as is or can i use a test to determine what to show?
# 2. arch/gnome doesn't show detail button in messagebox dialog. leave as is or provide workaround/alternate messagebox?
# 3. validation certificate not to be provided by default
# - add as an option to the main form above the 'exit' menu option.
# 4. improve layout: 
# 4.1. add text box for the CSV file and format file that are populated when selected.
# 4.2. better button positioning .


class CSVValidatorForm(QMainWindow):
    def __init__(self, parent=None):
        super(CSVValidatorForm, self).__init__(parent)
        self.statusBar().showMessage('Ready...', 2000)
        self.button_csv = QPushButton("CSV File")
        self.button_format_file = QPushButton("Format File")
        self.button_ok = QDialogButtonBox.Ok
        self.button_cancel = QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(self.button_ok | self.button_cancel)
        self.menu_bar = self.menuBar()

        self.width = 300
        self.height = 300

        self.file_csv = None
        self.file_format_file = None
        self.text_window_title = 'CSV Validation Utility'

        self.init_ui()

    def init_ui(self):
        self.resize(self.width, self.height)
        self.setWindowTitle(self.text_window_title)

        self.button_csv.setFixedWidth(110)
        self.button_format_file.setFixedWidth(110)

        self.button_csv.setStatusTip("Choose a CSV file.")
        self.button_csv.clicked.connect(self.button_getfile_csv_clicked)
        self.button_format_file.setStatusTip("Choose a format file.")
        self.button_format_file.clicked.connect(self.button_getfile_format_clicked)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Validate")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.button_ok_clicked)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.button_cancel_clicked)

        action_exit = QAction(QIcon('exit.png'), '&Exit', self)
        action_exit.setShortcut('Ctrl+Q')
        action_exit.setStatusTip('Exit application')
        action_exit.triggered.connect(self.button_cancel_clicked)

        action_help = QAction(QIcon('help.png'), '&Help', self)
        action_help.setShortcut('Ctrl+H')
        action_help.setStatusTip('Launch help')
        action_help.triggered.connect(self.button_help_clicked)

        menu_file = self.menu_bar.addMenu('&File')
        menu_help = self.menu_bar.addMenu('&Help')
        menu_file.addAction(action_exit)
        menu_help.addAction(action_help)

        self.apply_layout()

    def apply_layout(self):
        form_layout = QWidget()

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.button_csv, 1, 0)
        grid.addWidget(self.button_format_file, 2, 0)
        grid.addWidget(self.buttonBox, 3, 0)

        form_layout.setLayout(grid)
        self.setCentralWidget(form_layout)

    def apply_layout_box(self):
        form_layout = QWidget()

        h_box = QHBoxLayout()
        h_box.addWidget(self.button_csv)
        h_box.addWidget(self.button_format_file)

        h_box_ok_cancel = QHBoxLayout()
        h_box_ok_cancel.setAlignment(Qt.AlignLeft)
        h_box_ok_cancel.addWidget(self.buttonBox)

        v_box = QVBoxLayout()
        v_box.addLayout(h_box)
        v_box.addLayout(h_box_ok_cancel)

        form_layout.setLayout(v_box)
        self.setCentralWidget(form_layout)

    def button_getfile_csv_clicked(self):
        sender_caption = "Select the csv file..."
        sender_file_filter = "TSV (*.txt *.csv *.tsv)"
        self.statusBar().showMessage(sender_caption, 5000)
        file = self.getfile(sender_caption, sender_file_filter)
        if file:
            self.file_csv = QDir.toNativeSeparators(file[0])
            self.button_csv.setStatusTip(self.file_csv)
            self.check_files_are_set()

    def button_getfile_format_clicked(self):
        sender_caption = "Select the format file file..."
        sender_file_filter = "BCP Format Files (*.xml)"
        self.statusBar().showMessage(sender_caption, 5000)
        file = self.getfile(sender_caption, sender_file_filter)
        if file:
            self.file_format_file = QDir.toNativeSeparators(file[0])
            self.button_format_file.setStatusTip(self.file_format_file)
            self.check_files_are_set()

    def check_files_are_set(self):
        if self.file_csv and self.file_format_file:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def button_ok_clicked(self):
        v_csv = ValidateCSV.ValidateCSV(self.file_format_file, self.file_csv)
        self.show_message(v_csv.validate_state, v_csv.validate_message_title,
                          v_csv.validate_message_text, v_csv.validate_message_detailed)

    def button_cancel_clicked(self):
        self.statusBar().showMessage("bye")
        self.close()

    @staticmethod
    def button_help_clicked():
        # retval = HelpForm.HelpForm()
        HelpForm.HelpForm()

    def getfile(self, sender_caption, sender_file_filter):
        form_options = QFileDialog.DontUseNativeDialog
        file_path = QFileDialog().getOpenFileName(self, sender_caption, ''
                                                  , sender_file_filter, options=form_options)
        return file_path

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.button_cancel_clicked()

    @staticmethod
    def show_message(message_state, message_title, message_text, message_detail):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("CSV Validator")

        if message_state:
            icon_type = QMessageBox.Information
        else:
            icon_type = QMessageBox.Critical
        msg.setIcon(icon_type)

        msg.setText(message_title + '                                              ')
        msg.setInformativeText(message_text)
        if message_detail:
            msg.setDetailedText(message_detail)
        msg.setStandardButtons(QMessageBox.Ok)
        # retval = msg.exec_()
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CSVValidatorForm()
    ex.show()
    sys.exit(app.exec_())
