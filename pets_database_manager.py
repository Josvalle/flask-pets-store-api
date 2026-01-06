from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, literal_column, and_
from sqlalchemy import insert, select, update,delete,func
from flask import jsonify

engine = create_engine('postgresql://postgres:PLACEHOLDER@******:5432/postgres')
metadata_obj = MetaData()


class User():
    def __init__(self):
        self.users_table = Table('users', metadata_obj, autoload_with=engine, schema='pets_store')
    
    
    def insert_user(self, username, password, ):
        stmt = insert(self.users_table).returning(self.users_table.c.id, self.users_table.c.role).values(username=username, password=password, role = 'client')
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()
        return result.all()[0]

    def get_user(self, username, password):
        stmt = select(self.users_table).where(self.users_table.c.username == username).where(self.users_table.c.password == password)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            users = result.all()

            if(len(users)==0):
                return None
            else:
                return users[0]

    def get_user_by_id(self, id):
        stmt = select(self.users_table).where(self.users_table.c.id == id)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            users = result.all()
            if(len(users)==0):
                return None
            else:
                return users[0]
    def modify_user(self, id, column, new_value ):
        try:
            column_modification = literal_column(column)
            modification = (update(self.users_table).where(self.users_table.c.id == id).values({column_modification: new_value}))
            with engine.begin() as conn:
                    result = conn.execute(modification)
                    
        except:
            return('Something when wrong!')
    

    def delete_user(self, id):
        try:
            delete_user = delete(self.users_table).where(self.users_table.c.id == id)
            with engine.begin() as conn:
                    result = conn.execute(delete_user)
                    return(print('user delete'))
                    
        except Exception as ex:
            print(ex)


class Products():
    def __init__(self):
        self.products_table = Table('products', metadata_obj, autoload_with=engine, schema='pets_store')
    
    def insert_new_product(self, name, price, entry_date, quantity):
        try:
            stmt = insert(self.products_table).values(name=name, price=price, entry_date = entry_date,  quantity = quantity)
            with engine.begin() as conn:
                result = conn.execute(stmt)
            #conn.commit()
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def show_products(self, id = None):
        
        try:
            if id != None:
                stmt = select(self.products_table).where(self.products_table.c.id == id)
                with engine.connect() as conn:
                    result = conn.execute(stmt)
                    conn.commit()
                return result
            else:
                    
                stmt = select(self.products_table) 
                with engine.begin() as conn:
                    query = conn.execute(stmt)
                    result = [dict(result._mapping) for result in query]
                return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def verify_available_stock(self, product):
        stock = select(self.products_table.c.quantity).where(self.products_table.c.id == product)
        with engine.connect() as conn:
                result = conn.execute(stock).scalar()
                conn.commit()
        return result
    

    def obtain_price_product(self, product_id, quantity_of_product):
        price = select(self.products_table.c.price).where(self.products_table.c.id == product_id)
        with engine.connect() as conn:
                result = conn.execute(price).scalar()
                conn.commit()
        
        total = result*quantity_of_product
        return int(total)
    
    def modify_product(self, id, column, new_value):
        try:
            column_modification = literal_column(column)
            modification = (update(self.products_table).where(self.products_table.c.id == id).values( {column_modification: new_value}))
            with engine.begin() as conn:
                    result = conn.execute(modification)
        except:
            return('Something when wrong!')

    def delete_product(self, id):
        try:
            delete_user = delete(self.products_table).where(self.products_table == id)
            with engine.begin() as conn:
                    result = conn.execute(delete_user)
                    
        except Exception as ex:
            print(ex)



class Cart():
    def __init__(self):
        self.cart_table = Table('carts', metadata_obj, autoload_with=engine, schema='pets_store' )

    def create_new_cart(self,user_id,):
        try:
            stmt = insert(self.cart_table).values(user_id=user_id, status = 'Active')
            with engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def check_if_user_as_active_car(self, user_id):
        try:
            
            status_cart = select(self.cart_table.c.status).where(and_(self.cart_table.c.user_id == user_id,self.cart_table.c.status == "Active" ))
            with engine.connect() as conn:
                    result = conn.execute(status_cart).scalar()
                    conn.commit()
                    print(result)
                    
            if result == None:
                
                return False
            elif result.strip().lower() == 'active':
                
                return True
            
            else:
                
                return False
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def obtain_cart_id(self, user_id):
        
        try:
            active_cart = self.check_if_user_as_active_car(user_id)
            
            if active_cart == True:
                cart_id = select(self.cart_table.c.id).where(and_(self.cart_table.c.user_id == user_id,self.cart_table.c.status == "Active" ))
            if active_cart == False:
                
                create_cart = self.create_new_cart(user_id)
                cart_id = select(self.cart_table.c.id).where(and_(self.cart_table.c.user_id == user_id,self.cart_table.c.status == "Active" ))
            
            with engine.connect() as conn:
                    result = conn.execute(cart_id).scalar()
                    conn.commit()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None

