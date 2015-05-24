import pytest
from util.assemble import SPYMHeader

ideal_from_sections = SPYMHeader()
ideal_from_sections.text_off = 20
ideal_from_sections.text_size = 4
ideal_from_sections.data_off = 24
ideal_from_sections.data_size = 4


def headers_are_same(one, two):
    return all([one.text_off == two.text_off,
                one.text_size == two.text_size,
                one.data_off == two.data_off,
                one.data_size == two.data_size])


def test_spym_header():
    assert headers_are_same(ideal_from_sections,
                            SPYMHeader({'text': 'text', 'data': 'data'}))
    with pytest.raises(Exception):
        SPYMHeader(binary='lessthan20')
    with pytest.raises(Exception):
        SPYMHeader(binary='a'*20)
