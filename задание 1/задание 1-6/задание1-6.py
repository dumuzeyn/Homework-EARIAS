import math

def text_input(prompt):
    while True:
        text = input(prompt + ': ').strip()
        if text:
            return text
        print('Введите значение.')

def number(prompt, low=None, high=None, integer=False):
    while True:
        try:
            value = float(input(prompt + ': ').strip().replace(',', '.'))
            if not math.isfinite(value):
                raise ValueError
            if integer and (not value.is_integer()):
                raise ValueError
            if low is not None and value < low or (high is not None and value > high):
                raise ValueError
            return int(value) if integer else value
        except ValueError:
            print('Неверное число.')

def fmt(value):
    return f'{value:.6g}'

def run():
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nВвод прерван.')
    except OverflowError:
        print('Числа слишком велики.')
import re

def expression(text, facts, dual):
    parts = re.findall('\\d+|and|or|not|или|и|не|[()]', text.lower())
    if re.sub('\\s+', '', text.lower()) != ''.join(parts):
        raise ValueError('Допустимы номера фактов, and/or/not, и/или/не и скобки.')
    tokens = [{'и': 'and', 'или': 'or', 'не': 'not'}.get(x, x) for x in parts]
    position = 0
    steps = []

    def atom():
        nonlocal position
        if position >= len(tokens):
            raise ValueError('Не хватает операнда.')
        token = tokens[position]
        position += 1
        if token == 'not':
            md, mnd = atom()
            result = (1 - md, 1 - mnd)
            steps.append(f'NOT: MD = 1-{fmt(md)} = {fmt(result[0])}; MND = 1-{fmt(mnd)} = {fmt(result[1])}')
            return result
        if token == '(':
            result = disjunction()
            if position >= len(tokens) or tokens[position] != ')':
                raise ValueError('Не хватает закрывающей скобки.')
            position += 1
            return result
        if not token.isdigit() or not 1 <= int(token) <= len(facts):
            raise ValueError('Неверный номер факта.')
        return facts[int(token) - 1]

    def combine(left, right, op):
        md_func = min if op == 'and' else max
        mnd_func = (max if op == 'and' else min) if dual else md_func
        md, mnd = (md_func(left[0], right[0]), mnd_func(left[1], right[1]))
        steps.append(f'{op.upper()}: MD = {md_func.__name__}({fmt(left[0])},{fmt(right[0])}) = {fmt(md)}; MND = {mnd_func.__name__}({fmt(left[1])},{fmt(right[1])}) = {fmt(mnd)}')
        return (md, mnd)

    def conjunction():
        nonlocal position
        result = atom()
        while position < len(tokens) and tokens[position] == 'and':
            position += 1
            result = combine(result, atom(), 'and')
        return result

    def disjunction():
        nonlocal position
        result = conjunction()
        while position < len(tokens) and tokens[position] == 'or':
            position += 1
            result = combine(result, conjunction(), 'or')
        return result
    result = disjunction()
    if position != len(tokens):
        raise ValueError('Лишний операнд или скобка.')
    return (result, steps)

def main():
    count = number('Количество фактов', 1, integer=True)
    facts = []
    for i in range(count):
        name = text_input(f'Название факта {i + 1}')
        print(f'Факт {i + 1}: {name}')
        facts.append((number('MD', 0, 1), number('MND', 0, 1)))
    hypothesis = text_input('Заключение H')
    hypotheses = number('Количество предположений E', 1, 2, True)
    dual = number('MND: 1 — AND min / OR max, 2 — AND max / OR min', 1, 2, True) == 2
    results = []
    for i in range(hypotheses):
        while True:
            text = text_input(f'Выражение E{i + 1} (номера фактов, and/or/not, скобки)')
            try:
                result, steps = expression(text, facts, dual)
                break
            except (ValueError, RecursionError) as error:
                print('Неверное выражение:', error)
        print(f'\nE{i + 1}: {text}')
        for step in steps:
            print('  ' + step)
        md, mnd = result
        print(f'  MD(H:E{i + 1}) = {fmt(md)}; MND(H:E{i + 1}) = {fmt(mnd)}')
        print(f'  KU(H:E{i + 1}) = {fmt(md)}-{fmt(mnd)} = {fmt(md - mnd)}')
        results.append(result)
    md, mnd = results[0]
    print('\nОбъединение предположений')
    for next_md, next_mnd in results[1:]:
        combined_md = md + next_md * (1 - md)
        combined_mnd = mnd + next_mnd * (1 - mnd)
        print(f'  MD = {fmt(md)}+{fmt(next_md)}*(1-{fmt(md)}) = {fmt(combined_md)}')
        print(f'  MND = {fmt(mnd)}+{fmt(next_mnd)}*(1-{fmt(mnd)}) = {fmt(combined_mnd)}')
        md, mnd = (combined_md, combined_mnd)
    if len(results) == 1:
        print('  Одно предположение: объединение не требуется.')
    confidence = md - mnd
    print(f'KU = MD-MND = {fmt(md)}-{fmt(mnd)} = {fmt(confidence)}')
    print(f'Ответ для H «{hypothesis}»: MD = {fmt(md)}, MND = {fmt(mnd)}, KU = {fmt(confidence)}')
    print('Проверка диапазона [-1;1]:', 'выполнена' if -1 <= confidence <= 1 else 'ошибка')
if __name__ == '__main__':
    run()
