import re

# --- Définition des types de tokens ---
TOKEN_TYPES = {
    'KEYWORD': 'KEYWORD',
    'IDENTIFIER': 'IDENTIFIER',
    'OPERATOR': 'OPERATOR',
    'DELIMITER': 'DELIMITER',
    'INT_LITERAL': 'INT_LITERAL',
    'FLOAT_LITERAL': 'FLOAT_LITERAL',
    'STR_LITERAL': 'STR_LITERAL',
    'TYPE_KEYWORD': 'TYPE_KEYWORD',
    'NEWLINE': 'NEWLINE',
    'EOF': 'EOF'
}

# --- Listes des mots-clés, opérateurs et délimiteurs ---
KEYWORDS = {
    'func', 'if', 'elif', 'else', 'while', 'print', 'input', 'return',
    'int', 'float', 'STR', 'List', 'Dictionary', 'none',
    'import',
    'and', 'or', 'not', 'in'
}

OPERATORS = {
    '==', '!=', '>=', '<=', '**', '///',
    '+', '-', '*', '/', '%', '=', '>', '<', '//'
}

DELIMITERS = {
    '(', ')', '{', '}', '[', ']', ':', ',', ';',
    '||'
}

# --- Classe Token ---
class Token:
    def __init__(self, type, value, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        if self.line is not None and self.column is not None:
            return f"Token({self.type}, '{self.value}', L{self.line} C{self.column})"
        return f"Token({self.type}, '{self.value}')"

# --- Classe Lexer ---
class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def current_char(self):
        if self.position < len(self.code):
            return self.code[self.position]
        return None

    def advance(self):
        char = self.current_char()
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
        return char

    def peek(self, offset=1):
        if self.position + offset < len(self.code):
            return self.code[self.position + offset]
        return None

    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char().isspace() and self.current_char() != '\n':
            self.advance()

    def tokenize_number(self):
        start_pos = self.position
        start_col = self.column
        while self.current_char() is not None and self.current_char().isdigit():
            self.advance()
        if self.current_char() == '.':
            self.advance()
            while self.current_char() is not None and self.current_char().isdigit():
                self.advance()
            value = self.code[start_pos:self.position]
            self.tokens.append(Token(TOKEN_TYPES['FLOAT_LITERAL'], float(value), self.line, start_col))
        else:
            value = self.code[start_pos:self.position]
            self.tokens.append(Token(TOKEN_TYPES['INT_LITERAL'], int(value), self.line, start_col))

    def tokenize_string(self, quote_char):
        start_pos = self.position
        start_col = self.column
        self.advance()
        string_value = ""
        while self.current_char() is not None and self.current_char() != quote_char:
            string_value += self.advance()
        
        if self.current_char() != quote_char:
            raise Exception(f"Erreur lexicale à L{self.line} C{self.column}: Chaîne non terminée, guillemet '{quote_char}' attendu.")
        
        self.advance()
        self.tokens.append(Token(TOKEN_TYPES['STR_LITERAL'], string_value, self.line, start_col))

    def tokenize_identifier_or_keyword(self):
        start_pos = self.position
        start_col = self.column
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        
        value = self.code[start_pos:self.position]
        
        if value in KEYWORDS:
            if value in {'int', 'float', 'STR', 'List', 'Dictionary', 'none'}:
                self.tokens.append(Token(TOKEN_TYPES['TYPE_KEYWORD'], value, self.line, start_col))
            else:
                self.tokens.append(Token(TOKEN_TYPES['KEYWORD'], value, self.line, start_col))
        else:
            self.tokens.append(Token(TOKEN_TYPES['IDENTIFIER'], value, self.line, start_col))

    def get_tokens(self):
        while self.position < len(self.code):
            self.skip_whitespace()

            char = self.current_char()

            if char is None:
                break

            if char == '#':
                self.advance()
                while self.current_char() is not None and self.current_char() != '\n':
                    self.advance()
                continue
            
            if char.isdigit():
                self.tokenize_number()
                continue

            if char == '"' or char == "'":
                self.tokenize_string(char)
                continue

            if char.isalpha() or char == '_':
                self.tokenize_identifier_or_keyword()
                continue
            
            found_operator = False
            for op in sorted(OPERATORS, key=len, reverse=True):
                if self.code[self.position:].startswith(op):
                    self.tokens.append(Token(TOKEN_TYPES['OPERATOR'], op, self.line, self.column))
                    self.position += len(op)
                    self.column += len(op)
                    found_operator = True
                    break
            if found_operator:
                continue

            found_delimiter = False
            for delim in sorted(DELIMITERS, key=len, reverse=True):
                if self.code[self.position:].startswith(delim):
                    self.tokens.append(Token(TOKEN_TYPES['DELIMITER'], delim, self.line, self.column))
                    self.position += len(delim)
                    self.column += len(delim)
                    found_delimiter = True
                    break
            if found_delimiter:
                continue

            if char == '\n':
                self.tokens.append(Token(TOKEN_TYPES['NEWLINE'], char, self.line, self.column))
                self.advance()
                continue

            raise Exception(f"Erreur lexicale à L{self.line} C{self.column}: Caractère non reconnu '{char}'")
        
        self.tokens.append(Token(TOKEN_TYPES['EOF'], 'EOF', self.line, self.column))
        return self.tokens


# --- Classes pour les Nœuds de l'Arbre Syntaxique Abstrait (AST) ---
class ASTNode:
    """Classe de base pour tous les nœuds de l'AST."""
    def __init__(self, token=None):
        self.token = token

    def __repr__(self):
        return f"{self.__class__.__name__}({self.token.value if self.token else ''})"

    def visit(self, visitor):
        method_name = 'visit_' + self.__class__.__name__
        visitor_method = getattr(visitor, method_name, self.generic_visit)
        return visitor_method(self)

    def generic_visit(self, node):
        raise Exception(f"Aucune méthode visit_{node.__class__.__name__} n'est définie pour le visiteur.")

class NumberNode(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.value = token.value

    def __repr__(self):
        return f"Number({self.value})"

class StringNode(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.value = token.value

    def __repr__(self):
        return f"String('{self.value}')"

class IdentifierNode(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.name = token.value

    def __repr__(self):
        return f"Identifier('{self.name}')"

class NoneNode(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.value = None

    def __repr__(self):
        return "None"

class BinaryOpNode(ASTNode):
    def __init__(self, left, op_token, right):
        super().__init__(op_token)
        self.left = left
        self.op = op_token
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op.value}, {self.right})"

class UnaryOpNode(ASTNode):
    def __init__(self, op_token, operand):
        super().__init__(op_token)
        self.op = op_token
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op.value}, {self.operand})"

class ListNode(ASTNode):
    def __init__(self, elements, token=None):
        super().__init__(token)
        self.elements = elements

    def __repr__(self):
        return f"List({self.elements})"

class DictionaryNode(ASTNode):
    def __init__(self, pairs, token=None):
        super().__init__(token)
        self.pairs = pairs

    def __repr__(self):
        return f"Dictionary({self.pairs})"

class SubscriptNode(ASTNode):
    """Représente l'accès à un élément de liste ou de dictionnaire (ex: list[index], dict["key"])."""
    def __init__(self, target, index_expr, token=None):
        super().__init__(token)
        self.target = target
        self.index_expr = index_expr

    def __repr__(self):
        return f"Subscript({self.target}, {self.index_expr})"

class ProgramNode(ASTNode):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements

    def __repr__(self):
        return f"Program(Statements={self.statements})"

class AssignmentNode(ASTNode):
    def __init__(self, identifier, expression, token=None):
        super().__init__(token)
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.identifier}, {self.expression})"

