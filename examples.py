#if example
loadInstruction(VM.instructions, OP.PUSH.value, [12], S32BI) #0  01234
loadInstruction(VM.instructions, OP.PUSH.value, [10], S32BI) #5  56789
loadInstruction(VM.instructions, OP.GT.value, [], VOID)      #10 10
loadInstruction(VM.instructions, OP.JZ.value, [21], U8BI)    #11 11-12 

loadInstruction(VM.instructions, OP.PUSH.value, [1], S32BI)  #13 13-15-16-17-18
loadInstruction(VM.instructions, OP.PRINT.value, [], VOID)   #18 18
loadInstruction(VM.instructions, OP.JMP.value, [27], U8BI)   #19 19-20

loadInstruction(VM.instructions, OP.PUSH.value, [0], S32BI)  #21 21-22-23-24-25
loadInstruction(VM.instructions, OP.PRINT.value, [], VOID)   #26 26

loadInstruction(VM.instructions, OP.HALT.value, [], VOID)    #27 27
#=============
#while example
loadInstruction(VM.instructions, OP.PUSH.value,  [0], S32BI) 
loadInstruction(VM.instructions, OP.STORE.value, [0], U8BI)  
loadInstruction(VM.instructions, OP.PUSH.value,  [1], S32BI) 
loadInstruction(VM.instructions, OP.STORE.value, [4], U8BI) 

VM.labels.append(VM.instructions.na) #While condition label-0
loadInstruction(VM.instructions, OP.LOAD.value,  [4], U8BI) 
loadInstruction(VM.instructions, OP.PUSH.value,  [5], S32BI)
loadInstruction(VM.instructions, OP.GT.value,    [], VOID)  
loadInstruction(VM.instructions, OP.JZ.value,    [LABEL, 1], U8BI)
loadInstruction(VM.instructions, OP.JMP.value,   [LABEL, 2], U8BI)

VM.labels.append(VM.instructions.na) #While body label-1
loadInstruction(VM.instructions, OP.LOAD.value,  [0], U8BI) 
loadInstruction(VM.instructions, OP.LOAD.value,  [4], U8BI) 
loadInstruction(VM.instructions, OP.ADD.value,   [], VOID)  
loadInstruction(VM.instructions, OP.STORE.value, [0], U8BI) 

loadInstruction(VM.instructions, OP.LOAD.value,  [4], U8BI) 
loadInstruction(VM.instructions, OP.PUSH.value,  [1], S32BI)
loadInstruction(VM.instructions, OP.ADD.value,   [], VOID)
loadInstruction(VM.instructions, OP.STORE.value, [4], U8BI)

loadInstruction(VM.instructions, OP.JMP.value,   [LABEL, 0], U8BI)

VM.labels.append(VM.instructions.na) #End label-2
loadInstruction(VM.instructions, OP.LOAD.value,  [0], U8BI) 
loadInstruction(VM.instructions, OP.PRINT.value, [], VOID)  
loadInstruction(VM.instructions, OP.HALT.value,  [], VOID)   
#=============
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