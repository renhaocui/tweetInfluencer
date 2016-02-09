__author__ = 'renhao.cui'

def posConvert(input):
    output = []
    tags = {'^': 0, 'G': 0, 'A': 0, 'N': 0, ',': 0, 'D': 0, 'P': 0, 'U': 0, 'O': 0, 'V': 0, 'L': 0, '!': 0, 'R': 0, '&': 0,
            'T': 0, '$': 0, 'Z': 0, '~': 0, 'X': 0, 'E': 0, 'S': 0, '#': 0, 'Y': 0, '@': 0}

    inputFile = open(input)
    for line in inputFile:
        text = line.strip()
        if len(text) > 0:
            seg = text.split('\t')
            if seg[0] == 'urrl':
                seg[1] = 'U'
            tags[seg[1]] += 1
        if len(text) == 0:
            out = []
            for k in tags:
                out.append(float(tags[k]))
            output.append(out)
            tags = {'^': 0, 'G': 0, 'A': 0, 'N': 0, ',': 0, 'D': 0, 'P': 0, 'U': 0, 'O': 0, 'V': 0, 'L': 0, '!': 0, 'R': 0,
                    '&': 0, 'T': 0, '$': 0, 'Z': 0, '~': 0, 'X': 0, 'E': 0, 'S': 0, '#': 0, 'Y': 0, '@': 0}

    inputFile.close()
    return output