class PrintStatementNode(ASTNode):
    def __init__(self, expressions, token=None):
        super().__init__(token)
        self.expressions = expressions

    def __repr__(self):
        return f"Print({self.expressions})"

class InputFunctionCallNode(ASTNode):
    def __init__(self, prompt_expr, token=None):
        super().__init__(token)
        self.prompt_expr = prompt_expr

    def __repr__(self):
        return f"Input({self.prompt_expr})"

class TypeConversionNode(ASTNode):
    def __init__(self, type_token, expression, token=None):
        super().__init__(token)
        self.type_token = type_token
        self.expression = expression

    def __repr__(self):
        return f"TypeConvert({self.type_token.value}, {self.expression})"

class FunctionCallNode(ASTNode):
    def __init__(self, identifier, arguments, token=None):
        super().__init__(token)
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self):
        return f"Call({self.identifier.name}, {self.arguments})"

class FunctionDeclarationNode(ASTNode):
    def __init__(self, identifier, parameters, body_statements, token=None):
        super().__init__(token)
        self.identifier = identifier
        self.parameters = parameters
        self.body_statements = body_statements

    def __repr__(self):
        return f"FuncDecl({self.identifier.name}, Params={self.parameters}, Body={self.body_statements})"

class ReturnStatementNode(ASTNode):
    def __init__(self, expression=None, token=None):
        super().__init__(token)
        self.expression = expression

    def __repr__(self):
        return f"Return({self.expression})"

class IfStatementNode(ASTNode):
    def __init__(self, condition, if_body, elif_branches, else_body, token=None):
        super().__init__(token)
        self.condition = condition
        self.if_body = if_body
        self.elif_branches = elif_branches
        self.else_body = else_body

    def __repr__(self):
        return f"If(Cond={self.condition}, IfBody={self.if_body}, Elif={self.elif_branches}, Else={self.else_body})"

class WhileStatementNode(ASTNode):
    def __init__(self, condition, body_statements, token=None):
        super().__init__(token)
        self.condition = condition
        self.body_statements = body_statements

    def __repr__(self):
        return f"While(Cond={self.condition}, Body={self.body_statements})"

class ImportStatementNode(ASTNode):
    def __init__(self, file_path_token, token=None):
        super().__init__(token)
        self.file_path = file_path_token.value

    def __repr__(self):
        return f"Import('{self.file_path}')"


