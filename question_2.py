import os


# *****TOKENIZER*****
def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            num = ch
            i += 1
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                num += expr[i]
                i += 1
            tokens.append(("NUM", float(num)))
            continue

        if ch in "+-*/":
            tokens.append(("OP", ch))
            i += 1
            continue

        if ch == "(":
            tokens.append(("LPAREN", ch))
            i += 1
            continue

        if ch == ")":
            tokens.append(("RPAREN", ch))
            i += 1
            continue

        return "ERROR"

    tokens.append(("END", None))
    return tokens


# *****PARSER (Recursive Descent)*****
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok
    
    def parse_expression(self): # expression -> term ((+|-) term)*
        node = self.parse_term()

        while self.peek()[0] == "OP" and self.peek()[1] in "+-":
            op = self.consume()[1]

            if self.peek()[0] == "OP": # ERROR if two operators in a row
                return "ERROR"
            right = self.parse_term()
            node = (op, node, right)

        return node

    def parse_term(self): # term -> factor ((*|/) factor)*
        node = self.parse_factor()

        while self.peek()[0] == "OP" and self.peek()[1] in "*/":
            op = self.consume()[1]
            right = self.parse_factor()
            node = (op, node, right)

        return node

    def parse_factor(self): # factor -> -factor | number | (expression)
        tok = self.peek()

        if tok[0] == "OP" and tok[1] == "+": # UNARY PLUS (NOT ALLOWED)
            return "ERROR"
    
        if tok[0] == "OP" and tok[1] == "-": # UNARY MINUS
            self.consume()
            return ("neg", self.parse_factor())

        if tok[0] == "NUM": # NUMBER
            value = tok[1]
            self.consume()

        
            if self.peek()[0] == "LPAREN": # check implicit multiplication like 2(3+4)
                right = self.parse_factor()
                return ("*", value, right)

            return value

        if tok[0] == "LPAREN": # PARENTHESES
            self.consume()
            node = self.parse_expression()
            if self.peek()[0] == "RPAREN":
                self.consume()
                return node
            return "ERROR"

        return "ERROR"
    

# *****TREE FORMAT*****
def tree_to_str(node):
    if node == "ERROR":
        return "ERROR"

    if isinstance(node, float):
        if node.is_integer():
            return str(int(node))
        return str(node)

    if isinstance(node, tuple):
        if node[0] == "neg":
            return f"(neg {tree_to_str(node[1])})"

        op, left, right = node
        return f"({op} {tree_to_str(left)} {tree_to_str(right)})"

    return "ERROR"


# *****EVALUATION*****
def evaluate_node(node):
    if node == "ERROR":
        return "ERROR"

    if isinstance(node, float):
        return node

    if isinstance(node, tuple):
        if node[0] == "neg":
            val = evaluate_node(node[1])
            if val == "ERROR":
                return "ERROR"
            return -val

        op, left, right = node
        l = evaluate_node(left)
        r = evaluate_node(right)

        if l == "ERROR" or r == "ERROR":
            return "ERROR"

        if op == "+":
            return l + r
        if op == "-":
            return l - r
        if op == "*":
            return l * r
        if op == "/":
            if r == 0:
                return "ERROR"
            return l / r

    return "ERROR"



# *****MAIN FUNCTION*****
def evaluate_file(input_path: str) -> list[dict]:
    results = []

    with open(input_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        expr = line.strip()

        tokens = tokenize(expr)

        if tokens == "ERROR":
            results.append({
                "input": expr,
                "tree": "ERROR",
                "tokens": "ERROR",
                "result": "ERROR"
            })
            continue

        parser = Parser(tokens)
        tree = parser.parse_expression()

        tree_str = tree_to_str(tree)
        result = evaluate_node(tree)

        if result == "ERROR": # format result
            final_result = "ERROR"
        else:
            if isinstance(result, float) and result.is_integer():
                final_result = int(result)
            else:
                final_result = round(result, 4)

    
        token_str = " ".join( # tokens format
            f"[{t[0]}:{int(t[1]) if isinstance(t[1], float) and t[1].is_integer() else t[1]}]"
            if t[1] is not None else f"[{t[0]}]"
            for t in tokens
        )

        results.append({
            "input": expr,
            "tree": tree_str,
            "tokens": token_str,
            "result": final_result
        })

    output_path = os.path.join(os.path.dirname(input_path), "output.txt") # For output.txt

    with open(output_path, "w") as out:
        for res in results:
            out.write(f"Input: {res['input']}\n")
            out.write(f"Tree: {res['tree']}\n")
            out.write(f"Tokens: {res['tokens']}\n")
            out.write(f"Result: {res['result']}\n\n")

    return results


# *****RUN*****
if __name__ == "__main__":
    evaluate_file("input.txt")