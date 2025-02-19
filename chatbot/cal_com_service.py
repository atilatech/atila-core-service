import requests
import pytz
from datetime import datetime, timedelta
from chatbot.models import ServiceBooking, ServiceProvider


class CalComService:
    BASE_URL = "https://api.cal.com/v2"
    RESERVATION_DURATION = 10  # minutes

    API_VERSIONS = {
        "slots": "2024-09-04",
        "bookings": "2024-08-13",
        "slots/reservations": "2024-09-04"
    }

    def _get_headers(self, endpoint: str, api_key: str):
        return {
            "Authorization": f"Bearer {api_key}",
            "cal-api-version": self.API_VERSIONS.get(endpoint, "2024-09-04"),
            "Content-Type": "application/json"
        }

    def get_available_slots(self, provider: ServiceProvider, days_ahead: int = 7) -> dict:
        """
        Fetch available slots for a given service provider from Cal.com.
        """
        end_point = "slots"
        current_date = datetime.now().date()
        end_date = current_date + timedelta(days=days_ahead)

        url = f"{self.BASE_URL}/{end_point}"
        query_params = {
            "start": current_date.isoformat(),
            "end": end_date.isoformat(),
            "eventTypeId": provider.cal_com_event_type_id,
            "timeZone": "America/Toronto"
        }

        try:
            response = requests.get(url,
                                    headers=self._get_headers(end_point, provider.cal_com_api_key),
                                    params=query_params)
            response.raise_for_status()
            # Check if the API response is successful
            if response.status_code != 200:
                return {"error": response.json()}
            return response.json().get("data", {})
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def reserve_a_slot(self, booking: ServiceBooking, reservation_duration: int = RESERVATION_DURATION) -> dict:
        """
        Reserve a specific slot for a given event type.
        """
        endpoint = "slots/reservations"
        url = f"{self.BASE_URL}/{endpoint}"
        provider = booking.provider

        # Ensure slot_start is in UTC
        slot_start_utc = booking.start_date.astimezone(pytz.utc)

        payload = {
            "eventTypeId": int(provider.cal_com_event_type_id),
            "slotStart": slot_start_utc.isoformat(),
            "reservationDuration": reservation_duration,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(endpoint, provider.cal_com_api_key)
            )
            response.raise_for_status()
            if response.status_code != 201:
                return {"error": response.json()}
            return response.json().get("data", {})
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_reservation(self, booking: ServiceBooking) -> dict:
        """
        Delete a specific reservation by UID.
        """
        endpoint = "slots/reservations"
        url = f"{self.BASE_URL}/{endpoint}/{booking.reservation_uid}"
        provider = booking.provider

        try:
            response = requests.request("DELETE",
                                        url,
                                        headers=self._get_headers(endpoint,
                                                                  provider.cal_com_api_key))
            response.raise_for_status()

            if response.status_code != 200:
                return {"error": response.json()}

            return {"message": "Reservation successfully deleted"}

        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def book_a_slot(self, service_booking: ServiceBooking) -> dict:
        """
        Send a booking request to Cal.com.
        """
        end_point = "bookings"
        client = service_booking.client
        provider = service_booking.provider
        start_date = service_booking.start_date.astimezone(pytz.utc)

        payload = {
            "start": start_date.isoformat(),
            "eventTypeId": int(provider.cal_com_event_type_id),
            "attendee": {
                "name": client.name,
                "email": client.email,
                "timeZone": "America/Toronto",
                "phoneNumber": client.phone_number,
                "language": "en"
            },
        }

        try:
            url = f"{self.BASE_URL}/{end_point}"
            response = requests.post(url,
                                     json=payload,
                                     headers=self._get_headers(end_point, provider.cal_com_api_key))
            response.raise_for_status()
            # Check if the API response is successful
            if response.status_code != 201:
                return {"error": response.json()}
            return response.json().get("data", {})
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
