import numpy as np

# Ваш массив координат latLng
latLng = np.array([
    (3, 41.054, 60.28133333333334, "3_Ulgnar"),
    # Добавьте остальные координаты сюда
])

# Заданная точка
target_point = (3, 41.054, 65.28133333333334, "3_Ulgnar")

# Преобразование элементов массива к числовым типам данных
latLng_numeric = latLng[:, 1:3].astype(float)
target_point_numeric = np.array(target_point[1:3], dtype=float)

# Вычислите расстояния между заданной точкой и всеми точками в массиве
distances = np.linalg.norm(latLng_numeric - target_point_numeric, axis=1)

# Найдите индекс ближайшей точки
closest_point_index = np.argmin(distances)

# Ближайшая точка
closest_point = latLng[closest_point_index]

print(f"Самая близкая точка: {closest_point[1:3]} с расстоянием {distances[closest_point_index]} и дополнительными данными: {closest_point[0]}")
