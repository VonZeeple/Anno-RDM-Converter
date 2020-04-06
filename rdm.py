from typing import NamedTuple
from typing import List
from struct import *


class NotRDMError(Exception):
    pass


class IntegerArrayError(Exception):
    pass

class VertexSizeError(Exception):
    pass
class VertexPackingError(Exception):
    pass

vertex_formats = {8: r'P4h',
                  16: r'P4h_T2h_C4c',
                  20: r'P4h_N4b_T2h_I4b',
                  24: r'P4h_N4b_G4b_B4b_T2h',
                  28: r'P4h_N4b_G4b_B4b_T2h_I4b',
                  32: r'P4h_N4b_G4b_B4b_T2h_C4b_C4b',
                  56: r'P4h_N4b_G4b_B4b_T2h_I4b_I4b_I4b_I4b_W4b_W4b_W4b_W4b',
                  # 60: r'P3f_N3b_37_T2f',
                  # 64: r'P3f_N3b_41_T2f',
                  # 68: r'P3f_N3b_45_T2f',
                  # 72: r'P3f_N3b_49_T2f',
                  }
vertex_length = {v: k for k, v in vertex_formats.items()}
data_size = {'e': 2, 'f': 4, 'b': 1, 'B': 1, 'c': 1}

# TODO use dataclass
class Vertex(dict):
    @staticmethod
    def parse(data):
        v_size = len(data)
        if v_size not in vertex_formats.keys():
            raise VertexSizeError

        letter_to_arg = {'P': 'pos', 'T': 'tex', 'N': 'norm', 'I': 'unknown_I'}
        format_str = vertex_formats[v_size]
        vertex_arg = {'vformat': format_str}
        i = 0
        for s in format_str.replace('h', 'e').replace('b', 'B').split('_'):
            # TODO: implement regex for >56 bytes vertex
            num_data = int(s[1])
            if s[0] in letter_to_arg.keys():
                vertex_arg[letter_to_arg[s[0]]] = unpack(s[1:3], data[i:i + int(s[1]) * data_size[s[2]]])
            i += num_data * data_size[s[2]]
        return Vertex(vertex_arg)

    def pack(self):
        format_str = self['vformat']
        letter_to_arg = {'P': 'pos', 'T': 'tex', 'N': 'norm'}
        out = bytearray()
        for s in format_str.replace('h', 'e').replace('b', 'B').split('_'):
            # TODO: implement regex for >56 bytes vertex
            out += pack(s[1:3], *self.get(letter_to_arg.get(s[0], ''), [0]*s[1]))
        if len(out) != vertex_length[format_str]:
            raise VertexPackingError
        return out


class TriangleSizeError(Exception):
    pass


triangle_formats = {2: r'HHH',
                    4: r'III',
                    }


class Triangle(NamedTuple):
    format: str
    indices: List[int]

    @staticmethod
    def parse(data):
        t_size = int(len(data) / 3)
        if t_size not in triangle_formats.keys():
            raise TriangleSizeError
        indices = unpack(triangle_formats[t_size], data)
        return Triangle(format=triangle_formats[t_size], indices=list(indices))

    def pack(self):
        out = pack(self.format, *self.indices)
        return out


class SingleInt(int):
    def pack(self, *arg):
        return int(self)


class IntArray(list):
    @staticmethod
    def parse(data, offset):
        if offset < 8:
            return None
        num, size = unpack('II', data[offset - 8:offset])
        out = [IntArray.unpack_ints(data[offset + i * size: offset + (i + 1) * size]) for i in range(num)]
        return IntArray(out)

    def pack(self, data):
        n0 = len(data)
        n_1 = len(self)
        if isinstance(self[0], (list, tuple)):
            n_2 = len(self[0])
            data += pack('II', n_1, n_2 * 4)
            for i in range(n_1):
                data += pack(str(n_2) + 'I', *self[i])
        else:
            data += pack('II', 1, n_1 * 4)
            data += pack(str(n_1) + 'I', *self)
        return n0 + 8

    @staticmethod
    def unpack_ints(data):
        n = len(data)
        if n % 4 != 0:
            raise IntegerArrayError
        return unpack(int(n / 4) * 'I', data)