# --- Classe Parser ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return self.tokens[-1]

    def advance(self):
        self.current_token_index += 1
        return self.current_token()

    def eat(self, token_type, token_value=None):
        token = self.current_token()
        if token.type == token_type and (token_value is None or token.value == token_value):
            self.advance()
            return token
        else:
            self.error(f"Attendu {token_type} ('{token_value}' si spécifié), trouvé {token.type} ('{token.value}')")

    def error(self, message):
        token = self.current_token()
        raise Exception(f"Erreur de syntaxe à L{token.line} C{token.column}: {message} (Token: {token.type}, Valeur: '{token.value}')")

    def parse_program(self):
        statements = []
        while self.current_token().type != TOKEN_TYPES['EOF']:
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            while self.current_token().type == TOKEN_TYPES['NEWLINE'] or \
                  (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ';'):
                self.advance()
        return ProgramNode(statements)

    def parse_statement(self):
        token = self.current_token()

        if token.type == TOKEN_TYPES['KEYWORD']:
            if token.value == 'func':
                return self.parse_function_declaration()
            elif token.value == 'if':
                return self.parse_if_statement()
            elif token.value == 'while':
                return self.parse_while_statement()
            elif token.value == 'print':
                return self.parse_print_statement()
            elif token.value == 'input':
                self.error("L'instruction 'input' doit être assignée à une variable ou utilisée dans une expression.")
            elif token.value == 'return':
                return self.parse_return_statement()
            elif token.value == 'import':
                return self.parse_import_statement()
            elif token.value in {'and', 'or', 'not', 'in'}:
                self.error(f"Le mot-clé '{token.value}' ne peut pas commencer une instruction de haut niveau.")
            elif token.type == TOKEN_TYPES['TYPE_KEYWORD']:
                self.error(f"Le mot-clé de type '{token.value}' ne peut pas commencer une instruction de haut niveau.")
            else:
                self.error(f"Mot-clé inattendu '{token.value}' au début d'une instruction.")

        elif token.type == TOKEN_TYPES['IDENTIFIER']:
            # La cible de l'affectation ou l'appel de fonction peut commencer par un identifiant.
            # Nous devons regarder le token suivant pour distinguer.
            # Cependant, l'affectation peut désormais être 'identifiant[index] = expr;'
            # Il est plus robuste d'analyser l'expression de gauche (qui peut être un SubscriptNode)
            # puis de voir si un '=' suit.

            # Sauvegarder la position actuelle pour pouvoir revenir en arrière si ce n'est pas une affectation
            start_index = self.current_token_index 
            
            # Tenter d'analyser ce qui pourrait être la L-value d'une affectation (Identifier ou Subscript)
            # Ou ce qui pourrait être le début d'une expression comme un appel de fonction
            temp_node = self.parse_factor() # Appelle parse_factor pour gérer les identifiants et les subscripting

            # Après avoir analysé le 'temp_node', si le token suivant est '=', c'est une affectation.
            if self.current_token().type == TOKEN_TYPES['OPERATOR'] and self.current_token().value == '=':
                # C'est une affectation, nous avons déjà parsé la cible (L-value)
                # Assurez-vous que la cible est bien un IdentifierNode ou un SubscriptNode
                if not isinstance(temp_node, (IdentifierNode, SubscriptNode)):
                    self.error(f"Cible d'affectation invalide. Attendu un identifiant ou une expression d'indexation.")
                
                assignment_op_token = self.eat(TOKEN_TYPES['OPERATOR'], '=')
                expression_node = self.parse_expression()
                self.eat(TOKEN_TYPES['DELIMITER'], ';')
                return AssignmentNode(temp_node, expression_node, assignment_op_token)
            elif isinstance(temp_node, FunctionCallNode):
                # Si temp_node est un appel de fonction, c'est une instruction valide si elle est terminée par ';'
                self.eat(TOKEN_TYPES['DELIMITER'], ';')
                return temp_node
            else:
                # Si ce n'est ni une affectation ni un appel de fonction valide, c'est une erreur.
                self.error(f"Instruction inattendue. Attendu '=' ou '(' après l'identifiant, ou fin de ligne/';'.")

        elif token.type == TOKEN_TYPES['NEWLINE']:
            self.advance()
            return None

        self.error(f"Instruction non reconnue ou syntaxe invalide. Token: {token.type}, Valeur: '{token.value}'")


    def parse_expression(self):
        return self.parse_logical_or_expression()

    def parse_logical_or_expression(self):
        node = self.parse_logical_and_expression()
        while self.current_token().type == TOKEN_TYPES['KEYWORD'] and self.current_token().value == 'or':
            op_token = self.eat(TOKEN_TYPES['KEYWORD'], 'or')
            right = self.parse_logical_and_expression()
            node = BinaryOpNode(node, op_token, right)
        return node

    def parse_logical_and_expression(self):
        node = self.parse_comparison_expression()
        while self.current_token().type == TOKEN_TYPES['KEYWORD'] and self.current_token().value == 'and':
            op_token = self.eat(TOKEN_TYPES['KEYWORD'], 'and')
            right = self.parse_comparison_expression()
            node = BinaryOpNode(node, op_token, right)
        return node

    def parse_comparison_expression(self):
        node = self.parse_arithmetic_expression()
        
        while True:
            current_token = self.current_token()
            op_value = current_token.value
            op_type = current_token.type

            is_comparison_op = (op_type == TOKEN_TYPES['OPERATOR'] and op_value in ['==', '!=', '>', '<', '>=', '<='])
            is_in_op = (op_type == TOKEN_TYPES['KEYWORD'] and op_value == 'in')
            is_not_in_op = False
            
            # Vérifier 'not in' avec prudence pour ne pas aller au-delà des tokens
            if op_type == TOKEN_TYPES['KEYWORD'] and op_value == 'not':
                if self.current_token_index + 1 < len(self.tokens) and \
                   self.tokens[self.current_token_index + 1].type == TOKEN_TYPES['KEYWORD'] and \
                   self.tokens[self.current_token_index + 1].value == 'in':
                    is_not_in_op = True

            if not (is_comparison_op or is_in_op or is_not_in_op):
                break 

            op_token = current_token

            if is_not_in_op:
                self.eat(TOKEN_TYPES['KEYWORD'], 'not')
                self.eat(TOKEN_TYPES['KEYWORD'], 'in')
                op_token.value = 'not in' # Change value for AST representation
            else:
                self.advance()
            
            right = self.parse_arithmetic_expression()
            node = BinaryOpNode(node, op_token, right)
            
        return node

    def parse_arithmetic_expression(self):
        node = self.parse_term()
        while self.current_token().type == TOKEN_TYPES['OPERATOR'] and \
              self.current_token().value in ['+', '-']:
            op_token = self.current_token()
            self.advance()
            right = self.parse_term()
            node = BinaryOpNode(node, op_token, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token().type == TOKEN_TYPES['OPERATOR'] and \
              self.current_token().value in ['*', '/', '//', '**', '///', '%']:
            op_token = self.current_token()
            self.advance()
            right = self.parse_factor()
            node = BinaryOpNode(node, op_token, right)
        return node

    def parse_factor(self):
        token = self.current_token()
        node = None

        if token.type == TOKEN_TYPES['INT_LITERAL'] or token.type == TOKEN_TYPES['FLOAT_LITERAL']:
            self.advance()
            node = NumberNode(token)
        elif token.type == TOKEN_TYPES['STR_LITERAL']:
            self.advance()
            node = StringNode(token)
        elif token.type == TOKEN_TYPES['KEYWORD'] and token.value == 'none':
            self.advance()
            node = NoneNode(token)
        elif token.type == TOKEN_TYPES['IDENTIFIER']:
            if self.current_token_index + 1 < len(self.tokens) and \
               self.tokens[self.current_token_index + 1].type == TOKEN_TYPES['DELIMITER'] and \
               self.tokens[self.current_token_index + 1].value == '(':
                node = self.parse_function_call()
            else:
                self.advance()
                node = IdentifierNode(token)
        elif token.type == TOKEN_TYPES['DELIMITER'] and token.value == '(':
            self.eat(TOKEN_TYPES['DELIMITER'], '(')
            node = self.parse_expression()
            self.eat(TOKEN_TYPES['DELIMITER'], ')')
        elif token.type == TOKEN_TYPES['DELIMITER'] and token.value == '[':
            node = self.parse_list_literal()
        elif token.type == TOKEN_TYPES['DELIMITER'] and token.value == '||':
            node = self.parse_dictionary_literal()
        elif token.type == TOKEN_TYPES['KEYWORD'] and token.value == 'not':
            op_token = self.eat(TOKEN_TYPES['KEYWORD'], 'not')
            operand = self.parse_factor()
            node = UnaryOpNode(op_token, operand)
        elif token.type == TOKEN_TYPES['KEYWORD'] and token.value == 'input':
            node = self.parse_input_function_call()
        elif token.type == TOKEN_TYPES['TYPE_KEYWORD'] and token.value in {'int', 'float', 'STR'}:
            type_token = self.advance()
            self.eat(TOKEN_TYPES['DELIMITER'], '(')
            expression_to_convert = self.parse_expression()
            self.eat(TOKEN_TYPES['DELIMITER'], ')')
            node = TypeConversionNode(type_token, expression_to_convert)
        else:
            self.error(f"Expression inattendue. Token: {token.type}, Valeur: '{token.value}'")

        while self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == '[':
            bracket_token = self.eat(TOKEN_TYPES['DELIMITER'], '[')
            index_expr = self.parse_expression()
            self.eat(TOKEN_TYPES['DELIMITER'], ']')
            node = SubscriptNode(node, index_expr, bracket_token)
            
        return node


    def parse_list_literal(self):
        list_token = self.eat(TOKEN_TYPES['DELIMITER'], '[')
        elements = []
        if self.current_token().type != TOKEN_TYPES['DELIMITER'] or self.current_token().value != ']':
            elements.append(self.parse_expression())
            while self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ',':
                self.eat(TOKEN_TYPES['DELIMITER'], ',')
                elements.append(self.parse_expression())
        self.eat(TOKEN_TYPES['DELIMITER'], ']')
        return ListNode(elements, list_token)

    def parse_dictionary_literal(self):
        dict_token = self.eat(TOKEN_TYPES['DELIMITER'], '||')
        pairs = []
        if self.current_token().type != TOKEN_TYPES['DELIMITER'] or self.current_token().value != '||':
            while True:
                key_node = self.parse_expression()
                
                self.eat(TOKEN_TYPES['DELIMITER'], ':')
                value_node = self.parse_expression()
                pairs.append((key_node, value_node))
                
                if self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ',':
                    self.eat(TOKEN_TYPES['DELIMITER'], ',')
                else:
                    break
        self.eat(TOKEN_TYPES['DELIMITER'], '||')
        return DictionaryNode(pairs, dict_token)

    def parse_print_statement(self):
        print_token = self.eat(TOKEN_TYPES['KEYWORD'], 'print')
        self.eat(TOKEN_TYPES['DELIMITER'], '(')
        
        expressions = []
        expressions.append(self.parse_expression())
        while self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ',':
            self.eat(TOKEN_TYPES['DELIMITER'], ',')
            expressions.append(self.parse_expression())
            
        self.eat(TOKEN_TYPES['DELIMITER'], ')')
        self.eat(TOKEN_TYPES['DELIMITER'], ';')
        
        return PrintStatementNode(expressions, print_token)

    def parse_input_function_call(self):
        input_token = self.eat(TOKEN_TYPES['KEYWORD'], 'input')
        self.eat(TOKEN_TYPES['DELIMITER'], '(')
        prompt_expr = self.parse_expression()
        self.eat(TOKEN_TYPES['DELIMITER'], ')')
        return InputFunctionCallNode(prompt_expr, input_token)

    def parse_function_call(self):
        identifier_token = self.eat(TOKEN_TYPES['IDENTIFIER'])
        identifier_node = IdentifierNode(identifier_token)
        
        self.eat(TOKEN_TYPES['DELIMITER'], '(')
        
        arguments = []
        if self.current_token().type != TOKEN_TYPES['DELIMITER'] or self.current_token().value != ')':
            arguments.append(self.parse_expression())
            while self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ',':
                self.eat(TOKEN_TYPES['DELIMITER'], ',')
                arguments.append(self.parse_expression())
                
        self.eat(TOKEN_TYPES['DELIMITER'], ')')
        
        return FunctionCallNode(identifier_node, arguments, identifier_token)

    def parse_function_declaration(self):
        func_token = self.eat(TOKEN_TYPES['KEYWORD'], 'func')
        identifier_token = self.eat(TOKEN_TYPES['IDENTIFIER'])
        identifier_node = IdentifierNode(identifier_token)
        
        self.eat(TOKEN_TYPES['DELIMITER'], '(')
        
        parameters = []
        if self.current_token().type == TOKEN_TYPES['IDENTIFIER']:
            parameters.append(IdentifierNode(self.eat(TOKEN_TYPES['IDENTIFIER'])))
            while self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ',':
                self.eat(TOKEN_TYPES['DELIMITER'], ',')
                parameters.append(IdentifierNode(self.eat(TOKEN_TYPES['IDENTIFIER'])))
                
        self.eat(TOKEN_TYPES['DELIMITER'], ')')
        self.eat(TOKEN_TYPES['DELIMITER'], '{')
        
        body_statements = []
        while not (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == '}'):
            statement = self.parse_statement()
            if statement:
                body_statements.append(statement)
            while self.current_token().type == TOKEN_TYPES['NEWLINE'] or \
                  (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ';'):
                self.advance()

        self.eat(TOKEN_TYPES['DELIMITER'], '}')
        self.eat(TOKEN_TYPES['DELIMITER'], ';')
        
        return FunctionDeclarationNode(identifier_node, parameters, body_statements, func_token)

    def parse_return_statement(self):
        return_token = self.eat(TOKEN_TYPES['KEYWORD'], 'return')
        expression = None
        if self.current_token().type != TOKEN_TYPES['DELIMITER'] or self.current_token().value != ';':
            expression = self.parse_expression()
        self.eat(TOKEN_TYPES['DELIMITER'], ';')
        return ReturnStatementNode(expression, return_token)

    def parse_if_statement(self):
        if_token = self.eat(TOKEN_TYPES['KEYWORD'], 'if')
        self.eat(TOKEN_TYPES['DELIMITER'], '(')
        condition = self.parse_expression()
        self.eat(TOKEN_TYPES['DELIMITER'], ')')
        self.eat(TOKEN_TYPES['DELIMITER'], '{')
        
        if_body = []
        while not (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == '}'):
            statement = self.parse_statement()
            if statement:
                if_body.append(statement)
            while self.current_token().type == TOKEN_TYPES['NEWLINE'] or \
                  (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ';'):
                self.advance()
        self.eat(TOKEN_TYPES['DELIMITER'], '}')
        
        elif_branches = []
        while self.current_token().type == TOKEN_TYPES['KEYWORD'] and self.current_token().value == 'elif':
            elif_token = self.eat(TOKEN_TYPES['KEYWORD'], 'elif')
            self.eat(TOKEN_TYPES['DELIMITER'], '(')
            elif_condition = self.parse_expression()
            self.eat(TOKEN_TYPES['DELIMITER'], ')')
            self.eat(TOKEN_TYPES['DELIMITER'], '{')
            
            elif_body = []
            while not (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == '}'):
                statement = self.parse_statement()
                if statement:
                    elif_body.append(statement)
                while self.current_token().type == TOKEN_TYPES['NEWLINE'] or \
                      (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ';'):
                    self.advance()
            self.eat(TOKEN_TYPES['DELIMITER'], '}')
            elif_branches.append((elif_condition, elif_body))
        
        else_body = None
        if self.current_token().type == TOKEN_TYPES['KEYWORD'] and self.current_token().value == 'else':
            self.eat(TOKEN_TYPES['KEYWORD'], 'else')
            self.eat(TOKEN_TYPES['DELIMITER'], '{')
            
            else_body = []
            while not (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == '}'):
                statement = self.parse_statement()
                if statement:
                    else_body.append(statement)
                while self.current_token().type == TOKEN_TYPES['NEWLINE'] or \
                      (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ';'):
                    self.advance()
            self.eat(TOKEN_TYPES['DELIMITER'], '}')
        
        self.eat(TOKEN_TYPES['DELIMITER'], ';')
        return IfStatementNode(condition, if_body, elif_branches, else_body, if_token)

    def parse_while_statement(self):
        while_token = self.eat(TOKEN_TYPES['KEYWORD'], 'while')
        self.eat(TOKEN_TYPES['DELIMITER'], '(')
        condition = self.parse_expression()
        self.eat(TOKEN_TYPES['DELIMITER'], ')')
        self.eat(TOKEN_TYPES['DELIMITER'], '{')
        
        body_statements = []
        while not (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == '}'):
            statement = self.parse_statement()
            if statement:
                body_statements.append(statement)
            while self.current_token().type == TOKEN_TYPES['NEWLINE'] or \
                  (self.current_token().type == TOKEN_TYPES['DELIMITER'] and self.current_token().value == ';'):
                self.advance()
        self.eat(TOKEN_TYPES['DELIMITER'], '}')
        self.eat(TOKEN_TYPES['DELIMITER'], ';')
        return WhileStatementNode(condition, body_statements, while_token)

    def parse_import_statement(self):
        import_token = self.eat(TOKEN_TYPES['KEYWORD'], 'import')
        file_path_token = self.eat(TOKEN_TYPES['STR_LITERAL'])
        self.eat(TOKEN_TYPES['DELIMITER'], ';')
        return ImportStatementNode(file_path_token, import_token)


# --- Classes pour l'Analyse Sémantique ---
class Symbol:
    def __init__(self, name, type=None, value=None):
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self):
        return f"<Symbol: {self.name}, Type: {self.type}>"

