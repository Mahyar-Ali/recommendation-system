from os import listdir
from os.path import isfile, join
import pickle

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.Read_Database import Read_Database

class Recommend_Products:
    def __init__(self, product_id, num_responses) -> None:
        self.product_id = product_id
        self.num_responses = num_responses

        self.products_datastore_path = "database/product"

        self.doc_embeddings_map = {}

    async def read_datastore(self):
        
        onlyfiles = [f for f in listdir(self.products_datastore_path) if isfile(join(self.products_datastore_path, f))]
        main_file = ""
        staged_files = []
        for file_name in onlyfiles:
            if file_name[0:2] == "st":
                staged_files.append(file_name)
            else:
                main_file = file_name

        pickle_files = [main_file] + staged_files
        for file in pickle_files:
            if file:
                with open(f"{self.products_datastore_path}/{file}", "rb",) as pkl:
                    doc_embeddings = pickle.load(pkl)
                self.doc_embeddings_map.update(doc_embeddings)

    async def find_recommended_products(self):
        current_product_embeddings = self.doc_embeddings_map.get(self.product_id, [])
        

        if list(current_product_embeddings):
            similarities_dict = {}
            for product_id, embedding in self.doc_embeddings_map.items():
                current_product_embeddings = current_product_embeddings.reshape(1, -1)
                embedding = embedding.reshape(1, -1)
                similarity = cosine_similarity(current_product_embeddings, embedding)
                similarities_dict[product_id] = similarity
            
            # sorted and get the top n similar items
            sorted_similarities = sorted(similarities_dict.items(), key=lambda x: x[1], reverse=True)
            top_n_similarities = sorted_similarities[1:self.num_responses+1]

            databse_handler = Read_Database()
            product_ids_from_database = await databse_handler.get_product_ids()
            products = []
            for product_id, score in top_n_similarities:
                if product_id in product_ids_from_database:
                    products.append(product_id)
            return products
        else:
            []



    async def recommend_product(self):
        await self.read_datastore()
        products = await self.find_recommended_products()

        return products