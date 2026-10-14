from dataclasses import dataclass, field
from enum import Enum

import array

#instruction reference
#OP(dec/hex), Assembly name, parameters (name-s/u size) (0 - no parameters)
#1  /01 - PUSH  value-s4
#10 /0A - ADD   0
#12 /0C - MUL   0
#32 /20 - STORE adress-u1
#33 /21 - LOAD  adress-u1
#48 /30 - EQ    0
#49 /31 - LT    0
#50 /32 - GT    0
#64 /40 - JMP   toLabel-u1 instruction-u1
#65 /41 - JZ    toLabel-u1 instruction-u1
#254/FE - PRINT 0
#255/FF - HALT  0

ADRESS = 0
LABEL  = 1

S32BI = 4
U8BI  = 1
VOID  = 0

class OP(Enum):
    PUSH  = 1
    ADD   = 10
    MUL   = 12
    STORE = 32
    LOAD  = 33
    EQ    = 48
    LT    = 49
    GT    = 50
    JMP   = 64
    JZ    = 65
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
    labels : array.array = field(default_factory=lambda: array.array('B'))

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
    if(s.sp + bLen > s.na):
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
#while
loadInstruction(VM.instructions, OP.PUSH.value,  [0], S32BI) #0 
loadInstruction(VM.instructions, OP.STORE.value, [0], U8BI) #5 
loadInstruction(VM.instructions, OP.PUSH.value,  [1], S32BI) #7 
loadInstruction(VM.instructions, OP.STORE.value, [4], U8BI) #12

VM.labels.append(VM.instructions.na) #While condition label-0
loadInstruction(VM.instructions, OP.LOAD.value,  [4], U8BI)  #14
loadInstruction(VM.instructions, OP.PUSH.value,  [5], S32BI) #16
loadInstruction(VM.instructions, OP.GT.value,    [], VOID)     #21
loadInstruction(VM.instructions, OP.JZ.value,    [LABEL, 1], U8BI)   #22
loadInstruction(VM.instructions, OP.JMP.value,   [LABEL, 2], U8BI)  #24

VM.labels.append(VM.instructions.na) #While body label-1
loadInstruction(VM.instructions, OP.LOAD.value,  [0], U8BI)  #26
loadInstruction(VM.instructions, OP.LOAD.value,  [4], U8BI)  #28
loadInstruction(VM.instructions, OP.ADD.value,   [], VOID)    #30
loadInstruction(VM.instructions, OP.STORE.value, [0], U8BI) #31

loadInstruction(VM.instructions, OP.LOAD.value,  [4], U8BI)  #33
loadInstruction(VM.instructions, OP.PUSH.value,  [1], S32BI) #35
loadInstruction(VM.instructions, OP.ADD.value,   [], VOID)    #40
loadInstruction(VM.instructions, OP.STORE.value, [4], U8BI) #41 

loadInstruction(VM.instructions, OP.JMP.value,   [LABEL, 0], U8BI)  #43

VM.labels.append(VM.instructions.na) #End label-2
loadInstruction(VM.instructions, OP.LOAD.value,  [0], U8BI)  #45
loadInstruction(VM.instructions, OP.PRINT.value, [], VOID)  #47
loadInstruction(VM.instructions, OP.HALT.value,  [], VOID)   #48
#=============

#VM before processing instructions
#printVM(VM)

#Processing instructions
while(1):
    opcode = readNextInstruction(VM.instructions, U8BI)
    match opcode:
        case OP.PUSH.value:
            Arg = readNextInstruction(VM.instructions, S32BI)
            stackPush(VM.data, Arg)
        case OP.ADD.value:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            stackPush(VM.data, Y + X)
        case OP.MUL.value:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            stackPush(VM.data, Y * X)
        case OP.STORE.value:
            adrr = readNextInstruction(VM.instructions, U8BI)
            sv = stackPop(VM.data)
            registerStore(VM.RAM, sv, adrr, S32BI)
        case OP.LOAD.value:
            adrr = readNextInstruction(VM.instructions, U8BI)
            v = registerLoad(VM.RAM, adrr, S32BI)
            stackPush(VM.data, v)
        case OP.EQ.value:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            stackPush(VM.data, Y == X)
        case OP.LT.value:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            stackPush(VM.data, Y < X)
        case OP.GT.value:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            stackPush(VM.data, Y > X)
        case OP.JMP.value:
            toLabel = readNextInstruction(VM.instructions, U8BI)
            if toLabel:
                labelID = readNextInstruction(VM.instructions, U8BI)
                adrr    = VM.labels[labelID]
            else:
                adrr = readNextInstruction(VM.instructions, U8BI)

            if(adrr > VM.instructions.capacity):
                raise ValueError(f"Trying to jump to a instruction({adrr}) outside of instruction set")
            
            VM.instructions.sp = adrr
        case OP.JZ.value:
            toLabel = readNextInstruction(VM.instructions, U8BI)
            if toLabel:
                labelID = readNextInstruction(VM.instructions, U8BI)
                adrr    = VM.labels[labelID]
            else:
                adrr = readNextInstruction(VM.instructions, U8BI)
            
            if(adrr > VM.instructions.capacity):
                raise ValueError(f"Trying to jump to a instruction({adrr}) outside of instruction set")
            
            condition = stackPop(VM.data)
            if condition == 0:
                VM.instructions.sp = adrr
        case OP.PRINT.value:
            print("PVM has something to tell you - ", stackPop(VM.data))
        case OP.HALT.value:
            print("Halt reached. VM finished execution")
            break
        case _:
            raise SyntaxError(f"Unknown OP {opcode}, isp - {VM.instructions.sp}")
        
#VM after processing instructions
#printVM(VM)