import os


xslt_line = '<?xml-stylesheet type="text/xsl" href="junit.xslt" ?>\n'


def assoc_xsl(filename):
    with open(filename, 'r') as infile:
        lines = infile.readlines()

    lines.insert(1, xslt_line)

    with open(filename, 'w') as outfile:
        outfile.writelines(lines)
    print filename


if __name__ == '__main__':
    reports_dir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'tests/reports/nightwatch'))
    reports = filter(lambda f: f.endswith('.xml'), os.listdir(reports_dir))
    reports = map(lambda f: os.path.join(reports_dir, f), reports)
    map(assoc_xsl, reports)
