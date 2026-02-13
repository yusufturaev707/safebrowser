"""
API Client - Server bilan aloqa qilish uchun
"""
import requests
from typing import Optional, Dict, Any
from utils.logger import error


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
        if response.status_code in [400, 401, 404, 405]:
            return {
                "status": False,
                "message": f"{response.json().get('message', response.status_code)}"
            }

        try:
            return {"status": True, "data": response.json()}
        except ValueError:
            return {"status": False, "message": "JSON parse xatoligi"}

    def load_tests(self) -> Dict[str, Any]:
        """Testlar ro'yxatini yuklash"""
        result = self.get("load-tests/")
        print(result)
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
        return result

    def send_bulk_warning(self, exam_key: str, imei: str, warning_type: str,
                          description: str, confidence: float,
                          ip_address: str, mac_address: str) -> Dict[str, Any]:
        """
        Bulk warning API ga ogohlantirish yuborish

        Returns:
            {status: True, task_id: "..."} yoki {status: False, message: "..."}
        """
        try:
            result = self.post(
                "bulk-send-warning-notification/",
                json={
                    "warnings":[
                        {
                            "exam_key": exam_key,
                            "imei": imei,
                            "warning_type": warning_type,
                            "description": description,
                            "confidence": confidence,
                            "ip_address": ip_address,
                            "mac_address": str(mac_address).upper()
                        }
                    ]
                }
            )
            if result.get("status"):
                data = result.get("data", {})
                task_id = data.get("task_id")
                return {"status": True, "task_id": task_id}
            return result
        except Exception as e:
            error(f"Send bulk warning error: {e}")
            return {"status": False, "message": str(e)}

    def check_warning_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Bulk warning task statusini tekshirish

        Returns:
            {status: True, data: {state: "SUCCESS/PENDING/STARTED/FAILURE", ...}}
        """
        return self.get(f"bulk-warning-task-status/{task_id}/")
