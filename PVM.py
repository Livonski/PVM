from dataclasses import dataclass, field
from enum import Enum

import array

ADRESS = 0
LABEL  = 1

S32BI = 4
U8BI  = 1
VOID  = 0

#instruction reference
#OP(dec/hex), Assembly name, parameters (name-s/u size) (0 - no parameters)
#1  /01 - PUSH   value-s4
#10 /0A - ADD    0
#12 /0C - MUL    0
#32 /20 - STORE  adress-u1
#33 /21 - LOAD   adress-u1
#34 /22 - LSTORE index-u1
#35 /23 - LLOAD  index-u1
#48 /30 - EQ     0
#49 /31 - LT     0
#50 /32 - GT     0
#64 /40 - JMP    toLabel-u1 instruction-u1
#65 /41 - JZ     toLabel-u1 instruction-u1
#66 /42 - CALL   adress u1
#67 /43 - RET    0
#68 /44 - ENTER  count-u1
#254/FE - PRINT  0
#255/FF - HALT   0


class OP(Enum):
    PUSH   = 1
    ADD    = 10
    MUL    = 12
    STORE  = 32
    LOAD   = 33
    LSTORE = 34
    LLOAD  = 35
    EQ     = 48
    LT     = 49
    GT     = 50
    JMP    = 64
    JZ     = 65
    CALL   = 66
    RET    = 67
    ENTER  = 68
    PRINT  = 254
    HALT   = 255

class memorySize(Enum):
    STACK        = 256
    REGISTERS    = 256
    CALLSTACK    = 32
    LMINDEX      = 32
    LMCOUNT      = 32
    LMDATA       = 256
    INSTRUCTIONS = 256

@dataclass
class stack:
    na: int
    sp: int
    capacity: int
    items: bytearray

@dataclass
class registers:
    numRegisters: int
    items: bytearray

@dataclass
class PVM:
    data:         stack
    RAM:          registers
    callstack:    stack
    LMIndex:      stack
    LMCount:      stack
    LMData:       registers
    instructions: stack
    labels:       array.array = field(default_factory=lambda: array.array('B'))

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

def localMemoryAllocate(VM, count, size):
    totalLocalMemoryUsed = 0
    OLMCNA = VM.LMCount.na
    VM.LMCount.na = 0
    for i in range(0, OLMCNA):
        v = stackRead(VM.LMCount)
        totalLocalMemoryUsed += int.from_bytes(v, byteorder = "little", signed = False)
        VM.LMCount.na += 1
    stackPush(VM.LMIndex, totalLocalMemoryUsed)
    stackPush(VM.LMCount, count*size)

def localMemoryStore(VM, v, ladrr, size):
    lCount = int.from_bytes(stackRead(VM.LMCount), byteorder = "little", signed = False)
    if(ladrr + size > lCount):
        raise MemoryError(f"Trying to read a local adress({ladrr}) outside of allocated adress space({lCount})")
    adrr = int.from_bytes(stackRead(VM.LMIndex), byteorder = "little", signed = False) + ladrr
    registerStore(VM.LMData, v, adrr, size)

def localMemoryLoad(VM, ladrr, size):
    lCount = int.from_bytes(stackRead(VM.LMCount), byteorder = "little", signed = False)
    if(ladrr + size > lCount):
        raise MemoryError(f"Trying to write to a local adress({ladrr}) outside of allocated adress space({lCount})")
    adrr = int.from_bytes(stackRead(VM.LMIndex), byteorder = "little", signed = False) + ladrr
    return registerLoad(VM.LMData, adrr, size)
    
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

