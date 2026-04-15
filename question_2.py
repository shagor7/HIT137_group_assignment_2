# (PASTE START)

import os
from typing import Optional, Union, TypeAlias

TokenValue: TypeAlias = Optional[Union[float, str]]
Token: TypeAlias = tuple[str, TokenValue]
Node: TypeAlias = Union[float, tuple, str]

# TOKENIZER
def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit() or ch == ".":
            start = i
            dot_count = 0

            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    dot_count += 1
                i += 1

            text = expr[start:i]

            if text == "." or dot_count > 1:
                return "ERROR"

            try:
                value = float(text)
            except ValueError:
                return "ERROR"

            tokens.append(("NUM", value))
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


# PARSER
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ("END", None)

    def consume(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        node = self.parse_expression()
        if node == "ERROR":
            return "ERROR"
        if self.peek()[0] != "END":
            return "ERROR"
        return node

    def parse_expression(self):
        node = self.parse_term()
        if node == "ERROR":
            return "ERROR"

        tok_type, tok_value = self.peek()
        while tok_type == "OP" and isinstance(tok_value, str) and tok_value in "+-":
            op = self.consume()[1]
            right = self.parse_term()
            if right == "ERROR":
                return "ERROR"
            node = (op, node, right)
            tok_type, tok_value = self.peek()

        return node

    def parse_term(self):
        node = self.parse_implicit()
        if node == "ERROR":
            return "ERROR"

        tok_type, tok_value = self.peek()
        while tok_type == "OP" and isinstance(tok_value, str) and tok_value in "*/":
            op = self.consume()[1]
            right = self.parse_implicit()
            if right == "ERROR":
                return "ERROR"
            node = (op, node, right)
            tok_type, tok_value = self.peek()

        return node

    def parse_implicit(self):
        node = self.parse_unary()
        if node == "ERROR":
            return "ERROR"

        while self._starts_implicit_factor(self.peek()):
            right = self.parse_unary()
            if right == "ERROR":
                return "ERROR"
            node = ("*", node, right)

        return node

    def parse_unary(self):
        tok_type, tok_value = self.peek()

        if tok_type == "OP" and tok_value == "+":
            return "ERROR"

        if tok_type == "OP" and tok_value == "-":
            self.consume()
            child = self.parse_unary()
            if child == "ERROR":
                return "ERROR"
            return ("neg", child)

        return self.parse_primary()

    def parse_primary(self):
        tok_type, tok_value = self.peek()

        if tok_type == "NUM":
            if not isinstance(tok_value, float):
                return "ERROR"
            self.consume()
            return tok_value

        if tok_type == "LPAREN":
            self.consume()
            node = self.parse_expression()
            if node == "ERROR":
                return "ERROR"
            if self.peek()[0] != "RPAREN":
                return "ERROR"
            self.consume()
            return node

        return "ERROR"

    @staticmethod
    def _starts_implicit_factor(tok):
        tok_type, _ = tok
        return tok_type == "NUM" or tok_type == "LPAREN"


# FORMAT
def format_number(v):
    return str(int(v)) if v.is_integer() else str(v)


def tree_to_str(node):
    if node == "ERROR":
        return "ERROR"
    if isinstance(node, float):
        return format_number(node)
    if isinstance(node, tuple):
        if node[0] == "neg":
            return f"(neg {tree_to_str(node[1])})"
        return f"({node[0]} {tree_to_str(node[1])} {tree_to_str(node[2])})"
    return "ERROR"


def tokens_to_str(tokens):
    if tokens == "ERROR":
        return "ERROR"

    out = []
    for t, v in tokens:
        if t == "END":
            out.append("[END]")
        elif t == "NUM":
            out.append(f"[NUM:{format_number(v)}]")
        elif t == "OP":
            out.append(f"[OP:{v}]")
        elif t == "LPAREN":
            out.append("[LPAREN:(]")
        elif t == "RPAREN":
            out.append("[RPAREN:)]")
    return " ".join(out)


# EVAL
def evaluate_node(node):
    if node == "ERROR":
        return "ERROR"

    if isinstance(node, float):
        return node

    if isinstance(node, tuple):
        if node[0] == "neg":
            val = evaluate_node(node[1])
            if not isinstance(val, float):
                return "ERROR"
            return -val

        op, l, r = node
        lv = evaluate_node(l)
        rv = evaluate_node(r)

        if not isinstance(lv, float) or not isinstance(rv, float):
            return "ERROR"

        if op == "+": return lv + rv
        if op == "-": return lv - rv
        if op == "*": return lv * rv
        if op == "/":
            if rv == 0: return "ERROR"
            return lv / rv

    return "ERROR"


def format_result(r):
    if r == "ERROR":
        return "ERROR"
    return int(r) if isinstance(r, float) and r.is_integer() else round(r, 4)


# MAIN FILE PROCESS
def evaluate_file(path):
    results = []

    # ✅ Check if file exists FIRST
    if not os.path.exists(path):
        print(f"❌ Error: File '{path}' not found.")
        return []

    # ✅ Safe file opening
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"❌ Error reading file: {e}")
        return []

    for line in lines:
        expr = line.strip()
        if expr == "":
            results.append({
                "input": expr,
                "tree": "ERROR",
                "tokens": "ERROR",
                "result": "ERROR"
            })
            continue

        tokens = tokenize(expr)

        if tokens == "ERROR":
            results.append({"input": expr, "tree": "ERROR", "tokens": "ERROR", "result": "ERROR"})
            continue

        tree = Parser(tokens).parse()

        if tree == "ERROR":
            results.append({
                "input": expr,
                "tree": "ERROR",
                "tokens": tokens_to_str(tokens),
                "result": "ERROR"
            })
            continue

        value = evaluate_node(tree)
        final = format_result(value)

        results.append({
            "input": expr,
            "tree": tree_to_str(tree),
            "tokens": tokens_to_str(tokens),
            "result": final
        })

    # ✅ Safe output writing
    try:
        with open("output.txt", "w", encoding="utf-8") as f:
            for i, r in enumerate(results):
                f.write(f"Input: {r['input']}\n")
                f.write(f"Tree: {r['tree']}\n")
                f.write(f"Tokens: {r['tokens']}\n")
                f.write(f"Result: {r['result']}\n")
                if i != len(results) - 1:
                    f.write("\n")
    except OSError as e:
        print(f"❌ Error writing output file: {e}")

    return results


