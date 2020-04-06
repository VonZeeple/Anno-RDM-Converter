import rdm
from converter import *
from obj import *


filename = 'D:/modding/Anno1800/data_Anno1800/data/graphics/buildings/production/workshop_colony01_01/rdm/workshop_colony01_01_lod0.rdm'

with open(filename, 'rb') as f:
    data_0 = f.read()
rdm_file = rdm.RDMFile.parse(data_0)


write_obj_file('test_out.obj', rdm_to_obj(rdm_file))



# To convert from obj to RDM:
# first check if all polygons are triangles
