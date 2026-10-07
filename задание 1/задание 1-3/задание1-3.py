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

def mean(values):
    rated = [x for x in values if x != 0]
    return sum(rated) / len(rated) if rated else None

def run():
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nВвод прерван.')
    except OverflowError:
        print('Числа слишком велики.')

def encode(data, columns):
    values, rows, cols = ([], [], [])
    pointers = [0]
    ell_values, ell_cols = ([], [])
    width = max((sum((x != 0 for x in row)) for row in data), default=0)
    for i, row in enumerate(data):
        ev, ec = ([], [])
        for j, value in enumerate(row):
            if value != 0:
                print(f'  A[{i},{j}] = {fmt(value)}')
                values.append(value)
                rows.append(i)
                cols.append(j)
                ev.append(value)
                ec.append(j)
        pointers.append(len(values))
        ell_values.append(ev + [0] * (width - len(ev)))
        ell_cols.append(ec + [-1] * (width - len(ec)))
    print('COO: Value =', values, '; Row =', rows, '; Col =', cols)
    print('CSR: Value =', values, '; Col =', cols, '; RowIndex =', pointers)
    print(f'ELLPACK: ширина строки {width}')
    print('Value =', ell_values)
    print('Column =', ell_cols)
    restored = [[0] * columns for _ in data]
    for v, i, j in zip(values, rows, cols):
        restored[i][j] = v
    restored_csr = [[0] * columns for _ in data]
    for i in range(len(data)):
        for k in range(pointers[i], pointers[i + 1]):
            restored_csr[i][cols[k]] = values[k]
    restored_ell = [[0] * columns for _ in data]
    for i in range(len(data)):
        for value, j in zip(ell_values[i], ell_cols[i]):
            if j != -1:
                restored_ell[i][j] = value
    print('Проверка восстановления COO, CSR и ELLPACK:', 'совпадает' if restored == restored_csr == restored_ell == data else 'ошибка')

def main():
    data, maximum = matrix_input()
    threshold = number('Минимальный средний рейтинг товара', 0, maximum)
    print('\nИсходная матрица')
    table(data, [f'P{i + 1}' for i in range(len(data))], [f'U{i + 1}' for i in range(len(data[0]))])
    print('\nCOO, CSR и ELLPACK')
    encode(data, len(data[0]))
    print('\nСредние рейтинги')
    kept_rows = []
    for i, row in enumerate(data):
        rated = [x for x in row if x]
        rating = mean(row)
        if rating is None:
            print(f'  P{i + 1}: все оценки нулевые — исключаем')
        else:
            keep = rating >= threshold
            print(f'  P{i + 1}: {fmt(sum(rated))}/{len(rated)} = {fmt(rating)}; ' + ('оставляем' if keep else 'исключаем'))
            if keep:
                kept_rows.append(i)
    print('\nНеактивные пользователи')
    kept_cols = []
    for j in range(len(data[0])):
        active = any((data[i][j] != 0 for i in kept_rows))
        print(f'  U{j + 1}: ' + ('оставляем' if active else 'все оставшиеся оценки нулевые — исключаем'))
        if active:
            kept_cols.append(j)
    filtered = [[data[i][j] for j in kept_cols] for i in kept_rows]
    print('\nИтоговая матрица')
    table(filtered, [f'P{i + 1}' for i in kept_rows], [f'U{j + 1}' for j in kept_cols])
    print(f'Размер: {len(filtered)} x {len(kept_cols)}')
    print('Соответствие строк товарам:', [f'P{i + 1}' for i in kept_rows])
    print('Соответствие столбцов пользователям:', [f'U{j + 1}' for j in kept_cols])
    print('\nХранение итоговой матрицы')
    encode(filtered, len(kept_cols))
if __name__ == '__main__':
    run()
