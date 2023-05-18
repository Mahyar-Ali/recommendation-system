from src.config import database_url
from src.configurations.Types import Request_Method_Type
from src.utils.call_apis_async import call_api


class Read_Database:
    def __init__(self) -> None:
        self.products_uri = "product/all"
        self.user_uri = "buyer/all"

    async def read_database(self, product=True, user=False):
        if product:
            (
                self.response_json_product,
                self.response_status_code_product,
            ) = await call_api(
                url=database_url + self.products_uri, method=Request_Method_Type.get
            )
            if self.response_status_code_product != 200:
                raise Exception("Couldn't Read Database")
        if user:
            self.response_json_user, self.response_status_code_user = await call_api(
                url=database_url + self.user_uri, method=Request_Method_Type.get
            )
            if self.response_status_code_product != 200:
                raise Exception("Couldn't Read Database")

    async def get_product_ids(self):
        await self.read_database()
        product_ids = []
        if self.response_json_product["status"] == "Success":
            for product in self.response_json_product["product"]:
                product_ids.append(product["_id"])
        else:
            product_ids = []
        return product_ids

    async def get_product_id_to_photos_map(self):
        await self.read_database()
        product_id_to_photos_map = {}
        if self.response_json_product["status"] == "Success":
            for product in self.response_json_product["product"]:
                product_id_to_photos_map[product["_id"]] = product["photos"]
        else:
            product_id_to_photos_map = {}

        return product_id_to_photos_map

    async def get_product_attributes_for_product_model(self):
        await self.read_database()
        product_id_to_attributes_map = {}

        if self.response_json_product["status"] == "Success":
            for product in self.response_json_product["product"]:
                product_id_to_attributes_map[product["_id"]] = {
                    "title": product["productName"],
                    "description": product["description"],
                    "price": product["originalPrice"],
                }
        else:
            product_id_to_attributes_map = {}

        return product_id_to_attributes_map

    async def get_attributes_for_user_model(self, user_id):
        await self.read_database(user=True, product=True)
        self.user_id_to_attributes_map = {}

        if self.response_json_user["status"] == "success":
            for user in self.response_json_user["data"]["user"]:
                if user["_id"] == user_id:
                    self.user_id_to_attributes_map[user["_id"]] = {
                        "region": user["location"]["cityName"],
                        "ratings": [],
                    }

        if self.response_json_product["status"] == "Success":
            for product in self.response_json_product["product"]:
                try:
                    for review in product["reviews"]:
                        user_id = review["user"]["_id"]
                        if user_id in self.user_id_to_attributes_map.keys():
                            rating = review["rating"]
                            product_id = product["_id"]
                        else:
                            continue
                        if user_id in self.user_id_to_attributes_map.keys():
                            self.user_id_to_attributes_map[user_id]["ratings"].append(
                                {"product_id": product_id, "rating": rating}
                            )
                except:
                    continue
        return self.user_id_to_attributes_map

    async def get_attributes_for_user_model_all(self):
        await self.read_database(user=True, product=True)
        self.user_id_to_attributes_list = []

        if self.response_json_user["status"] == "success":
            for user in self.response_json_user["data"]["user"]:
                self.user_id_to_attributes_list.append(
                    {
                        "reviewerID": user["_id"],
                        "region": user["location"]["cityName"],
                        "ratings": [],
                    }
                )

        self.reviewer_id_to_product_ratings = {
            data["reviewerID"]: [] for data in self.user_id_to_attributes_list
        }
        if self.response_json_product["status"] == "Success":
            for product in self.response_json_product["product"]:
                try:
                    for review in product["reviews"]:
                        user_id = review["user"]["_id"]
                        if user_id in self.reviewer_id_to_product_ratings.keys():
                            rating = review["rating"]
                            product_id = product["_id"]
                            self.reviewer_id_to_product_ratings[user_id].append(
                                (product_id, rating)
                            )
                        else:
                            continue
                except:
                    continue
        self.user_id_to_attributes = []
        for data in self.user_id_to_attributes_list:
            for product_id, ratings in self.reviewer_id_to_product_ratings[
                data["reviewerID"]
            ]:
                self.user_id_to_attributes.append(
                    {
                        "reviewerID": data["reviewerID"],
                        "region": data["region"],
                        "overall": ratings,
                        "asin": product_id,
                    }
                )
        return self.user_id_to_attributes
