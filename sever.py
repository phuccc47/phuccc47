from pprint import pprint 
import json
import requests
from bottle import debug, request, route, run
import random
import chatbot_res as cr
from openpyxl import Workbook
GRAPH_URL = "https://graph.facebook.com/v14.0/820259788937263/"
PAGE_TOKEN = "EAAHwre7Y8HYBALehAbYiwWiDqaZAaH9dVj1GcGZC7mR9lEF3bZAdwDyi68JkrrYjxX56ZC8vJ49ZAaGsT8pJ6Q1IeRgzSqiZCTS2K1MsPILFDvQZBQefB7ZB8B0303YfDOrbx2J99LAN41pN38iD2k6lrhuZC4hBxyayKTXIUu5kdqs839IZCO5noo"
img_response_links = [
	"https://img5.thuthuatphanmem.vn/uploads/2021/12/17/anh-hello-an-tuong-dep-nhat_020638880.jpg",
	"https://img5.thuthuatphanmem.vn/uploads/2021/12/17/anh-nen-hello-dep_020642646.png",
	"https://img5.thuthuatphanmem.vn/uploads/2021/12/17/hinh-anh-hello-de-thuong_020644850.jpg"
	
]

with open("items_data.json", "r", encoding="utf-8") as json_data:
	database = json.load(json_data)


wb = Workbook()
sheet = wb.active
sheet['A1']='Sản phẩm'
sheet['C1'] ='Thời gian'
sheet['D1'] ='Địa chỉ'
sheet['E1'] = 'Ngày đặt hàng'
sheet['B1'] = 'Số điện thoại'
sheet['F1'] = 'Tổng tiền'
status_code = -1 
user_info = {}
user_info['item'] = []
user_info['total_cost'] = 0

alphabet = ['A','B','C','D','E','F']

	
def send_to_messenger(ctx):
	url = "https://graph.facebook.com/v14.0/me/messages?access_token={0}".format(PAGE_TOKEN)
	response = requests.post(url, json=ctx)



def create_all_items_elements():
	all_items_list = []
	idx = 0
	for values in database.values():
		for value in values:
			a_dict = {}
			a_dict["title"] = value["name"]
			a_dict["image_url"] = value["image"]
			a_dict["subtitle"] = " Giá: {}Đ".format( value["price"])
			a_dict["buttons"] = [
				{
					"type": "postback",
					"payload": "/order_item_{}".format(value['id']),
					"title": "Đặt hàng"
				}
			]
			all_items_list.append(a_dict)
			idx += 1
			if idx == 10:
				return all_items_list
	return all_items_list

def get_item_value_by_payload(payload):
	for values in database.values():
		for value in values:
			if str(value['id']) == payload.split('_')[-1]:
				return value

def get_item_value_by_name(name):
	for values in database.values():
		for value in values:
			if value['name'] == name:
				return value


