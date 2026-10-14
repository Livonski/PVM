from dataclasses import dataclass, field
from enum import Enum

import array

#instruction reference
#OP(dec/hex), Assembly name, parameters (name-s/u size) (0 - no parameters)
#1  /01 - PUSH  value-s4
#10 /0A - ADD   0
#12 /0C - MUL   0
#20 /20 - STORE adress-u1
#21 /21 - LOAD  adress-u1
#254/FE - PRINT 0
#255/FF - HALT  0

class OP(Enum):
    PUSH  = 1
    ADD   = 10
    MUL   = 12
    STORE = 20
    LOAD  = 21
    PRINT = 254
    HALT  = 255

class memorySize(Enum):
    STACK        = 256
    REGISTERS    = 256
    INSTRUCTIONS = 256

@dataclass
class stack:
    na : int
    sp : int
    capacity: int
    items: bytearray

@dataclass
class registers:
    numRegisters: int
    items: bytearray

@dataclass
class PVM:
    data: stack
    RAM: registers
    instructions: stack

def stackPush(s, v):
    if(s.na + 4 > s.capacity):
        raise MemoryError("Stack overflow")
    s.items[s.na:s.na + 4] = v.to_bytes(4, byteorder = "little", signed = True)
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

def registerStore(r, v, adrr, size):
    if(adrr + size > r.numRegisters):
        raise MemoryError(f"Trying to write to a register({adrr}:{adrr+size}) outside of memory({r.numRegisters})")
    r.items[adrr:adrr + size] = v.to_bytes(size, byteorder = "little", signed = True)

def registerLoad(r, adrr, size):
    if(adrr + size > r.numRegisters):
        raise MemoryError(f"Trying to read a register({adrr}:{adrr+size}) outside of memory({r.numRegisters})")
    v = r.items[adrr:adrr + size]
    return int.from_bytes(v, byteorder = "little", signed = True)


def readNextInstruction(s, bLen):
    if(s.sp + bLen > s.capacity):
        raise MemoryError("Trying to read instructions outside of memory")
    operand = s.items[s.sp:s.sp + bLen]
    s.sp = s.sp + bLen
    return int.from_bytes(operand, byteorder = "little", signed = (bLen == 4))

def loadInstruction(s, operand, args, argSize):
    #OP size is always 1 byte, args are represented as 32b integers so 4 bytes for each arg
    opSize = 1 + len(args) * argSize
    if(s.na + opSize > s.capacity):
        raise MemoryError("Instruction stack overflow")
    s.items[s.na] = operand
    s.na += 1
    for arg in args:
        s.items[s.na:s.na + argSize] = arg.to_bytes(argSize, byteorder="little", signed =(argSize == 4))
        s.na += argSize

def printVM(vm):
    print("Stack:")
    print(VM.data.items)

    print("Registers:")
    print(VM.RAM.items)

    print("Instructions:")
    print(VM.instructions.items)

data = stack(sp = -1, na = 0, capacity = memorySize.STACK.value, items = bytearray(memorySize.STACK.value))
instructions = stack(sp = 0, na = 0, capacity = memorySize.INSTRUCTIONS.value, items = bytearray(memorySize.INSTRUCTIONS.value))
RAM = registers(numRegisters = memorySize.REGISTERS.value, items = bytearray(memorySize.REGISTERS.value))
VM = PVM(data = data, RAM = RAM, instructions = instructions)

#Loading instructions in memory
loadInstruction(VM.instructions, OP.PUSH.value, [6], 4)
loadInstruction(VM.instructions, OP.PUSH.value, [7], 4)
loadInstruction(VM.instructions, OP.MUL.value, [], 0)
loadInstruction(VM.instructions, OP.STORE.value, [0], 1)

loadInstruction(VM.instructions, OP.LOAD.value, [0], 1)
loadInstruction(VM.instructions, OP.PUSH.value, [2], 4)
loadInstruction(VM.instructions, OP.ADD.value, [], 0)
loadInstruction(VM.instructions, OP.STORE.value, [4], 1)

loadInstruction(VM.instructions, OP.LOAD.value, [4], 1)
loadInstruction(VM.instructions, OP.PRINT.value, [], 0)
loadInstruction(VM.instructions, OP.HALT.value, [], 0)

#VM before processing instructions
#printVM(VM)

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
        case OP.STORE.value:
            adrr = readNextInstruction(VM.instructions, 1)
            sv = stackPop(VM.data)
            registerStore(VM.RAM, sv, adrr, 4)
        case OP.LOAD.value:
            adrr = readNextInstruction(VM.instructions, 1)
            v = registerLoad(VM.RAM, adrr, 4)
            stackPush(VM.data, v)
        case OP.PRINT.value:
            #print("PRINT")
            print("PVM has something to tell you - ", stackPop(VM.data))
        case OP.HALT.value:
            #print("HALT")
            print("Halt reached. VM finished execution")
            break
        case _:
            raise SyntaxError(f"Unknown OP {opcode}, isp - {VM.instructions.sp}")
        
#VM after processing instructions
#printVM(VM)