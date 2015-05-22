from util.assemble import assemble


def test_assemble():
    assert assemble('test/power.s') == bytearray(b'SPYM\x1c\x00\x00\x004\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00\x06\x00\x00\x00$\x02\x00\x05\x00\x00\x00\x0c$\x08\x00\x01\x00\x02H!\x15 \x00\x06\x08\x00\x00\n\x01\x02\x00\x18\x00\x00@\x12!)\xff\xff\x08\x00\x00\x04$\x02\x00\x01\x00\x08 !\x00\x00\x00\x0c\x80\x02}q\x00.')

