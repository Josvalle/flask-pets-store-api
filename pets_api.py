from flask import Flask,request,Response,jsonify
from pets_database_manager import User, Products,ProductCart,InvoiceProduct, Invoices
from authenticator import JWT_Manager, admin_only 
from cache_manager import CacheManager, check_cache

app = Flask(__name__)

jwt_manager = JWT_Manager()
user = User()
products = Products()
product_cart = ProductCart()
invoices = Invoices()
invoices_products = InvoiceProduct()
cache = CacheManager('PLACEHOLDER','PLACEHOLDER','PLACEHOLDER')


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() 
    if(data.get('username') == None or data.get('password') == None):
        return Response(status=400)
    else:
        result = user.insert_user(data.get('username'), data.get('password'))
        user_id = result[0]
        role = result[1]

        token = jwt_manager.encode({'id':user_id, 'role': role})
        
        return jsonify(token=token)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  
    if(data.get('username') == None or data.get('password') == None):
        return Response(status=400)
    else:
        result = user.get_user(data.get('username'), data.get('password'))

        if(result == None):
            return Response(status=403)
        else:
            user_id = result[0]
            role = result[3]
            token = jwt_manager.encode({'id':user_id, 'role': role})
        
            return jsonify(token=token)

@app.route('/me')
def me():
    try:
        token = request.headers.get('Authorization')
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            user_id = decoded['id']
            role_value = decoded['role']
            user_value = user.get_user_by_id(user_id)
            return jsonify(id=user_id, username=user_value[1], role=role_value)
        else:
            return Response(status=403)
    except Exception as e:
        return Response(status=500)
    

@app.route('/user/modification', methods=['POST'])
@admin_only
def modify_user():
    try:
        data = request.get_json() 
        user.modify_user(int(data.get('user_id')),data.get('column'),data.get('new_value'))
        return jsonify('User modify', 200)
    except Exception as e:
        return Response(status=500)

@app.route('/user/delete', methods=['DELETE'])
@admin_only
def delete_users():
    try:
        data = request.get_json() 
        user.delete_user(data.get('user_id'))
        return jsonify('user delete', 200)
    except Exception as e:
        return Response(status=500)


@app.route('/products/new_product', methods =['POST'])
@admin_only
def add_new_product():
    try:
        data = request.get_json() 
        products.insert_new_product(data.get('name'),data.get('price'),data.get('entry_date'), data.get('quantity'))
        if cache.check_key('products'):
            cache.delete_data('products')
        return jsonify(f'product: {data.get('name')} add', 200)
    except Exception as e:
        return Response(status=500)

@app.route('/products/list')
@check_cache('products',False)
def show_list_products():
    try:
            result = products.show_products()
            print(type(result))
            cache.store_data("products",result)
            return jsonify(result), 200
            
    except Exception as e:
        print(e)
        return Response(status=500)

@app.route('/products/modification', methods=['POST'])
@admin_only
def modify_product():
    try:
        data = request.get_json() 
        products.modify_product (data.get('product_id'),data.get('column'),data.get('new_value'))
        if cache.check_key('products'):
            cache.delete_data('products')
        return jsonify(f'Products has been modified', 200)
    except Exception as e:
        return Response(status=500)

@app.route('/products/delete', methods=['DELETE'])
@admin_only
def delete_products():
    try:
        data = request.get_json() 
        products.delete_product (data.get('product_id'))
        if cache.check_key('products'):
            cache.delete_data('products')
        return jsonify(f'Product with ID: {data.get('product_id')} has been delete')
    except Exception as e:
        return Response(status=500)

@app.route('/cart/add',methods=['POST'])
def new_purchase():
    try:
        token = request.headers.get('Authorization')
        data = request.get_json()
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            user_id = decoded['id']
            product_id = data.get('product_id')
            quantity_of_product = data.get('quantity_of_product')
            add_product = product_cart.insert_new_product_to_cart(user_id,product_id,quantity_of_product)
            
            if add_product == True:
                if cache.check_key(user_id):
                    cache.delete_data(user_id)
                return jsonify('Product add to cart succesfully', 200)
            elif add_product == False:
                return jsonify({"error":'Stock for  product is lower that quantity need it '}), 409
        else:
            return Response(status=403)
    except Exception as e:
        return Response(status=500)