data         = stack(sp = -1, na = 0, capacity = memorySize.STACK.value, items = bytearray(memorySize.STACK.value))
RAM          = registers(numRegisters = memorySize.REGISTERS.value, items = bytearray(memorySize.REGISTERS.value))
instructions = stack(sp = 0, na = 0,  capacity = memorySize.INSTRUCTIONS.value, items = bytearray(memorySize.INSTRUCTIONS.value))
callstack    = stack(sp = -1, na = 0, capacity = memorySize.CALLSTACK.value, items = bytearray(memorySize.CALLSTACK.value))
LMIndex      = stack(sp = -1, na = 0, capacity = memorySize.LMINDEX.value, items = bytearray(memorySize.LMINDEX.value))
LMCount      = stack(sp = -1, na = 0, capacity = memorySize.LMCOUNT.value, items = bytearray(memorySize.LMCOUNT.value))
LMData       = registers(numRegisters = memorySize.LMDATA.value, items = bytearray(memorySize.LMDATA.value))

VM = PVM(data = data, RAM = RAM, callstack = callstack, LMIndex = LMIndex, LMCount = LMCount, LMData = LMData, instructions = instructions)

#Loading instructions in memory
#square example
loadInstruction(VM.instructions, OP.PUSH.value,  [7], S32BI)
loadInstruction(VM.instructions, OP.CALL.value,  [1, 0], U8BI)
loadInstruction(VM.instructions, OP.PRINT.value, [], VOID)
loadInstruction(VM.instructions, OP.HALT.value,  [], VOID)

#Label-0 Square function
VM.labels.append(VM.instructions.na)
loadInstruction(VM.instructions, OP.ENTER.value,  [1], U8BI)
loadInstruction(VM.instructions, OP.LSTORE.value, [0], U8BI)
loadInstruction(VM.instructions, OP.LLOAD.value,  [0], U8BI)
loadInstruction(VM.instructions, OP.LLOAD.value,  [0], U8BI)
loadInstruction(VM.instructions, OP.MUL.value,    [0], VOID)
loadInstruction(VM.instructions, OP.RET.value,    [0], VOID)
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
        case OP.LSTORE.value:
            adrr = readNextInstruction(VM.instructions, U8BI)
            sv = stackPop(VM.data)
            localMemoryStore(VM, sv, adrr, S32BI)
        case OP.LLOAD.value:
            adrr = readNextInstruction(VM.instructions, U8BI)
            v = localMemoryLoad(VM, adrr, S32BI)
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
                raise ValueError(f"Trying to jump to an instruction({adrr}) outside of instruction set")
            
            VM.instructions.sp = adrr
        case OP.JZ.value:
            toLabel = readNextInstruction(VM.instructions, U8BI)
            if toLabel:
                labelID = readNextInstruction(VM.instructions, U8BI)
                adrr    = VM.labels[labelID]
            else:
                adrr = readNextInstruction(VM.instructions, U8BI)
            
            if(adrr > VM.instructions.capacity):
                raise ValueError(f"Trying to jump to an instruction({adrr}) outside of instruction set")
            
            condition = stackPop(VM.data)
            if condition == 0:
                VM.instructions.sp = adrr
        case OP.CALL.value:
            toLabel = readNextInstruction(VM.instructions, U8BI)
            if toLabel:
                labelID = readNextInstruction(VM.instructions, U8BI)
                adrr    = VM.labels[labelID]
            else:
                adrr = readNextInstruction(VM.instructions, U8BI)
                        
            if(adrr > VM.instructions.capacity):
                raise ValueError(f"Trying to call an instruction({adrr}) outside of instruction set")

            stackPush(VM.callstack, VM.instructions.sp)
            VM.instructions.sp = adrr
        case OP.ENTER.value:
            count = readNextInstruction(VM.instructions, U8BI)
            localMemoryAllocate(VM, count, S32BI)
        case OP.RET.value:
            stackPop(VM.LMCount)
            stackPop(VM.LMIndex)
            rAdrr = stackPop(VM.callstack)
            VM.instructions.sp = rAdrr
        case OP.PRINT.value:
            print("PVM has something to tell you - ", stackPop(VM.data))
        case OP.HALT.value:
            print("Halt reached. VM finished execution")
            break
        case _:
            raise SyntaxError(f"Unknown OP {opcode}, isp - {VM.instructions.sp}")
        
#VM after processing instructions
printVM(VM)