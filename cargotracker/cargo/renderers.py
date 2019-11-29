import json

from rest_framework.renderers import JSONRenderer

from authentication.models import User


class CargoJSONRenderer(JSONRenderer):
    """
    Properly render responses of Cargo objects.
    """

    charset = "utf-8"

    def format_cargo_detail_view_response(self, data):
        """
        Return appropriate responses for the Cargo detail views.
        """

        clearing_agent_id = data.get("clearing_agent")
        clearing_agent = User.objects.get_user(id=clearing_agent_id)

        booking_agent_id = data.get("booking_agent")
        booking_agent = User.objects.get_user(id=booking_agent_id)

        sender_id = data.get("sender")
        sender = User.objects.get_user(id=sender_id)

        data['booking_agent'] = booking_agent.email
        data['sender'] = sender.email
        data['clearing_agent'] = clearing_agent.email

        return data

    def format_cargo_list_view(self, return_list):
        """
        Whenever we have more than one Cargo to return, ensure it is properly formated.
        """

        for cargo in return_list:
            self.format_cargo_detail_view_response(cargo)
        
        return return_list





    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, dict):
            if "error" in str(data).lower():
                    return super().render(data)
            if data.get("data"):
                payload = self.format_cargo_detail_view_response(data.get("data"))
                return json.dumps({"data": payload})

            payload = self.format_cargo_detail_view_response(data)
            return json.dumps({"data": payload})

        if isinstance(data, list):
            payload = self.format_cargo_list_view(data)
            return json.dumps({"data": payload})


        return json.dumps(data)
