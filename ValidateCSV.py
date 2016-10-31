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
        self.format_file_file_path = formatfile_filepath
        self.csv_file_path = csv_filepath
        self.current_time = utility.get_current_time()
        self.username = utility.getuser()
        self.delimiter = "\t"
        self.validation_certificate_path = None
        self.format_file_path = utility.path_from_file_path(self.format_file_file_path)
        self.format_file_filename = utility.file_from_file_path(self.format_file_file_path)
        self.csv_path = utility.path_from_file_path(self.csv_file_path)
        self.csv_filename = utility.file_from_file_path(self.csv_file_path)
        self.csv_file = os.path.splitext(self.csv_filename)[0]
        self.csv_created_date = utility.get_file_date_time(self.csv_file_path, 0)
        self.csv_modified_date = utility.get_file_date_time(self.csv_file_path, 1)
        self.ff = FormatFile.FormatFile(self.format_file_file_path)
        if not self.ff.isValid:
            self.set_validate(False, "ERROR", "Error:", "Format File is invalid.")
            return
        else:
            self.dic_format_file = self.ff.get_fields()
            self.field_count = len(self.dic_format_file)
            self.list_csv = self.get_csv(self)
            self.validate_header(self)
            if self.validate_state:
                self.validate_content(self)
                # if self.validate_state:
                #   self.create_validation_certificate(self)

    def set_validate(self, state, v_type, title, message, detail=None):
        self.validate_state = state
        self.validate_type = v_type
        self.validate_message_title = title
        self.validate_message_text = message
        self.validate_message_detailed = detail

    @staticmethod
    def create_validation_certificate(self):
        self.validation_certificate_path = os.path.join(self.csv_path, self.csv_file + "_certificate.txt")
        validation_certificate_items = self.get_valid_items(self)
        with open(self.validation_certificate_path, "w") as fhw:
            fhw.writelines(validation_certificate_items)

    @staticmethod
    def get_valid_items(self):
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
        '''.format(csv_file_name=self.csv_filename, format_file_name=self.format_file_filename,
                   csv_file_path=self.csv_file_path, format_file_file_path=self.format_file_file_path)
        return ('"{current_time}"|"{username}"|"{csv_filename}"|"{csv_modified_date}"'.format(
            current_time=self.current_time, username=self.username, csv_filename=self.csv_filename,
            csv_modified_date=self.csv_modified_date), "\n", "\n", certificate_template)

    @staticmethod
    def get_csv(self):
        with open(self.csv_file_path, "r") as fh:
            reader = csv.reader(fh, delimiter=self.delimiter, quoting=csv.QUOTE_NONE)
            list_csv = list(reader)
        return list_csv

    @staticmethod
    def validate_header(self):
        header = self.list_csv[0]
        if len(header) == self.field_count:
            self.validate_column_count = 1
            for key, val in self.dic_format_file.items():
                if val.get('isSkipped'):
                    continue
                else:
                    ff_column_heading = val.get('NAME')
                    csv_column_heading = header[int(key)]
                    if csv_column_heading == ff_column_heading:
                        self.validate_column_headings = 1
                        continue
                    else:
                        # state, type, title, message, detail
                        detail = '''
    F:    {format_file_column_heading}
    C:   {csv_column_heading}'''.format(format_file_column_heading=ff_column_heading,
                                        csv_column_heading=csv_column_heading)
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
    def validate_content(self):
        for y in range(0, self.field_count):  # loop all columns
            for x in range(1, len(self.list_csv)):  # loop all rows in each column
                # get the item from the format file
                if self.dic_format_file[y + 1].get("isSkipped"):
                    continue
                else:
                    column_name = self.dic_format_file[y + 1].get("NAME")
                    value = self.list_csv[x][y]  # grab the row|column value
                    regex = re.compile(self.dic_format_file[y + 1].get("regex"))
                    # nullable = self.dic_format_file[y + 1].get("NULLABLE")
                    cell = self.validate_cell(x + 1, column_name, value, regex)
                    if cell:
                        continue
                    else:
                        return
        self.set_validate(True, "Information", "Success:", "Content is valid.")

    def validate_cell(self, row, column_name, value, regex):
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
