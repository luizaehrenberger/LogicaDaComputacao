import sys
import operator

def sanitize_expression(expression):
    """Remove espaços extras da expressão."""
    return expression.replace(" ", "")

def evaluate_math_expression(expression):
    """Avalia uma expressão matemática simples contendo apenas + e -."""

    # Dicionário de operadores permitidos
    allowed_operators = {
        '+' : operator.add,
        '-' : operator.sub,
    }

    number_buffer = ''  # Armazena temporariamente os números
    numbers = []  # Lista de números extraídos
    operations = []  # Lista de operadores extraídos

    for char in expression:
        if char.isdigit():
            number_buffer += char  # Constrói o número dígito por dígito
        else:
            if number_buffer:  # Se houver um número acumulado, adiciona à lista
                numbers.append(int(number_buffer))
                number_buffer = ''
            if char in allowed_operators:
                operations.append(char)  # Adiciona operador encontrado
            else:
                raise ValueError(f"Caractere inválido encontrado: {char}")

    if number_buffer:
        numbers.append(int(number_buffer))  # Adiciona o último número acumulado

    # Verificação de erro: a quantidade de operadores deve ser exatamente a de números - 1
    if len(numbers) != len(operations) + 1:
        raise ValueError("Expressão inválida")

    if not operations:
        raise ValueError("Operador ausente na expressão")

    # Processamento da operação matemática
    result = numbers[0]
    for i, op in enumerate(operations):
        result = allowed_operators[op](result, numbers[i + 1])

    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Uso correto: python main.py '<expressão>'")

    input_expression = sys.argv[1]

    cleaned_expression = sanitize_expression(input_expression)

    try:
        result = evaluate_math_expression(cleaned_expression)
        print(f"{int(result)}")  # Garante que a saída seja um número inteiro
    except Exception as e:
        raise ValueError(f"Erro ao avaliar expressão: {e}")