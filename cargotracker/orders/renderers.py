import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList

from orders.models import Order


class OrderJSONRenderer(JSONRenderer):
    """
    Properly return results for querying for Orders.
    """
    charset = "utf-8"

    def format_order_detail_view_response(self, data):
        """
        Return appropriate responses for the Order detail views.
        """

        order_instance = Order.objects.get(id=data.get('id'))

        cargo_instance = order_instance.cargo

        order_price = data.get("price")
        data['price'] = f"{order_price:.3f}"
        data['tracking_id'] = str(order_instance.tracking_id)

        cargo_weight = cargo_instance.weight


        cargo_data = {
            "sender": cargo_instance.sender.email,
            "recepient": cargo_instance.recepient.email,
            "booking_agent": cargo_instance.booking_agent.email,
            "clearing_agent": cargo_instance.clearing_agent.email,
            "destination": cargo_instance.destination.city,
            "weight": f"{cargo_weight:.3f}"
        }

        status = order_instance.get_status_display().title()

        data['status'] = status
        data['cargo'] = cargo_data

        return data

    def format_order_list_view(self, return_list):
        """
        Define responses when Users query for multpile Order objects.
        """

        for order in return_list:
            self.format_order_detail_view_response(order)

        return return_list


    def render(self, data, media_type=None, renderer_context=None):

        if isinstance(data, dict):
            if "error" in str(data).lower():
                return super().render(data)
            if data.get("data"):
                payload = self.format_order_detail_view_response(data.get("data"))
                return json.dumps({"data": payload})

            payload = self.format_order_detail_view_response(data)
            return json.dumps({"data": payload})

        if isinstance(data, list):
            payload = self.format_order_list_view(data)
            return json.dumps({"data": payload})


        return json.dumps(data)
