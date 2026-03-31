import requests

class PlantNetAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://my-api.plantnet.org/v2/identify/all"

    def identify_plant(self, image_path):
        try:
            with open(image_path, "rb") as img_file:
                files = {
                    "images": img_file
                }

                params = {
                    "api-key": self.api_key,
                    "organs": ["leaf"]
                }

                response = requests.post(self.url, files=files, params=params)
                data = response.json()

                if "results" not in data or len(data["results"]) == 0:
                    return {
                        "plant_name": "Unknown",
                        "confidence": 0
                    }

                best = data["results"][0]

                plant_name = best["species"]["scientificNameWithoutAuthor"]
                confidence = best["score"]

                return {
                    "plant_name": plant_name,
                    "confidence": round(confidence * 100, 2)
                }

        except Exception as e:
            return {
                "plant_name": "Error",
                "confidence": 0,
                "error": str(e)
            }
