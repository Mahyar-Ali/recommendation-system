
import time
import pickle
from os import listdir
from os.path import isfile, join
import pickle

import numpy as np

import os, shutil

from src.Global_Locks import Image_Clusters_Model_Lock

class Image_Recommendation_Model_Update:
    def __init__(self, image_id) -> None:
        self.image_id = image_id
        self.products_datastore_path = "database/images"
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

    def lock_end_point(self):
        Image_Clusters_Model_Lock.lock = True
        time.sleep(secs=8)

    async def update_batch(self,):
        current_image_embeddings = []
        with open(f"st_{self.product_id}.pickle") as file:
            pass

    async def update_cluster(self,):
        await self.read_datastore()

        current_image_embeddings = []

        self.embeddings_map.update({self.image_id:current_image_embeddings})

        await self.clean_datastore()

        embeddings_map = ""
    
    async def check_if_batch_update(self):
        onlyfiles = [f for f in listdir(self.products_datastore_path) if isfile(join(self.products_datastore_path, f))]
        if len(onlyfiles)>=self.max_batch_files:
            return False
        else:
            return True
    

    async def update_model(self):
        do_batch_update = await self.check_if_batch_update()
        if not do_batch_update:
            self.lock_end_point()
            self.update_cluster()
        else:
            self.update_batch()