import rdm
from converter import *
import obj


filename = 'substation'

obj_file = obj.parse_obj_file(filename+'.obj')
rdm_file = obj_to_rdm(obj_file)

rdm.write_rdm_file(filename+'.rdm', rdm_file)

obj_file2 = rdm_to_obj(rdm_file)
obj.write_obj_file(filename+'_copy.obj', obj_file2)

#obj_file3 = obj.parse_obj_file(filename+'_copy.obj')

