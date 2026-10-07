import math

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

def matrix_input():
    rows = number('Количество товаров', 1, integer=True)
    cols = number('Количество пользователей', 1, integer=True)
    maximum = number('Верхняя граница оценок', 1e-06)
    result = []
    for i in range(rows):
        while True:
            text = input(f'P{i + 1}, {cols} оценок через пробел: ')
            try:
                row = [float(x.replace(',', '.')) for x in text.split()]
                if len(row) != cols or any((not math.isfinite(x) or not 0 <= x <= maximum for x in row)):
                    raise ValueError
                result.append(row)
                break
            except ValueError:
                print(f'Нужно {cols} чисел от 0 до {fmt(maximum)}.')
    return (result, maximum)

def table(matrix, rows, cols):
    width = max([9] + [len(x) + 2 for x in rows + cols])
    print(''.rjust(width) + ''.join((x.rjust(width) for x in cols)))
    for name, row in zip(rows, matrix):
        print(name.rjust(width) + ''.join((fmt(x).rjust(width) for x in row)))

def cosine(a, b, detail=False):
    dot = sum((x * y for x, y in zip(a, b)))
    aa = sum((x * x for x in a))
    bb = sum((y * y for y in b))
    if detail:
        print('  A =', [fmt(x) for x in a], '; B =', [fmt(x) for x in b])
        print('  A*B = ' + ' + '.join((f'{fmt(x)}*{fmt(y)}' for x, y in zip(a, b))) + f' = {fmt(dot)}')
        print(f'  Сумма A^2 = {fmt(aa)}; сумма B^2 = {fmt(bb)}')
    if aa == 0 or bb == 0:
        if detail:
            print('  Нулевой вектор, cos не определён.')
        return None
    answer = max(-1.0, min(1.0, dot / (math.sqrt(aa) * math.sqrt(bb))))
    if detail:
        print(f'  cos = {fmt(dot)} / (sqrt({fmt(aa)})*sqrt({fmt(bb)})) = {answer:.6f}')
    return answer

def run():
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nВвод прерван.')
    except OverflowError:
        print('Числа слишком велики.')

def main():
    data, _ = matrix_input()
    print('\nМатрица предпочтений')
    table(data, [f'P{i + 1}' for i in range(len(data))], [f'U{i + 1}' for i in range(len(data[0]))])
    for title, vectors, prefix in [('товаров', data, 'P'), ('пользователей', list(zip(*data)), 'U')]:
        print(f'\nСходство {title}')
        pairs = []
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                print(f'{prefix}{i + 1} — {prefix}{j + 1}')
                value = cosine(vectors[i], vectors[j], True)
                if value is not None:
                    pairs.append((value, i, j))
        pairs.sort(key=lambda x: (-x[0], x[1], x[2]))
        print(f'Пары {title} по убыванию сходства')
        for value, i, j in pairs:
            print(f'  {prefix}{i + 1} — {prefix}{j + 1}: {value:.6f}')
        if pairs:
            best = pairs[0][0]
            for value, i, j in pairs:
                if math.isclose(value, best, abs_tol=1e-12):
                    print(f'Ответ: ближайшие {prefix}{i + 1} и {prefix}{j + 1}; cos = {value:.6f}')
        else:
            print('Ответ: нет двух ненулевых векторов для сравнения.')
if __name__ == '__main__':
    run()