@app.route('/cart/remove/product',methods=['DELETE'])
def remove_product_from_cart():
    try:
        token = request.headers.get('Authorization')
        data = request.get_json()
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            user_id = decoded['id']
            product_id = data.get('product_id')
            product_cart.remove_product_from_cart(user_id,product_id)
            if cache.check_key(user_id):
                cache.delete_data(user_id)
            return jsonify('item remove correctly succesfully ', 200)
        else:
            return Response(status=403)
    except Exception as e:
        return Response(status=500)


@app.route('/cart/modify/amount',methods=['POST'])
def modify_amount_product():
    try:
        token = request.headers.get('Authorization')
        data = request.get_json()
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            user_id = decoded['id']
            product_id = data.get('product_id')
            new_amount = data.get('new_amount')
            product_cart.modify_amount(user_id,product_id,new_amount)
            if cache.check_key(user_id):
                cache.delete_data(user_id)
            return jsonify('Product has been modified to cart succesfully', 200)
        else:
            return Response(status=403)
    except Exception as e:
        return Response(status=500)

@app.route('/cart')
@check_cache('cart',True)
def show_cart_items():
    try:
        token = request.headers.get('Authorization')
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            user_id = decoded['id']
            print('antes de la funsion')
            cart_information = product_cart.show_cart_information(user_id)
            cache.store_data(user_id, cart_information)
            return jsonify(cart_information),200
        else:
            return Response(status=403)
    except Exception as e:
        return Response(status=500)

@app.route('/complete/purchase', methods=['POST'])
def complete_purhcase_and_cart():
    try:
        token = request.headers.get('Authorization')
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            user_id = decoded['id']
            cache_key_invoice = f'Invoice_{user_id}'
            complete_cart = invoices.create_invoice(user_id)
            invoice_id = complete_cart
            create_invoice_detail =  invoices_products.create_detail_invoice(invoice_id)
            if cache.check_key(user_id):
                cache.delete_data(user_id)
            if cache.check_key(cache_key_invoice):
                cache.delete_data(cache_key_invoice)
            return jsonify({f"Success":"Your purchase is completed"}), 200
    except Exception as e:
        return Response(status=500)

@app.route('/me/invoices/detail')
def show_detail_invoice():
    data = request.get_json() 
    if data.get('invoice_id') == None:
        return Response(status=400)
    else:
        result_invoice = invoices_products.show_detail_invoice(data.get('invoice_id'))
        return jsonify(result_invoice),200
@app.route('/me/invoices')
@check_cache('Invoice',True)
def my_invoices():
    try:
        token = request.headers.get('Authorization')
        if(token is not None):
            token = token.replace("Bearer ","")
            decoded = jwt_manager.decode(token)
            user_id = decoded['id']
            cache_key_invoice = f'Invoice_{user_id}'
            invoices = Invoices.show_invoices_per_client(user_id)
            cache.store_data(cache_key_invoice,invoices)
            return jsonify(invoices, 200)
        else:
            return Response(status=403)
    except Exception as e:
        return Response(e,status=500)

@app.route('/invoices/modification', methods=['POST'])
@admin_only
def modify_invoice():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if (user_id is not None): 
            cache_key_invoice = f'Invoice_{user_id}'
            invoices.modify_invoice (data.get('invoice_id'),data.get('column'),data.get('new_value'))
            if cache.check_key(cache_key_invoice):
                cache.delete_data(cache_key_invoice)
            return jsonify(f'The invoice with id {data.get('invoice_id')} has been modified ', 200)
        else:
            return jsonify({"error":"missing User_id"})
    except Exception as e:
        return Response(e,status=500)

@app.route('/invoices/delete', methods=['DELETE'])
@admin_only
def delete_invoice():
    try:
        user_id = data.get('user_id')
        if (user_id is not None): 
            cache_key_invoice = f'Invoice_{user_id}'
            data = request.get_json() 
            invoices.delete_invoice (data.get('invoice_id'))
            if cache.check_key(cache_key_invoice):
                cache.delete_data(cache_key_invoice)
            return jsonify(f'The invoice with id {data.get('invoice_id')} has been Delete ', 200)
        else:
            return jsonify({"error":"missing User_id"})
    except Exception as e:
        return Response(e,status=500)

if __name__ == "__main__":
    
    app.run(host='localhost', debug=True)