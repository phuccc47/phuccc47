
import requests
from bs4 import BeautifulSoup
import json

category_list = ['protein.html','energy-heathy.html','fatloss.html']
item= {}  
def get_data(rows_inserted) :
  for i in category_list:
    item_list=[]
    response = requests.get('https://www.thol.com.vn/' + i + '?product_list_limit=30')  
    #                       https://www.thol.com.vn/ protein.html ?product_list_limit=30
    # lấy link tương ứng với link mỗi trang sản phẩm

    soup = BeautifulSoup(response.content,"html.parser")
    # chuyển đổi nội dung
    
    titles = soup.findAll('li', class_='item product product-item')
    # lấy danh sách sản phẩm

    links = [link.find('a').attrs["href"] for link in titles]
    # lấy link cho từng thuộc tính attrs trong thẻ <a>

    for link in links:  
        one_item={}
        products = requests.get(link)
        # gán nội dung của trang qua biến products
        # https://www.thol.com.vn/ration-whey-protein-blend.html
        
        soup = BeautifulSoup(products.content, "html.parser")
        # từ biến products chuyển đổi nội dung
        
        title = soup.find("h1", class_="page-title").text.replace("\n","")
        # Tìm tên sản phẩm qua thẻ h1 với tên class = "page-title" 
       
        price = soup.find("span", class_="price").text.replace("₫","").replace(".","")
        price = price.replace(u'\xa0', u' ')
        # Tìm giá sản phẩm qua thẻ span với tên class="price" 
        rows_inserted += 1
        one_item['id'] = rows_inserted
        one_item['name'] = title

        one_item['price'] =price
        item_list.append(one_item)
        item['Category'] = item_list
        print(rows_inserted," record inserted.")
    return item

def main():
    rows_inserted = 0
    item = get_data(rows_inserted)
    with open('items_data.json', 'w+', encoding='utf-8') as f:
	    json.dump(item, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
	main()
    
    