class AnnoString(bytes):
    @staticmethod
    def parse(data, offset):
        if offset >= 8:
            strLen, dummy = unpack('II', data[offset - 8:offset])
            string, = unpack(str(strLen) + 's', data[offset:offset + strLen])
        else:
            return None
        return AnnoString(string)

    def pack(self, data):
        n0 = len(data)
        str_data = self
        data += pack('II', len(str_data), 1)
        data += str_data
        return n0 + 8


class DataArray(list):
    @staticmethod
    def parse(data, offset):
        if offset == 0:
            return None
        num, size = unpack('II', data[offset - 8:offset])
        array = [data[offset + size * i:offset + size * (i + 1)] for i in range(num)]
        return DataArray(array)

    def pack(self, data):
        n0 = len(data)
        num = len(self)
        size = len(self[0])
        data += pack('II', num, size)
        for i in range(num):
            data += self[i]
        return n0 + 8


class Record(dict):
    @staticmethod
    def parse(data, offset):
        header = IntArray.parse(data, offset)
        childs = {'unknown_{:}'.format(i): None for i in range(len(header))}

        return Record(childs)

    def pack(self, data):
        n0 = len(data)
        header = IntArray([0] * len(self))
        header.pack(data)
        for i, (k, v) in enumerate(self.items()):
            if v is not None:
                header[i] = v.pack(data)
            else:
                header[i] = 0
        data[n0 + 8:n0 + 8 + 4 * len(header)] = pack(str(len(header)) + 'I', *header)
        return n0 + 8


class StringRecord(Record):

    @staticmethod
    def parse(data, offset):
        header, = IntArray.parse(data, offset)
        if header is None:
            return None
        child = {'string_1': AnnoString.parse(data, header[0]),
                 'string_2': AnnoString.parse(data, header[1])
                 }
        for i, h in enumerate(header[2::]):
            child['unknown_string_{:}'.format(i + 2)] = AnnoString.parse(data, h)
        return StringRecord(child)


class Group(NamedTuple):
    offset: int
    size: int
    n: int

    @staticmethod
    def parse(array):
        return Group(offset=array[0], size=array[1], n=array[2])

    def pack(self):
        return self.offset, self.size, self.n, 0, 0, 0, 0


class GroupRecord(Record):
    @staticmethod
    def parse(data, offset):
        if offset == 0:
            return None
        header = IntArray.parse(data, offset)
        child = {'group_{:}'.format(i): Group.parse(h) for i, h in enumerate(header)}
        return GroupRecord(child)

    def pack(self, data):
        n0 = len(data)
        array = IntArray([v.pack() for k, v in self.items()])
        return array.pack(data)


class MeshRecord(Record):
    """"Contains info about the mesh. Contains usually 23 fields:
     - strings
     - unknown_0
     - unknown_1
     - vertices
     - faces
     - groups
     - some unknown flags [17]"""

    @staticmethod
    def parse(data, offset):
        header, = IntArray.parse(data, offset)
        child = {'strings': StringRecord.parse(data, header[0]),
                 'unknown_0': UnknownRecord.parse(data, header[1]),
                 'unknown_1': IntArray.parse(data, header[2]),
                 'vertices': DataArray.parse(data, header[3]),
                 'faces': DataArray.parse(data, header[4]),
                 'groups': GroupRecord.parse(data, header[5])
                 }
        for i in range(6, len(header)):
            child['unknown_flag_{:}'.format(i - 6)] = SingleInt(header[i])
        return MeshRecord(child)

    # For some reason, vertices are encoded afters groups in the binary file
    def pack(self, data):
        n0 = len(data)
        header = IntArray([0] * len(self))
        header.pack(data)
        order = {'strings': 0, 'unknown_0': 1, 'unknown_1': 2, 'groups': 5, 'vertices': 3, 'faces': 4}
        for i, (k, v) in enumerate(order.items()):
            if self[k] is not None:
                header[v] = self[k].pack(data)
            else:
                header[v] = 0
        #Loop over the rest
        for i, (k, v) in enumerate(self.items()):
            if k in order.keys():
                continue
            if self[k] is not None:
                header[i] = self[k].pack(data)
            else:
                header[i] = 0
        data[n0 + 8:n0 + 8 + 4 * len(header)] = pack(str(len(header)) + 'I', *header)
        return n0 + 8


