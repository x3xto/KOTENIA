from PIL import Image
from pathlib import Path

def crop_image_by_coordinates(original_image_path: str, coordinates_data: dict, output_folder: str = "output/cropped_fragments") -> dict:
    cropped_image_paths = {}

    if not Path(original_image_path).is_file():
        print(f"[Cropper] Помилка: Оригінальний файл зображення не знайдено: {original_image_path}")
        return cropped_image_paths

    try:
        img = Image.open(original_image_path)
        img_width, img_height = img.size
    except Exception as e:
        print(f"[Cropper] Помилка відкриття оригінального зображення: {e}")
        return cropped_image_paths

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    if not isinstance(coordinates_data, dict):
        print("[Cropper] Помилка: Дані координат не є словником.")
        return cropped_image_paths

    for identifier_name, details in coordinates_data.items():
        if not (isinstance(details, dict) and
                all(k in details for k in ["x_min", "y_min", "x_max", "y_max"])):
            print(f"[Cropper] Попередження: Неповні або некоректні дані координат для '{identifier_name}'. Деталі: {details}. Пропускаємо.")
            continue
        try:
            padding = 25
            x_min = max(0, int(details["x_min"]) - padding)
            y_min = max(0, int(details["y_min"]) - padding)
            x_max = min(img_width, int(details["x_max"]) + padding)
            y_max = min(img_height, int(details["y_max"]) + padding)

            box = (x_min, y_min, x_max, y_max)

            if not (0 <= box[0] < box[2] <= img_width and \
                    0 <= box[1] < box[3] <= img_height):
                print(f"[Cropper] Попередження: Невалідні координати для '{identifier_name}': {box}. Розміри зображення: {img_width}x{img_height}. Пропускаємо.")
                continue
            
            print(f"[Cropper] Обрізаємо '{identifier_name}' за координатами: {box}")
            cropped_img = img.crop(box)
            
            safe_identifier_name = "".join(c if c.isalnum() else "_" for c in identifier_name)
            file_extension = ".jpg"
            
            cropped_image_filename = f"{safe_identifier_name}{file_extension}"
            cropped_image_save_path = Path(output_folder) / cropped_image_filename
            
            cropped_img.save(cropped_image_save_path)
            print(f"[Cropper] Фрагмент '{identifier_name}' збережено як: {cropped_image_save_path}")
            cropped_image_paths[identifier_name] = str(cropped_image_save_path)

        except ValueError:
            print(f"[Cropper] Помилка: Координати для '{identifier_name}' не є числовими. Пропускаємо.")
        except Exception as e:
            print(f"[Cropper] Помилка при обрізанні фрагмента '{identifier_name}': {e}")
            
    return cropped_image_paths