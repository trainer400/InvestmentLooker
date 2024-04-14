from coinbase.rest import RESTClient


def get_current_price(client: RESTClient, coin_name: str):
    data = client.get_product(product_id=coin_name)
    return float(data["price"])
