from copy import copy
from symbols import (
    DOUBLE_QUOTE,
    TYPES,
    VALID_CHARS,
    VALID_NUMBERS,
    WHITESPACE,
    SYMBOLS,
    TOKEN_TYPES,
    CALL_FUNC,
    DECLARE_FUNC,
    STRING_VALUE,
    NUMBER_VALUE,
    RETURN_FUNC,
    ORIGINAL_ENTRY_POINT,
    PRINTF_CODE,
    RESERVED_WORDS,
    INLINE_ASSEMBLY,
)


def _get_same_depth_nodes_values(nodes):
    values = []
    for child in nodes:
        values.append(child["options"]["value"])
    return values


def _node_generator(node_type, options=None, child_nodes=None):
    return {
        "node_type": node_type,
        "options": {} if not options else options,
        "child_nodes": [] if not child_nodes else child_nodes,
    }


class Lexer:
    """
    Type: int
    Identifier: main
    Symbol (
    Symbol )
    Symbol: {
    Identifier: printf
    Symbol (
    String "Hello world"
    Symbol )
    Symbol ;
    Symbol }
    """

    def __init__(self, file_path):
        with open(file_path, 'r') as fp:
            self.code = fp.read()
        self.index = 0
        self.code_len = len(self.code)
        self.token = {"type": '', "value": ''}

    @property
    def cursor_char(self):
        return self.code[self.index]

    def _get_next_char(self):
        self.index += 1
        if self.index >= self.code_len:
            return None
        return self.code[self.index]

    def get_token(self):
        def _get_identifier():
            _value = self.cursor_char
            _char1 = self._get_next_char()
            while _char1 in VALID_CHARS:
                _value += _char1
                _char1 = self._get_next_char()

            return _value

        def _get_number():
            _value = self.cursor_char
            _char1 = self._get_next_char()
            while _char1 in VALID_NUMBERS:
                _value += _char1
                _char1 = self._get_next_char()

            return _value

        def _get_string():
            _value = self.cursor_char
            _char1 = self._get_next_char()
            while _char1 != DOUBLE_QUOTE:
                _value += _char1
                _char1 = self._get_next_char()
            _value += char1
            self._get_next_char()
            return _value

        if self.index >= self.code_len:
            return self.token

        char1 = self.cursor_char

        while char1 in WHITESPACE:
            self.token["type"] = WHITESPACE
            self.token["value"] += char1
            char1 = self._get_next_char()

        if char1 is None:
            self.token["type"] = TOKEN_TYPES["EOF"]
            return self.token
        if char1 in VALID_CHARS:
            value = _get_identifier()
            if value in RESERVED_WORDS:
                self.token["type"] = TOKEN_TYPES["RESERVED_WORDS"]
            else:
                self.token["type"] = TOKEN_TYPES[value] if value in TYPES else TOKEN_TYPES["IDENTIFIER"]
            self.token["value"] = value
        elif char1 in VALID_NUMBERS:
            self.token["value"] = _get_number()
            self.token["type"] = TOKEN_TYPES["NUMBER"]
        elif char1 in DOUBLE_QUOTE:
            self.token["value"] = _get_string()
            self.token["type"] = TOKEN_TYPES["STRING"]
        elif char1 in SYMBOLS:
            self.token["value"] = char1
            self.token["type"] = TOKEN_TYPES["SYMBOL"]
            self._get_next_char()
        else:
            # TODO: Add other token types
            raise NotImplementedError

        return self.token


