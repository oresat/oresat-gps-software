import struct

line = b'\xA0\xA1\x00\x3B\xA8\x02\x08\x06\x04\x02\x32\x18\x18\x0E\xC5\xE1\x99\x48\x20\x78\xED\x00\x00\x2E\x3B\x00\x00\x26\x93\x00\x93\x00\x93\x00\x93\x00\x93\x00\x93\xEE\x35\x4D\x30\x1D\x99\xAA\x37\x0F\xD7\x0B\x74\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xF5\x0D\x0A'

data_byte = struct.unpack('<4x3BHI2i2I5H6i3x', line)

print(data_byte)

for i in line:
    print(bin(i))

def valid_message(message) -> bool:
    message_len = len(message)
    payload_len = message_len - 8

    if message_len <= 8:
        return False

    unpack_str = "2bh{}b".format(payload_len+4)
    print(unpack_str)

    try:
        data_byte = struct.unpack(unpack_str, message)
    except struct.error as exc:
        print('Parse error: {}\n'.format(exc))
        return False

    print(bin(data_byte[0]))
    print(hex(data_byte[1]))
    print(hex(data_byte[2]))
    if data_byte[0] != 0xA0 or \
            data_byte[1] != 0xA1 or \
            data_byte[2] != payload_len or \
            data_byte[-2] != 0x0D or \
            data_byte[-1] != 0x0A:
        print("invalid header or tails bytes")
        return False

    cs = 0
    for i in data_byte[3:-3]:
        cs = bin(cs) ^ bin(i)

    if cs != data_byte[-3]:
        print("invalid cs")
        return False


print(valid_message(line))
