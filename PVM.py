from dataclasses import dataclass, field
from enum import Enum

import array

#instruction reference
#OP, Assembly name, How many parameters
#1   - PUSH 1
#10  - ADD 0
#12  - MUL 0
#254 - PRINT 0
#255 - HALT 0

class OP(Enum):
    PUSH  = 1
    ADD   = 10
    MUL   = 12
    PRINT = 254
    HALT  = 255

@dataclass
class stack:
    na : int
    sp : int
    capacity: int
    items: array.array = field(default_factory=lambda: array.array('b'))

@dataclass
class PVM:
    data: stack
    instructions: stack


def stackPush(s, v):
    if(s.na >= s.capacity):
        raise MemoryError("Stack overflow")
    s.items[s.na] = v
    s.sp = s.sp + 1
    s.na = s.na + 1

def stackPop(s):
    if(s.sp == -1):
        raise MemoryError("Stack underflow")
    v = stackRead(s)
    s.na = s.na - 1
    s.sp = s.sp - 1
    return v

def stackRead(s):
    #for a case where we attempt to read a 0 element of the stack
    if(s.sp == -1):
        raise MemoryError("Stack is empty")
    return s.items[s.sp]

def readNextInstruction(s):
    if(s.sp >= s.capacity):
        raise MemoryError("Trying to read instructions outside of memory")
    operand = s.items[s.sp]
    s.sp = s.sp + 1
    return operand

def loadInstruction(s, operand):
    if(s.na == s.capacity):
        raise MemoryError("Instruction stack overflow")
    s.items[s.na] = operand
    s.na = s.na + 1

def printVM(vm):
    print("Stack:")
    for i in range(0, vm.data.capacity):
        if(i == vm.data.sp):
            print("  ->", vm.data.items[i])
        else:    
            print("    ", vm.data.items[i])

    print("Instructions:")
    for i in range(0, vm.instructions.capacity):
        if(i == vm.instructions.sp):
            print("  ->", vm.instructions.items[i])
        else:    
            print("    ", vm.instructions.items[i])

data = stack(sp = -1, na = 0, capacity = 16, items = [0] * 16)
instructions = stack(sp = 0, na = 0, capacity = 16, items = [0] * 16)
VM = PVM(data = data, instructions = instructions)

#Loading instructions in memory
loadInstruction(VM.instructions, OP.PUSH)
loadInstruction(VM.instructions, 6)
loadInstruction(VM.instructions, OP.PUSH)
loadInstruction(VM.instructions, 7)
loadInstruction(VM.instructions, OP.MUL)
loadInstruction(VM.instructions, OP.PUSH)
loadInstruction(VM.instructions, 2)
loadInstruction(VM.instructions, OP.ADD)
loadInstruction(VM.instructions, OP.PRINT)
loadInstruction(VM.instructions, OP.HALT)

#VM before processing instructions
#printVM(VM)

#Processing instructions
for i in range(0, VM.instructions.capacity):
    opcode = readNextInstruction(VM.instructions)
    match opcode:
        case OP.PUSH:
            Arg = readNextInstruction(VM.instructions)
            #print("PUSH ", Arg)
            stackPush(VM.data, Arg)
        case OP.ADD:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            #print("ADD")
            stackPush(VM.data, X + Y)
        case OP.MUL:
            X = stackPop(VM.data)
            Y = stackPop(VM.data)
            #print("MUL")
            stackPush(VM.data, X * Y)
        case OP.PRINT:
            #print("PRINT")
            print("PVM has something to tell you - ", stackRead(VM.data))
        case OP.HALT:
            #print("HALT")
            print("Halt reached. VM finished execution")
            break
        case _:
            raise SyntaxError(f"Unknown OP {opcode}, isp - {VM.instructions.sp}")
        
#VM after processing instructions
#printVM(VM)