# This class provides static utility routines for manipulating strings.

import logging
import time


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

    # ------------------------------------------------------------------------------
    #  beak_string_list - get a list of strings from a string
    # ------------------------------------------------------------------------------
    #  Notes:	(1)	The list is assumed to be of the form "val,val,val",
    # 			where the commas indicate the delimiter character.
    # 		(2)	Call "HMFreeStringList" when done with the list.
    # 		(3)	The list always has one NULL element at the end so that
    # 			we know how to free the memory.  However, "nlist" does
    # 			not include this element.
    # 		(4)	If the HMDELIM_ALLOW_STRINGS flag is set, then we
    # 			strings to be treated as one token, even if they contain
    # 			blanks.  The first quote character, either " or ' is
    # 			used to contain the string.  The quote characters
    # 			cannot be in the list of delimiting characters.
    # 		(5)	It would be nice to allow return of all the tokens.
    # 			Add the "flag" variable to allow for this enhancement
    # 			in the future.
    # ------------------------------------------------------------------------------
    # Variable	I/O	Description
    #
    # delim	I	Character delimiter list.
    # flag		I	Flag to modify parsing.
    # i		L	Counter for characters in substring.
    # instring	L	Indicates if we are inside a quoted string.
    # list		L	List of broken out strings.
    # nlist	O	Number of strings in the final list.
    # nlist2	L	Used when adding strings to list.
    # pt		L	Pointer to original string.
    # pt2		L	Pointer to split out string.
    # quote	L	Character used for a quoted string.
    # routine	L	Name of this routine.
    # string	I	String of delimiter-separated items.
    # tempstr	L	String used when splitting out sub-strings.
    # ------------------------------------------------------------------------------
    @staticmethod
    def break_string_list(string, delim, flag):
        """
        Break a delimited string into a list of Strings.  The end of the string is
        considered as a delimiter so "xxxx,xxxx" returns two strings if the comma is a
        delimiter and "xxxxx" returns one string if the comma is the delimiter.  If a
        delimiter character is actually the last character, no empty/null field is returned at
        the end.  If multiple delimiters are at the front and skip blanks is specified,
        all the delimiters will be skipped.  Escaped single characters are passed through
        as is.  Therefore \" (two characters) will be two characters in the output.  Other
        code needs to interpret the two characters as the actual special character.
        :param string: The string to break.
        :param delim: A string containing characters to treat as delimiters. Each
        character in the string is checked (the complete string is not used as a
        multi-character delimiter).  Cannot be null.
        :param flag: Bitmask indicating how to break the string.  Specify
        DELIM_SKIP_BLANKS to skip blank fields (delimiters that are next to each other
        are treated as one delimiter - delimiters at the front are ignored).  Specify
        DELIM_ALLOW_STRINGS to allow quoted strings (which may contain delimiters).
        Specify DELIM_ALLOW_STRINGS_RETAIN_QUOTES to retain the quotes in the return strings when
        DELIM_ALLOW_QUOTES is used.
        Specify 0 (zero) to do simple tokenizing where repeated delimiters are not
        merged and quoted strings are not handled as one token.  Note that when allowing
        quoted strings the string "xxxx"yy is returned as xxxxyy because no intervening delimiter is present.
        :return: A list of strings, guaranteed to be non-null
        """
        logger = logging.getLogger("StateMod")
        routine = "StringUtil.breakStringList"
        list = []

        if string is None:
            return list
        if len(string) == 0:
            return list
        length_string = len(string)
        instring = False
        retainQuotes = False
        istring = 0
        cstring = ''
        quote = '\"'
        tempstr = ""
        allow_strings = False
        skip_blanks = False
        if (flag and StringUtil.DELIM_ALLOW_STRINGS) != 0:
            allow_strings = True
        if (flag and StringUtil.DELIM_SKIP_BLANKS) != 0:
            skip_blanks = True
        if allow_strings and ((flag and StringUtil.DELIM_ALLOW_STRINGS_RETAIN_QUOTES) != 0):
            retainQuotes = True
        # Loop through the characters in the string. If in the main loop or
        # the inner "while" the end of the string is reached, the last
        # Characters will be added to the last string that is broken out...
        at_start = True  # If only delimiters are at the front this will be true.
        for istring in range(length_string):
            cstring = string[istring]
            # Start the next string in this list. Move characters to the
            # temp string until a delimiter is found. If inside a string
            # then go until a closing delimiter is found.
            instring = False
            str = ""  # Clear memory
            while istring < length_string:
                # Process a sub-string between delimiters...
                cstring= string[istring]
                # Check for escaped special characters...
                if (cstring == '\\') and (istring < (length_string - 1)) and (string[istring + 1] == '\"'):
                    # Add the backslash and the next character - currently only handle single characters
                    tempstr += cstring
                    # Now increment to the next character...
                    istring += 1
                    cstring = string[istring]
                    tempstr += cstring
                    istring += 1
                    continue
                if allow_strings:
                    # Allowing quoted strings so do check for the starts and end of quotes...
                    if ((not instring) and ((cstring == '"') or (cstring == '\''))):
                        # The start of a quoted string...
                        instring = True
                        at_start = False
                        quote = cstring
                        if retainQuotes:
                            tempstr += cstring
                        # Skip over the quote since we don't want to store or process again..
                        istring += 1
                        continue
                    # Check for the end of the quote...
                    elif instring and (cstring == quote):
                        # In a quoted string and  have found the closing quote. Need to skip over it.
                        # However, could still be in the string and be escaped, so check for that by looking
                        # for another string. Any internal escaped quotes will be a pair "" or ''
                        # so look ahead one and if a pair, treat as character to be retained.
                        # This is usally only going to be encountered when reading CSV files, etc.
                        if (istring < (length_string - 1)) and (string[istring + 1] == quote):
                            # Found a pair of the quote character so absorb both and keep looking for ending
                            # quote for teh token
                            tempstr += cstring
                            istring += 1
                            if retainQuotes:
                                # Want to retain all the quotes
                                tempstr += cstring
                            istring += 1
                            # instring still true
                            continue
                        # Else... process as if not an escaped string but and end of quoted string
                        if retainQuotes:
                            tempstr += cstring
                        instring = False
                        istring += 1
                        if istring < length_string:
                            cstring = string[istring]
                            # If the current string is now another quote, just continue so it can be processed
                            # again as the start of another string (but don't by default add
                            # the quote character)...
                            if (cstring == '\'') or (string == '"'):
                                if retainQuotes:
                                    tempstr += cstring
                                continue
                        else:
                            # The quote was the last character in the original string. Break out so
                            # the last string can be added...
                            break
                        # If here the closing quote has been skipped but don't want to break here
                        # in case the final quote isn't the last character in teh sub-string
                        # (e.g, might be ""xxx).
                # Now check for a delimiter to break the string...
                if delim.find(cstring) != -1:
                    # Have a delimiter character that could be in a string or not...
                    if not instring:
                        # Not in a string so OK to break...
                        break
                else:
                    # Else, treat as a character that needs to be part of the token and add below...
                    at_start = False
                # It is OK to add the character...
                tempstr += cstring
                # Now increment to the next character...
                istring += 1
                # Go to the top of the "while" and evaluate the current character that was just set.
                # cstring is set at top of while...
            # Now have a sub-string and the last character read is a delimiter
            # character (or at the end of the original string).
            #
            # See if we are at the end of the string...
            if instring:
                # No further action is required...
                pass
            elif skip_blanks:
                while (istring < length_string) and (delim.find(cstring) != -1):
                    istring += 1
                    if istring < length_string:
                        cstring = string[istring]
                if at_start:
                    # Just want to skip the initial delimiters without adding a string to
                    # to the returned list...
                    at_start = False
                    continue
                # After this the current character will be that which needs to be evaluated. "cstring"
                # is reset at the top of the main "for" loop but it needs to be assigned here also
                # because of the check in the above while loop
            else:
                # Not skipping multiple delimiters so advance over the character that triggered
                # the break in the main while loop...
                istring += 1
                # cstring will be assigned in the main "for" loop
            # Now add the string token to the list...
            list.append(tempstr)
        return list

    @staticmethod
    def fixed_read(string, format):
        """
        Parse a fixed-format string (e.g., a FORTRAN data file) using a simplified
        notation.  <b>This routine needs to be updated to accept C-style formatting
        commands.  Requesting more fields than there are data results in default (zero
        or blank) data being returned.</b>
        This method can be used to read integers and floating point numbers from a
        string containing fixed-format information.
        :return: A List of objects that are read from the string according to the
        specified format described below.  Integers are returned as Integers, doubles
        as Doubles, etc.  Blank "x" fields are not returned (therefore the list of returned
        objects has a size of all non-x formats).
        :param string: String to parse.
        :param format: Format to use for parsing, as shown in the following table.
        An example is: "i5f10x3a10", or in general
        "v#", where "v" indicates a variable type and "#" indicates the TOTAL width
        of the variable field in the string.
        NO WHITESPACE OR DELIMITERS IN THE FORMAT!
        <p>

        <table width=100% cellpadding=10 cellspacing=0 border=2>
        <tr>
        <td><b>Data Type</b></td>	<td><b>Format</b></td>	<td><b>Example</b></td>
        </tr

        <tr>
        <td><b>integer, Integer</b></td>
        <td>i</td>
        <td>i5</td>
        </tr>

        <tr>
        <td><b>float, Float</b></td>
        <td>f</td>
        <td>f10</td>
        </tr>

        <tr>
        <td><b>double, Double</b></td>
        <td>d</td>
        <td>d10</td>
        </tr>

        <tr>
        <td><b>Spaces (not returned)</b></td>
        <td>x</td>
        <td>x20</td>
        </tr>

        <tr>
        <td><b>char</b></td>
        <td>c</td>
        <td>c</td>
        </tr>

        <tr>
        <td><b>String</b></td>
        <td>s, a</td>
        <td>s10, a10</td>
        </tr>
        </table>
        :return:
        """

        # Determine the format types and widths...

        # First loop through the format string and count the number of valid format specifier characters...
        format_length = 0
        if format is not None:
            format_length = len(format)
        field_count = 0
        cformat = ''
        for i in range(format_length):
            cformat = format[i]
            if ( (cformat == 'a') or (cformat == 'A') or
			(cformat == 'c') or (cformat == 'C') or
			(cformat == 'd') or (cformat == 'D') or
			(cformat == 'f') or (cformat == 'F') or
			(cformat == 'i') or (cformat == 'I') or
			(cformat == 's') or (cformat == 'S') or
			(cformat == 'x') or (cformat == 'X') ):
                field_count += 1
        # Now set the array sizes for formats...
        field_types = [int()]*field_count
        field_widths = [int()]*field_count
        field_count = 0  # Reset for detailed loop...
        width_string = ""
        for iformat in range(format_length):
            width_string = ""
            # Get a format character...
            cformat = format[iformat]
            if cformat == 'c' or cformat == 'C':
                field_types[field_count] = StringUtil.TYPE_CHARACTER
                field_widths[field_count] = 1
                continue
            elif cformat == 'd' or cformat == 'D':
                field_types[field_count] = StringUtil.TYPE_DOUBLE
            elif cformat == 'f' or cformat == 'F':
                field_types[field_count] = StringUtil.TYPE_FLOAT
            elif cformat == 'i' or cformat == 'I':
                field_types[field_count] = StringUtil.TYPE_INTEGER
            elif cformat == 'a' or cformat == 'A' or cformat == 's' or cformat == 'S':
                field_types[field_count] = StringUtil.TYPE_STRING
            elif cformat == 'x' or cformat == 'X':
                field_types[field_count] = StringUtil.TYPE_SPACE
            else:
                # Problem!!!
                continue
            # Determine the field width...
            iformat += 1
            while iformat < format_length:
                cformat = format[iformat]
                if not cformat.isdigit():
                    # Went into the next field...
                    iformat -= 1
                    break
                else:
                    width_string += cformat
                    iformat += 1
            field_widths[field_count] = int(width_string)
            field_count += 1
        width_string = None
        # ... END OF INLINED CODE
        # Now do the read...
        v = StringUtil.fixed_read2(string, field_types, field_widths, None)
        return v


    # TODO smalers 2019-12-31 need to rework to provide overloaded behavior similar to Java
    @staticmethod
    def fixed_read2(string, field_types, field_widths, results):
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

        start = time.time()

        var = ""
        istring = 0  # Position in string to parse.
        for i in range(size):
            dtype = field_types[i]
            var = ""
            # Read the variable...
            if eflag:
                # End of the line has been reached before the processing has finished...
                pass
            else:
                isize = field_widths[i]
                for j in range(isize):
                    #print("ISIZE: " + str(isize))
                    #print("J: " + str(j))
                    #print("istring: " + str(istring))
                    if istring >= string_length:
                        # End of string. Process the rest of the variables so that they are
                        # given a value of zero...
                        eflag = True
                        break
                    else:
                        var += str(string[istring])
                    istring += 1
            #print(var)
            # 1. Convert the variable that was read as a character
            #    string to the proper representation.
            # 2. Add to the list.
            if dtype == StringUtil.TYPE_CHARACTER:
                tokens.append(var[0])
            elif dtype == StringUtil.TYPE_DOUBLE:
                sdouble = var.strip()
                if len(sdouble) == 0:
                    tokens.append(float("0.0"))
                else:
                    tokens.append(float(sdouble))
            elif dtype == StringUtil.TYPE_FLOAT:
                sfloat = var.strip()
                if len(sfloat) == 0:
                    tokens.append(float("0.0"))
                else:
                    tokens.append(float(sfloat))
            elif dtype == StringUtil.TYPE_INTEGER:
                sinteger = var.strip()
                if len(sinteger) == 0:
                    tokens.append(int("0"))
                else:
                    # Check for "+"
                    if sinteger.startswith("+"):
                        sinteger = sinteger[1]
                    tokens.append(int(sinteger))
            elif dtype == StringUtil.TYPE_STRING:
                tokens.append(var)
            nread += 1
        return tokens

    @staticmethod
    def read_to_delim(string0, delim):
        """
        String up to but not including the delimiter character.
        :param string0: String to read from.
        :param delim: Delimiter character to read to.
        :return: String up to but not including the delimiter character.
        """
        i = 0
        c = ''
        string = ""

        if string0 is None:
            return string
        while True:
            c = string[i]
            if c == delim:
                return string
            else:
                string += c
            i += 1
            if c == '\0':
                break
        return string