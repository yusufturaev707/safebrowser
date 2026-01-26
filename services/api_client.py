"""
API Client - Server bilan aloqa qilish uchun
"""
import requests
from typing import Optional, Dict, Any


class APIClient:
    """
    REST API client - server bilan aloqa
    """

    def __init__(self, base_url: str = None, timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout

    def get(self, endpoint: str, params: dict = None) -> Dict[str, Any]:
        """GET request"""
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {"status": False, "message": "Server javob bermadi (timeout)"}
        except requests.exceptions.RequestException as e:
            return {"status": False, "message": f"Ulanish xatoligi: {e}"}

    def post(self, endpoint: str, data: dict = None, json: dict = None) -> Dict[str, Any]:
        """POST request"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                data=data,
                json=json,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {"status": False, "message": "Server javob bermadi (timeout)"}
        except requests.exceptions.RequestException as e:
            return {"status": False, "message": f"Ulanish xatoligi: {e}"}

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Response'ni qayta ishlash"""
        if response.status_code in [500, 502]:
            return {
                "status": False,
                "message": f"Server xatoligi: {response.json().get('message', response.status_code)}"
            }
        if response.status_code in [400, 404, 405]:
            return {
                "status": False,
                "message": f"{response.json().get('message', response.status_code)}"
            }

        try:
            return { "status": True, "data": response.json()}
        except ValueError:
            return {"status": False, "message": "JSON parse xatoligi"}

    def load_tests(self) -> Dict[str, Any]:
        """Testlar ro'yxatini yuklash"""
        result = self.get("load-tests/")
        if result.get("status") == "success":
            return {
                "status": True,
                "result": result.get("data", []),
                "message": "Muvaffaqiyatli yuklandi"
            }
        return {
            "status": False,
            "result": [],
            "message": result.get("message", "Xatolik")
        }

    def verify_face(self, embedding: list) -> Dict[str, Any]:
        """Yuzni server orqali tekshirish"""
        return self.post(
            "users/face_identification/",
            json={"embedding": str(embedding)}
        )

    def check_pinfl(self, pinfl: str, test_key: str = None) -> Dict[str, Any]:
        params = {
            "imei": pinfl,
            "test_key": test_key,
        }
        result = self.get("check-candidate-exam/", params=params)

        if result.get("status") == True and result['data'].get("status") == "success":
            return {
                "status": True,
                "data": result['data'],
                "message": result['data'].get("message", "Muvaffaqiyatli")
            }

        return {
            "status": False,
            "data": None,
            "message": result.get("message", "Foydalanuvchi topilmadi")
        }
