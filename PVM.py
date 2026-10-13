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
class PVM:
    data: stack
    instructions: stack

@dataclass
class stack:
    head: int
    capacity: int
    items: array.array = field(default_factory=lambda: array.array('d'))

def stackPush(s, v):
    if(s.head == s.capacity):
        raise MemoryError("Stack overflow")
    s.items[s.head] = v
    s.head = s.head + 1

def stackPop(s):
    if(s.head == 0):
        raise MemoryError("Stack underflow")
    v = stackRead(s)
    s.head = s.head - 1
    return v

def stackRead(s):
    if(s.head == 0 | s.head == s.capacity):
        raise IndexError(f"Trying to read a value outside of stack")
    return s.items[s.head - 1]

def readNextInstruction(s):
    OP = s.items[s.head]
    s.head = s.head + 1
    return OP

def printVM(vm):
    print("Stack:")
    for i in range(0, vm.data.capacity):
        if(i == vm.data.head):
            print("  ->", vm.data.items[i])
        else:    
            print("    ", vm.data.items[i])

    print("Instructions:")
    for i in range(0, vm.instructions.capacity):
        if(i == vm.instructions.head):
            print("  ->", vm.instructions.items[i])
        else:    
            print("    ", vm.instructions.items[i])

data = stack(head = 0, capacity = 16, items = [0] * 16)
instructions = stack(head = 0, capacity = 16, items = [0] * 16)
VM = PVM(data = data, instructions = instructions)

#Loading instructions in memory
stackPush(VM.instructions, OP.PUSH)
stackPush(VM.instructions, 6)
stackPush(VM.instructions, OP.PUSH)
stackPush(VM.instructions, 7)
stackPush(VM.instructions, OP.MUL)
stackPush(VM.instructions, OP.PUSH)
stackPush(VM.instructions, 2)
stackPush(VM.instructions, OP.ADD)
stackPush(VM.instructions, OP.PRINT)
stackPush(VM.instructions, OP.HALT)
VM.instructions.head = 0

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
            break
        case OP.HALT:
            #print("HALT")
            break
        case _:
            raise SyntaxError(f"Unknown OP {opcode}")
        
#VM after processing instructions
#printVM(VM)