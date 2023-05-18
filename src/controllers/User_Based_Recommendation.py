import asyncio
import random
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import tensorflow as tf

from src.utils.Read_Database import Read_Database

model = tf.saved_model.load("model")


class User_Based_Recommendation:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    async def get_entries_from_database(self):
        database_handler = Read_Database()
        self.user_id_to_attributes_map = await database_handler.get_attributes_for_user_model(
            user_id=self.user_id
        )

    async def get_recommended_products(self, payload):
        _, titles = model(payload)
        return titles

    def multiprocessing_recommend(self, get_recommended_product_func, *args):
        recommended_products = get_recommended_product_func(*args)
        return asyncio.run(recommended_products)

    async def prepare_payloads(self):
        await self.get_entries_from_database()
        payload = []
        if self.user_id_to_attributes_map.get(self.user_id, {}):
            ratings = self.user_id_to_attributes_map[self.user_id].get("ratings", [])
            if ratings:
                select_payloads = random.sample(list(range(len(ratings))), 2)

                product_ids = [
                    (product_dict["product_id"], product_dict["rating"])
                    for idx, product_dict in enumerate(ratings)
                    if idx in select_payloads
                ]
                for (product_id, ratings) in product_ids:
                    payload.append(
                        {
                            "reviewerID": tf.constant([self.user_id]),
                            "region": tf.constant(
                                [self.user_id_to_attributes_map[self.user_id]["region"]]
                            ),
                            "overall": tf.constant([f"{ratings}"]),
                            "asin": tf.constant([product_id]),
                        }
                    )
        return payload

    async def recommended_products(self):
        payloads = await self.prepare_payloads()
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=2)
        future_products = [
            loop.run_in_executor(
                executor,
                self.multiprocessing_recommend,
                self.get_recommended_products,
                data,
            )
            for data in payloads
        ]
        await asyncio.gather(*future_products)

        product_ids = []
        for product in future_products:
            product_ids.extend(
                [product_id.numpy().decode() for product_id in product.result()[0][:2]]
            )

        return list(set(product_ids))
