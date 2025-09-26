import state
from lexer import giveNextToken, Token
import symboltable
from intermediate import genquad, nextquad, newtmp, makelist, merge, backpatch, emptylist
from assembly import storevr, loadvr

token = None

def parser():
    global token
    token = giveNextToken()
    program()

def program():
    global token, program_name
    if token.word == "πρόγραμμα":
        token = giveNextToken()
        if token.type == "definition":
            state.program_name = token.word
            token = giveNextToken()
            programblock(state.program_name)
        else:
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: το πρόγραμμα πρέπει να έχει έγκυρο όνομα, πήρα {token.word}")
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: το πρόγραμμα πρέπει να ξεκινάει με 'πρόγραμμα'")

def programblock(prname):
    global token
    declarations()
    subprograms()
    if token.word == "αρχή_προγράμματος":
        genquad("begin_block", prname, "_", "_")
        token = giveNextToken()
        sequence()
        if token.word != "τέλος_προγράμματος":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'τέλος_προγράμματος', πήρα {token.word}")
        else:
            genquad("halt", "_", "_", "_")
            genquad("end_block", prname, "_", "_")
            token = giveNextToken()
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'αρχή_προγράμματος', πήρα {token.word}")

def declarations():
    global token
    while token.word == "δήλωση":
        token = giveNextToken()
        varlist()

def varlist():
    global token
    if token.type != "definition":
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται μεταβλητή, πήρα {token.word}")
    while True:
        varname = token.word
        ent = symboltable.Entity(varname, 'var', 0, parMode="")
        state.currentScope.add_entity(ent)
        state.variables.append(varname)
        token = giveNextToken()
        if token.word != ",":
            break
        token = giveNextToken()

def subprograms():
    global token
    while token.word in {"συνάρτηση", "διαδικασία"}:
        if token.word == "συνάρτηση":
            func()
        elif token.word == "διαδικασία":
            proc()

def func():
    global token, funcList , currentScope
    token = giveNextToken()
    if token.type == "definition":
        fname = token.word
        ent = symboltable.Entity(fname, 'func', 0, parMode="")
        state.scopeStack[0].add_entity(ent)
        state.funcList.append(fname)
        newScope = symboltable.Scope(state.currentScope.nestinglevel + 1)
        state.scopeStack.append(newScope)
        state.currentScope = newScope
        token = giveNextToken() 
        if token.word == "(":
            token = giveNextToken()  
            formalparlist()
            if token.word == ")":
                token = giveNextToken()
                funcblock(fname)
                state.scopeStack.pop()
                state.currentScope = state.scopeStack[-1]
            else:
                raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: περίμενα ')' αλλά πήρα {token.word}")
        else:
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: μετά το όνομα συνάρτησης αναμένεται '('")
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: μετά τη λέξη 'συνάρτηση' αναμένεται όνομα, πήρα {token.word}")

def proc():
    global token, funcList , currentScope
    token = giveNextToken()
    if token.type == "definition":
        pname = token.word
        ent = symboltable.Entity(pname, 'proc', 0,parMode="")
        state.scopeStack[0].add_entity(ent)
        state.funcList.append(pname)
        newScope = symboltable.Scope(state.currentScope.nestinglevel + 1)
        state.scopeStack.append(newScope)
        state.currentScope = newScope
        token = giveNextToken()  
        if token.word == "(":
            token = giveNextToken()  
            formalparlist()
            if token.word == ")":
                token = giveNextToken()  
                procblock(pname)
                state.scopeStack.pop()
                state.currentScope = state.scopeStack[-1]
            else:
                raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: περίμενα ')' αλλά πήρα {token.word}")
        else:
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: μετά το όνομα διαδικασίας αναμένεται '('")
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: μετά τη λέξη 'διαδικασία' αναμένεται όνομα, πήρα {token.word}")

def formalparlist():
    global token
    if token.type == "definition":
        varlist()

