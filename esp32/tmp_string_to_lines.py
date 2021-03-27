

DEFAULT_LINE_LENGTH = 60

# Returns an array of lines with a max_length of DEFAULT_LINE_LENGTH
def string_to_lines(text, max_length=DEFAULT_LINE_LENGTH):
    words = text.split()
    lines = []
    tmp_line = ''

    # If the text is less than a line, return it
    if len(text) <= max_length:
        return [text]

    # else split to lin es
    for word in words:
        next = ' '.join([tmp_line, word])
        if len(next) <= max_length:
            tmp_line = next
        else:
            lines.append(tmp_line.strip())
            tmp_line = word  
    # for the last words
    lines.append(tmp_line.strip())
    return lines



if __name__ == "__main__":
    txt = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam suscipit, justo id tincidunt gravida, magna metus pellentesque lacus, eget tincidunt quam tellus eget."
    print(string_to_lines("hi"))
    print(string_to_lines(txt))
