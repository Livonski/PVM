from dataclasses import dataclass, field
from enum import Enum

import array

#instruction reference
#OP(dec/hex), Assembly name, How many parameters
#1  /01 - PUSH 1
#10 /0A - ADD 0
#12 /0C - MUL 0
#254/FE - PRINT 0
#255/FF - HALT 0

class OP(Enum):
    PUSH  = 1
    ADD   = 10
    MUL   = 12
    PRINT = 254
    HALT  = 255

class stackSize(Enum):
    DATA         = 32
    INSTRUCTIONS = 32

@dataclass
class stack:
    na : int
    sp : int
    capacity: int
    items: bytearray

@dataclass
class PVM:
    data: stack
    instructions: stack

def stackPush(s, v):
    if(s.na + 4 >= s.capacity):
        raise MemoryError("Stack overflow")
    s.items[s.na:s.na + 4] = v.to_bytes(4, byteorder="little", signed = True)
    s.sp = s.sp + 4
    s.na = s.na + 4

def stackPop(s):
    if(s.sp == -1):
        raise MemoryError("Stack underflow")
    v = stackRead(s)
    s.na = s.na - 4
    s.sp = s.sp - 4
    return int.from_bytes(v, byteorder = "little", signed = True)

def stackRead(s):
    #for a case where we attempt to read a 0 element of the stack
    if(s.sp == -1):
        raise MemoryError("Stack is empty")
    return s.items[s.sp - 3:s.sp + 1]

def readNextInstruction(s, bLen):
    if(s.sp + bLen > s.capacity):
        raise MemoryError("Trying to read instructions outside of memory")
    operand = s.items[s.sp:s.sp + bLen]
    s.sp = s.sp + bLen
    return int.from_bytes(operand, byteorder = "little", signed = (bLen == 4))

def loadInstruction(s, operand, args):
    #OP size is always 1 byte, args are represented as 32b integers so 4 bytes for each arg
    opSize = 1 + len(args) * 4
    if(s.na + opSize > s.capacity):
        raise MemoryError("Instruction stack overflow")
    s.items[s.na] = operand
    s.na = s.na + 1
    for arg in args:
        s.items[s.na:s.na + 4] = arg.to_bytes(4, byteorder="little", signed = True)
        s.na = s.na + 4



def printVM(vm):
    print("Stack:")
    print(VM.data.items)

    print("Instructions:")
    print(VM.instructions.items)

data = stack(sp = -1, na = 0, capacity = stackSize.DATA.value, items = bytearray(stackSize.DATA.value))
instructions = stack(sp = 0, na = 0, capacity = stackSize.INSTRUCTIONS.value, items = bytearray(stackSize.INSTRUCTIONS.value))
VM = PVM(data = data, instructions = instructions)

#Loading instructions in memory
loadInstruction(VM.instructions, OP.PUSH.value, [6])
loadInstruction(VM.instructions, OP.PUSH.value, [7])
loadInstruction(VM.instructions, OP.MUL.value, [])
loadInstruction(VM.instructions, OP.PUSH.value, [2])
loadInstruction(VM.instructions, OP.ADD.value, [])
loadInstruction(VM.instructions, OP.PRINT.value, [])

loadInstruction(VM.instructions, OP.PUSH.value, [-100000])
loadInstruction(VM.instructions, OP.PRINT.value, [])
loadInstruction(VM.instructions, OP.HALT.value, [])

#VM before processing instructions
printVM(VM)

#Processing instructions
while(1):
    opcode = readNextInstruction(VM.instructions, 1)
    match opcode:
        case OP.PUSH.value:
            Arg = readNextInstruction(VM.instructions, 4)
            #print("PUSH ", Arg)
            stackPush(VM.data, Arg)
        case OP.ADD.value:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            #print("ADD")
            stackPush(VM.data, X + Y)
        case OP.MUL.value:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            #print("MUL")
            stackPush(VM.data, X * Y)
        case OP.PRINT.value:
            #print("PRINT")
            print("PVM has something to tell you - ", stackPop(VM.data))
        case OP.HALT.value:
            #print("HALT")
            VM.data.sp = -1
            print("Halt reached. VM finished execution")
            break
        case _:
            raise SyntaxError(f"Unknown OP {opcode}, isp - {VM.instructions.sp}")
        
#VM after processing instructions
printVM(VM)