def funcblock(name):
    global token
    if token.word == "διαπροσωπεία":
        genquad("begin_block", name, "_", "_")
        token = giveNextToken()
        funcinput()
        funcoutput()
        if token.word == "δήλωση":
            declarations()
            token = giveNextToken()
        if token.word == "αρχή_συνάρτησης":
            token = giveNextToken()
            sequence()
            if token.word != "τέλος_συνάρτησης":
                raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'τέλος_συνάρτησης', πήρα {token.word}")
            else:
                genquad("end_block", name, "_", "_")
                token = giveNextToken()
        else:
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'αρχή_συνάρτησης', πήρα {token.word}")
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'διαπροσωπεία', πήρα {token.word}")

def procblock(name):
    global token
    if token.word == "διαπροσωπεία":
        genquad("begin_block", name, "_", "_")
        token = giveNextToken()
        funcinput()
        funcoutput()
        if token.word == "δήλωση":
            declarations()
            token = giveNextToken()
        if token.word == "αρχή_διαδικασίας":
            token = giveNextToken()
            sequence()
            if token.word != "τέλος_διαδικασίας":
                raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'τέλος_διαδικασίας', πήρα {token.word}")
            else:
                genquad("end_block", name, "_", "_")
                token = giveNextToken()
        else:
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'αρχή_διαδικασίας', πήρα {token.word}")
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'διαπροσωπεία', πήρα {token.word}")

def funcinput():
    global token
    if token.word == "είσοδος":
        token = giveNextToken()
        varlist()

def funcoutput():
    global token
    if token.word == "έξοδος":
        token = giveNextToken()
        varlist()

def sequence():
    global token
    if token.word in {"τέλος_προγράμματος", "εάν_τέλος", "τέλος_συνάρτησης", "τέλος_διαδικασίας"}:
        return
    statement()
    while token.word == ";":
        token = giveNextToken()
        if token.word in {"τέλος_προγράμματος", "εάν_τέλος", "τέλος_συνάρτησης", "τέλος_διαδικασίας"}:
            break
        statement()

def statement():
    global token
    if token.type == "definition":
        assignment_stat(token.word)
    elif token.word == "εάν":
        if_stat()
    elif token.word == "όσο":
        while_stat()
    elif token.word == "επανάλαβε":
        do_stat()
    elif token.word == "για":
        for_stat()
    elif token.word == "διάβασε":
        input_stat()
    elif token.word == "γράψε":
        print_stat()
    elif token.word == "εκτέλεσε":
        call_stat()
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: λανθασμένη δήλωση statement, πήρα {token.word}")

def assignment_stat(variable_name):
    global token
    token = giveNextToken()
    if token.word == ":=":
        token = giveNextToken()
        exp = expression()
        genquad(":=", exp, "_", variable_name)
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: ίσως χρειάζεται ':='")

def input_stat():
    global token
    token = giveNextToken()
    if token.type != "definition":
        raise SyntaxError(
            f"Σφάλμα στη γραμμή {token.lineNum}: "
            f"μετά τη λέξη 'διάβασε' αναμένεται όνομα μεταβλητής, πήρα {token.word}"
        )
    token = giveNextToken()


def if_stat():
    global token
    token = giveNextToken()
    t_list, f_list = condition()

    if token.word != "τότε":
        raise SyntaxError(
            f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'τότε', πήρα {token.word}"
        )
    token = giveNextToken()
    backpatch(t_list, nextquad())
    sequence()

    if_list = makelist(nextquad())
    genquad("jump", "_", "_", "_")

    backpatch(f_list, nextquad())

    if token.word == "αλλιώς":
        backpatch(t_list, nextquad())
        elsepart()
        if token.word != "εάν_τέλος":
            raise SyntaxError(
                f"Σφάλμα στη γραμμή {token.lineNum}: "
                f"αναμένεται 'εάν_τέλος' μετά το else, πήρα {token.word}"
            )
        token = giveNextToken()
    elif token.word == "εάν_τέλος":
        token = giveNextToken()
    else:
        raise SyntaxError(
            f"Σφάλμα στη γραμμή {token.lineNum}: "
            f"αναμένεται 'αλλιώς' ή 'εάν_τέλος', πήρα {token.word}"
        )

    backpatch(if_list, nextquad())

