#!/usr/bin/python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

from utility import get_ordinal_position


# TODO:
# 1. bulkload schema does not allow ID and COLUMN fields to start with a number.
# can code be updated to accommodate a string?
# 2. change FormatFile.py to validate all field types allowed by schema, or leave it as a subset?

class FormatFile:
    # returns a dictionary if it's a valid format file
    # dictionary items are related to the BCP Format file used to import CSV data to TSQL
    # for an example check out: .\files\formatfiles\example_formatfile.xml

    def __init__(self, file_path):
        self.path = file_path
        self.isValid = True
        self.message = None
        self.dic_field = {}
        fh = open(self.path, "r")
        self.soup = BeautifulSoup(fh.read(), "xml")
        self.records = self.soup.findAll("FIELD")
        self.rows = self.soup.findAll("COLUMN")
        # print(self.soup.prettify())
        self.test_file_validity()
        if self.isValid:
            self.test_field_attributes()
        if self.isValid:
            self.test_column_attributes()

    def test_file_validity(self):
        tag_list = ('BCPFORMAT', 'RECORD', 'ROW', 'FIELD', 'COLUMN')
        for tag in tag_list:
            if self.verify_tag_exists(tag):
                self.isValid = True
                continue
            else:
                self.isValid = False
                self.message = "The tag '{tag_name}' does not exist in the format file".format(tag_name=tag)
                break

    def verify_tag_exists(self, tag_name):
        test = self.soup.find(tag_name)
        if test is None:
            exists = False
        else:
            exists = True
        return exists

    def test_field_attributes(self):
        mandatory_attribute_list = ("ID", "xsi:type", "TERMINATOR")
        optional_attribute_list = ("MAX_LENGTH", "COLLATION")
        self.test_mandatory_attributes("FIELD", mandatory_attribute_list)
        i = 0
        for record in self.records:
            i += 1
            for att, val in record.attrs.items():
                if att == "MAX_LENGTH":
                    if not val.isdigit():
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag requires a number for its {attribute} attribute.".format(
                            position=get_ordinal_position(i), tag_name=record.name, attribute=att)
                        break
                    else:
                        continue
                elif att == "xsi:type":
                    if not val == "CharTerm":
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an invalid value ('{error_value}') for the {attribute} attribute.".format(
                            position=get_ordinal_position(i), error_value=val, tag_name=record.name, attribute=att)
                        break
                    else:
                        continue
                else:
                    if att not in optional_attribute_list and att not in mandatory_attribute_list:
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an unrecognised attribute '{attribute}'.".format(
                            position=get_ordinal_position(i), tag_name=record.name, attribute=att)
                        break
                    else:
                        continue

    def test_column_attributes(self):
        mandatory_attribute_list = ("SOURCE", "NAME", "xsi:type")
        optional_attribute_list = ("PRECISION", "SCALE", "NULLABLE")
        allowed_data_types = (
            "SQLTINYINT", "SQLSMALLINT", "SQLINT", "SQLBIGINT", "SQLDATE", "SQLDATETIME", "SQLDECIMAL", "SQLMONEY",
            "SQLBIT", "SQLVARYCHAR", "SQLNVARCHAR")
        self.test_mandatory_attributes("COLUMN", mandatory_attribute_list)
        i = 0
        for row in self.rows:
            i += 1
            for att, val in row.attrs.items():
                if att == "PRECISION" or att == "SCALE":
                    if not val.isdigit():
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag requires a number for its {attribute} attribute.".format(
                            position=get_ordinal_position(i), attribute=att, tag_name=row.name)
                        break
                    else:
                        continue
                elif att == "NULLABLE":
                    if val not in ("YES", "NO"):
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an invalid value ('{error_value}') for the {attribute} attribute.".format(
                            position=get_ordinal_position(i), error_value=val, attribute=att, tag_name=row.name)
                        break
                    else:
                        continue
                elif att == "xsi:type":
                    if val not in allowed_data_types:
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an unrecognised data type '{error_value}' in the {attribute} attribute.".format(
                            position=get_ordinal_position(i), error_value=val, tag_name=row.name, attribute=att)
                        break

                else:
                    if att not in optional_attribute_list and att not in mandatory_attribute_list:
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an unrecognised attribute '{error}'.".format(
                            position=get_ordinal_position(i), error=att, tag_name=row.name)
                        break
                    else:
                        continue

    def test_mandatory_attributes(self, tag, attributes):
        for att in attributes:
            exists = self.verify_attribute_exists(tag, att)
            if exists[0]:
                self.isValid = True
            else:
                position = get_ordinal_position(int(exists[1]))
                self.message = "Format file is invalid: the {ordinal_position} '{tag_name}' tag does not include the attribute '{missing_attribute}'." \
                    .format(ordinal_position=position, tag_name=tag, missing_attribute=att)
                self.isValid = False
                break

    def verify_attribute_exists(self, tag_name, attribute):
        tags = self.soup.findAll(tag_name)
        i = 0
        for tag in tags:
            i += 1
            if tag.has_attr(attribute):
                exists = True
            else:
                exists = False
                break
        return exists, i

    def get_fields(self):
        if self.isValid:
            for field in self.records:
                field_id = len(self.dic_field) + 1
                dic_record = {}
                for attr, value in field.attrs.items():
                    dic_record[attr] = value
                self.dic_field[field_id] = dic_record

            for row in self.rows:
                row_source = row.get("SOURCE")
                # get the item from the dictionary where the SOURCE in the self.rows
                # matches the ID in the self.records
                column_position = self.get_matching_id_key(row_source)
                dic_row = self.dic_field.get(column_position, None)
                if dic_row is None:
                    # this is bad as it means that there is an id in the column tags that doesnt exist in the FIELD tags
                    print(False, "SOURCE attribute is missing for column.")
                else:
                    for attr, value in row.attrs.items():
                        dic_row[attr] = value
                    self.dic_field[column_position] = dic_row

            for key, value in self.dic_field.items():
                value['isSkipped'] = (value.get("NAME") is None)
                if not value['isSkipped']:
                    max_length = value.get("MAX_LENGTH")
                    precision = value.get("PRECISION", 18)
                    scale = value.get("SCALE", 0)
                    nullable = value.get("NULLABLE")
                    if nullable == "YES":
                        nullable = "|^$"
                        value["NULLABLE"] = True
                    else:
                        nullable = ""
                        value["NULLABLE"] = False

                    data_type = value.get("xsi:type")
                    value['regex'] = self.get_regex(data_type, max_length, nullable, precision, scale)
            return self.dic_field
        else:
            return

    def get_matching_id_key(self, source):
        matching_key = None
        for key, item in self.dic_field.items():
            # print(source, item.get("ID", None))
            if source == item.get("ID", None):
                matching_key = key
                break
            else:
                continue
        # print(matching_key)
        return matching_key

    @staticmethod
    def get_regex(data_type, field_max_length, field_nullable, decimal_precision=18, decimal_scale=0):
        if data_type == "SQLTINYINT":
            if field_max_length is None:
                field_max_length = 3
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif data_type == "SQLSMALLINT":
            if field_max_length is None:
                field_max_length = 5
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif data_type == "SQLINT":
            if field_max_length is None:
                field_max_length = 9
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif data_type == "SQLBIGINT":
            if field_max_length is None:
                field_max_length = 19
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif data_type == "SQLDATE":
            regex = r"^[\d]{{4}}-[\d]{{2}}-[\d]{{2}}${regex_nullable}".format(regex_nullable=field_nullable)
        elif data_type == "SQLDATETIME":
            regex = r"^[\d]{{4}}-[\d]{{2}}-[\d]{{2}} [\d]{{2}}:[\d]{{2}}:[\d]{{2}}${regex_nullable}".format(
                regex_nullable=field_nullable)
        elif data_type == "SQLMONEY":
            regex = r"^(?P<pounds>[\d]{{1,19}})(?P<pence>\.[\d]{{1,4}})?${regex_nullable}".format(
                regex_nullable=field_nullable)
        elif data_type == "SQLDECIMAL":
            regex = r"^(?:[\d]{{1,{regex_precision}}})(?:\.[\d]{{1,{regex_scale}}})?$|^${regex_nullable}".format(
                regex_precision=decimal_precision,
                regex_scale=decimal_scale,
                regex_nullable=field_nullable)
        elif data_type == "SQLVARYCHAR" or data_type == "SQLNVARCHAR":
            if field_max_length is None:
                field_max_length = str(1)
            regex = r"^.{{1,{regex_max_length}}}${regex_nullable}".format(
                regex_max_length=field_max_length, regex_nullable=field_nullable)
        elif data_type == "SQLBIT":
            regex = "^(TRUE|FALSE|0|1)${regex_nullable}".format(regex_nullable=field_nullable)
        else:
            regex = "Unrecognised xsi:type '{error_data_type}'.".format(error_data_type=data_type)
        return regex
