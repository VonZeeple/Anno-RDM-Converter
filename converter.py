from struct import *
import math
import rdm
from obj import *


def unpack_v_index(data):
    if len(data) == 2:
        out, = unpack('H', data)
    elif len(data) == 4:
        out, = unpack('I', data)
    else:
        out = None
    return out


def convert_normal2obj(norm):
    n_1 = [n * 1. / 255 * 2 - 1 for n in norm]
    length = math.sqrt(sum([n ** 2 for n in n_1]))
    return [n/length for n in n_1]

def convert_normal2rdm(norm):
    pass
def obj_to_rdm(obj_file):
    pass

def rdm_to_obj(rdm_file):
    vertices = [rdm.Vertex.parse(data) for data in rdm_file.main_record.get('Mesh', {}).get('vertices')]
    groups = list(rdm_file.main_record.get('Mesh', {}).get('groups', {}).values())

    faces_v_indices = [unpack_v_index(data) for data in rdm_file.main_record.get('Mesh', {}).get('faces')]
    materials = list(rdm_file.main_record.get('Materials', {}).values())

    obj_objects = []
    obj_v = [vertices[i]['pos'] for i in range(len(vertices))]
    obj_n = [convert_normal2obj(vertices[i]['norm']) for i in range(len(vertices))]
    obj_uv = [vertices[i]['tex'] for i in range(len(vertices))]

    for p, group in enumerate(groups):

        name = materials[p].name.decode('ascii')
        n0 = int(group.offset)
        n1 = int(n0 + group.size)
        group_v_index = faces_v_indices[n0: n1]

        faces = [group_v_index[p:p + 3] for p in range(0, len(group_v_index), 3)]
        obj_f = [[[f[0]+1] * 3, [f[1]+1] * 3, [f[2]+1] * 3] for f in faces]

        obj_group = OBJGroup(name=name, faces=obj_f)
        obj_objects.append(OBJObject(name=name, groups=[obj_group]))

    obj_file = OBJFile(vertices=obj_v, normals=obj_n, uv=obj_uv, objects=obj_objects)
    return obj_file
