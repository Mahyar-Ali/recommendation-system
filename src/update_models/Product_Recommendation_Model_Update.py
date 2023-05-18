from src.Global_Locks import Product_Clusters_Model_Lock
import time
import pickle
from os import listdir
from os.path import isfile, join
import pickle

import numpy as np

import os, shutil
from src.utils.Read_Database import Read_Database

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L12-v2')


class Update_Product_Model:
    def __init__(self, product_id) -> None:
        self.product_id = product_id
        self.products_datastore_path = "database/product"
        self.embeddings_map = {}
        self.max_batch_files = 100

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
                self.embeddings_map.update(doc_embeddings)


    async def clean_datastore(self):
        folder = self.products_datastore_path
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def lock_end_point(self, lock=True):
        Product_Clusters_Model_Lock.lock = lock
        time.sleep(8)

    async def update_batch(self,):

        database_handler = Read_Database()
        self.products_map = await database_handler.get_product_attributes_for_product_model()
        self.products_map = self.products_map[self.product_id]
        product_attributes = np.array(list(self.products_map.values()))
        current_product_embeddings = model.encode(product_attributes, show_progress_bar=False)

        with open(f"{self.products_datastore_path}/st_{self.product_id}.pkl", 'wb') as f:
            pickle.dump({self.product_id:current_product_embeddings}, f)

    async def update_cluster(self,):
        await self.read_datastore()

        database_handler = Read_Database()
        self.products_map = await database_handler.get_product_attributes_for_product_model()
        self.products_map = self.products_map[self.product_id]
        product_attributes = np.array(list(self.products_map.values()))
        current_product_embeddings = model.encode(product_attributes, show_progress_bar=False)

        self.embeddings_map.update({self.product_id:current_product_embeddings})  

        self.lock_end_point(lock=True)
        await self.clean_datastore()
        with open(f"{self.products_datastore_path}/main.pkl", 'wb') as f:
            pickle.dump(self.embeddings_map, f)      
        self.lock_end_point(lock=False)
    
    async def check_if_batch_update(self):
        onlyfiles = [f for f in listdir(self.products_datastore_path) if isfile(join(self.products_datastore_path, f))]
        if len(onlyfiles)>=self.max_batch_files:
            return False
        else:
            return True
    

    async def update_model(self):
        do_batch_update = await self.check_if_batch_update()
        if not do_batch_update:
            await self.update_cluster()
        else:
            await self.update_batch()
