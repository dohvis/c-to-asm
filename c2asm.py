from copy import copy
from symbols import (
    DOUBLE_QUOTE,
    TYPES,
    VALID_CHARS,
    VALID_NUMBERS,
    WHITESPACE,
    SYMBOLS,
    TOKEN_TYPES,
    STATE_TYPES,
    ORIGINAL_ENTRY_POINT,
    PRINTF_CODE,
)


class Node:
    def __init__(self, state=None, value=None):
        self.state = state
        self.value = value
        self.parent = None
        self.children = []
        self.depth = 0

    def append_child(self, node):
        node.parent = self
        node.depth = self.depth + 1
        self.children.append(node)

    def __repr__(self):
        return '<state: %s, value: %s, depth: %d>' % (self.state, self.value, self.depth)


class Lexer:
    """
    Type: void
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
            self.token["type"] = TOKEN_TYPES[value.upper()] if value in TYPES else TOKEN_TYPES["IDENTIFIER"]
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
    """
    main
        printf
            "hello world"
    """

    def __init__(self, file_path):
        self.lexer = Lexer(file_path)
        self.symbol_table = []

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
        symbol = {"type": return_type, "isFunc": True, "identifier": func_name}
        token = self.consume('(')

        args = []
        while token["value"] != "{":
            # parse function's arguments
            token = self.lexer.get_token()
            if token["value"] in TYPES:
                arg_type = token["value"]
            else:
                break
            arg_identifier = copy(self.lexer.get_token()["value"])
            args.append((arg_type, arg_identifier))
            token = self.lexer.get_token()
        symbol["args"] = args
        node = Node()
        while token["value"] != "}":
            _node = self.state_handler(token, node)
            if _node is not None:
                node.append_child(_node)
            token = self.lexer.get_token()
        symbol["node"] = node
        self.symbol_table.append(symbol)

    def _call_function(self):
        args = []
        function_name = self.lexer.token["value"]

        token = self.consume('(')
        while token["value"] != ")":
            # parse function's arguments
            if token["type"] == TOKEN_TYPES["STRING"]:
                args.append(token["value"])
            else:
                # TODO: Check the type of arguments
                raise NotImplementedError
            token = self.lexer.get_token()

        if function_name == "printf":
            strlen = len(args[0])
            node = Node(state=STATE_TYPES["INLINE_ASSEMBLY"], value={"code": PRINTF_CODE % strlen})
            symbol = {"type": "void", "isFunc": True, "identifier": "printf", "node": node}
            self.symbol_table.append(symbol)
        value = {"func_name": function_name, "args": args}
        node = Node(state=STATE_TYPES["CALL_FUNC"], value=value)
        return node

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
        elif token["type"] == TOKEN_TYPES["SYMBOL"]:
            pass
        elif token["type"] == TOKEN_TYPES["EOF"]:
            pass
        else:
            # Undefined state
            raise NotImplementedError

    def run(self):
        token = self.lexer.get_token()
        root_node = Node()
        while token["type"] != TOKEN_TYPES["EOF"]:
            self.state_handler(token, root_node)
            token = self.lexer.get_token()
        return self.symbol_table

    def show(self):
        token = self.lexer.get_token()
        while token["type"] != TOKEN_TYPES["EOF"]:
            token = self.lexer.get_token()
            print(self.lexer.token)


class Compiler:
    """
    section .text
    global _start

    printf:
            push ebp
            mov ebp, esp
            mov eax, 4
            mov ebx,1
            mov ecx, [ebp+8]
            mov edx, string1_size
            int 0x80
            leave
            ret

    _start:
            push string1
            call my_printf
            add esp, 4

    exit:
            mov eax, 1
            xor ebx, ebx
            int 0x80
    section .data
    string1    db      'Hello World'
    string1_size    equ     $-string

    ; nasm -f elf printf.s && ld -melf_i386 printf.o -o printf
    """

    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.prologue = "push ebp\nmov ebp, esp"
        self.epilogue = "leave\nret\n"
        self.text_section = 'section .text\nglobal %s' % ORIGINAL_ENTRY_POINT
        self.data_section = 'section .data\n'

    def make_assembly(self, node, is_assembly=False):
        if is_assembly:
            return "\n%s" % node.value["code"]
        for child in node.children:
            if child.state == STATE_TYPES["CALL_FUNC"]:
                func_name = child.value["func_name"]
                args = child.value["args"]
                for arg in args:
                    if isinstance(arg, str):
                        identifier = self.alloc_string(arg)
                        args[args.index(arg)] = identifier
                push_args = '\n'.join(map(lambda a: 'push %s' % a, args))
                call_func = "call %s\nadd esp, %d" % (func_name, len(args) * 4)
                return '\n%s:\n%s\n%s\n' % (ORIGINAL_ENTRY_POINT, push_args, call_func)
            else:
                # TODO: Compile operation code ex) 1+2*3
                raise NotImplementedError

    def alloc_string(self, string, identifier=None):
        if not identifier:
            identifier = 'string1'
        self.data_section += '%s\tdb\t%s\n' % (identifier, string)
        self.data_section += '%s_size\t%s\t$-%s\n' % (identifier, 'equ', identifier)
        return identifier

    def alloc_func(self, symbol):
        name = symbol["identifier"]
        node = symbol["node"]
        if name == "main":
            self.text_section += self.make_assembly(node)
        else:
            is_assembly = symbol["node"].state == STATE_TYPES["INLINE_ASSEMBLY"]
            self.text_section += "\n\n%s:\n%s%s\n%s" % (
                name, self.prologue, self.make_assembly(node, is_assembly=is_assembly), self.epilogue)

    def run(self):
        for symbol in self.symbol_table:
            if symbol["isFunc"]:
                self.alloc_func(symbol)
            else:
                # TODO: Alloc global variable
                raise NotImplementedError
        self.text_section += "\nexit:\nmov eax, 1\nxor ebx, ebx\nint 0x80\n"
        asm = "%s\n%s" % (self.text_section, self.data_section)
        return asm


def main(c_file):
    parser = Parser(c_file)
    symbol_table = parser.run()

    compiler = Compiler(symbol_table)
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
