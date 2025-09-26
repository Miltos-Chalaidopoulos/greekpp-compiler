import state

class Scope:
    def __init__(self, level):
        self.nestinglevel = level
        self.entities = []
        self.offset_counter = -4
        state.allScopes.append(self)
    def add_entity(self, entity):
        if entity.kind == "var":
            entity.offset = self.offset_counter
            self.offset_counter -= 4
        self.entities.append(entity)
    def get_entities(self):
        return self.entities
    def get_next_offset(self):
        return self.offset_counter - 4

class Entity:
    def __init__(self, name, kind, offset,parMode=""):
        self.name = name
        self.kind = kind
        self.offset = offset
        self.parMode = parMode

def lookupEntity(name):
    sorted_scopes = sorted(state.allScopes, key=lambda s: -s.nestinglevel)
    for scope in sorted_scopes:
        for entity in scope.get_entities():
            if entity.name == name:
                return entity, scope.nestinglevel
    return None, None

def currentLevel():
    if state.scopeStack:
        return state.scopeStack[-1].nestinglevel
    else:
        return 0

def find_entity_and_scope(x, scopes):
    for scope in scopes:
        for ent in scope.get_entities():
            if ent.name == x:
                return ent, scope
    return None, None

class Argument :
    def __init__(self,parMode,type):
        self.parMode = parMode
        self.type = type
        self.numofArgs = numofArgs
        self.nextArg = 0


#currentScope = Scope(0)
#scopeStack.append(currentScope)
root_scope = Scope(0)
state.currentScope = root_scope
state.scopeStack.append(root_scope)
