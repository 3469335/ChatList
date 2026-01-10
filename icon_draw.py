from PIL import Image, ImageDraw
import math

def draw_icon(size):
    """Рисует восьмиконечную золотистую звезду на фиолетовом фоне."""
    # Создаем RGB изображение с фиолетовым фоном
    purple_bg = (138, 43, 226)  # BlueViolet - фиолетовый фон
    img = Image.new("RGB", (size, size), purple_bg)
    draw = ImageDraw.Draw(img)
    
    # Центр изображения
    center_x = size // 2
    center_y = size // 2
    
    # Радиусы для внешних и внутренних точек звезды
    padding = int(size * 0.15)  # Отступ от краёв
    outer_radius = (size // 2) - padding  # Внешний радиус (концы лучей)
    inner_radius = outer_radius * 0.4  # Внутренний радиус (впадины между лучами)
    
    # Золотистый цвет (Gold)
    gold_color = (255, 215, 0)
    
    # Создаём точки для восьмиконечной звезды
    # Восьмиконечная звезда: 8 внешних точек и 8 внутренних точек
    points = []
    num_points = 8
    
    for i in range(num_points * 2):
        # Угол в радианах
        angle = (i * math.pi) / num_points - math.pi / 2  # Начинаем сверху
        
        # Чередуем внешний и внутренний радиус
        if i % 2 == 0:
            radius = outer_radius
        else:
            radius = inner_radius
        
        # Вычисляем координаты точки
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    
    # Рисуем звезду
    draw.polygon(points, fill=gold_color, outline=gold_color)
    
    return img

# Размеры иконки
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = [draw_icon(s) for s, _ in sizes]

# Изображения уже в RGB режиме, просто убеждаемся
rgb_icons = []
for icon in icons:
    # Убеждаемся, что изображение в RGB режиме (не палитра)
    if icon.mode != "RGB":
        rgb_img = icon.convert("RGB")
    else:
        rgb_img = icon
    rgb_icons.append(rgb_img)

# Сохранение с явным указанием формата и цветов
# ВАЖНО: Изображения уже в RGB режиме с фиолетовым фоном, что гарантирует
# сохранение цветов и избегает автоматической конвертации в градации серого
try:
    rgb_icons[0].save(
        "app.ico",
        format="ICO",
        sizes=sizes,
        append_images=rgb_icons[1:]
    )
    print("[OK] Иконка 'app.ico' создана!")
    print("   Дизайн: восьмиконечная золотистая звезда на фиолетовом фоне")
    print("   Цвета: фиолетовый фон (BlueViolet), золотистая звезда (Gold)")
except Exception as e:
    print(f"[ERROR] Ошибка при сохранении: {e}")
    # Альтернативный способ - сохранить каждое изображение отдельно
    print("Попытка альтернативного метода сохранения...")
    rgb_icons[0].save("app.ico", format="ICO")
    print("[OK] Иконка 'app.ico' создана (только один размер)")