def elsepart():
    global token
    token = giveNextToken()
    sequence()

def while_stat():
    global token
    start = nextquad()
    token = giveNextToken()
    t_list, f_list = condition()
    if token.word != "επανάλαβε":
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'επανάλαβε', πήρα {token.word}")
    else:
        backpatch(t_list,nextquad())
    token = giveNextToken()
    sequence()
    genquad("jump", "_", "_", str(start))
    backpatch(f_list, nextquad())
    if token.word != "όσο_τέλος":
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'όσο_τέλος', πήρα {token.word}")
    token = giveNextToken()

def do_stat():
    global token
    token = giveNextToken()
    sequence()
    if token.word != "μέχρι":
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'μέχρι', πήρα {token.word}")
    token = giveNextToken()
    t_list, f_list = condition()
    backpatch(t_list, nextquad())
    backpatch(f_list, nextquad())


def for_stat():
    global token
    token = giveNextToken()
    if token.type == "definition":
        loop_var = token.word
        token = giveNextToken()
        if token.word != ":=":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται ':=', πήρα {token.word}")
        token = giveNextToken()
        lower = expression()
        genquad(":=", lower, "_", loop_var)
        counter_tmp = newtmp()
        genquad(":=", "0", "_", counter_tmp)
        
        if token.word != "έως":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'έως', πήρα {token.word}")
        token = giveNextToken()
        upper = expression()

        if token.word != "με_βήμα":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'με_βήμα', πήρα {token.word}")
        token = giveNextToken()
        step_val = expression()
        loop_entry = nextquad()
        tmp_sum = newtmp()
        genquad("+", loop_var, step_val, tmp_sum)
        pos = nextquad()
        genquad(">", "0", counter_tmp, str(pos))
        genquad("jump", "_", "_", "_")
        genquad(":=", tmp_sum, "_", loop_var)
        cond_quad = nextquad()
        genquad("<=", loop_var, upper, str(cond_quad + 2))
        exit_jump = genquad("jump", "_", "_", "_")
        if token.word != "επανάλαβε":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'επανάλαβε', πήρα {token.word}")
        token = giveNextToken()
        sequence()
        genquad(":=", "1", "_", counter_tmp)
        genquad("jump", "_", "_", str(loop_entry))
        exit_label = nextquad()
        backpatch([exit_jump], exit_label)
        if token.word != "για_τέλος":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'για_τέλος', πήρα {token.word}")
        token = giveNextToken()
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται όνομα μεταβλητής μετά το 'για', πήρα {token.word}")

def step():
    global token
    if token.word == "με_βήμα":
        token = giveNextToken()
        return expression()
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται 'με_βήμα', πήρα {token.word}")

def print_stat():
    global token
    token = giveNextToken()
    exp = expression()
    genquad("out",exp, "_","_")

def input_stat():
    global token
    token = giveNextToken()
    if token.type != "definition":
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: μετά τη λέξη 'διάβασε' αναμένεται όνομα μεταβλητής, πήρα {token.word}")
    genquad("inp",token.word,"_","_",)
    token = giveNextToken()

def call_stat():
    global token
    token = giveNextToken()
    if token.type != "definition":
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: μετά τη λέξη 'εκτέλεσε' αναμένεται όνομα συνάρτησης, πήρα {token.word}")
    call_name = token.word
    token = giveNextToken()
    params = []
    if token.word == "(":
        params = actualpars()
    for param in params:
        genquad("par", param[0], param[1].lower(), "_")
    ret_temp = newtmp()
    genquad("call", call_name, "_", "_")
    return ret_temp

def idtail():
    global token
    if token.word == "(":
        a = actualpars()
        return (True, a)
    else:
        return (False, None)

def actualpars():
    global token
    if token.word == "(":
        token = giveNextToken()
        a = []
        if token.word != ")":
            a = actualparlist()
        if token.word != ")":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: περίμενα ')' αλλά πήρα {token.word}")
        token = giveNextToken()
        return a
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: περίμενα '('")

