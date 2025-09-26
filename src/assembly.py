import sys
import state
import symboltable

def gnlvcode(v):
    entity, entityLevel = symboltable.lookupEntity(v)
    if entity is None:
        print(f"Σφάλμα: αδήλωτη μεταβλητή {v}")
        sys.exit(1)
    if entity.kind != "var":
        print(f"Σφάλμα η {v} δεν είναι μεταβλητή")
        sys.exit(1)

    d = symboltable.currentLevel() - entityLevel
    code = ["lw t0, -4(sp)"]
    for _ in range(1, d):
        code.append("lw t0, -4(t0)")
    code.append(f"addi t0, t0, -{entity.offset}")
    return code

def loadvr(v, r):
    if v.isdigit():
        return f"li $t{r}, {v}"
    
    entity, entityLevel = symboltable.lookupEntity(v)
    if entity is None:
        raise Exception(f"Loadvr:Η μεταβλητή {v} δεν βρέθηκε")
    
    current_level = symboltable.currentLevel()
    code = []
    
    if entityLevel == 0:
        code.append(f"lw $t{r}, -{entity.offset}($s0)")
    elif entityLevel == current_level and entity.kind == "var":
        code.append(f"lw $t{r}, -{entity.offset}($sp)")
    else:
        gnlv_code = gnlvcode(v)
        code.extend(gnlv_code)
        code.append(f"lw $t{r}, ($t0)")
    
    return '\n\t'.join(code)

def storevr(v, r):
    entity, entityLevel = symboltable.lookupEntity(v)
    if entity is None:
        raise Exception(f"Storevr: Η μεταβλητή {v} δεν βρέθηκε")
    current_level = symboltable.currentLevel()
    code = []
    if entityLevel == 0:
        code.append(f"sw $t{r}, -{entity.offset}($s0)")
    elif entityLevel == current_level and entity.kind == "var":
        code.append(f"sw $t{r}, -{entity.offset}($sp)")
    elif entity.parMode == 'inout' and entityLevel < current_level:
        code.append(f"lw $t0, -{entity.offset}($sp)")
        code.append(f"sw $t{r}, ($t0)")
    elif entity.parMode in ('', 'in') or entityLevel < current_level:
        gnlv_code = gnlvcode(v)
        code.extend(gnlv_code)
        code.append(f"sw $t{r}, ($t0)")
    else:
        raise Exception(f"Storevr: μη υποστηριζόμενη περίπτωση για τη μεταβλητή {v}")
    return '\n\t'.join(code)

