# Utils for Erika Printing

def lines_to_print_instructions(lines:list):
    ''' 
    Takes an array of lines, and returns an array of lines+print instuctions.
    lines(list): the lines to print
    
    returns: A list of tuples like [(FORWARD_PRINTING, "lorem ipsum"),(BACKWARD_PRINTING, "dolor sit amet")]
    '''
    
    FORWARD_PRINTING = 0
    BACKWARD_PRINTING = 1

    new_lines = []
    cursor = 0
    line_diff = 0

    lines = [line.strip() for line in lines]

    for i, line in enumerate(lines):
        
        if (
            (cursor > len(line)) # We are at the end of a line; this one is shorter
            or 
            (line_diff < cursor)  # It would be longer to go back, than to got ahead and print backwards
            and
            (len(line) > 3)): # not worth going back for just some letters; can also be \n
                # Backwards
                cursor = 0
                line += line_diff * ' ' # add spaces so the length will match next line
                line = ''.join(reversed(line))
                new_lines.append((BACKWARD_PRINTING, line)) # True is Backwards
                #print(f"R {i}: {line} | {cursor} | diff: {line_diff}")
                #print(line)  
        else:
            # Forward     
            line += line_diff * ' '
            new_lines.append((FORWARD_PRINTING, line)) 
            cursor = len(line)
            #print(line) 
            #print(f"F {i}: {line} | {cursor} | diff: {line_diff}")     
        try:
            # Will fail for the last line
            line_diff = abs(len(lines[i+1]) - len(line))
        except IndexError:
            line_diff = 0
    return new_lines


def string_to_lines(text, max_length, linefeed=True):
    '''
    Returns an array of lines with a max_length of DEFAULT_LINE_LENGTH
    All newlines from the original lines are used
    in case a line is to long, an extra newline is inserted
    '''
    newline = '\n'
    if linefeed:
        last_char = newline
    else:
        last_char = ''
    all_lines = text.split(newline)
    lines = []
    for aline in all_lines:
        words = aline.split()
        tmp_line = ''

        # If the text is less than a line, return it
        if len(aline) <= max_length:
            lines.append(aline + last_char)
        else:
            # else split to lines
            for word in words:
                next = ' '.join([tmp_line, word])
                if len(next) <= max_length:
                    tmp_line = next
                else:
                    lines.append(tmp_line.strip() + newline)
                    tmp_line = word

            # for the last words
            lines.append(tmp_line.strip() + last_char)
    return lines


class PageControls:

    # Line-Spacing
    LINE_SPACING_10 = "84"
    LINE_SPACING_15 = "85"
    LINE_SPACING_20 = "86"

    # Char-Spaces
    CHAR_SPACING_10 = "87"
    CHAR_SPACING_12= "88"

    # Directions
    DIR_RIGHT = "73"
    DIR_LEFT = "74"
    DIR_UP = "76"
    DIR_DOWN = "75"

    # Print direction
    PRINT_DIR_FOREWARD = "8D"
    PRINT_DIR_BACKWARD = "8E"