if __name__ == "__main__":
    file_name = "input.txt"

    # ✅ Case 1: File does NOT exist
    if not os.path.exists(file_name):
        print("⚠️ input.txt not found. Creating a new file.")

        expressions = []
        print("Enter expressions (type 'exit' to stop):")

        while True:
            line = input("> ")
            if line.lower() == "exit":
                break
            expressions.append(line)

        if not expressions:
            print("No input provided. Program exiting.")
            exit()

        # create file
        with open(file_name, "w", encoding="utf-8") as f:
            for expr in expressions:
                f.write(expr + "\n")

        print("✅ input.txt created.")

    # ✅ Case 2: File exists
    else:
        print("📄 input.txt already exists.")
        choice = input("Do you want to update it? (y/n): ").lower()

        if choice == "y":
            expressions = []
            print("Enter new expressions (type 'exit' to stop):")

            while True:
                line = input("> ")
                if line.lower() == "exit":
                    break
                expressions.append(line)

            if not expressions:
                print("No input provided. Keeping existing file.")
            else:
                with open(file_name, "w", encoding="utf-8") as f:
                    for expr in expressions:
                        f.write(expr + "\n")

                print("✅ input.txt updated.")

        else:
            print("Using existing input.txt.")

    # ✅ Run evaluation
    evaluate_file(file_name)
    print("✅ Output written to output.txt")