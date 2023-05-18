import pandas as pd

from src.update_models.utils.Train_User_Model import train
from src.utils.Read_Database import Read_Database


class Update_User_Model:
    def __init__(self) -> None:
        self.user_attributes_path = "user_attributes_dataframe.csv"
        self.product_attributes_path = "product_attributes_dataframe.csv"

    async def process_product_attributes(self):
        product_attributes_list = []
        product_ids = [data["asin"] for data in self.user_attributes]

        for product_id, attributes in self.product_attributes.items():
            if product_id in product_ids:
                attributes.update({"asin": product_id})
                product_attributes_list.append(attributes)

        return product_attributes_list

    async def get_attributes_from_database(self):
        database_handler = Read_Database()

        self.product_attributes = (
            await database_handler.get_product_attributes_for_product_model()
        )
        self.user_attributes = (
            await database_handler.get_attributes_for_user_model_all()
        )
        self.product_attributes = await self.process_product_attributes()

        self.user_attributes_dataframe = pd.DataFrame(self.user_attributes)
        self.product_attributes_dataframe = pd.DataFrame(self.product_attributes)

        self.user_attributes_dataframe.to_csv(self.user_attributes_path, index=False)
        self.product_attributes_dataframe.to_csv(
            self.product_attributes_path, index=False
        )

    async def update_model(self):
        await self.get_attributes_from_database()
        train(
            output_dir="",
            ratings_path=self.user_attributes_path,
            product_path=self.product_attributes_path,
        )
