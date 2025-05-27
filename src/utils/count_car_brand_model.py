import json

def count_brands_and_models(file_path):
    """
    Counts the total number of car brands and models from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        tuple: A tuple containing (number_of_brands, number_of_models).
               Returns (0, 0) if the file is not found or is empty/malformed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        brands_data = data.get('brands', {})
        num_brands = len(brands_data)
        num_models = 0

        for models_list in brands_data.values():
            num_models += len(models_list)

        return num_brands, num_models

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return 0, 0
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Check file format.")
        return 0, 0
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 0, 0

if __name__ == "__main__":
    json_file_path = 'data/car_data.json'
    num_brands, num_models = count_brands_and_models(json_file_path)

    if num_brands > 0 or num_models > 0:
        print(f"Total number of brands: {num_brands}")
        print(f"Total number of models: {num_models}")