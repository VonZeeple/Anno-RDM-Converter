from typing import NamedTuple
from typing import List


class OBJGroup(NamedTuple):
    name: str

    faces: List[List[List[int]]]


class OBJObject(NamedTuple):
    name: str
    groups: List[OBJGroup]


class OBJFile(NamedTuple):
    vertices: List[List[float]]
    normals: List[List[float]]
    uv: List[List[float]]
    objects: List[OBJObject]


def write_obj_file(filename, obj_file):
    with open(filename, 'w') as f:

        for v in obj_file.vertices:
            f.write("v {0:f} {1:f} {2:f}\n".format(*v))
        for v in obj_file.uv:
            f.write("vt {0:f} {1:f}\n".format(*v))
        for v in obj_file.normals:
            f.write("vn {0:f} {1:f} {2:f}\n".format(*v))

        for object in obj_file.objects:
            f.write("o {:}\n".format(object.name))
            for obj_group in object.groups:
                f.write("g {:}\n".format(obj_group.name))

                for face in obj_group.faces:
                    s = ''
                    for v in face:
                        s += ' {0:}/{1:}/{2:}'.format(*v).replace('None', '')
                    f.write("f" + s + "\n")


# TODO handle objects and groups
def parse_obj_file(filename):
    v_pos = []
    v_norm = []
    v_tex = []
    objects = []
    faces = []

    with open(filename, 'rb') as f:
        for line in f:
            s = line.decode().split()
            if s[0] == 'v':
                v_pos.append([float(a) for a in s[1::]])
            if s[0] == 'vn':
                v_norm.append([float(a) for a in s[1::]])
            if s[0] == 'vt':
                v_tex.append([float(a) for a in s[1::]])

            if s[0] == 'f':
                faces.append([[int(a) if a else None for a in s2.split('/')] for s2 in s[1::]])

    return OBJGroup(name='unnamed', vertices=v_pos, normals=v_norm, uv=v_tex, faces=faces)