class UnknownRecord(Record):
    """"Purpose of this is unknown"""
    @staticmethod
    def parse(data, offset):
        header, = IntArray.parse(data, offset)
        child = {'unknown_{:}'.format(i): IntArray.parse(data, h) for i, h in enumerate(header)}
        return UnknownRecord(child)


class Material(NamedTuple):
    """"Has 3 attributes:
     - name
     - texture
     - flag
     """
    name: AnnoString
    texture: AnnoString
    flag: SingleInt

    @staticmethod
    def parse(data, offset):
        if offset == 0:
            return None
        header, = IntArray.parse(data, offset)
        name = AnnoString.parse(data, header[0])
        texture = AnnoString.parse(data, header[1])
        flag = SingleInt(header[2])
        return Material(name=name, texture=texture, flag=flag)

    def pack(self, data):
        n0 = len(data)
        header = IntArray([0] * 12)
        header.pack(data)
        for i, v in enumerate(self):
            if v is not None:
                header[i] = v.pack(data)
            else:
                header[i] = 0
        data[n0 + 8:n0 + 8 + 4 * len(header)] = pack(str(len(header)) + 'I', *header)
        return n0 + 8


class MaterialsRecord(Record):
    """"A list of all materials. Contains usually 7 fields:
     - material_#
     some of them can be None"""
    @staticmethod
    def parse(data, offset):
        header = IntArray.parse(data, offset)
        materials = {}
        for i, h in enumerate(header):
            materials['material_{:}'.format(i + 1)] = Material.parse(data, h[0])
        return MaterialsRecord(materials)

    def pack(self, data):
        n0 = len(data)
        header = [[0]*7 for i in self]
        IntArray(header).pack(data)
        for i, (k, v) in enumerate(self.items()):
            if v is not None:
                header[i][0] = v.pack(data)
            else:
                header[i][0] = 0

        packed_header = bytearray()
        _ = IntArray(header).pack(packed_header)
        data[n0:n0 + len(packed_header)] = packed_header
        return n0 + 8



class MainRecord(Record):
    """"Contains usually 12 fields:
     - strings
     - mesh
     - materials
     - some unknown flags [9]"""

    @staticmethod
    def parse(data, offset):
        header, = IntArray.parse(data, offset)
        child = {
            'Strings': StringRecord.parse(data, header[0]),
            'Mesh': MeshRecord.parse(data, header[1]),
            'Materials': MaterialsRecord.parse(data, header[2])
        }
        for i in range(12 - 3):
            child['unknown_{:}'.format(i + 1)] = None
        return MainRecord(child)


class RDMFile(NamedTuple):
    """"A RDM file is composed of:
     - rdm_tag (3 char)
     - dummy_char (byte)
     - unknown_0: a list a int with unknown purpose
     - main_record
     """

    rdm_tag: str
    dummy_char: int
    unknown_0: List[int]
    main_record: MainRecord

    @staticmethod
    def parse(data):
        rdm_tag, dummy_char = unpack('3sB', data[0:4])
        if rdm_tag != b'RDM':
            raise NotRDMError
        unknown_0 = list(unpack('4I', data[4:20]))
        return RDMFile(rdm_tag=rdm_tag, dummy_char=dummy_char, unknown_0=unknown_0,
                       main_record=MainRecord.parse(data, 28))

    def pack(self):
        data = bytearray()
        data += pack('3sB', self.rdm_tag, self.dummy_char)
        data += pack('4I', *self.unknown_0)
        self.main_record.pack(data)
        return data
