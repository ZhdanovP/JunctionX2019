import pickle

def predict(item_weight, item_type, item_price, outlet_size):
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
