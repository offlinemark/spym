import pytest
from util.assemble import SPYMHeader, SPYM_HDR_LEN

ideal_from_sections = SPYMHeader()
ideal_from_sections.text_off = SPYM_HDR_LEN
ideal_from_sections.text_size = 4
ideal_from_sections.data_off = SPYM_HDR_LEN + 4
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
        SPYMHeader(binary='lessthanhdrlen')
    with pytest.raises(Exception):
        SPYMHeader(binary='a'*SPYM_HDR_LEN)
