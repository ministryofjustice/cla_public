import sys
import os
import shutil


TEMP_DIR = 'temp'
CODECS = ['utf8', 'cp1252', 'win1251']


class Utf8LineConverter(object):
    def __init__(self, input_path):
        self.input_file = file(input_path)
        self.output_file = None

    def split_lines(self):
        os.makedirs(TEMP_DIR)

        for num, line in enumerate(self.input_file.readlines()):
            f = open(os.path.join(TEMP_DIR, "%06d.txt" % num), 'w+')
            f.write(line)
            f.close()

    def convert(self, output_path, encoding='utf8'):
        self.output_file = file(output_path, 'w+')

        self.split_lines()

        for fn in os.listdir(TEMP_DIR):
            fp = os.path.join(TEMP_DIR, fn)
            if os.path.isfile(fp):
                write_line = None
                read_line = open(fp).read()
                for c in CODECS:
                    try:
                        write_line = read_line.decode(c).encode(encoding)
                        print c
                        break
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        pass

                if not write_line:
                    raise Exception(u'CANT ENCODE LINE: %s - %s' % (fn, read_line))
                self.output_file.write(write_line)
                print fp

        shutil.rmtree(TEMP_DIR)

        self.output_file.close()


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    converter = Utf8LineConverter(input_file)
    converter.convert(output_file)