@route("/webhook", method=["GET", "POST"])
def bot_endpoint():
	if request.method.lower() == "get":
		verify_token = request.GET.get("hub.verify_token")
		print("Verifytoke:",verify_token)
		hub_challenge = request.GET.get("hub.challenge")
		url = "{0}subscribed_apps?subscribed_fields=messages&access_token={1}".format(GRAPH_URL, PAGE_TOKEN)
		print(url)
		response = requests.post(url)
		return hub_challenge
	else:
		global status_code
		global user_info

		body = json.loads(request.body.read())
		user_id = body["entry"][0]["messaging"][0]["sender"]["id"]
		page_id = body["entry"][0]["id"]
		pprint(body)
		ctx = {}
		if user_id != page_id:
			ctx["recipient"] = {"id":user_id}

		if "message" in body["entry"][0]["messaging"][0]:
			message = body["entry"][0]["messaging"][0]["message"]
			
			# sticker, image, gif
			if "attachments" in message:
				new_dict = {}
				new_dict["type"] = "image"
				random_link = random.choice(img_response_links)
				new_dict["payload"] = {"url":random_link}
				ctx["message"] = {"attachment":new_dict}
			# Regular text or icon
			elif "text" in message:
				text = message["text"]
				
				if status_code == -1:
					tag, _ = cr.classify(text)
					
					if tag != "ask_item" and tag != "order" and tag != "payment":
						ctx["message"] = {"text": cr.response(tag)}
						
					elif tag == "payment":
						small_ctx = ctx.copy()
						small_ctx["message"] = {"text": cr.response(tag)}
						response = send_to_messenger(small_ctx)

						status_code = 0
						ctx["message"] = {"text": "Số điện thoại của bạn là: (Ví dụ: 0944944691, +84944944691,...)"}
					else:
						small_ctx = ctx.copy()
						small_ctx["message"] = {"text": cr.response(tag)}
						response = send_to_messenger(small_ctx)

						new_dict = {}
						new_dict["type"] = "template"
						new_dict["payload"] = {"template_type":"generic", "elements":create_all_items_elements()}
						ctx["message"] = {"attachment":new_dict}
				else:
					if status_code == 0:
						try:
							phone = message['nlp']['entities']['wit$phone_number:phone_number'][0]['value']
							user_info['phone'] = phone
							status_code += 1
							ctx["message"] = {"text": "OK Mình đã ghi nhận số điện thoại của bạn. Tiếp theo cho mình xin thời gian bạn muốn nhận đồ nhé. (Ví dụ: 3am,3pm, 15:00,...)"}
						except KeyError:
							ctx["message"] = {"text": "Mình không thể nhận ra số điện thoại của bạn. Nhập lại giúp mình nhé"}
					elif status_code == 1:
						try:
							datatime = message['nlp']['entities']['wit$datetime:datetime'][0]['value']
							time =datatime.split('T')
							user_info['datetime'] = time[1]
							user_info['date'] = time[0]
							status_code += 1
							ctx["message"] = {"text": "Mình đã có thông tin về thời gian bạn muốn nhận đồ. Cuối cùng cho mình xin địa chỉ nhé. (Ví dụ: số 1, Võ Văn Ngân, TP.Thủ Đức,...)"}
						except KeyError:
							ctx["message"] = {"text": "Mình không biết bạn nhập mấy giờ luôn. Cho mình xin lại nhé!"}
					elif status_code == 2: 
						try: 
							location = message['nlp']['entities']['wit$location:location'][0]['value']
							user_info['location'] = location
							item_str = ''
							for i, item in enumerate(user_info['item']):
								item = user_info['item'][i]
	
								item_str += str(item) + '\n'
								item_str.replace('None'," ")
                                
							status_code =3
							
							ctx["message"] = {
							"text": 'Mình tổng kết lại nhé:\n*Đồ uống:\n'
								'{}*Số điện thoại: {}\n'
								'*Giờ lấy đồ: {}\n'
								'*Địa chỉ bạn nhập: {}\n'
								'*Tổng thiệt hại vị chi là: {} nha.'
								.format(
									item_str, 
									user_info['phone'], 
									user_info['datetime'],  
									user_info['location'], 
									user_info['total_cost']
									)
							}
							for count in range (6) :
								string = alphabet[count] +'2'
								if string[0] == "A":
									sheet[string] = item_str
								if string[0] == "B":
									sheet[string] = user_info['phone']
								if string[0] == "C":
									sheet[string] = user_info['datetime']
								if string[0] == "D":
									sheet[string] = user_info['location']
								if string[0] == "F":
									sheet[string] = user_info['total_cost']
								if string[0] == 'E':
									sheet[string] = user_info['date']
							wb.save('Chatbot.xlsx')

						except KeyError:
							ctx["message"] = {"text": "Địa chỉ bạn lạ quá . Cho mình xin lại nhé!"}

					else:
						user_info = {}
						user_info['item'] = []
						user_info['total_cost'] = 0
						ctx["message"] = {"text": "Phi vụ cũ của chúng ta xong rồi đó. Chúng ta làm đơn hàng mới thôi nhể."}
						
						status_code = -1
		# postback
		elif "postback" in body["entry"][0]["messaging"][0]:
			payload = body["entry"][0]["messaging"][0]["postback"]["payload"]

			if payload.startswith("/order_item"):
				value = get_item_value_by_payload(payload)
				user_info['item'].append(value["name"])
				user_info['total_cost'] += int(value["price"])

				ctx["message"] = {
					"attachment": {
						"type": "template",
						"payload": {
							"template_type": "generic",
							"elements": [
								{
									"title": "Bạn có muốn mua thêm sản phẩm không?",
									"buttons": [
										{
											"type": "postback",
											"payload": "/yes",
											"title": "OK"
										},
									  {
											"type": "postback",
											"payload": "/no",
											"title": "Không nha"
										},  
									]
								}
							]
						}
					}
				}
			elif payload.startswith("/no"):
				user_info['item'].append(None)
				ctx["message"] = {"text": "OK. Bạn có thể mua thêm đồ khác hoặc hú mình kiểu như \"Cho mình thanh toán cái\" để thanh toán nhé."}
			elif payload.startswith("/yes"):
				small_ctx = ctx.copy()
				small_ctx["message"] = {"text": "Mời chọn thêm ạ:"}
				response = send_to_messenger(small_ctx)
				new_dict = {}
				new_dict["type"] = "template"
				new_dict["payload"] = {"template_type":"generic", "elements":create_all_items_elements()}
				ctx["message"] = {"attachment":new_dict}
			
		# print("================================")
		print(ctx)
		response = send_to_messenger(ctx)
		return ""


debug(True)
run(reloader=True, port=8080)