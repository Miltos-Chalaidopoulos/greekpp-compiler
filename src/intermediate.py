import state
import symboltable

class Quad:
    def __init__(self, ID, op, x, y, z):
        self.ID = int(ID)
        self.op = str(op)
        self.x = str(x)
        self.y = str(y)
        self.z = str(z)
    def toString(self):
        return f"{self.ID}: {self.op} , {self.x} , {self.y} , {self.z}"

def emptylist():
    return []

def makelist(x):
    return [x]

def merge(list1, list2):
    return list1 + list2

def backpatch(lst, z):
    for quad in state.quadList:
        if quad.ID in lst:
            quad.z = str(z)

def nextquad():
    return state.quadPos

def genquad(op, x, y, z):
    state.quadPos = nextquad()
    state.quadPos += 1
    quad = Quad(state.quadPos, op, x, y, z)
    state.quadList.append(quad)
    return quad

def newtmp():
    state.T_i += 1
    tmp = f"T_{state.T_i}"
    tmp_entity = symboltable.Entity(name=tmp, kind="var", offset=0,parMode="")
    state.currentScope.add_entity(tmp_entity)
    return tmp