def actualparlist():
    global token
    parlist = []
    par = actualparitem()
    parlist.append(par)
    while token.word == ",":
        token = giveNextToken()
        par = actualparitem()
        parlist.append(par)
    return parlist

def actualparitem():
    global token
    if token.word == "%":
        token = giveNextToken()
        if token.type != "definition":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: απαιτείται όνομα μεταβλητής μετά το '%'")
        name = token.word
        token = giveNextToken()
        ent = symboltable.Entity(name=name, kind="var", offset=0, parMode="inout")
        state.currentScope.add_entity(ent)
        return (name, "REF")
    else:
        result = expression()
        ent = symboltable.Entity(name=result, kind="var", offset=0, parMode="in")
        state.currentScope.add_entity(ent)
        return (result, "CV")

def condition():
    global token
    T_1, F_1 = boolterm()
    B_true = T_1
    B_false = F_1
    while token.word == "ή":
        backpatch(B_false,nextquad())
        token = giveNextToken()
        T_2, F_2 = boolterm()
        B_true = merge(B_true,T_2)
        B_false = F_2
    return B_true, B_false

def boolterm():
    global token
    T_1, F_1 = boolfactor()
    B_true = T_1
    B_false = F_1
    while token.word == "και":
        backpatch(B_true,nextquad())
        token = giveNextToken() 
        T_2, F_2 = boolfactor()
        B_false = merge(B_false,F_2)
        B_true = T_2
    return B_true, B_false

def boolfactor():
    global token
    if token.word == "όχι":
        token = giveNextToken()
        if token.word == "[":
            token = giveNextToken()
            t_list, f_list = condition()
            if token.word != "]":
                raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται ']' αλλά πήρα {token.word}")
            token = giveNextToken()
            return f_list, t_list
        else:
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται '[' μετά το 'όχι'")
    elif token.word == "[":
        token = giveNextToken()
        t_list, f_list = condition()
        if token.word != "]":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται ']' αλλά πήρα {token.word}")
        token = giveNextToken()
        return t_list, f_list
    else:
        result = expression()
        if token.type == "relational oparation":
            op = token.word
            token = giveNextToken()
            right = expression()
            tmp = newtmp()
            genquad(op, result, right, tmp)
            return makelist(nextquad()-1), makelist(nextquad())
        else:
            return emptylist(), []

def expression():
    global token
    sign = ""
    if token.word in {"+", "-"}:
        sign = token.word
        token = giveNextToken()
    val = term()
    while token.word in {"+", "-"}:
        op = token.word
        token = giveNextToken()
        right = term()
        tmp = newtmp()
        genquad(op, val, right, tmp)
        val = tmp
    return sign + val

def term():
    global token
    val = factor()
    while token.word in {"*", "/"}:
        op = token.word
        token = giveNextToken()
        right = factor()
        tmp = newtmp()
        genquad(op, val, right, tmp)
        val = tmp
    return val

def factor():
    global token
    if token.word == "(":
        token = giveNextToken()
        val = expression()
        if token.word != ")":
            raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται ')' αλλά πήρα {token.word}")
        token = giveNextToken()
        return val
    elif token.type == "definition":
        name = token.word
        token = giveNextToken()
        isCall, paramList = idtail()
        if isCall:
            for param in paramList:
                genquad("par", param[0], param[1].lower(), "_")
            ret_temp = newtmp()
            genquad("par", ret_temp, "ret", "_")
            genquad("call", name, "_", "_")
            return ret_temp
        else:
            return name
    elif token.type == "number":
        val = token.word
        token = giveNextToken()
        return val
    else:
        raise SyntaxError(f"Σφάλμα στη γραμμή {token.lineNum}: αναμένεται αριθμός ή παράμετρος αλλά πήρα {token.word}")


def optional_sign():
    global token
    if token.type == "add operation":
        token = giveNextToken()