class Parser:
    def __init__(self, file_path):
        self.lexer = Lexer(file_path)
        self.parse_tree = []

    def consume(self, char):
        token = self.lexer.get_token()
        first_pass = True
        while token["value"] != char:
            token = self.lexer.get_token()
            first_pass = False
        return token if not first_pass else self.lexer.get_token()

    def _declare_func(self):
        return_type = copy(self.lexer.token)["value"]
        func_name = copy(self.lexer.get_token())["value"]
        root_node = _node_generator(DECLARE_FUNC, {"func_name": func_name, "return_type": return_type})
        token = self.consume('(')

        while token["value"] != "{":
            # parse function's parameters
            token = self.lexer.get_token()
            if token["value"] in TYPES:
                arg_type = token["value"]
            else:
                break
            arg_identifier = copy(self.lexer.get_token()["value"])
            root_node["options"]["params"].append((arg_type, arg_identifier))
            token = self.lexer.get_token()
        while token["value"] != "}":
            child_node = self.state_handler(token, root_node)
            if child_node is not None:
                root_node["child_nodes"].append(child_node)
            token = self.lexer.get_token()
        self.parse_tree.append(root_node)

    def _call_function(self):
        params = []
        func_name = self.lexer.token["value"]

        token = self.consume('(')
        while token["value"] != ")":
            # parse function's arguments
            if token["type"] == TOKEN_TYPES["STRING"]:
                params.append(token["value"])
            else:
                # TODO: Check the type of arguments
                raise NotImplementedError
            token = self.lexer.get_token()

        node = _node_generator(
            CALL_FUNC,
            {"func_name": func_name},
        )
        for param in params:
            child_node = _node_generator(STRING_VALUE, {"value": param})
            node["child_nodes"].append(child_node)
        return node

    def _return_function(self):
        return_value = self.lexer.get_token()
        if return_value["type"] == TOKEN_TYPES["NUMBER"]:
            node = _node_generator(RETURN_FUNC)
            node["child_nodes"].append(_node_generator(NUMBER_VALUE, {"value": return_value["value"]}))
            return node
        else:
            raise NotImplementedError

    def state_handler(self, token, node):
        """
        statement = declare_function | call_function
        declare_function = TYPES IDENTIFIER(expression){ expression }
        call_function = IDENTIFIER(expression);
        """
        if token["value"] in TYPES:
            if self.lexer.code[self.lexer.index + 2] == '=':
                # TODO: declare_variable
                raise NotImplementedError
            else:
                self._declare_func()

        elif token["type"] == TOKEN_TYPES["IDENTIFIER"]:
            if self.lexer.cursor_char == '(':
                # function call
                return self._call_function()
            else:
                # TODO: assign variable
                raise NotImplementedError
        elif token["type"] == TOKEN_TYPES["RESERVED_WORDS"]:
            if token["value"] == "return":
                return self._return_function()
        elif token["type"] == TOKEN_TYPES["SYMBOL"]:
            pass
        elif token["type"] == TOKEN_TYPES["EOF"]:
            pass
        else:
            # Undefined state
            raise NotImplementedError

    def run(self):
        token = self.lexer.get_token()
        root_node = {}
        while token["type"] != TOKEN_TYPES["EOF"]:
            self.state_handler(token, root_node)
            token = self.lexer.get_token()
        return self.parse_tree

    def show(self):
        token = self.lexer.get_token()
        while token["type"] != TOKEN_TYPES["EOF"]:
            token = self.lexer.get_token()
            print(self.lexer.token)


class Compiler:
    def __init__(self, symbol_table):
        self.parse_tree = symbol_table
        self.prologue = "push ebp\nmov ebp, esp"
        self.epilogue = "leave\nret\n"
        self.text_section = 'section .text\nglobal %s\n' % ORIGINAL_ENTRY_POINT
        self.data_section = 'section .data\n'

    def make_assembly(self, node, is_assembly=False):
        if is_assembly:
            return "\n%s" % node["value"]
        asm = ''
        for child in node["child_nodes"]:
            node_type = child["node_type"]
            if node_type == CALL_FUNC:
                func_name = child["options"]["func_name"]
                if func_name == "printf":
                    node = _node_generator(DECLARE_FUNC, {"func_name": func_name, "return_type": "void"})
                    code_node = _node_generator(INLINE_ASSEMBLY, {"value": PRINTF_CODE})
                    node["child_nodes"].append(code_node)
                    self.text_section += self.alloc_func(node)
                child_nodes = child["child_nodes"]
                params = []
                for child in child_nodes:
                    if child["node_type"] == STRING_VALUE:
                        identifier = self.alloc_string(child["options"]["value"])
                        params.append(identifier)
                push_params = '\n'.join(map(lambda a: 'push %s' % a, params))
                call_func = "call %s\nadd esp, %d" % (func_name, len(child_nodes) * 4)
                asm += '\n%s\n%s\n' % (push_params, call_func)
            elif node_type == RETURN_FUNC:
                return_value = child["child_nodes"][0]["options"]["value"]
                asm += "mov eax, %s" % return_value
            elif node_type == INLINE_ASSEMBLY:
                asm += child["options"]["value"]
            else:
                # TODO: Compile operation code ex) 1+2*3
                raise NotImplementedError
        return asm

    def alloc_string(self, string, identifier=None):
        if not identifier:
            identifier = 'string1'
        self.data_section += '%s\tdb\t%s\n' % (identifier, string)
        # self.data_section += '%s_size\t%s\t$-%s\n' % (identifier, 'equ', identifier)
        return identifier

    def alloc_func(self, node):
        func_name = node["options"]["func_name"]
        asm = "\n\n%s:\n%s%s\n%s" % (func_name, self.prologue, self.make_assembly(node), self.epilogue)
        return asm

    def run(self):
        for node in self.parse_tree:
            if node["node_type"] == DECLARE_FUNC:
                asm = self.alloc_func(node)
                self.text_section = "%s%s" % (self.text_section, asm)
            else:
                # TODO: Alloc global variable
                raise NotImplementedError
        self.text_section += "\n_start:\ncall main\nmov ebx, eax\nmov eax, 1\nint 0x80\n"
        asm = "%s\n%s" % (self.text_section, self.data_section)
        return asm


def main(c_file):
    parser = Parser(c_file)
    parse_tree = parser.run()
    """
    from json import dump
    with open("parsing_tree.json", "w") as fp:
        dump(parse_tree, fp, indent=2)
    """
    compiler = Compiler(parse_tree)
    asm = compiler.run()
    with open("%s.s" % c_file[:c_file.find(".c")], "w") as fp:
        fp.write(asm)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        c_file = "./helloworld.c"
    else:
        c_file = sys.argv[1]
    main(c_file)
