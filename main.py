import rdm
from struct import *
from obj import *
import math

filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_colony01_01/rdm/workshop_colony01_01_lod0.rdm'

with open(filename, 'rb') as f:
    data_0 = f.read()
rdm_file = rdm.RDMFile.parse(data_0)

vertices = [rdm.Vertex.parse(data) for data in rdm_file.main_record.get('Mesh', {}).get('vertices')]
groups = list(rdm_file.main_record.get('Mesh', {}).get('groups', {}).values())


def unpack_v_index(data):
    if len(data) == 2:
        out, = unpack('H', data)
    elif len(data) == 4:
        out, = unpack('I', data)
    else:
        out = None
    return out


def convert_normal(norm):
    n_1 = [n * 1. / 255 * 2 - 1 for n in norm]
    length = math.sqrt(sum([n ** 2 for n in n_1]))
    return [n/length for n in n_1]


faces_v_indices = [unpack_v_index(data) for data in rdm_file.main_record.get('Mesh', {}).get('faces')]
materials = list(rdm_file.main_record.get('Materials', {}).values())

# To convert into obj file:
# we sort vertices an faces by group
obj_objects = []
k = 1
for p, group in enumerate(groups):

    # TODO: take name from materials
    name = 'group_{:}'.format(p)
    v_map = {}
    n0 = int(group.offset)
    n1 = int(n0 + group.size)
    group_v_index = faces_v_indices[n0: n1]

    for i in group_v_index:
        vertex = vertices[i]
        if i not in v_map.keys():
            v_map[i] = k
            k += 1
            
    obj_v = [vertices[i]['pos'] for i in v_map.keys()]
    obj_n = [convert_normal(vertices[i]['norm']) for i in v_map.keys()]
    obj_uv = [vertices[i]['tex'] for i in v_map.keys()]
    faces = [group_v_index[p:p + 3] for p in range(0, len(group_v_index), 3)]
    obj_f = [[[v_map[f[0]]] * 3, [v_map[f[1]]] * 3, [v_map[f[2]]] * 3] for f in faces]

    obj_group = OBJGroup(name=name, vertices=obj_v, normals=obj_n, uv=obj_uv, faces=obj_f)
    obj_objects.append(OBJObject(name=name, groups=[obj_group]))

obj_file = OBJFile(obj_objects)
write_obj_file('test_out.obj', obj_file)
# To convert from obj to RDM:
# first check if all polygons are triangles