class ProductCart():
    def __init__(self):
        self.product_cart_table = Table('products_carts', metadata_obj, autoload_with=engine, schema='pets_store' )
        self.products_table = Products()
        self.cart_table = Cart()
    
    def insert_new_product_to_cart(self, user_id, product_id,quantity_of_product):
        try:
            available_product = self.products_table.verify_available_stock(product_id)
            
            if available_product > quantity_of_product:
                new_quantity = available_product - quantity_of_product
                cart_id = self.cart_table.obtain_cart_id(user_id)
                stmt = insert(self.product_cart_table).values(cart_id=cart_id, product_id=product_id, amount = quantity_of_product)
                update_product = (update(self.products_table.products_table).where(
                    self.products_table.products_table.c.id == product_id).values(quantity=new_quantity))
                with engine.begin() as conn:
                    conn.execute(stmt)
                    conn.execute(update_product)
                    return True
            else:
                return False
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def remove_product_from_cart(self,user_id,product_id):
        active_cart = self.cart_table.check_if_user_as_active_car(user_id)
        if active_cart == True:
            available_product = self.products_table.verify_available_stock(product_id)
            cart_id_query = select(self.cart_table.cart_table.c.id).where(
                self.cart_table.cart_table.c.user_id == user_id)
            with engine.begin() as conn:
                
                cart_id = conn.execute(cart_id_query).scalar()
                amount_query = select(self.product_cart_table.c.amount).where(
                and_(
                    self.product_cart_table.c.cart_id == cart_id, self.product_cart_table.c.product_id == product_id))
                amount = conn.execute(amount_query).scalar()
                new_quantity = available_product + amount
                delete_product_from_cart = delete(self.product_cart_table
                                            ).where(
                                                and_(self.product_cart_table.c.product_id == product_id,self.product_cart_table.c.cart_id == cart_id))
                update_product = (update(self.products_table.products_table).where(self.products_table.products_table.c.id == product_id).values(quantity=new_quantity))
            
                conn.execute(delete_product_from_cart)
                conn.execute(update_product)
            
        else:
            jsonify({"error":'Your purchase is already complete, please contact support for refound '}), 409
    
    def modify_amount(self,user_id,product_id,new_amount):
        cart_id_query = select(self.cart_table.cart_table.c.id).where(self.cart_table.cart_table.c.user_id == user_id)
        available_product = self.products_table.verify_available_stock(product_id)
        with engine.begin() as conn:
                
                cart_id = conn.execute(cart_id_query).scalar()
                amount_query = select(self.product_cart_table.c.amount).where(and_(
                self.product_cart_table.c.cart_id == cart_id, self.product_cart_table.c.product_id == product_id))

                amount = conn.execute(amount_query).scalar()
                if (amount-new_amount) <= 0:
                    return jsonify({"error":"If you want to reduce the amount to 0, please remove the product from the cart"}),400
                elif amount > new_amount:
                    update_stock = available_product + (amount-new_amount)
                    update_new_amount = (update(self.product_cart_table).where(and_(
                        self.product_cart_table.c.product_id == product_id,self.product_cart_table.c.cart_id == cart_id)).values(amount=new_amount))
                    update_product = (update(self.products_table.products_table).where(self.products_table.products_table.c.id == product_id).values(quantity=update_stock))
                    
                    conn.execute(update_new_amount)
                    conn.execute(update_product)
                elif amount < new_amount:
                    update_stock = available_product - (amount-new_amount)
                    update_new_amount = (update(self.product_cart_table).where(and_(
                        self.product_cart_table.c.product_id == product_id,self.product_cart_table.c.cart_id == cart_id)).values(amount=new_amount))
                    update_product = (update(self.products_table.products_table).where(self.products_table.products_table.c.id == product_id).values(quantity=update_stock))
                    
                    conn.execute(update_new_amount)
                    conn.execute(update_product)

    
    def show_cart_information(self,user_id):
        try:
            active_cart = self.cart_table.check_if_user_as_active_car(user_id)
            if active_cart == True:
                cart_id_query = select(self.cart_table.cart_table.c.id).where(self.cart_table.cart_table.c.user_id == user_id)
                with engine.begin() as conn:
                    cart_id = conn.execute(cart_id_query).scalar()
                    stmt = select(self.product_cart_table).where(self.product_cart_table.c.cart_id == cart_id)
                    query = conn.execute(stmt)
                    result = [dict(result._mapping) for result in query]
                return result
        except Exception as e:
            print(f"Error: {e}")
            return None

