"""
Скрипт для создания инсталлятора Inno Setup
Автоматически подставляет версию из version.py
"""
import os
import sys
import subprocess
import version

def create_installer():
    """Создать инсталлятор с помощью Inno Setup"""
    app_version = version.__version__
    exe_name = f"ChatList-v{app_version}.exe"
    
    print("=" * 50)
    print("ChatList - Создание инсталлятора")
    print("=" * 50)
    print(f"\nВерсия приложения: {app_version}")
    print()
    
    # Проверка наличия Inno Setup
    iscc_path = None
    
    # Сначала проверяем PATH
    try:
        result = subprocess.run(['iscc', '/?'], 
                              capture_output=True, 
                              timeout=5)
        iscc_path = 'iscc'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Пробуем найти в стандартных местах установки
        standard_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe",
        ]
        
        for path in standard_paths:
            if os.path.exists(path):
                iscc_path = path
                break
    
    if not iscc_path:
        print("Ошибка: Inno Setup не найден!")
        print("Пожалуйста, установите Inno Setup:")
        print("1. Скачайте с: https://jrsoftware.org/isdl.php")
        print("2. Установите Inno Setup")
        print("3. Добавьте его в PATH или запустите скрипт снова")
        print("   (скрипт автоматически найдет Inno Setup в стандартных местах)")
        return False
    
    # Проверка наличия собранного исполняемого файла
    exe_path = os.path.join("dist", exe_name)
    if not os.path.exists(exe_path):
        print(f"Ошибка: Исполняемый файл не найден!")
        print(f"Ожидается: {exe_path}")
        print("\nСначала выполните сборку приложения: build.bat")
        return False
    
    # Чтение шаблона и замена версии
    template_path = "setup.iss.template"
    if not os.path.exists(template_path):
        print(f"Ошибка: Шаблон {template_path} не найден!")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Замена версии в шаблоне
    content = content.replace('{{VERSION}}', app_version)
    # Замена AppId плейсхолдера на реальный AppId (экранируем фигурные скобки для Inno Setup)
    content = content.replace('APPID_PLACEHOLDER', '{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}')
    
    # Сохранение setup.iss
    with open('setup.iss', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Создан setup.iss с версией", app_version)
    
    # Создание директории для инсталлятора
    if not os.path.exists("installer"):
        os.makedirs("installer")
    
    print("\nКомпиляция инсталлятора...")
    
    # Компиляция инсталлятора
    try:
        result = subprocess.run([iscc_path, 'setup.iss'], 
                              check=True,
                              capture_output=True,
                              text=True)
        print(result.stdout)
        
        installer_name = f"ChatList-Setup-{app_version}.exe"
        installer_path = os.path.join("installer", installer_name)
        
        if os.path.exists(installer_path):
            print("\n" + "=" * 50)
            print("Инсталлятор успешно создан!")
            print(f"Файл: {installer_path}")
            print("=" * 50)
            return True
        else:
            print("\nОшибка: Инсталлятор не был создан!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\nОшибка при компиляции инсталлятора!")
        print(e.stderr)
        return False

if __name__ == "__main__":
    success = create_installer()
    sys.exit(0 if success else 1)
