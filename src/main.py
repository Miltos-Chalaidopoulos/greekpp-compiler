import sys
import state
from lexer import lex,categorizelex,giveNextToken
from parser import parser
from intermediate import genquad
from assembly import FinalCode_Transformer

def run_file(filename):
    if not filename.endswith(".gr"):
        print(f"Σφάλμα: το όνομα αρχείου πρέπει να τελειώνει σε .gr, πήρα '{filename}'")
        sys.exit(1)
    result = lex(filename)
    state.lexer_List = categorizelex(result)

    parser()
    print("Η συνακτική ανάλυση ολοκληρώθηκε")
    
    print("\nΠίνακας Συμβόλων:")
    for sc in state.scopeStack:
        print(f"  Scope level {sc.nestinglevel}:")
        for e in sc.get_entities():
            print(f"    {e.name} ({e.kind}), offset={e.offset}")
    output_filename = filename[:-3] + ".int"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            for q in state.quadList:
                f.write(q.toString() + "\n")
            print(f"Τα Quads γράφτηκαν στο αρχείο '{output_filename}'")
    except IOError as e:
        print(f"Σφάλμα κατά την εγγραφή στο αρχείο '{output_filename}': {e}")
    
    transformer = FinalCode_Transformer(state.quadList, state.program_name)
    final_code_lines = transformer.transform()
    asm_filename = filename[:-3] + ".asm"
    try:
        with open(asm_filename, "w", encoding="utf-8") as f:
            for quad_lines in final_code_lines:
                for line in quad_lines:
                    f.write(line + "\n")
        print(f"Ο τελικός κώδικας γράφτηκε στο αρχείο '{asm_filename}'")
    except IOError as e:
        print(f"Σφάλμα κατά την εγγραφή στο αρχείο '{asm_filename}': {e}")
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        print("Λανθασμένη δήλωση αρχείου. Παρακαλώ γράψτε: python main.py FileName.gr")

