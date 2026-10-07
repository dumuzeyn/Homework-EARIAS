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

def similarities(vectors):
    mode = number('Сходство: 1 — ввод, 2 — косинус из оценок', 1, 2, True)
    n = len(vectors)
    result = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if mode == 1:
                value = number(f'Сходство {i + 1} и {j + 1}', 0, 1)
            else:
                print(f'Пара {i + 1}, {j + 1}:')
                value = cosine(vectors[i], vectors[j], True)
                value = 0 if value is None else value
            result[i][j] = result[j][i] = value
    return result

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
    target = number('Пользователь для расчёта (0 — все)', 0, len(data[0]), True)
    threshold = number('Минимальное сходство товаров', 0, 1)
    neighbors = number('Максимум похожих товаров K', 1, integer=True)
    count = number('Количество рекомендаций', 1, integer=True)
    print('\nМатрица предпочтений')
    table(data, [f'P{i + 1}' for i in range(len(data))], [f'U{j + 1}' for j in range(len(data[0]))])
    print('\nМатрица сходства товаров')
    sim = similarities(data)
    table(sim, [f'P{i + 1}' for i in range(len(data))], [f'P{i + 1}' for i in range(len(data))])
    targets = range(len(data[0])) if target == 0 else [target - 1]
    for a in targets:
        print(f'\nРекомендации U{a + 1}')
        if not any((row[a] for row in data)):
            popular(data, count)
            continue
        predictions = []
        for i, row in enumerate(data):
            if row[a] != 0:
                print(f'  P{i + 1}: уже оценён — пропускаем')
                continue
            candidates = [j for j in range(len(data)) if data[j][a] != 0 and j != i and (sim[i][j] > 0) and (sim[i][j] >= threshold)]
            candidates.sort(key=lambda j: (-sim[i][j], j))
            candidates = candidates[:neighbors]
            print(f'  P{i + 1}: подходящие товары', [f'P{j + 1}' for j in candidates])
            numerator, denominator = (0.0, 0.0)
            for j in candidates:
                term = data[j][a] * sim[i][j]
                numerator += term
                denominator += abs(sim[i][j])
                print(f'    P{j + 1}: {fmt(data[j][a])}*{fmt(sim[i][j])} = {fmt(term)}')
            if denominator == 0:
                print('    Знаменатель равен нулю; прогноз недоступен')
                continue
            raw = numerator / denominator
            prediction = max(0, min(maximum, raw))
            print(f'    Прогноз = {fmt(numerator)}/{fmt(denominator)} = {fmt(raw)}')
            predictions.append((prediction, i))
        predictions.sort(key=lambda x: (-x[0], x[1]))
        for prediction, i in predictions[:count]:
            print(f'Ответ U{a + 1}: рекомендовать P{i + 1}, прогноз {fmt(prediction)}')
        if not predictions:
            print('Рекомендаций нет: нет доступного прогноза для неоценённых товаров.')
if __name__ == '__main__':
    run()
