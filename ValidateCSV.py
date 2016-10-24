#!/usr/bin/python3
# -*- coding: utf-8 -*-
import csv
import os
import re

import FormatFile
import utility


class ValidateCSV:
    def __init__(self, formatfile_filepath, csv_filepath):
        self.validate_state = False
        self.validate_type = ""
        self.validate_message_title = ""
        self.validate_message_text = ""
        self.validate_message_detailed = ""
        self.formatfile_filepath = formatfile_filepath
        self.csv_filepath = csv_filepath
        self.currenttime = utility.getcurrenttime()
        self.username = utility.getuser()
        self.delimiterchar = "\t"
        self.validation_certificate_path = None
        self.formatfile_path = utility.path_from_filepath(self.formatfile_filepath)
        self.formatfile_filename = utility.file_from_filepath(self.formatfile_filepath)
        self.csv_path = utility.path_from_filepath(self.csv_filepath)
        self.csv_filename = utility.file_from_filepath(self.csv_filepath)
        self.csv_file = os.path.splitext(self.csv_filename)[0]
        self.csv_createddate = utility.getfiledatetime(self.csv_filepath, 0)
        self.csv_modifieddate = utility.getfiledatetime(self.csv_filepath, 1)
        self.ff = FormatFile.FormatFile(self.formatfile_filepath)
        if not self.ff.isValid:
            self.set_validate(False, "ERROR", "Error:", "Format File is invalid.")
        else:
            self.dic_format_file = self.ff.getfields()
            self.field_count = len(self.dic_format_file)
            self.listcsv = self.getcsv(self)

            self.validateheader(self)
            if self.validate_state:
                # print("Success header")
                self.validatecontent(self)
                if self.validate_state:
                    # print("Success content")
                    self.create_validation_certificate(self)

    def set_validate(self, state, type, title, message, detail=None):
        self.validate_state = state
        self.validate_type = type
        self.validate_message_title = title
        self.validate_message_text = message
        self.validate_message_detailed = detail

    @staticmethod
    def create_validation_certificate(self):
        self.validation_certificate_path = os.path.join(self.csv_path, self.csv_file + "_certificate.txt")
        validation_certificate_items = self.getvaliditems(self)
        with open(self.validation_certificate_path, "w") as fhw:
            fhw.writelines(validation_certificate_items)
            # print(self.validation_certificate_path)

    @staticmethod
    def getvaliditems(self):
        # print(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

        certificate_template = '''
###########################################################################################################
####################################### file validation certificate #######################################
###########################################################################################################

This file was created after the successful validation of '{csv_file_name}'
against the format file '{format_file_name}'.

csv: 		{csv_file_path}
format file:	{format_file_file_path}

The first line of the file is a pipe-delimited, double-quote text-qualified, string of the following data:
validation date time|username|csv file name|csv file modified datetime

Note: all dates above are localtime in ISO 8601 format (yyyy-mm-dd hh:mm:ss).
        '''.format(csv_file_name=self.csv_filename, format_file_name=self.formatfile_filename,
                   csv_file_path=self.csv_filepath, format_file_file_path=self.formatfile_filepath)
        return ('"{current_time}"|"{username}"|"{csv_filename}"|"{csv_modified_date}"'.format(
            current_time=self.currenttime, username=self.username, csv_filename=self.csv_filename,
            csv_modified_date=self.csv_modifieddate), "\n", "\n", certificate_template)

    @staticmethod
    def getcsv(self):
        with open(self.csv_filepath, "r") as fh:
            reader = csv.reader(fh, delimiter=self.delimiterchar, quoting=csv.QUOTE_NONE)
            listcsv = list(reader)
        return listcsv

    @staticmethod
    def validateheader(self):
        header = self.listcsv[0]
        if len(header) == self.field_count:
            self.validatecolumncount = 1
            for key, val in self.dic_format_file.items():
                if val.get('isSkipped'):
                    continue
                else:
                    ff_columnheading = val.get('NAME')
                    csv_columnheading = header[key - 1]
                    if csv_columnheading == ff_columnheading:
                        self.validate_column_headings = 1
                        continue
                    else:
                        # state, type, title, message, detail
                        detail = '''
    F:    {format_file_column_heading}
    C:   {csv_column_heading}'''.format(format_file_column_heading=ff_columnheading,
                                        csv_column_heading=csv_columnheading)
                        self.set_validate(False, "critical", "Error:", "Column headings don't match.", detail)
                        break
            self.set_validate(True, "Success", "Success:", "Column headings match.")
        else:
            if len(header) == 1:
                message = "The column count doesn't match the format file. Check that the file uses the correct delimiter."
            else:
                message = "The column count doesn't match the format file."
            self.set_validate(False, "critical", "Error:", "Column headings don't match.", message)

    @staticmethod
    def validatecontent(self):
        for y in range(0, self.field_count):  # loop all columns
            for x in range(1, len(self.listcsv)):  # loop all rows in each column
                if self.dic_format_file[y + 1].get("isSkipped"):
                    continue
                else:
                    column_name = self.dic_format_file[y + 1].get("NAME")
                    value = self.listcsv[x][y]  # grab the row|column value
                    regex = re.compile(self.dic_format_file[y + 1].get("regex"))
                    # print(column_name, value, regex)
                    # nullable = self.dic_format_file[y + 1].get("NULLABLE")
                    vcell = self.validatecell(x + 1, column_name, value, regex)
                    if vcell:
                        continue
                    else:
                        return
        self.set_validate(True, "Information", "Success:", "Content is valid.")

    def validatecell(self, row, column_name, value, regex):
        match = regex.search(value)
        if match is None:
            message = """
Column Name:    [{column}]
Row:            [{row_number}]
Value:          [{row_value}]
Regex:          [{regex_pattern}]""".format(column=column_name, row_number=row, row_value=value, regex_pattern=regex)
            self.set_validate(False, "critical", "Error:",
                              "Row " + str(row) + " in column '" + column_name + "' contains invalid data.", message)
            return False
        else:
            return True
