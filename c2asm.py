from copy import copy

DOUBLE_QUOTE = '"'  # string identifier
TYPES = ("void", "string")
VALID_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrustuvwxyz_"
VALID_NUMBERS = "0123456789."
WHITESPACE = (" ", "\t", "\n")
SYMBOLS = ("(", ")", "{", "}", ",", ";")
TOKEN_TYPES = {"EOF": 0, "IDENTIFIER": 1, "NUMBER": 2, "STRING": 3, "SYMBOL": 4, "VOID": 5}
NULL = "\0"
SYMBOL_TABLES = [
    {"type": "string", "isFunc": False, "identifier": "string1", "value": '"hello world"'},
    {"type": "void", "isFunc": True, "identifier": "main",
     "value": {"func": "printf", "args": ["string1"]}
     },
    {"type": "void", "isFunc": True, "identifier": "printf",
     "value": "mov eax, 4\bmov ebx,1\nmov ecx, [ebp+8]\nmov edx,size\nint 0x80"}
]
ORIGINAL_ENTRY_POINT = "_start"


class Node:
    def __init__(self, type=None, value=None):
        self.type = type
        self.value = value
        self.parent = None
        self.children = []
        self.depth = 0

    def add_node(self, value):
        child = Node(value)
        child.depth = self.depth + 1
        child.parent = self
        self.children.append(child)

    def get_root(self):
        node = self
        while node.depth != 0:
            print(node)
            node = node.parent
            break

    def __repr__(self):
        return 'value: %s, parent: %s depth:  %s, children: %s' % (self.value, self.parent, self.depth, self.children)

    def __str__(self):
        return self.__repr__()


class Lexer:
    """
            Here are the tokens returned by the lexer:
            0 Type: void
            4 Identifier: main
            5 Symbol (
            6 Symbol )
            5 Symbol: {
            6 Identifier: printf
            0 Symbol (
            0 String "Hello world"
            6 Symbol )
            6 Symbol ;
            7 Symbol }
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
            raise NotImplementedError

        return self.token


class Parser:
    """
    :declare_func
    my_printf
        args: [
                string:
                printed_string
            ]
            :call_func
            write
                syscall4(1, &string, size)
    :declare_func
    main
        :call_func # state
        my_printf
            "hello world"
    """

    def __init__(self, file_path):
        self.lexer = Lexer(file_path)

    def expression(self):
        pass

    def _declare_func(self, node):
        func_type = copy(self.lexer.token)["value"]
        func_name = copy(self.lexer.get_token())["value"]
        func_node = Node(type=func_type, value=func_name)

        token = self.lexer.get_token()  # consume('(')
        while token["value"] != "{":
            token = self.lexer.get_token()
            if token["value"] in TYPES:
                arg_type = token["value"]
            else:
                break
            arg_identifier = copy(self.lexer.get_token()["value"])
            arg_node = Node(type=arg_type, value=arg_identifier)
            func_node.children.append(arg_node)
            token = self.lexer.get_token()
        while token["value"] != "}":
            self.state_handler(token, func_node)
            token = self.lexer.get_token()
        node.children.append(func_node)

    def _call_function(self, node):
        func_name = copy(self.lexer.token)
        args = []
        token = self.lexer.get_token()
        while token["value"] != ")":
            if token["type"] in (TOKEN_TYPES["NUMBER"], TOKEN_TYPES["STRING"]):
                args.append(token["value"])
            token = self.lexer.get_token()
        func_node = Node(value=func_name)
        func_node.children.append(Node(value=args))
        node.children.append(func_node)

    def state_handler(self, token, node):
        """
        statement = declare_function | call_function
        declare_function = TYPES IDENTIFIER(expression){ expression }
        call_function = IDENTIFIER(expression);
        """
        if token["value"] in TYPES:
            self._declare_func(node)
            # TODO: declare_variable
        elif token["type"] == TOKEN_TYPES["IDENTIFIER"]:
            self._call_function(node)
        elif token["type"] == TOKEN_TYPES["SYMBOL"]:
            pass
        elif token["type"] == TOKEN_TYPES["EOF"]:
            pass
        else:
            raise NotImplementedError

    def run(self):
        token = self.lexer.get_token()
        node = Node()
        while token["type"] != TOKEN_TYPES["EOF"]:
            self.state_handler(token, node)
            token = self.lexer.get_token()
        return node

    def show(self):
        token = self.lexer.get_token()
        while token["type"] != TOKEN_TYPES["EOF"]:
            token = self.lexer.get_token()
            print(self.lexer.token)


class Assembler:
    """
    section .text
    global _start

    my_printf:
            push ebp
            mov ebp, esp
            mov eax, 4
            mov ebx,1
            mov ecx, [ebp+8]
            mov edx,size
            int 0x80
            leave
            ret

    _start:
            push string1
            call my_printf
            add esp, 4

    exit:   mov eax, 1
            int 0x80
    section .data
    string1    db      'Hello World'
    string1_size    equ     $-string

; nasm -f elf printf.s && ld -melf_i386 printf.o -o printf

    """

    def __init__(self, ast):
        self.ast = ast
        self.prologue = "push ebp\nmov ebp, esp"
        self.epilogue = "leave\nlet"
        self.text_section = 'section .text\n'
        self.data_section = 'section .data\n'

    def alloc_string(self, symbol):
        name = symbol["identifier"]
        type = symbol["type"]
        value = symbol["value"]
        self.data_section += '%s\t%s\t%s\n' % (name, 'db' if type == 'string' else '', value)
        self.data_section += '%s_size\t%s\t$-%s\n' % (name, 'equ', name)

    def alloc_func(self, symbol):
        name = symbol["identifier"]
        value = symbol["value"]
        if name == "main":
            callee = value["func"]
            args = value["args"]
            push_args = '\n'.join(map(lambda a: 'push %s' % a, args))
            call_func = "call %s\nadd esp, %d" % (callee, len(args) * 4)
            self.text_section += '\n%s:\n%s\n%s\n' % (ORIGINAL_ENTRY_POINT, push_args, call_func)
        else:
            self.text_section += "\n%s:\n%s\n%s\n%s" % (name, self.prologue, value, self.epilogue)

    def run(self):
        for symbol in SYMBOL_TABLES:
            if symbol["isFunc"]:
                self.alloc_func(symbol)
            else:
                self.alloc_string(symbol)
        self.text_section += "\n\nexit:\nmov eax, 1\nint 0x80\n"
        asm = "%s\n%s" % (self.text_section, self.data_section)
        return asm


if __name__ == "__main__":
    parser = Parser("./helloworld.c")
    # parser.show()
    ast = parser.run()
    from pprint import pprint

    pprint(ast)
    assembler = Assembler(ast)
    asm = assembler.run()
    with open("helloworld.s", "w") as fp:
        fp.write(asm)
