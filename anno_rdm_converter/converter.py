from struct import *
from anno_rdm_converter import rdm
from anno_rdm_converter.obj import *
import math


def calc_tan(v1, v2, v3):
    """" Computes tangent and bitangent for a face. Input is 3 dictionnaries containing the keys pos, tex and norm"""
    p1, p2, p3 = (v.get('pos') for v in [v1, v2, v3])
    t1, t2, t3 = (v.get('tex') for v in [v1, v2, v3])
    n1, n2, n3 = (convert_normal2obj(v.get('norm')) for v in [v1, v2, v3])
    dp1 = [pa - pb for pa, pb in zip(p1, p2)]
    dp2 = [pa - pb for pa, pb in zip(p3, p2)]
    dt1 = [pa - pb for pa, pb in zip(t1, t2)]
    dt2 = [pa - pb for pa, pb in zip(t3, t2)]

    det = -(dt1[0] * dt2[1] - dt1[1] * dt2[0])

    x = (dp1[0] * dt2[1] - dp2[0] * dt1[1]) / det
    y = (dp1[1] * dt2[1] - dp2[1] * dt1[1]) / det
    z = (dp1[2] * dt2[1] - dp2[2] * dt1[1]) / det
    mag = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    tan = [x / mag, y / mag, z / mag]

    x = n1[1]*tan[2]-n1[2]*tan[1]
    y = n1[2]*tan[0]-n1[0]*tan[2]
    z = n1[0]*tan[1]-n1[1]*tan[0]
    mag = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    bitan = [x / mag, y / mag, z / mag]

    return convert_normal2rdm(bitan), convert_normal2rdm(tan)


def unpack_v_index(data):
    if len(data) == 2:
        out, = unpack('H', data)
    elif len(data) == 4:
        out, = unpack('I', data)
    else:
        out = None
    return out


def convert_normal2obj(norm):
    n_1 = [n * 1. / 127.5 - 1 for n in norm]
    return n_1


def convert_normal2rdm(norm):
    return [int((n + 1) * 127.5) for n in norm]

def convert_uv(uv):
    return [uv[0], 1 - uv[1]]


def padding(vec, length, value=0):
    if len(vec) < length:
        return vec + [value] * (length - len(vec))
    return vec


# we first try the 'P4h_N4b_T2h_I4b' vertex format
def obj_to_rdm(obj_file):
    # First we parse groups of faces from the obj file
    groups = {}
    vertices = []
    faces = []
    materials = []

    obj_v = obj_file.vertices
    obj_n = obj_file.normals
    obj_t = obj_file.uv

    rdm_vertices = []
    # We iterate over the number of objects, which become groups in the rdm file
    n = 0
    for i, obj in enumerate(obj_file.objects):
        groups['group_{:}'.format(i)] = rdm.Group(offset=n, size=len(obj.faces) * 3, n=i)

        for k, face in enumerate(obj.faces):
            # We check that we have indeed triangles
            if len(face) != 3:
                raise ValueError("Faces should be triangles, not lines nor quads")

            for v in face:
                if v in vertices:
                    # The vertex has already been parsed
                    new_index = vertices.index(v)
                else:
                    # We obtain position and uv from the obj file
                    v_tmp = [{'pos': obj_v[vk[0] - 1], 'tex': obj_t[vk[1] - 1], 'norm': obj_n[vk[2]-1]} for vk in face]
                    # We compute here the tangent and bitangent for this face (very approximative atm)
                    bitan, tan = calc_tan(*v_tmp)
                    # We then parse the vertex
                    vertex = rdm.Vertex({'vformat': 'P4h_N4b_G4b_B4b_T2h',
                                         'pos': padding(obj_v[v[0] - 1], 4, value=0),
                                         'norm': padding(convert_normal2rdm(obj_n[v[2] - 1]), 4, value=0),
                                         'tex': convert_uv(obj_t[v[1] - 1]),
                                         'tan': padding(tan, 4),
                                         'bitan': padding(bitan, 4),
                                         'unknown_I': (0, 0, 0, 0)}).pack()
                    rdm_vertices.append(vertex)
                    vertices.append(v)
                    new_index = len(vertices) - 1

                faces.append(rdm.VertexIndex(format='H', index=new_index).pack())
                n += 1

        name = rdm.AnnoString('group_{:}'.format(i).encode('ascii'))
        texture = rdm.AnnoString('dummy_texture.tga'.encode('ascii'))
        materials.append(rdm.Material(name=name, texture=texture, flag=rdm.SingleInt(0)))


    # Now we create all the necessary records
    mesh_strings = rdm.StringRecord.from_strings(['mesh_name'] + [None] * 6)
    unknown_0 = rdm.UnknownRecord.from_list(
        [rdm.IntArray([(0, 6, 0, 4), (1, 5, 6, 1), (2, 5, 6, 1), (3, 5, 6, 1), (4, 6, 0, 2)])] + [None] * 5)
    unknown_1 = rdm.IntArray([(3, 0, 0, 0, 0)])
    mesh_flags = {'unknown_{:}'.format(i + 2): rdm.SingleInt(v) for i, v in enumerate(
        [4294967295, 3229040640, 3214516224, 3227828224, 1082277888, 1078779904, 1079975936] + 10 * [0])}
    mesh_record = rdm.MeshRecord({**{'strings': mesh_strings,
                                     'unknown_0': unknown_0,
                                     'unknown_1': unknown_1,
                                     'vertices': rdm.DataArray(rdm_vertices),
                                     'faces': rdm.DataArray(faces),
                                     'groups': rdm.GroupRecord(groups)}, **mesh_flags})

    string_record = rdm.StringRecord.from_strings(
        ['generated by VonZeeple\'s awesome rdm converter', 'static_norm.rmp'] + [None] * 16)

    flags = {'unknown_{:}'.format(i): v for i, v in enumerate([None] * 9)}

    materials_record = rdm.MaterialsRecord({'material_{:}'.format(i): m for i, m in enumerate(materials)})
    main_record = rdm.MainRecord({**{'strings': string_record, 'mesh': mesh_record, 'materials': materials_record},
                                  **flags})

    rdm_file = rdm.RDMFile(rdm_tag='RDM', dummy_char=1, unknown_0=[20, 0, 4, 28], main_record=main_record)
    return rdm_file


def rdm_to_obj(rdm_file):
    raw_vertices = rdm_file.main_record.get('mesh', {}).get('vertices')
    vertices = [rdm.Vertex.parse(data) for data in raw_vertices]
    groups = list(rdm_file.main_record.get('mesh', {}).get('groups', {}).values())
    raw_faces = rdm_file.main_record.get('mesh', {}).get('faces')
    faces_v_indices = [unpack_v_index(data) for data in raw_faces]
    materials = list(rdm_file.main_record.get('materials', {}).values())

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
        obj_f = [[[f[0] + 1] * 3, [f[1] + 1] * 3, [f[2] + 1] * 3] for f in faces]

        obj_objects.append(OBJObject(name=name, faces=obj_f))

    obj_file = OBJFile(vertices=obj_v, normals=obj_n, uv=obj_uv, objects=obj_objects)
    return obj_file
