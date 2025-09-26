import state

class Token:
    def __init__(self, word, type, lineNum):
        self.word = word
        self.type = type
        self.lineNum = lineNum

def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Το αρχείο '{filename}' δεν βρέθηκε.")

def tokenize(text):
    words_with_lines = []
    line_num = 1
    word = ""
    for char in text:
        if char == "\n":
            if word:
                words_with_lines.append((word, line_num))
                word = ""
            line_num += 1
            continue
        if char.isalnum() or char == "_":
            word += char
        else:
            if word:
                words_with_lines.append((word, line_num))
                word = ""
            if not char.isspace():
                words_with_lines.append((char, line_num))
    if word:
        words_with_lines.append((word, line_num))
    return words_with_lines

def merge_symbols(words_with_lines):
    merged_list = []
    i = 0
    while i < len(words_with_lines):
        current = words_with_lines[i]
        if i < len(words_with_lines) - 1:
            nxt = words_with_lines[i+1]
            if current[0] == ":" and nxt[0] == "=":
                merged_list.append((current[0]+nxt[0], current[1]))
                i += 2
                continue
            if current[0] == ">" and nxt[0] == "=":
                merged_list.append((current[0]+nxt[0], current[1]))
                i += 2
                continue
            if current[0] == "<" and nxt[0] == "=":
                merged_list.append((current[0]+nxt[0], current[1]))
                i += 2
                continue
            if current[0] == "<" and nxt[0] == ">":
                merged_list.append((current[0]+nxt[0], current[1]))
                i += 2
                continue
        merged_list.append(current)
        i += 1
    return merged_list

def remove_comments(words_with_lines):
    filtered_list = []
    writing_comments = False
    for word, line_num in words_with_lines:
        if word == "{":
            writing_comments = True
            continue
        elif word == "}":
            if not writing_comments:
                raise ValueError(f"Σφάλμα στη γραμμή {line_num}: κλείσιμο σχολίου χωρίς άνοιγμα")
            writing_comments = False
            continue
        if not writing_comments:
            filtered_list.append((word, line_num))
    if writing_comments:
         raise ValueError("Σφάλμα: έχουν ανοίξει σχόλια χωρίς να έχουν κλείσει")
    return filtered_list

def check_illegal_chars(words_with_lines):
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωςάέήίόύώΆΈΉΊΌΎΏΑϊΪΫϋ0123456789_+-*/=<>;:,[]{}()\"%"
    for word, line_num in words_with_lines:
        for char in word:
            if char not in valid_chars:
                raise ValueError(f"Παράνομος χαρακτήρας '{char}' στη γραμμή {line_num}")

def lex(filename):
    text = read_file(filename)
    tokens = tokenize(text)
    merged_tokens = merge_symbols(tokens)
    filtered_tokens = remove_comments(merged_tokens)
    check_illegal_chars(filtered_tokens)
    return filtered_tokens

def categorizelex(input_tokens):
    keywords = {"πρόγραμμα", "δήλωση", "εάν", "τότε", "αλλιώς", "εάν_τέλος",
                "επανάλαβε", "μέχρι", "όσο", "όσο_τέλος", "για", "έως", "με_βήμα", "για_τέλος",
                "διάβασε", "γράψε", "συνάρτηση", "διαδικασία", "διαπροσωπεία", "είσοδος", "έξοδος",
                "αρχή_συνάρτησης", "τέλος_συνάρτησης", "αρχή_διαδικασίας", "τέλος_διαδικασίαs",
                "αρχή_προγράμματος", "τέλος_προγράμματος", "ή", "και", "εκτέλεσε"}
    realational_oper = {"=", "<", ">", "<=", ">=", "<>"}
    add_oper = {"+", "-"}
    mul_oper = {"*", "/"}
    delimiter = {",", ";"}
    grouping_symbols = {"{", "}", "[", "]", "(", ")", "\""}
    categorized = []
    for word, line_num in input_tokens:
        if word.isdigit():
            category = "number"
        elif word in add_oper:
            category = "add operation"
        elif word in mul_oper:
            category = "multyply operation"
        elif word in grouping_symbols:
            category = "grouping sumbols"
        elif word in realational_oper:
            category = "relational oparation"
        elif word in delimiter:
            category = "delimiter"
        elif word == ":=":
            category = "assignment"
        elif word == "%":
            category = "variable by reference"
        elif word in keywords:
            category = "keyword"
        elif word.isalpha() or word.isdigit() or "_" in word:
            category = "definition"
        else:
            category = "other"
        if len(word) > 30:
            raise ValueError(f"Σφάλμα στη γραμμή {line_num}: η λέξη {word} είναι μεγαλύτερη των 30 επιτρεπόμενων χαρακτήρων")
        categorized.append((word, line_num, category))
    return categorized

def giveNextToken():
    if state.tokenToGive < len(state.lexer_List):
        entry = state.lexer_List[state.tokenToGive]
        tok = Token(entry[0], entry[2], entry[1])
        state.tokenToGive += 1
        return tok