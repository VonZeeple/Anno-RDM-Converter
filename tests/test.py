import converter
import rdm
import pytest

v2 = {'pos': [0.1, 0.1, 0.1], 'norm': [1.0, 0, 0], 'tex': [1.0, 1.0]}
v3 = {'pos': [0.1, 1.0, 0.1], 'norm': [1.0, 0, 0], 'tex': [1.0, 1.0]}


@pytest.mark.parametrize("args, expected", [
    ([None, v2, v3], 'AttributeError'),
    ([{'pos': [0.1, 0.1, 0.1], 'norm': [0.0, 0, 0], 'tex': [1.0, 1.0]}, v2, v3], 'ZeroDivisionError'),
    ([v2, v3], 'TypeError')
])
def test_calc_tan_attribute_error(args, expected):
    with pytest.raises(Exception) as error:
        converter.calc_tan(*args)
    assert str(error.typename) == expected
    # TODO write positive test


@pytest.mark.parametrize("input_list, input_bytes, output_bytes, output_offset", [
    ([0, 1, 2], bytearray(), b'\x01\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00', 8),
    ([0, 1, 2], bytearray(b'\x00\x00'),
     b'\x00\x00\x01\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00', 10),
    ([0, 1], bytearray(), b'\x01\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00', 8),
    ((0, 1), bytearray(), b'\x01\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00', 8),
    ([[1, 1], [1, 1]], bytearray(),
     b'\x02\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00', 8),
    ([[1, 1]], bytearray(), b'\x01\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00', 8),
    ([[1, 1]], bytes(), b'', 8),
    ([[1, 1]], b'', b'', 8),
    ([], bytearray(), bytearray(), 0),
])
def test_pack_int_array(input_list, input_bytes, output_bytes, output_offset):
    offset = rdm.IntArray(input_list).pack(input_bytes)
    assert input_bytes == output_bytes
    assert output_offset == offset


@pytest.mark.parametrize("data, offset, output", [
    (b'\x01\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00', 8, ((0, 1, 2),)),
    (b'\x00\x00\x01\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00', 10, ((0, 1, 2),)),
    (b'\x01\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00', 8, ((0, 1),)),
    (b'\x02\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00', 8, ((1, 1), (1, 1))),
    (b'\x01\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00', 8, ((1, 1),)),

])
def test_parse_int_array(data, offset, output):
    out = rdm.IntArray.parse(data, offset)
    assert rdm.IntArray(output) == out


@pytest.mark.parametrize("input_list, input_bytes, typename, value", [
    (1, bytearray(), 'TypeError', '\'int\' object is not iterable'),
    (None, bytearray(), 'TypeError', '\'NoneType\' object is not iterable'),
    ([2 ** 32], bytearray(), 'error', 'argument out of range'),
    ([1.9], bytearray(), 'error', 'required argument is not an integer'),
    ([[1], [1, 2]], bytearray(), 'error', 'pack expected 1 items for packing (got 2)'),
    ([[1, 2], [1]], bytearray(), 'error', 'pack expected 2 items for packing (got 1)')
])
def test_parse_int_array_errors(input_list, input_bytes, typename, value):
    with pytest.raises(Exception) as error:
        rdm.IntArray(input_list).pack(input_bytes)
    assert str(error.typename) == typename
    assert str(error.value) == value
