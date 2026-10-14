def test(n):
    encoded = n.to_bytes(4, byteorder = "little", signed = True)
    decoded = int.from_bytes(encoded, byteorder = "little", signed = True)    
    print("original: ", n, " encoded: ", encoded, " decoded ", decoded)

test(256)
test(65535)
test(-1)

code = bytearray(16)
code[0] = 0x01
code[1] = 0x06
code[2] = 0x00
code[3] = 0x00
code[4] = 0x00

code[5] = 0x01
code[6] = 0x07
code[7] = 0x00
code[8] = 0x00
code[9] = 0x00

code[10] = 0x0C

code[11] = 0x01
code[12] = 0x02
code[13] = 0x00
code[14] = 0x00
code[15] = 0x00

print(code)

OP = code[0]
arg = int.from_bytes(code[1:4], byteorder = "little", signed = True)    
if(OP == 1):
    print("PUSH ", arg)
else:
    print("Failed to read correct OP")