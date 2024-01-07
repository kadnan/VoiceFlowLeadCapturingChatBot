import json, csv

from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)


def search_properties(search_type, location_id, min_price, max_price, min_bedrooms, property_type):
    property_types = [
        'semi-detached',
        'terraced',
        'bungalows',
        'flats-apartments',
    ]
    search_types = [
        'to-rent',
        'for-sale',
    ]

    headers = {
        'authority': 'www.onthemarket.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'no-cache',
        'content-type': 'application/json; charset=utf-8',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://www.onthemarket.com/to-rent/property/london/?max-price=1250&min-bedrooms=1&min-price=100',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    params = {
        'search-type': search_type,
        'location-id': location_id,
        'min-price': min_price,
        'max-price': max_price,
        'min-bedrooms': min_bedrooms,
        'prop-types': property_type,
    }
    r = requests.get('https://www.onthemarket.com/async/search/properties/', params=params, headers=headers)
    r.raise_for_status()
    data = r.json()['properties']
    return data


@app.route('/find', methods=['POST'])
def find_properties():
    refined_properties = []
    return_msg = {}
    try:
        form_data = request.form.to_dict()

        properties = search_properties(
            search_type=form_data['search-type'],
            location_id=form_data['location-id'],
            min_price=int(form_data['min-price']),
            max_price=int(form_data['max-price']),
            min_bedrooms=int(form_data['min-bedrooms']),
            property_type="flats-apartments"
        )

        for property in properties:
            if 'display_address' in property:
                address = property['display_address']
                price = property['price']
                property_link = property['property-link']
                image = property['cover-images']['default']
                refined_properties.append(
                    {'title': address,
                     'price': price,
                     'url': 'https://www.onthemarket.com{}'.format(property_link),
                     'image': image,
                     })
        return_msg = {'status': 'OK', 'msg': refined_properties}
        print(return_msg)
    except Exception as ex:
        return_msg = {'status': 'FAIL', 'msg': str(ex)}
    finally:
        return jsonify(data=return_msg)


@app.route('/store', methods=['POST'])
def store_client_record():
    record = []
    form_data = request.form.to_dict()
    client_name = form_data['name']
    client_phone = form_data['phone']
    client_selected_property = '"' + form_data['selected_property'] + '"'
    record.append(client_name)
    record.append(client_phone)
    record.append(client_selected_property)
    with open('clients.csv', 'a+', encoding='utf8', newline='') as f:
        f.write(','.join(record) + "\n")
    return jsonify(status="OK")


@app.route('/leads', methods=['GET'])
def show_leads():
    with open('clients.csv', 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        data = list(reader)
        return render_template('leads.html', data=data)


@app.route('/demo', methods=['GET'])
def demo():
    return render_template('demo.html')


if __name__ == '__main__':
    app.run(debug=True)
