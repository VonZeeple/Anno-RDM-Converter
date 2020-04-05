import rdm
import unittest


class UnpackingTest(unittest.TestCase):

    def test_parsing(self):

        #filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_03/rdm/workshop_03_01_lod0.rdm'
        #filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/props/storage/rdm/ammo_crate_01_lod2.rdm'
        filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_colony01_01/rdm/workshop_colony01_01_lod0.rdm'

        #we should obtain the same bytearray after parsing and packing:
        with open(filename, 'rb') as f:
            data_0 = f.read()
        parsed = rdm.RDMFile.parse(data_0)
        compiled = parsed.pack()
        self.assertEqual(bytearray(data_0), compiled, 'Problem with parsing or packing')




