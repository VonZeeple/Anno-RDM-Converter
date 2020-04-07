import rdm
import unittest
import pywavefront
import obj
import converter

class TangentCalculationTest(unittest.TestCase):


    def test_tangents(self):
        filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_03/rdm/workshop_03_01_lod0.rdm'
        with open(filename, 'rb') as f:
            model = rdm.RDMFile.parse(f.read())
        vertices = [rdm.Vertex.parse(data) for data in model.main_record.get('Mesh').get('vertices')]
        v_index = [rdm.VertexIndex.parse(data).index for data in model.main_record.get('Mesh').get('faces')]
        ordered_vertices = [vertices[i] for i in v_index]

        faces = [ordered_vertices[i:i+3] for i in range(0,len(ordered_vertices), 3)]


class UnpackingTest(unittest.TestCase):
    # filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_03/rdm/workshop_03_01_lod0.rdm'
    # filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/props/storage/rdm/ammo_crate_01_lod2.rdm'

    #We should be able to load the converted obj file with pywavefront
    def test_pywavefront(self):
        filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_colony01_01/rdm/workshop_colony01_01_lod0.rdm'
        with open(filename, 'rb') as f:
            model = rdm.RDMFile.parse(f.read())
        obj_model = converter.rdm_to_obj(model)
        obj.write_obj_file('test_out.obj', obj_model)
        scene = pywavefront.Wavefront('test_out.obj')
        print(scene.meshes)


    def test_parsing(self):
        filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_colony01_01/rdm/workshop_colony01_01_lod0.rdm'
        #filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/props/storage/rdm/ammo_crate_01_lod2.rdm'
        #we should obtain the same bytearray after parsing and packing:
        with open(filename, 'rb') as f:
            data_0 = f.read()
        parsed = rdm.RDMFile.parse(data_0)
        compiled = parsed.pack()
        self.assertEqual(bytearray(data_0), compiled, 'Problem with parsing or packing')




