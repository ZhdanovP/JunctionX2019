# JunctionX2019
## Building locally
Got to environment folder
1. do: ```make build``` to build docker image
! Note that requirements.txt should be in the root project foler before ``make build```
2. do: ```make run``` to run the container
After that you will be in container and work folder will be mounted. Work inside like local
3. In project folder run ```python app.py```
4. Got to localhost address written after step 3

## Accessing online:
Server can be accessed via https://tesco-x.herokuapp.com/ 

### Functionalities:
`GET /` - all excess food data from local TESCO markets

`POST /barcode` - returns prognosed quantity which will be left unsold(potentially excess food) by the end of the working day, for particular product, shop, weight, price

`POST /catalog/add` - adding new excees food item to catalog

`POST /catalog/<shop_id>` - get excess food items by shop_id

`GET /catalog/all` - returns JSON of all excess food data fetched from TESCO APIs

## Presentation
https://docs.google.com/presentation/d/18MVfpPrZl8RkRYwuwCpsQEH-K9ChxfWknRsDgci7zAc