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

def table(matrix, rows, cols):
    width = max([9] + [len(x) + 2 for x in rows + cols])
    print(''.rjust(width) + ''.join((x.rjust(width) for x in cols)))
    for name, row in zip(rows, matrix):
        print(name.rjust(width) + ''.join((fmt(x).rjust(width) for x in row)))

def run():
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nВвод прерван.')
    except OverflowError:
        print('Числа слишком велики.')

def main():
    n = number('Количество пользователей', 1, integer=True)
    threshold = number('Порог R', 0, 1)
    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            sim[i][j] = sim[j][i] = number(f'Сходство U{i + 1} и U{j + 1}', 0, 1)
    clusters = [[i] for i in range(n)]
    step = 1
    while True:
        names = ['{' + ','.join((f'U{i + 1}' for i in group)) + '}' for group in clusters]
        current = [[0 if a == b else max((sim[i][j] for i in clusters[a] for j in clusters[b])) for b in range(len(clusters))] for a in range(len(clusters))]
        print(f'\nМатрица сходства кластеров')
        table(current, names, names)
        if len(clusters) < 2:
            print('Остался один кластер.')
            break
        value, a, b = max(((current[a][b], -a, -b) for a in range(len(clusters)) for b in range(a + 1, len(clusters))))
        a, b = (-a, -b)
        print(f'Максимум: {names[a]} и {names[b]}, сходство {fmt(value)}')
        if value < threshold:
            print(f'{fmt(value)} < {fmt(threshold)}: объединение прекращаем.')
            break
        print(f'{fmt(value)} >= {fmt(threshold)}: объединяем.')
        for c in range(len(clusters)):
            if c not in (a, b):
                print(f'  Сходство с {names[c]} = max({fmt(current[a][c])}, {fmt(current[b][c])}) = {fmt(max(current[a][c], current[b][c]))}')
        clusters[a] = sorted(clusters[a] + clusters[b])
        del clusters[b]
        step += 1
    print('\nОтвет:')
    for group in clusters:
        print('  ' + ', '.join((f'U{i + 1}' for i in group)))
if __name__ == '__main__':
    run()