class FunctionSymbol(Symbol):
    def __init__(self, name, parameters=None, return_type=None):
        super().__init__(name, type='Function')
        self.parameters = parameters if parameters is not None else []
        self.return_type = return_type

    def __repr__(self):
        param_str = ', '.join([p.name for p in self.parameters])
        return f"<FunctionSymbol: {self.name}({param_str}) -> {self.return_type}>"

class VariableSymbol(Symbol):
    def __init__(self, name, type=None):
        super().__init__(name, type)

    def __repr__(self):
        return f"<VariableSymbol: {self.name}, Type: {self.type}>"


class SymbolTable:
    def __init__(self, parent=None):
        self.scopes = [{}]
        self.parent = parent
        self.depth = 0 if parent is None else parent.depth + 1

    def enter_scope(self):
        self.scopes.append({})
        self.depth += 1

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.depth -= 1
        else:
            raise Exception("Impossible de sortir de la portée globale.")

    def declare(self, symbol):
        current_scope = self.scopes[-1]
        if symbol.name in current_scope:
            raise Exception(f"Erreur sémantique: Le symbole '{symbol.name}' est déjà déclaré dans cette portée.")
        current_scope[symbol.name] = symbol

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        
        if self.parent:
            return self.parent.lookup(name)
            
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.global_symbol_table = SymbolTable()
        self.current_symbol_table = self.global_symbol_table
        self.errors = []

    def error(self, node, message):
        line = node.token.line if node.token else "Inconnu"
        column = node.token.column if node.token else "Inconnu"
        self.errors.append(f"Erreur sémantique à L{line} C{column}: {message}")

    def analyze(self, ast):
        self.visit(ast)
        if self.errors:
            print("\n--- Erreurs sémantiques détectées ---")
            for err in self.errors:
                print(err)
            raise Exception("Analyse sémantique échouée en raison d'erreurs.")
        print("\n--- Analyse sémantique terminée avec succès ---")

    def visit(self, node):
        if node is None:
            return
        
        method_name = 'visit_' + node.__class__.__name__
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        for attr_name in dir(node):
            if not attr_name.startswith('__') and not callable(getattr(node, attr_name)):
                attr = getattr(node, attr_name)
                if isinstance(attr, ASTNode):
                    self.visit(attr)
                elif isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, ASTNode):
                            self.visit(item)
                        elif isinstance(item, tuple) and all(isinstance(elem, ASTNode) for elem in item):
                            for elem in item:
                                self.visit(elem)


    def visit_ProgramNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_FunctionDeclarationNode(self, node):
        func_symbol = FunctionSymbol(node.identifier.name, parameters=[VariableSymbol(p.name) for p in node.parameters])
        self.current_symbol_table.declare(func_symbol)

        function_scope_table = SymbolTable(parent=self.current_symbol_table)
        old_symbol_table = self.current_symbol_table
        self.current_symbol_table = function_scope_table

        for param in node.parameters:
            param_symbol = VariableSymbol(param.name)
            self.current_symbol_table.declare(param_symbol)

        for statement in node.body_statements:
            self.visit(statement)

        self.current_symbol_table = old_symbol_table

    def visit_AssignmentNode(self, node):
        self.visit(node.expression) # Visiter l'expression de droite

        if isinstance(node.identifier, IdentifierNode):
            symbol = self.current_symbol_table.lookup(node.identifier.name)
            if symbol is None:
                # Si non déclaré, le déclarer comme une nouvelle variable
                var_symbol = VariableSymbol(node.identifier.name)
                self.current_symbol_table.declare(var_symbol)
            elif not isinstance(symbol, VariableSymbol):
                # Si c'est un autre type de symbole (ex: fonction), c'est une erreur de réassignation
                self.error(node, f"Le symbole '{node.identifier.name}' est déjà déclaré comme une fonction et ne peut être réassigné.")
            # else: C'est une réassignation à une variable existante, ce qui est OK
        elif isinstance(node.identifier, SubscriptNode):
            # Pour l'affectation à un élément de liste/dictionnaire (ex: maListe[0] = 10;)
            # On visite les composants du SubscriptNode pour s'assurer que 'maListe' et '0' sont valides
            self.visit(node.identifier.target)
            self.visit(node.identifier.index_expr)


    def visit_IdentifierNode(self, node):
        symbol = self.current_symbol_table.lookup(node.name)
        if symbol is None:
            self.error(node, f"Utilisation d'un identifiant non déclaré: '{node.name}'.")

    def visit_PrintStatementNode(self, node):
        for expr in node.expressions:
            self.visit(expr)

    def visit_BinaryOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOpNode(self, node):
        self.visit(node.operand)

    def visit_IfStatementNode(self, node):
        self.visit(node.condition)
        self.current_symbol_table.enter_scope()
        for stmt in node.if_body:
            self.visit(stmt)
        self.current_symbol_table.exit_scope()

        for cond, body in node.elif_branches:
            self.visit(cond)
            self.current_symbol_table.enter_scope()
            for stmt in body:
                self.visit(stmt)
            self.current_symbol_table.exit_scope()

        if node.else_body:
            self.current_symbol_table.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.current_symbol_table.exit_scope()

    def visit_WhileStatementNode(self, node):
        self.visit(node.condition)
        self.current_symbol_table.enter_scope()
        for stmt in node.body_statements:
            self.visit(stmt)
        self.current_symbol_table.exit_scope()

    def visit_FunctionCallNode(self, node):
        func_symbol = self.current_symbol_table.lookup(node.identifier.name)
        if func_symbol is None:
            self.error(node, f"Appel à une fonction non déclarée: '{node.identifier.name}'.")
        elif not isinstance(func_symbol, FunctionSymbol):
            self.error(node, f"'{node.identifier.name}' n'est pas une fonction et ne peut être appelée.")
        else:
            if len(node.arguments) != len(func_symbol.parameters):
                self.error(node, f"Nombre d'arguments incorrect pour l'appel de '{func_symbol.name}'. Attendu {len(func_symbol.parameters)}, trouvé {len(node.arguments)}.")

        for arg in node.arguments:
            self.visit(arg)

    def visit_ReturnStatementNode(self, node):
        if node.expression:
            self.visit(node.expression)

    def visit_InputFunctionCallNode(self, node):
        self.visit(node.prompt_expr)

    def visit_TypeConversionNode(self, node):
        self.visit(node.expression)

    def visit_ListNode(self, node):
        for element in node.elements:
            self.visit(element)

    def visit_DictionaryNode(self, node):
        for key_node, value_node in node.pairs:
            self.visit(key_node)
            self.visit(value_node)

    def visit_SubscriptNode(self, node):
        self.visit(node.target)
        self.visit(node.index_expr)

    def visit_NumberNode(self, node):
        pass 

    def visit_StringNode(self, node):
        pass 

    def visit_NoneNode(self, node):
        pass 

    def visit_ImportStatementNode(self, node):
        pass

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    tourte_code_example = """
# Ceci est un programme Tourte simple
func saluer(nom) {
    print("Bonjour, " + nom + " !");
};

maVariable = 10;
autreVariable = 3.14;

if (maVariable > 5 and autreVariable < 4.0) {
    print("Conditions remplies !");
} elif (maVariable == 10 or autreVariable == 3.14) {
    print("Une des conditions est vraie !");
} else {
    print("Conditions non remplies.");
};

compteur = 0;
while (compteur < 3) {
    print("Boucle:", compteur);
    compteur = compteur + 1;
};

import "utilitaires.tourte";

# UNCOMMENT LES LIGNES CI-DESSOUS POUR TESTER LES ERREURS SÉMANTIQUES :

# Erreur: Utilisation d'une variable non déclarée
# erreurNonDeclaree = variableQuiNExistePas; 

# Erreur: Appel de fonction non déclarée
# fonctionInconnue(); 

# Erreur: Nombre d'arguments incorrect
# saluer("Alice", 123);

# Erreur: Redéclaration d'une fonction (si on la mettait ici)
# func saluer(prenom) { print("Salut " + prenom); };

# Erreur: Redéclaration de variable dans la même portée
# maVariable = 20; # Ceci est une réaffectation, pas une redéclaration. OK.
# nouvelleVar = 1;
# nouvelleVar = 2; # Ceci est une réaffectation, pas une redéclaration. OK.
# {
#     scopeVar = 10;
#     scopeVar = 20; # OK
#     # nouvelleVar = 3; # Réaffectation de variable parent OK
#     # scopeVar = 100; # Ne déclenchera pas l'erreur de "déjà déclaré" car c'est une réaffectation
# }
# nouvelleVar = 1; # Déclencherait une erreur si la portée était la même, mais ici, c'est OK après la première déclaration

# Exemple de dictionnaire et de liste
infos_perso = ||"nom": "Jean", "age": 30, "ville": "Paris"||;
print("Nom:", infos_perso["nom"]);
print("Age:", infos_perso["age"]);

liste_courses = ["pommes", "bananes", "poires"];
print("Premier article:", liste_courses[0]);

liste_courses[0] = "cerises"; # Test d'affectation avec subscripting
print("Premier article modifié:", liste_courses[0]);
infos_perso["age"] = 31; # Test d'affectation avec subscripting
print("Nouvel âge:", infos_perso["age"]);


# Test de 'in' et 'not in'
if ("pommes" in liste_courses) {
    print("Les pommes sont dans la liste.");
};

if ("oranges" not in liste_courses) {
    print("Les oranges ne sont pas dans la liste.");
};

# Test de conversion de type et input
age_str = input("Quel est votre âge ? ");
age_int = int(age_str);
print("Votre âge est:", age_int);

# Test de l'opérateur racine n-ième
racine_cubique_8 = 8 /// 3;
print("Racine cubique de 8:", racine_cubique_8);

# Test de l'opérateur division euclidienne
division_euclidienne = 10 // 3;
print("Division euclidienne 10 // 3:", division_euclidienne);

fin_du_programme = "Oui";
print("Fin du programme:", fin_du_programme);

func testScope(valeur) {
    localVariable = 100;
    print("Dans la fonction, valeur:", valeur);
    print("Dans la fonction, localVariable:", localVariable);
    # testInner = 10; # Déclaré ici
    # print(testInner);
    # {
    #     testInner = 20; # Réaffectation dans la portée imbriquée
    #     innerInner = 30;
    # }
    # print(testInner); # Devrait être 20 si la réaffectation est persistante dans la fonction.
    # print(innerInner); # Erreur de portée
};

testScope(50);
# print(localVariable); # Décommenter pour tester l'erreur de portée: localVariable n'existe pas ici


func redeclarationTest() {
    x = 1;
    # func innerFunc() {
    #     # x = 4; # Ceci est une réaffectation de la `x` de la fonction parente, pas une redéclaration.
    # };
};

"""

    print("--- Démarrage de l'Analyse Lexicale ---")
    lexer = Lexer(tourte_code_example)
    try:
        tokens = lexer.get_tokens()
        print("Analyse lexicale terminée. Nombre de tokens:", len(tokens))

        print("\n--- Démarrage de l'Analyse Syntaxique (Parsing) ---")
        parser = Parser(tokens)
        ast = parser.parse_program()

        # print("\n--- Arbre Syntaxique Abstrait (AST) généré ---")
        # from pprint import pprint
        # pprint(ast) # Décommenter pour voir l'AST détaillé. Utilisez print_ast pour un affichage plus lisible.
        print("Analyse syntaxique terminée avec succès.")

        print("\n--- Démarrage de l'Analyse Sémantique ---")
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)

    except Exception as e:
        print(f"\n--- Une erreur est survenue ---")
        print(e)
    print("\n=== Exécution de code terminée ===")