class FinalCode_Transformer:
    def __init__(self, quad_list,main_program_name):
        self.quads = quad_list
        self.code = []
        self.all_scopes = state.allScopes
        self.main_program_name = main_program_name
        self.frame_lengths = {}
        self.current_nesting = 0
        self.current_quad = None

    def transform(self):
        for i, quad in enumerate(self.quads):
            self.current_quad = quad
            f = self.transform_quad(quad)
            self.code.append([f"# Quad {i+1}: {quad.toString()}"] + f)
        return self.code


    def transform_quad(self,quad):
        op, x, y, z = quad.op, quad.x, quad.y, quad.z
        if op == "begin_block":
            return self.handle_begin_block(x)
        elif op == "end_block":
            return self.handle_end_block(x)
        elif op == "halt":
            return self.handle_halt()
        elif quad.op in ["+","-","*","/"]:
            return self.handle_arithmetic(op, x, y, z)
        elif quad.op == ":=":
            return self.handle_assign(x,z)
        elif op in ["=", "<>", "<", ">", "<=", ">="]:
            return self.handle_conditional_jump(op, x, y, z)
        elif op == "par":
            return self.handle_par(x, y)
        elif op == "jump":
            return self.handle_jump(z)
        elif op == "inp":
            return self.handle_input(x)
        elif op == "out":
            return self.handle_output(x)
        elif op == "call":
            return self.handle_call(x)
        else :
            return ["unknown quad oparation"]
    
    def handle_arithmetic(self, op, x, y, z):
        op_map = {"+": "add", "-": "sub", "*": "mul", "/": "div"}
        return [loadvr(x, 1),loadvr(y, 2),f"{op_map[op]} $t3, $t1, $t2",storevr(z, 3)]
    
    def handle_assign(self,x,z):
        return [loadvr(x, 1),storevr(z, 1)]

    def handle_conditional_jump(self, op, x, y, z):
        cond_map = {"=": "beq", "<>": "bne", "<": "blt",">": "bgt", "<=": "ble", ">=": "bge"}
        return [loadvr(x, 1),loadvr(y, 2),f"{cond_map[op]} $t1, $t2, L{z}"]
    
    def handle_par(self, x, mode):
        code = []
        if not hasattr(self, "par_counter"):
            self.par_counter = 0
        if not hasattr(self, "next_call_scope"):
            self.next_call_scope = None

        if self.par_counter == 0:
            found_current = False
            for q in self.quads:
                if not found_current and q == self.current_quad:
                    found_current = True
                elif found_current and q.op == 'call':
                    self.next_call_scope = next(scope for scope in self.all_scopes
                                                if any(e.name == q.x and e.kind in ('func', 'proc') 
                                                       for e in scope.get_entities()))
                    frame_length = self.frame_lengths[q.x]
                    code.append(f"\taddi $fp, $sp, {frame_length}")
                    break

        temp_offset = 12 + 4 * self.par_counter
        self.par_counter += 1

        if mode == "CV" or mode == "cv":
            code.append(loadvr(x, 1))
            code.append(f"sw $t1, -{temp_offset}($fp)")

        elif mode == "ret":
            entity, _ = symboltable.lookupEntity(x)
            code.append(f"addi $t0, $sp, -{entity.offset}")
            code.append(f"sw $t0, -8($fp)")

        elif mode == "REF" or mode == "ref":
            entity, entity_level = symboltable.lookupEntity(x)
            cur_level = currentLevel()
            if entity_level == cur_level:
                code.append(f"addi $t0, $sp, -{entity.offset}")
            else:
                gnlv = gnlvcode(x)
                code.extend(gnlv)
            code.append(f"sw $t0, -{temp_offset}($fp)")

        else:
            code.append(f"Άγνωστος τύπος παραμέτρου: {mode}")
        
        return code


    def handle_begin_block(self, block_name):
        code = []
        if block_name == self.main_program_name:
            global_scope = next(scope for scope in self.all_scopes if scope.nestinglevel == 0)
            frame_length = (-4 - global_scope.offset_counter)
            self.frame_lengths[block_name] = frame_length
            self.current_nesting = 0
            code.extend([
                f"Lmain:",
                f"\taddi $sp, $sp, -{frame_length}",
                f"\tmove $s0, $sp"
            ])
        else:
            func_scope = next(scope for scope in self.all_scopes 
                            if any(e.name == block_name and e.kind in ('func', 'proc') 
                                   for e in scope.get_entities()))
            frame_length = (-4 - func_scope.offset_counter)
            self.frame_lengths[block_name] = frame_length
            self.current_nesting = func_scope.nestinglevel  
            code.extend([
                f"{block_name}:",
                f"\tsw $ra, 0($sp)",
                f"\taddi $sp, $sp, -{frame_length}",
                f"\tsw $fp, 4($sp)",
                f"\tmove $fp, $sp"
            ])
        return code

    def handle_end_block(self, block_name):
        code = []
        frame_length = self.frame_lengths.get(block_name, 0)
        code.extend([
            f"\tmove $sp, $fp",
            f"\tlw $fp, 4($sp)",
            f"\taddi $sp, $sp, {frame_length}",
            f"\tlw $ra, 0($sp)",
            f"\tjr $ra"
        ])
        return code


    def handle_halt(self):
        return ["\t\tli $v0, 10","\t\tsyscall"]

    def handle_jump(self,z):
        return ["\t\tj L_"+z]
    
    def handle_input(self, x):
        code = [f"\tli $v0, 5","\tsyscall","\tmove $t0, $v0",storevr(x, 0)]
        return code
    
    def handle_output(self, x):
        code = [f"\tli $v0, 1", loadvr(x, 0), "\tmove $a0, $t0", "\tsyscall"]
        return code
    
    def handle_call(self, func_name):
        func_scope = next(scope for scope in self.all_scopes 
                          if any(e.name == func_name and e.kind in ('func', 'proc') 
                                 for e in scope.get_entities()))
        func_nesting = func_scope.nestinglevel
        frame_length = self.frame_lengths.get(func_name, 0)

        if func_nesting == self.current_nesting:
            ret = '\t\tlw $t0,-4($sp)\n\t\tsw $t0,-4($fp)\n'
        else:
            ret = '\t\tsw $sp,-4($fp)\n'

        ret += f'\t\taddi $sp,$sp,{frame_length}\n\t\tjal {func_name}\n\t\taddi $sp,$sp,{-frame_length}'
        return [ret]