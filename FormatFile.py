#!/usr/bin/python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

from utility import get_ordinal_position


# TODO:
# DONE 1. are we working with an xml format file
# DONE 1.1 does it have all the required tags
# DONE 1.2 do each of the FIELD tags have the required attributes
# DONE 1.3 do each of the COLUMN tags have the required attributes
# DONE 2. handling skipped columns (i.e. column in file is to be ignored according to the format file)
# DONE 2.1 add a isSkipped item to the dictionary so the calling process can identify a skipped field
# DONE a skipped field is where a column provided in the CSV file is to be ignored.

class FormatFile:
    # returns a dictionary if it's a valid format file
    # dictionary items are related to the BCP Format file used to import CSV data to TSQL
    # for an example check out: .\files\formatfiles\example_formatfile.xml

    def __init__(self, filepath):
        self.path = filepath
        self.isValid = True
        self.message = None
        self.dic_field = {}
        fh = open(self.path, "r")
        self.soup = BeautifulSoup(fh.read(), "xml")
        self.fields = self.soup.findAll("FIELD")
        self.columns = self.soup.findAll("COLUMN")
        # print(self.soup.prettify())
        self.test_file_validity()
        if self.isValid:
            self.test_field_attributes()
        if self.isValid:
            self.test_column_attributes()

    def test_file_validity(self):
        taglist = ('BCPFORMAT', 'RECORD', 'ROW', 'FIELD', 'COLUMN')
        for tag in taglist:
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
        mandatory_attributelist = ("ID", "xsi:type", "TERMINATOR")
        optional_attributelist = ("MAX_LENGTH", "COLLATION")
        tag = "FIELD"
        self.test_mandatory_attributes(tag, mandatory_attributelist)
        i = 0
        for tag in self.fields:
            i += 1
            for att, val in tag.attrs.items():
                if att == "ID" or att == "MAX_LENGTH":
                    if not val.isdigit():
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag requires a number for its {attribute} attribute.".format(
                            position=get_ordinal_position(i), tag_name=tag.name, attribute=att)
                        break
                    else:
                        continue
                elif att == "xsi:type":
                    if not val == "CharTerm":
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an invalid value ('{error_value}') for the {attribute} attribute.".format(
                            position=get_ordinal_position(i), error_value=val, tag_name=tag.name, attribute=att)
                        break
                    else:
                        continue
                else:
                    if not att in optional_attributelist and not att in mandatory_attributelist:
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an unrecognised attribute '{attribute}'.".format(
                            position=get_ordinal_position(i), tag_name=tag.name, attribute=att)
                        break
                    else:
                        continue

    def test_column_attributes(self):
        mandatory_attributelist = ("SOURCE", "NAME", "xsi:type")
        optional_attributelist = ("PRECISION", "SCALE", "NULLABLE")
        allowed_data_types = (
            "SQLTINYINT", "SQLSMALLINT", "SQLINT", "SQLBIGINT", "SQLDATE", "SQLDATETIME", "SQLDECIMAL", "SQLMONEY",
            "SQLBIT", "SQLVARYCHAR", "SQLNVARCHAR")
        tag = "COLUMN"
        self.test_mandatory_attributes(tag, mandatory_attributelist)
        i = 0
        for tag in self.columns:
            i += 1
            for att, val in tag.attrs.items():
                if att == "SOURCE" or att == "PRECISION" or att == "SCALE":
                    if not val.isdigit():
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag requires a number for its {attribute} attribute.".format(
                            position=get_ordinal_position(i), attribute=att, tag_name=tag.name)
                        break
                    else:
                        continue
                elif att == "NULLABLE":
                    if not val in ("YES", "NO"):
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an invalid value ('{error_value}') for the {attribute} attribute.".format(
                            position=get_ordinal_position(i), error_value=val, attribute=att, tag_name=tag.name)
                        break
                    else:
                        continue
                elif att == "xsi:type":
                    if not val in allowed_data_types:
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an unrecognised data type '{error_value}' in the {attribute} attribute.".format(
                            position=get_ordinal_position(i), error_value=val, tag_name=tag.name, attribute=att)
                        break

                else:
                    if not att in optional_attributelist and not att in mandatory_attributelist:
                        self.isValid = False
                        self.message = "The {position} '{tag_name}' tag has an unrecognised attribute '{error}'.".format(
                            position=get_ordinal_position(i), error=att, tag_name=tag.name)
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

    def getfields(self):
        if self.isValid:
            for field in self.fields:
                dic_record = {}
                field_id = int(field.get("ID"))
                for attr, value in field.attrs.items():
                    dic_record[attr] = value
                self.dic_field[field_id] = dic_record

            for column in self.columns:
                source = column.get("SOURCE")
                column_id = int(source)
                dic_row = self.dic_field.get(column_id)
                if dic_row is None:
                    # this is bad as it means that there is an id in the column tags that doesnt exist in the FIELD tags
                    print(False, "SOURCE attribute is missing for column.")
                else:
                    for attr, value in column.attrs.items():
                        dic_row[attr] = value
                    self.dic_field[column_id] = dic_row

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

                    datatype = value.get("xsi:type")
                    value['regex'] = self.get_regex(datatype, max_length, nullable, precision, scale)
            return self.dic_field
        else:
            return

    @staticmethod
    def get_regex(datatype, field_max_length, field_nullable, decimal_precision=18, decimal_scale=0):
        if datatype == "SQLTINYINT":
            if field_max_length is None:
                field_max_length = 3
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif datatype == "SQLSMALLINT":
            if field_max_length is None:
                field_max_length = 5
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif datatype == "SQLINT":
            if field_max_length is None:
                field_max_length = 9
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif datatype == "SQLBIGINT":
            if field_max_length is None:
                field_max_length = 19
            regex = r"^[\d]{{1,{regex_max_length}}}${regex_nullable}".format(regex_max_length=field_max_length,
                                                                             regex_nullable=field_nullable)
        elif datatype == "SQLDATE":
            regex = r"^[\d]{{4}}-[\d]{{2}}-[\d]{{2}}${regex_nullable}".format(regex_nullable=field_nullable)
        elif datatype == "SQLDATETIME":
            regex = r"^[\d]{{4}}-[\d]{{2}}-[\d]{{2}} [\d]{{2}}:[\d]{{2}}:[\d]{{2}}${regex_nullable}".format(
                regex_nullable=field_nullable)
        elif datatype == "SQLMONEY":
            regex = r"^(?P<pounds>[\d]{{1,19}})(?P<pence>\.[\d]{{1,4}})?${regex_nullable}".format(
                regex_nullable=field_nullable)
        elif datatype == "SQLDECIMAL":
            regex = r"^(?:[\d]{{1,{regex_precision}}})(?:\.[\d]{{1,{regex_scale}}})?$|^${regex_nullable}".format(
                regex_precision=decimal_precision,
                regex_scale=decimal_scale,
                regex_nullable=field_nullable)
        elif datatype == "SQLVARYCHAR" or datatype == "SQLNVARCHAR":
            if field_max_length is None:
                field_max_length = str(1)
            regex = r"^.{{1,{regex_max_length}}}${regex_nullable}".format(
                regex_max_length=field_max_length, regex_nullable=field_nullable)
        elif datatype == "SQLBIT":
            regex = "^(TRUE|FALSE|0|1)${regex_nullable}".format(regex_nullable=field_nullable)
        else:
            regex = "Unrecognised xsi:type '{error_data_type}'.".format(error_data_type=datatype)
        return regex
