import sys

import FormatFile


def test_valid_format_file(filepath):
    ff = FormatFile.FormatFile(filepath)
    return filepath, ff.isValid, ff.message


def test_get_format_file_dictionary(filepath):
    ff = FormatFile.FormatFile(filepath)
    fields = ff.get_fields()
    print(fields)

if __name__ == '__main__':
    filepath = "examples\example_formatfile.xml"
    isValid = test_valid_format_file(filepath)
    print("isvalid_format_file=" + str(isValid))
    test_get_format_file_dictionary(filepath)

    # filepath = "example_formatfile_error_columnattributes.xml"
    # isValid = test_valid_format_file(filepath)
    # print("isvalid_format_file=" + str(isValid))
    # test_get_format_file_dictionary(filepath)

    # isValid = test_valid_format_file("example_formatfile_error.xml")
    # print("isvalid_format_file=" + str(isValid))

    # isValid = test_valid_format_file("example_formatfile_error_missingfieldid.xml")
    # print("isvalid_format_file=" + str(isValid))

    # isValid = test_valid_format_file("example_formatfile_error_missingattribute_ID.xml")
    # print("isvalid_format_file=" + str(isValid))

    # isValid = test_valid_format_file("example_formatfile_error_missingattribute_xsitype.xml")
    # print("isvalid_format_file=" + str(isValid))

    # isValid = test_valid_format_file("example_formatfile_error_tagcolumn_missingattribute_source.xml")
    # print("isvalid_format_file=" + str(isValid))
    sys.exit()
