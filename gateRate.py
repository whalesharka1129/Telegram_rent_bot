import requests

def convert_usd_to_eth(amount_usd):
    url = "https://rest.coinapi.io/v1/exchangerate/ETH/USD"
    headers = {
        "X-CoinAPI-Key": "D5404F1D-AF0E-4548-9CB5-635B7E2FE69A"
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    eth_rate = data['rate']
    amount_eth = float(amount_usd) / eth_rate
    formatedAmount_Eth = "{:.3f}".format(amount_eth)
    return formatedAmount_Eth
print(convert_usd_to_eth(200))