class InvoiceProduct():
    def __init__(self):
        self.invoices_products_table = Table('invoices_products', metadata_obj, autoload_with=engine, schema='pets_store' )
        self.product_cart_table = Table('products_carts', metadata_obj, autoload_with=engine, schema='pets_store' )
        self.invoice_table = Table('invoices', metadata_obj, autoload_with=engine, schema='pets_store')


    def create_detail_invoice(self,invoice_id):
        try:
            cart_id_query = select(self.invoice_table.c.cart_id).where(self.invoice_table.c.id == invoice_id)
            with engine.begin() as conn:
                cart_id = conn.execute(cart_id_query).scalar()
                product_amount_query = select(self.product_cart_table.c.product_id, self.product_cart_table.c.amount).where(
                    self.product_cart_table.c.cart_id == cart_id
                )
                product_amount = conn.execute(product_amount_query).fetchall()
                for product, amount in product_amount:
                    stmt = insert(self.invoices_products_table).values(invoice_id = invoice_id, product_id = product, amount = amount)
                    conn.execute(stmt)
        except Exception as e:
            print(f"Error: {e}")
            return None


    def show_detail_invoice(self,invoice_id):
        stmt = select(self.invoices_products_table).where(self.invoices_products_table.c.invoice_id == invoice_id)
        with engine.begin() as conn:
            query = conn.execute(stmt)
            result = [dict(result._mapping) for result in query]
        return result
    

class Invoices():
    def __init__(self):
        self.invoice_table = Table('invoices', metadata_obj, autoload_with=engine, schema='pets_store')
        self.products_table = Table('products', metadata_obj, autoload_with=engine, schema='pets_store')
        self.products_cart_table = Table('products_carts', metadata_obj, autoload_with=engine, schema='pets_store' )
        self.cart_table = Cart()
    
    def create_invoice(self, user_id):
        try:
            active_cart = self.cart_table.check_if_user_as_active_car(user_id)
            if active_cart ==  True:
                cart_id_query = select(self.cart_table.cart_table.c.id).where(self.cart_table.cart_table.c.user_id == user_id)
                
                with engine.begin() as conn:
                    cart_id = conn.execute(cart_id_query).scalar()
                    total_price_query = select(func.sum(self.products_cart_table.c.amount * self.products_table.c.price)
                            ).join(self.products_table, self.products_cart_table.c.product_id == self.products_table.c.id
                                ).where(self.products_cart_table.c.cart_id == cart_id)
                    total_price = conn.execute(total_price_query).scalar()
                    
                    complete_invoice = insert(self.invoice_table
                                            ).returning(self.invoice_table.c.id
                                                        ).values(user_id = user_id, price = total_price, cart_id = cart_id)
                    update_cart_status = (update(self.cart_table.cart_table
                                                ).where(self.cart_table.cart_table.c.id == cart_id
                                                        ).values(status = 'complete'))
                    result = conn.execute(complete_invoice)
                    conn.execute(update_cart_status)
                    result_convert = int(result.scalar())
                return result_convert
            else:
                return jsonify({"error":"You do not have any active cart"}), 400
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    
    
    def show_invoices_per_client(self, client):
            stmt = select(self.invoice_table).where(self.invoice_table.c.user_id == client)
            with engine.begin() as conn:
                    query = conn.execute(stmt)
                    result = [dict(result._mapping) for result in query]
                
            return result
    
    def modify_invoice(self, id, new_value, column):
        try:
            column_modification = literal_column(column)
            modification = (update(self.invoice_table).where(self.invoice_table.c.id == id).values( {column_modification: new_value}))
            with engine.begin() as conn:
                result = conn.execute(modification)
                    
        except:
            return('Something when wrong!')
    

    def delete_invoice(self, id):
        try:
            delete_invoice = delete(self.invoice_table).where(self.invoice_table.c.id == id)
            with engine.begin() as conn:
                    result = conn.execute(delete_invoice)
                    
        except Exception as ex:
            print(ex)



