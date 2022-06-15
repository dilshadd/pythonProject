import requests

url = "http://allotment-request.herokuapp.com/headout/allotments/"

payload = {
        "ticket_id": "HIT5121",
        "issued_by": "megha.sen",
        "tgid": 11015,
        "tid": 20700,
        "variant_name": "Skip the Line Ticket (20700)",
        "sp_name": "Mont St Michel Abbey (1889)",
        "currency": "EUR",
        "pax_type": "Adult",
        "quantity": 100,
        "net_price_per_ticket": 12.0,
        "total_net_price": 0,
        "redemption_cost": 0,
        "loss_liability_per_ticket": 0,
        "payment": "Payment by Card",
        "payment_type": "Prepaid",
        "order_fee": 0,
        "invoice": "",
        "due_date": "2020-11-17",
        "validity_date": "2020-11-30",
        "validity_type": "Flexible Entry Tickets",
        "Comments": "TEST TEST . Please Ignore"
    }
files = [

]
headers = {
  'Authorization': 'Token 821a00442ce835c11f4b6ad898e4d9f4550fcb51'
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))

