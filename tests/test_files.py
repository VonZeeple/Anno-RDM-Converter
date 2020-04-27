from anno_rdm_converter import rdm
import pytest
import os

#some test with real files from anno 1800
data_path = "D:\\modding\\Anno1800\\data_Anno1800\\data\\"

filenames = [
    "D:\\modding\\Anno1800\\data_Anno1800\\data\\graphics\\buildings\\production\\factory_colony_01_03\\rdm\\factory_colony01_03_lod0.rdm",
'dlc02\\graphics\\buildings\\cultural\\cultural_03\\cultural_03_module_04\\cultural_03_module_04_h\\rdm\\cultural_03_module_04_j.rdm'
]
@pytest.mark.parametrize("filename", filenames)
def test_parse_file_header(filename):
    rdm.load_rdm_file(os.path.join(data_path, filename))