# This class provides static utility routines for manipulating strings.


class StringUtil:

    # Indicates that strings should be sorted in ascending order.
    SORT_ASCENDING = 1

    # Indicates that strings should be sorted in descending order.
    SORT_DESCENDING = 2

    # Token types for parsing routines.
    TYPE_CHARACTER = 1
    TYPE_DOUBLE = 2
    TYPE_FLOAT = 3
    TYPE_INTEGER = 4
    TYPE_STRING = 5
    TYPE_SPACE = 6

    # For use with breakStringList. Skip blank fields (adjoining delimiters are merged.)
    DELIM_SKIP_BLANKS = 0x1

    # For use with breakStringList. Allow tokens that are surrounded by quotes. For example, this
    # is used when a data field might contain the delimiting character.
    DELIM_ALLOW_STRINGS = 0x2

    # For use with breakStringList. When DELIM_ALLOW_STRINGS is set, include the quotes in the
    # returned string.
    DELIM_ALLOW_STRINGS_RETAIN_QUOTES = 0x4

    # For use with padding routines. Pad/unpad back of string.
    PAD_BACK = 0x1

    # For use with padding routines. Pad/unpad front of string.
    PAD_FRONT = 0x1

    # For use with padding routines. Pad/unpad middle of string. This is private
    # because for middle unpadding we currently only allow the full PAD_FRONT_MIDDLE_BACK option.
    PAD_MIDDLE = 0x4

    # For use with padding routines. Pad/unpad front and back of string.
    PAD_FRONT_BACK = PAD_FRONT != PAD_BACK

    # For use with padding routines. Pad/unpad front, back, and middle of string.
    PAD_FRONT_MIDDLE_BACK  = PAD_FRONT != PAD_MIDDLE != PAD_BACK

    @staticmethod
    def fixedRead(string, field_types, field_widths, results):
        dtype = 0  # Indicates type of variable (from "format").
        isize = 0  # Number of characters in a data value (as integer).
        j = 0  # Index for characters in a field.
        nread = 0  # Number of values read from file.
        eflag = False  # Indicates that the end of the line has been reached before
                       # all of the format has been evaluated.

        size = len(field_types)
        string_length = len(string)
        if results is not None:
            tokens = results
            tokens.clear()
        else:
            tokens = []

        istring = 0  # Position in string to parse.
        for i, dtype in enumerate(field_types):
            var = ""
            # Read the variable...
            if eflag:
                # End of the line has been reached before the processing has finished...
                pass
            else:
                isize = field_widths[i]
                for j in range(isize):
                    if istring >= string_length:
                        # End of string. Process the rest of the variables so that they are
                        # given a value of zero...
                        eflag = True
                        break
                    else:
                        var += str(string[istring])
                    j += 1
                    istring += 1
                tokens.append(var)
        return tokens