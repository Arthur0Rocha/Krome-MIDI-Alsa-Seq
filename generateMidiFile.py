def midiSysEx(sysEx):
        message = [sysEx[0], len(sysEx) - 1] + sysEx[1:]

        header = [
                0x4d, 0x54, 0x68, 0x64,
                0x00, 0x00, 0x00, 0x06,
                0x00, 0x00, 
                0x00, 0x01,
                0x03, 0xc0
        ]

        content = [0x00] + message

        ending = [
                0x00, 0xff, 0x2f, 0x00
        ]

        track = [
                0x4d, 0x54, 0x72, 0x6b,
                0x00, 0x00, 0x00, len(content) + 4
        ]

        return bytes(header + track + content + ending)

combiProgram = [
        ([0xF0, 0x42, 0x30, 0x00, 0x01, 0x15, 0x4E, 0x02, 0xF7], 'PROGRAM'),
        ([0xF0, 0x42, 0x30, 0x00, 0x01, 0x15, 0x4E, 0x00, 0xF7], 'COMBI')
]

command = lambda chan, val: ([0xF0, 0x42, 0x30, 0x00, 0x01, 0x15, 0x41, 0x00, 0x00, 0x0C + chan - 1, 0x00, 0x35, 0x00, 0x00, 0x00, 0x00, val, 0xF7], f'MIDI.{chan}.{val}')
combinations = [(1, 1), (1, 0x7f), (2, 1), (2, 0x7f), (3, 1), (3, 0x7f), (4, 1), (4, 0x7f)]


for com in combinations:
        l, name = command(*com)
        f = open(name + '.MID', 'wb')
        f.write(midiSysEx(l))


# bank = 0
# tone = 16

# banks = ['A','B','C','D','E','F']

# bankname = banks[bank]

# strout =  b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x03\xc0MTrk\x00\x00\x00\x0f\x00\xb0\x00\x00\x00\xb0\x20'  \
#         + bytes([bank]) + b'\x00\xc0' \
#         + bytes([tone]) + b'\x00\xff\x2f\x00'

# f = open(f'midi-files/{bankname}{tone}.MID', 'wb')
# f.write(strout)