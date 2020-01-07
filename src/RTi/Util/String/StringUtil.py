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
    PAD_FRONT_BACK = PAD_FRONT | PAD_BACK

    # For use with padding routines. Pad/unpad front, back, and middle of string.
    PAD_FRONT_MIDDLE_BACK = PAD_FRONT | PAD_MIDDLE | PAD_BACK

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
        logger = logging.getLogger(__name__)
        parsed_list = []

        if string is None:
            return parsed_list
        if len(string) == 0:
            return parsed_list
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
                cstring = string[istring]
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
                    if (not instring) and ((cstring == '"') or (cstring == '\'')):
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
            parsed_list.append(tempstr)
        return parsed_list

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
            if ((cformat == 'a') or (cformat == 'A') or
                (cformat == 'c') or (cformat == 'C') or
                (cformat == 'd') or (cformat == 'D') or
                (cformat == 'f') or (cformat == 'F') or
                (cformat == 'i') or (cformat == 'I') or
                (cformat == 's') or (cformat == 'S') or
                (cformat == 'x') or (cformat == 'X')):
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
        # dtype = 0  # Indicates type of variable (from "format").
        # isize = 0  # Number of characters in a data value (as integer).
        # j = 0  # Index for characters in a field.
        nread = 0  # Number of values read from file.
        # Indicates that the end of the line has been reached before
        # all of the format has been evaluated.
        eflag = False

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
                    # print("ISIZE: " + str(isize))
                    # print("J: " + str(j))
                    # print("istring: " + str(istring))
                    if istring >= string_length:
                        # End of string. Process the rest of the variables so that they are
                        # given a value of zero...
                        eflag = True
                        break
                    else:
                        var += str(string[istring])
                    istring += 1
            # print(var)
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

    # TODO smalers 2020-01-02 not used - get the Java ported code to work
    @staticmethod
    def format_string(objects, format_string):
        """
        Format a string using the format string.
        This is like C sprintf so just call Python equivalent.
        :param objects: objects to format, can be tuple, [], or single value
        :param format_string: format string similar to C sprintf
        :return: None
        """
        do_java_code = False
        is_tuple = isinstance(objects, tuple)
        is_list = isinstance(objects, list)
        if do_java_code:
            # Use code ported from Java, which expects a list as input
            # - TODO smalers 2020-01-03 need a command parameter to indicate to call this code
            # - TODO smalers 2020-01-03 need more testing
            if is_tuple:
                return StringUtil.format_string_java(list(objects), format_string)
            elif is_list:
                return StringUtil.format_string_java(objects, format_string)
            else:
                # Create a one-item list
                object_list = [objects]
                return StringUtil.format_string_java(object_list, format_string)
        else:
            # Use built-in formatter, which expects a tuple as input
            # - handle argument as tuple or a list
            # - TODO smalers 2020-01-03 need to make sure it handles the same formatting as Java code
            if is_tuple:
                return format_string % objects
            elif is_list:
                return format_string % tuple(objects)
            else:
                objects_tuple = (objects,)  # Note that the comma is critical
                return format_string % objects_tuple

    @staticmethod
    def format_string_java(v, format_string):
        """
        Format a string like the C sprintf

        Notes:	(1)	Accept any of the formats:

                    %%		- literal percent
                    %c		- single character
                    %s %8.8s %-8s	- String
                    %d %4d		- Integer
                    %8.2f %#8.2f	- Float
                    %8.2F %#8.2F	- Double

        Format a string like the C sprintf function.
        :param v: The list of objects to format.  Floating point numbers must be Double, etc. because
        the toString function is called for each object (actually, a number can be
        passed in as a String since toString will work in that case too).
        :param format_string: The format to use for formatting, containing normal characters
        and the following formatting strings:
        <p>
        <table width=100% cellpadding=10 cellspacing=0 border=2>
        <tr>
        <td><b>Data Type</b></td>	<td><b>Format</b></td>	<td><b>Example</b></td>
        </tr

        <tr>
        <td><b>Literal %</b></td>
        <td>%%</td>
        <td>%%5</td>
        </tr>

        <tr>
        <td><b>Single character</b></td>
        <td>%c</td>
        <td>%c</td>
        </tr>

        <tr>
        <td><b>String</b></td>
        <td>%s</td>
        <td>%s, %-20.20s</td>
        </tr>

        <tr>
        <td><b>Integer</b></td>
        <td>%d</td>
        <td>%4d, %04d</td>
        </tr>

        <tr>
        <td><b>Float, Double</b></td>
        <td>%f, %F</td>
        <td>%8.2f, %#8.2f</td>
        </tr>

        </table>
        <p>

        The format can be preceded by a - (e.g., %-8.2f, %-s) to left-justify the
        formatted string.  The default is to left-justify strings and right-justify
        numbers.  Numeric formats, if preceded by a 0 will result in the format being
        padded by zeros (e.g., %04d will pad an integer with zeros up to 4 digits).
        To force strings to be a certain width use a format like %20.20s.  To force
        floating point numbers to always use a decimal point use the #.
        Additional capabilities may be added later.
        :return: The formatted string.
        """
        buffer = ""
        # dl = 75;

        if v is None:
            return buffer
        if format is None:
            return buffer

        # Now loop through the format and as format specifiers are encountered
        # put them in the formatted string...

        # int	diff;
        # int	i;
        # int	iend;
        # int	iformat;
        # int	iprecision;
        # int	iwidth;
        j = 0
        length_format = len(format_string)
        # int	length_temp;
        offset = 0  # offset in string or array
        precision = 0  # precision as integer
        # int	sign;
        width = 0
        vindex = 0
        # char cformat;
        # char cvalue;
        #sprecision = "\0"*20  # should be enough, equivalent to Java char[20]
        #swidth = "\0"*20
        # boolean	dot_found, first, left_shift, pound_format, zero_format;
        vsizem1 = len(v) - 1
        debug = False   # do extra handling because don't want calls to logger.debug to slow down code
        logger = logging.getLogger(__name__)

        for iformat in range(length_format):
            cformat = format_string[iformat]
            if debug:
                logger.debug("Format character :\"" + cformat + "\", vindex = " + str(vindex))
            if cformat == '%':
                # The start of a format field.  Get the rest so that we can process.  First advance one...
                dot_found = False
                left_shift = False
                pound_format = False
                zero_format = False
                sprecision = ""
                iprecision = 0
                swidth = ""
                iwidth = 0
                iformat = iformat + 1
                if iformat >= length_format:
                    # End of format...
                    break
                # On the character after the %
                first = True
                # This advances iformat from the loop above
                # - TODO smalers 2020-01-03 not sure if using the same index is an issue
                for iformat in range(iformat, length_format):
                    cformat = format_string[iformat]
                    if debug:
                        logger.debug("Format character :\"" + cformat + "\" vindex =" + str(vindex))
                    if first:
                        # First character after the %...
                        # Need to update so that some of the following can be combined.
                        if cformat == '%':
                            # Literal percent...
                            buffer = buffer + '%'
                            first = False
                            break
                        elif cformat == 'c':
                            # Append a Character from the list...
                            buffer = buffer + str(v[vindex])
                            if debug:
                                logger.debug("Processed list[" + str(vindex) + "], a char")
                            vindex = vindex + 1
                            first = False
                            break
                        elif cformat == '-':
                            # Left shift...
                            left_shift = True
                            continue
                        elif cformat == '#':
                            # Special format...
                            pound_format = True
                            continue
                        elif cformat == '0':
                            # Leading zeros...
                            zero_format = True
                            continue
                        else:
                            # Not a recognized formatting character so we will just go
                            # to the next checks outside this loop...
                            first = False
                    # Else retrieving characters until an ending "s", "i", "d", or "f" is encountered.
                    if cformat.isdigit() or (cformat == '.'):
                        if cformat == '.':
                            dot_found = True
                            continue
                        if dot_found:
                            # part of the precision...
                            sprecision = sprecision + cformat
                            iprecision = iprecision + 1
                        else:
                            # part of the width...
                            swidth = swidth + cformat
                            iwidth = iwidth + 1
                        continue
                    if (cformat != 'd') and (cformat != 'f') and (cformat != 'F') and (cformat != 's'):
                        logger.warning("Invalid format string character (" + cformat +
                                       ") in format (" + format_string + ").")
                        break
                    # If here, have a valid format string and need to process...

                    # First get the width and precision on the format...

                    # Get the desired output width and precision (already initialize to zeros above)...

                    if iwidth > 0:
                        width = int(swidth)

                    if iprecision > 0:
                        precision = int(sprecision)

                    # Check to see if the number of formats is greater than the input list.  If so, this
                    # is likely a programming error so print a warning so the developer can fix.

                    if vindex > vsizem1:
                        logger.warning("The number of format strings \"" + format_string +
                                       "\" is > the number of data.  Check code.")
                        return buffer

                    # Now format for the different data types...

                    if cformat == 'd':
                        # Integer.  If NULL or an empty string, just add a blank string of the desired width...
                        if v[vindex] is None:
                            if debug:
                                logger.debug("NULL integer")
                            # NULL string.  Set it to be spaces for the width requested.
                            for i in range(width):
                                buffer = buffer + ' '
                            vindex = vindex + 1
                            break
                        # Temp is a string, not char[], for manipulations below
                        temp = str(v[vindex])
                        if len(temp) == 0:
                            if debug:
                                logger.debug("Zero length string for integer")
                            # Empty string.  Set it to be spaces for the width requested.
                            for i in range(width):
                                buffer = buffer + ' '
                            vindex = vindex + 1
                            break
                        if debug:
                            logger.debug("Processing list[" + str(vindex) + "], an integer \"" + temp + "\"")
                        vindex = vindex + 1
                        cvalue = temp[0]
                        if cvalue == '-':
                            sign = 1
                        else:
                            sign = 0
                        # String will be left-justified so we need to see if we need to shiftright.
                        # Allow overflow.  "temp" already has the sign in it.
                        length_temp = len(temp)
                        diff = width - length_temp
                        if diff > 0:
                            if left_shift:
                                if zero_format:
                                    # Need to add zeros in the front...
                                    if sign == 1:
                                        offset = 1
                                    else:
                                        offset = 0
                                    for j in range(diff):
                                        # temp.insert(offset, '0')
                                        temp = temp[:offset] + '0' + temp[offset:]
                                else:
                                    # Add spaces at the end...
                                    for j in range(diff):
                                        # temp.insert(length_temp, ' ')
                                        temp = temp + ' '
                            else:
                                # Add spaces at the beginning...
                                if sign == 1:
                                    offset = 1
                                else:
                                    offset = 0
                                if zero_format:
                                    # Add zeros...
                                    for j in range(diff):
                                        # temp.insert(offset, '0')
                                        temp = temp[:offset] + '0' + temp[offset:]
                                else:
                                    for j in range(diff):
                                        # temp.insert(0, ' ')
                                        temp = ' ' + temp
                        buffer = buffer + temp
                    elif (cformat == 'f') or (cformat == 'F'):
                        # Float.  First, get the whole number as a string...
                        # If NULL, just add a blank string of the desired width...
                        if v[vindex] is None:
                            if debug:
                                logger.debug("NULL float")
                            # NULL string.  Set it to be spaces for the width requested.
                            for i in range(width):
                                buffer = buffer + ' '
                            vindex = vindex + 1
                            break
                        temp = ""
                        # String whole_number_string;
                        # String remainder_string;
                        number_as_string = ""
                        # int	point_pos;
                        if cformat == 'f':
                            number_as_string = str(v[vindex])
                        elif cformat == 'F':
                            number_as_string = str(v[vindex])
                        if len(number_as_string) == 0:
                            if debug:
                                logger.debug("Zero length string for float")
                            # Empty string.  Set it to be spaces for the width requested.
                            for i in range(width):
                                buffer = buffer + ' '
                            vindex = vindex + 1
                            break
                        elif number_as_string == "NaN":
                            # Pad with spaces and justify according to the formatting.
                            if left_shift:
                                buffer = buffer + "NaN"
                                for i in range(width - 3):
                                    buffer = buffer + ' '
                            else:
                                for i in range(width - 3):
                                    buffer = buffer + ' '
                                buffer = buffer + "NaN"
                            vindex = vindex + 1
                            break
                        # Need to check here as to whether the number is less than 10^-3 or greater
                        # than 10^7, in which case the string comes back in exponential notation
                        # and fouls up the rest of the process...
                        try:
                            e_pos = number_as_string.index('E')
                        except ValueError:
                            e_pos = -1
                        if e_pos >= 0:
                            # Scientific notation.  Get the parts to the number and then
                            # put back together.  According to the documentation, the
                            # format is -X.YYYE-ZZZ where the first sign is optional, the first digit (X)
                            # is mandatory (and non-zero), the YYYY are variable length, the sign after the E is
                            # mandatory, and the exponent is variable length.
                            # The sign after the E appears to be optional.
                            if debug:
                                logger.debug("Detected scientific notation for Double: " + number_as_string)
                            expanded_string = ""
                            sign_offset = 0
                            if number_as_string[0] == '-':
                                expanded_string = expanded_string + "-"
                                sign_offset = 1
                            # Position of dot in float...
                            try:
                                dot_pos = number_as_string.index('.')
                            except ValueError:
                                dot_pos = -1
                            # Sign of the exponent...
                            e_sign = number_as_string[e_pos+1]
                            # Exponent as an integer...
                            exponent = 0
                            if (e_sign == '-') or (e_sign == '+'):
                                exponent = int(number_as_string[e_pos + 2:])
                            else:
                                # No sign on exponent.
                                exponent = int(number_as_string[e_pos + 1:])
                            # Left side of number...
                            left = number_as_string[sign_offset:dot_pos]
                            # Right side of number...
                            right = number_as_string[(dot_pos + 1):e_pos]
                            # Add to the buffer on the left side of the number...
                            if e_sign == '-':
                                # Add zeros on the left...
                                dot_shift = exponent - 1
                                expanded_string = expanded_string + "."
                                for ishift in range(dot_shift):
                                    expanded_string = expanded_string + "0"
                                expanded_string = expanded_string + left
                                expanded_string = expanded_string + right
                            else:
                                # Shift the decimal to the right...
                                expanded_string = expanded_string + left
                                # Now transfer as many digits as available.
                                len_right = len(right)
                                for ishift in range(exponent):
                                    if ishift <= (len_right - 1):
                                        expanded_string = expanded_string + right[ishift]
                                    else:
                                        expanded_string = expanded_string + "0"
                                expanded_string = expanded_string + "."
                                # If we did not shift through all the original right-side digits, add them now...
                                if exponent < len_right:
                                    expanded_string = expanded_string + right[exponent:]
                            # Now reset the string...
                            number_as_string = expanded_string
                            if debug:
                                logger.debug("Expanded number: \"" + number_as_string + "\"")
                        if debug:
                            logger.debug("Processing list[" + str(vindex) + "], a float or double \"" +
                                         number_as_string + "\"")
                        vindex = vindex + 1
                        # Figure out if negative...
                        if number_as_string[0] == '-':
                            sign = 1
                        else:
                            sign = 0
                        # Find the position of the decimal point...
                        try:
                            point_pos = number_as_string.index('.')
                        except ValueError:
                            point_pos = -1
                        if point_pos == -1:
                            # No decimal point.
                            whole_number_string = number_as_string
                            remainder_string = ""
                        else:
                            # has decimal point
                            whole_number_string = number_as_string[0:point_pos]
                            remainder_string = number_as_string[point_pos + 1:]
                        # Round the number so that the number of precision digits exactly matches what we want...
                        if precision < len(remainder_string):
                            number_as_string = StringUtil.round(number_as_string, precision)
                            # We may need to recompute the parts of the string.  Just do it for now...
                            # Figure out if negative...
                            if number_as_string[0] == '-':
                                sign = 1
                            else:
                                sign = 0
                            # Find the position of the decimal point...
                            try:
                                point_pos = number_as_string.index('.')
                            except Exception:
                                point_pos = -1
                            if point_pos < 0:
                                # No decimal point.
                                whole_number_string = number_as_string
                                remainder_string = ""
                            else:
                                # has decimal point
                                whole_number_string = number_as_string[0:point_pos]
                                remainder_string = number_as_string[point_pos + 1:]
                        # Now start at the back of the string and start adding parts...
                        if precision > 0:
                            # First fill with zeros for the precision amount...
                            for iprec in range(precision):
                                # temp.insert(0,'0')
                                temp = ' ' + temp
                            # Now overwrite with the actual numbers...
                            iend = len(remainder_string)
                            if iend > precision:
                                iend = precision
                            for iprec in range(iend):
                                temp[iprec] = remainder_string[iprec]
                            # Round off the last one if there is truncation.  Deal with this later...
                            if precision < len(remainder_string):
                                # TODO - old comment: working on doing the round above...
                                pass
                            # Now add the decimal point...
                            # temp.insert(0, '.')
                            temp = '.' + temp
                        elif (precision == 0) and pound_format:
                            # Always add a decimal point...
                            # temp.insert(0, '.')
                            temp = '.' + temp
                        # Now add the whole number.  If it overflows, that is OK.  If it is
                        # less than the width we will deal with it in the next step.
                        # temp.insert(0, whole_number_string)
                        temp = whole_number_string + temp
                        # If the number that we have now is less than the desired width, we need
                        # to add spaces.  Depending on the sign in the format, we add them at the left or right.
                        if len(temp) < width:
                            iend = width - len(temp)
                            if left_shift:
                                # Add at the end...
                                for ishift in range(iend):
                                    # temp.insert(len(temp), ' ')
                                    temp = temp + ' '
                            else:
                                # Add at the front...
                                for ishift in range(iend):
                                    if zero_format:
                                        # Format was similar to "%05.1f"
                                        # temp.insert(0, '0')
                                        temp = '0' + temp
                                    else:
                                        # temp.insert(0, ' ')
                                        temp = ' ' + temp

                        # Append to our main string...
                        buffer = buffer + temp
                    elif cformat == 's':
                        # First set the string the requested size, which is the precision.  If the
                        # precision is zero, do the whole thing.  String will be left-justified so we
                        # need to see if we need to shift right.  Allow overflow...
                        # If NULL, just add a blank string of the desired width...
                        if v[vindex] is None:
                            if debug:
                                logger.debug("NULL string")
                            # NULL string.  Set it to be spaces for the width requested.
                            for i in range(precision):
                                buffer = buffer + ' '
                            vindex = vindex + 1
                            break
                        temp = str(v[vindex])
                        if len(temp) == 0:
                            if debug:
                                logger.debug("Zero length string")
                            # Empty string.  Set it to be spaces for the width requested.
                            for i in range(width):
                                buffer = buffer + ' '
                            vindex = vindex + 1
                            break
                        if debug:
                            logger.debug("Processing list[" + str(vindex) + "], a string \"" + temp + "\"")
                        vindex = vindex + 1
                        if iprecision > 0:
                            # Now figure out whether we need to right-justify...
                            diff = precision - len(temp)
                            if not left_shift:
                                # Right justify...
                                if diff > 0:
                                    for j in range(diff):
                                        # temp.insert(0, ' ')
                                        temp = ' ' + temp
                            else:
                                # Left justify.  Set the buffer to the precision...
                                temp = temp[:precision]
                                # Now fill the end with spaces instead of NULLs...
                                for j in range((precision - diff), precision):
                                    temp = temp[:j] + ' '
                            # If the string length is longer than the string, append a substring...
                            if len(temp) > precision:
                                buffer = buffer + temp[0:precision]
                            else:
                                # Do the whole string...
                                buffer = buffer + temp
                        else:
                            # Write the whole string...
                            if temp is not None:
                                buffer = buffer + temp
                    # End of a format string.  Break out and look for the next one...
                    break
            else:
                # A normal character so just add to the buffer...
                buffer = buffer + cformat

        return buffer

    @staticmethod
    def round(string, precision):
        """
        Given a string representation of a floating point number, round to the
        desired precision.  Currently this operates on a string (and not a double)
        because the method is called from the formatString() method that operates on strings.
        @return String representation of the rounded floating point number.
        @param string String containing a floating point number.
        @param precision Number of digits after the decimal point to round the number.
        """
        # First break the string into its integer and remainder parts...
        try:
            dot_pos = string.index('.')
        except ValueError:
            dot_pos = -1
        if dot_pos < 0:
            # No decimal.
            return string
        # If get to here there is a decimal.  Figure out the size of the integer and the remainder...
        integer_length = dot_pos
        remainder_length = len(string) - integer_length - 1
        if remainder_length == precision:
            # Then the precision matches the remainder length and can return the original string...
            return string
        elif remainder_length < precision:
            # If the remainder length is less than the precision,
            # then add zeros on the end of the original string until we get to the precision length...
            pass
        # If here need to do the more complicated roundoff stuff.
        # First check if the precision is zero.  If so, round off the main number and return...
        if precision == 0:
            ltemp = round(float(string))
            return str(int(ltemp))
        # If get to here, we have more than a zero precision and need to
        # jump through some hoops.  First, create a new string that has the remainder...
        remainder_string = string.substring[dot_pos + 1:]
        # Next insert a decimal point after the precision digits.
        # remainder_string.insert(precision,'.');
        remainder_string = remainder_string[:precision] + '.' + remainder_string[precision:]
        # Now convert the string to a Double...
        dtemp = float(remainder_string)
        # Now round...
        ltemp = round(dtemp)
        # Now convert back to a string...
        rounded_remainder = str(int(ltemp))
        integer_string = string[:integer_length]
        if len(rounded_remainder) < precision:
            # The number we were working with had leading zeros and we
            # lost that during the round.  Insert zeros again...
            buf = rounded_remainder
            number_to_add = precision - len(rounded_remainder)
            for i in range(number_to_add):
                buf = '0' + buf
            new_string = integer_string + "." + buf
            return new_string
        elif len(rounded_remainder) > precision:
            # We have, during rounding, had to carry over into the next
            # larger ten's spot (for example, 99.6 has been rounded to
            # 100.  Therefore, we need to use all but the first digit of
            # the rounded remainder and we need to increment our original number (or decrement if negative!).
            first_char = string[0]
            new_long = int(integer_string)
            if first_char == '-':
                # Negative...
                new_long = new_long - 1
            else:
                # Positive...
                new_long = new_long + 1
            new_string = str(new_long) + "." + rounded_remainder[1:]
            return new_string
        # Now put together the string again...
        new_string = integer_string + "." + ltemp

        """
        if ( Message.isDebugOn ) {
        Message.printDebug ( 20, routine, "Original: " + string +
        " new: " + new_string );
        }
        """
        return new_string

    @staticmethod
    def read_to_delim(string0, delim):
        """
        String up to but not including the delimiter character.
        :param string0: String to read from.
        :param delim: Delimiter character to read to.
        :return: String up to but not including the delimiter character.
        """
        i = 0
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
