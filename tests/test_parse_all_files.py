import pytest
import anno_rdm_converter.rdm as rdm
import os

data_path = "D:\\modding\\Anno1800\\data_Anno1800\\data\\"


def get_all_rdm_files():
    if not os.path.exists("tests\\files_to_test.txt"):
        find_all_files("tests\\files_to_test.txt")
    with open("tests\\files_to_test.txt", 'r') as f:
        filenames = f.read().split('\n')[:-1]
    return filenames


def find_all_files(out_filename):
    with open(out_filename, 'w') as f:
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.endswith(".rdm"):
                    f.write(os.path.join(os.path.relpath(root, data_path), file)+'\n')


# We check that all rdm files from anno 1800 can be parsed without error
# We discard files for animations
@pytest.mark.parametrize("filename", [s for s in get_all_rdm_files() if s.find("anim") == -1])
def test_parse_file(filename):
        rdm.load_rdm_file(os.path.join(data_path, filename))

# TODO: check that the file is the same bitwise after parsing and re-encoding.






