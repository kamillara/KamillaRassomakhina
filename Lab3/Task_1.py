total = 0   # сумма
count = 0   # количество

n = int(input("Введите число (0 - конец): "))
while n != 0:
    total = total + n
    count = count + 1
    n = int(input(""))

print("Сумма чисел: ", total)
print("Количество чисел: ", count)
