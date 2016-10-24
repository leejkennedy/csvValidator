#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import (Qt)
from PyQt5.QtWidgets import (QDialog, QTextBrowser, QGridLayout)


class HelpForm(QDialog):
    def __init__(self, parent=None):
        super(HelpForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)
        # self.setOpenExternalLinks(True)
        self.resize(500, 500)
        self.html_help = '''
    <!DOCTYPE html>
    <html>
       <head>
          <meta charset="utf-8">
          <title>CSV Validator</title>
       </head>
       <body>
          <header role="banner">
             <h1>CSV Validator</h1>
          </header>
            <p>Validate a CSV file against a BCP format file. If the CSV matches the structure
        described by the format file, you can create a validation certificate.</p>
            <p>The tool currently only validates files with tab-separated values and without any text-qualifier.</p>
            <h3>TODO</h3>
                <ul>
                    <li>Allow different delimiters</li>
                    <li>Allow text-qualifiers</li>
                    <li>Fixed-Width files</li>
                </ul>

        <hr/>
          <footer style="vertical-align:bottom">
             <p>Created by Lee Kennedy</a></p>
          </footer>
       </body>
    </html>'''


        #
        # This utility checks:
        # + the CSV file has the correct number of columns.
        # + each column has the correct, case-sensitive, name.
        # + each data item in each column matches the data type for that column.

        self.browser = QTextBrowser()
        self.browser.setHtml(self.html_help)
        self.layout = QGridLayout()
        self.layout.addWidget(self.browser, 1, 1, 1, 1)
        self.setWindowTitle("Help")
        self.setLayout(self.layout)
        self.show()
        self.exec_()  # wait for user
