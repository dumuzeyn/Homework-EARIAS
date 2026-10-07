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

def mean(values):
    rated = [x for x in values if x != 0]
    return sum(rated) / len(rated) if rated else None

def popular(matrix, count):
    print('Средние рейтинги:')
    ranking = []
    for i, row in enumerate(matrix):
        values = [x for x in row if x]
        rating = mean(row)
        if rating is not None:
            print(f'  P{i + 1}: {fmt(sum(values))}/{len(values)} = {fmt(rating)}')
            ranking.append((rating, i))
        else:
            print(f'  P{i + 1}: оценок нет, товар исключён.')
    ranking.sort(key=lambda x: (-x[0], x[1]))
    for rating, i in ranking[:count]:
        print(f'Рекомендовать P{i + 1}; средний рейтинг {fmt(rating)}')
    if not ranking:
        print('Рекомендаций нет: ни один товар не оценён.')

def run():
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('\nВвод прерван.')
    except OverflowError:
        print('Числа слишком велики.')

def main():
    data, maximum = matrix_input()
    n = len(data[0])
    while True:
        text = input('Исключить пользователей (номера через пробел, 0 — никого): ').strip()
        try:
            values = [int(x) for x in text.split()]
            if not values or (0 in values and values != [0]):
                raise ValueError
            excluded = set() if values == [0] else {x - 1 for x in values}
            if any((x < 0 or x >= n for x in excluded)):
                raise ValueError
            break
        except ValueError:
            print('Неверные номера.')
    target = number('Пользователь для расчёта (0 — все)', 0, n, True)
    neighbors = number('Максимум ближайших соседей K', 1, integer=True)
    count = number('Количество рекомендаций', 1, integer=True)
    threshold = number('Минимальное сходство соседей', 0, 1)
    active = [j for j in range(n) if j not in excluded]
    print('\nМатрица предпочтений')
    table(data, [f'P{i + 1}' for i in range(len(data))], [f'U{j + 1}' for j in range(n)])
    print('\nСходство пользователей')
    sim = [[0.0] * n for _ in range(n)]
    mode = number('Сходство: 1 — ввод, 2 — косинус из оценок', 1, 2, True)
    for p, a in enumerate(active):
        for b in active[p + 1:]:
            if mode == 1:
                value = number(f'Сходство U{a + 1} и U{b + 1}', 0, 1)
            else:
                print(f'U{a + 1} — U{b + 1}')
                value = cosine([row[a] for row in data], [row[b] for row in data], True)
                value = 0 if value is None else value
            sim[a][b] = sim[b][a] = value
    table([[sim[a][b] for b in active] for a in active], [f'U{j + 1}' for j in active], [f'U{j + 1}' for j in active])
    averages = [mean([row[j] for row in data]) for j in range(n)]
    print('\nСредние оценки пользователей без нулей')
    for j in active:
        values = [row[j] for row in data if row[j]]
        print(f'  U{j + 1}: ' + (f'{fmt(sum(values))}/{len(values)} = {fmt(averages[j])}' if values else 'оценок нет'))
    targets = active if target == 0 else [target - 1]
    for a in targets:
        print(f'\nРекомендации U{a + 1}')
        if a in excluded:
            print('Пользователь исключён из расчёта.')
            continue
        if averages[a] is None:
            popular(data, count)
            continue
        closest = [b for b in active if b != a and averages[b] is not None and (sim[a][b] > 0) and (sim[a][b] >= threshold)]
        closest.sort(key=lambda b: (-sim[a][b], b))
        closest = closest[:neighbors]
        print('Ближайшие соседи:', [f'U{b + 1} ({fmt(sim[a][b])})' for b in closest])
        predictions = []
        for i, row in enumerate(data):
            if row[a] != 0:
                print(f'  P{i + 1}: уже оценён — пропускаем')
                continue
            usable = [b for b in closest if row[b] != 0]
            numerator, denominator = (0.0, 0.0)
            for b in usable:
                term = (row[b] - averages[b]) * sim[a][b]
                numerator += term
                denominator += abs(sim[a][b])
                print(f'  P{i + 1}, U{b + 1}: ({fmt(row[b])}-{fmt(averages[b])})*{fmt(sim[a][b])} = {fmt(term)}')
            if denominator == 0:
                print(f'  P{i + 1}: у выбранных соседей нет оценки; прогноз недоступен')
                continue
            raw = averages[a] + numerator / denominator
            prediction = max(0, min(maximum, raw))
            print(f'  P{i + 1}: {fmt(averages[a])}+{fmt(numerator)}/{fmt(denominator)} = {fmt(raw)}; в шкале оценок {fmt(prediction)}')
            predictions.append((prediction, i))
        predictions.sort(key=lambda x: (-x[0], x[1]))
        for prediction, i in predictions[:count]:
            print(f'Ответ U{a + 1}: рекомендовать P{i + 1}, прогноз {fmt(prediction)}')
        if not predictions:
            print('Рекомендаций нет: нет доступного прогноза для неоценённых товаров.')
if __name__ == '__main__':
    run()
