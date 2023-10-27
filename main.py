
import re
from collections import namedtuple
from itertools import takewhile

def get_entries(path):
    Entry = namedtuple('Entry', '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> http://knowdive.disi.unitn.it/etype#has_latitude_GID-46264_Type-132 http://knowdive.disi.unitn.it/etype#has_seats_GID-15151_Type-5446 http://knowdive.disi.unitn.it/etype#has_covering_GID-22933_Type-5446  http://knowdive.disi.unitn.it/etype#has_longitude_GID-46270_Type-132 http://knowdive.disi.unitn.it/etype#has_wheelchair_accessibility_GID-300000_Type-1617 http://knowdive.disi.unitn.it/etype#has_name_GID-34017_Type-132')

    with open(path) as file:
        # an entry starts with `#@` line and ends with a blank line
        for line in file:
            if line.startswith('<'):
                buf = [line]
                buf.extend(takewhile(str.strip, file)) # read until blank line
                yield Entry(*re.findall(r'<([^>]+)>', ''.join(buf)))


if __name__ == "__main__":
    print("\n".join(map(str, get_entries('example.ttl'))))
    