import pickle

def do_prediction(item_weight, item_type, item_price, outlet_size):
	"""Function to predict number of items which potentially could be sold

    Parameters:
    Function takes parameters from API, which will be used for prediction

    Returns:
    int: value of items which potentially will be sold

   	"""

	#data = [[0, 9.3, 4, 1]]
	#df = pd.DataFrame(data, columns = ['Item_Weight', 'Item_Type', 'Item_Price', 'Outlet_Size']) 

	data = [[item_weight, item_type, item_price, outlet_size]]

	filename = 'sale_prediction_model.sav'
	loaded_model = pickle.load(open(filename, 'rb'))
	result = loaded_model.predict(data)

	return int(result)

def predict(tesco_row):
	import random
	item_weight, item_type, item_price, outlet_size = convert(tesco_row)

	how_many_will_be_sold = do_prediction(item_weight, item_type, item_price, outlet_size)
	how_many_will_be_sold = abs(how_many_will_be_sold)

	return (how_many_will_be_sold+random.uniform(1, 20))-how_many_will_be_sold

def convert(tesco_row):
    import re
    '''
    tesco_row: dictionary{weight:3, name:'sfsdfsf', price:232}
    need2 add store type, product quantity
    "Hovis Soft White Medium Bread 800G"
    
    '''
    
    item_weight= tesco_row['weight']
    item_price = tesco_row['price']
    outlet_size = 1
    
    if re.search('drink', tesco_row['name'], flags=re.IGNORECASE) is not None:
           item_type = 14
    elif re.search('Baking', tesco_row['name'], flags=re.IGNORECASE)is not None:
           item_type = 0
    elif re.search('Breakfast', tesco_row['name'], flags=re.IGNORECASE)is not None:
           item_type = 2
    elif re.search('Fruits|Vegetables', tesco_row['name'], flags=re.IGNORECASE)is not None:
           item_type = 6
    elif re.search('frozen', tesco_row['name'], flags=re.IGNORECASE)is not None:
           item_type = 5
    elif re.search('snack', tesco_row['name'], flags=re.IGNORECASE)is not None:
           item_type = 13
    elif re.search('meat', tesco_row['name'], flags=re.IGNORECASE)is not None:
           item_type = 10
    else:
           item_type = 3 # canned
    return item_weight, item_type, item_price, outlet_size
