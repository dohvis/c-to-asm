DOUBLE_QUOTE = '"'  # string identifier
TYPES = ("void", "string", "int")
VALID_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrustuvwxyz_"
VALID_NUMBERS = "0123456789."
WHITESPACE = (" ", "\t", "\n")
SYMBOLS = ("(", ")", "{", "}", ",", ";")
TOKEN_TYPES = {"EOF": 0, "IDENTIFIER": 1, "NUMBER": 2, "STRING": 3, "SYMBOL": 4, "RESERVED_WORDS": 5}
NULL = "\0"
PRINTF_CODE = "\nmov eax, 4\nmov ebx,1\nmov ecx, [ebp+8]\nmov edx, %d\nint 0x80"
ORIGINAL_ENTRY_POINT = "_start"
RESERVED_WORDS = ("return",) + TYPES

## NODE TYPES
CALL_FUNC = "call function"
DECLARE_FUNC = "Declare function"
INLINE_ASSEMBLY = "INLINE_ASSEMBLY"
RETURN_FUNC = "return function"
STRING_VALUE = "String value"
NUMBER_VALUE = "Number value"
INLINE_ASSEMBLY = "Inline assembly"
