import pickle

from sklearn.metrics.pairwise import cosine_similarity
from os import listdir
from os.path import isfile, join

from src.utils.Read_Database import Read_Database
from src.Global_Locks import Image_Clusters_Model_Lock

class Image_Based_Recommendation:
    def __init__(self) -> None:
        self.image_embeddings_datastore = "database/images"
        self.doc_embeddings_map = {}



    async def find_similar_images(self, test_image_id, top_n=5):
        onlyfiles = [f for f in listdir(self.image_embeddings_datastore) if isfile(join(self.image_embeddings_datastore, f))]
        main_file = ""
        staged_files = []

        for file_name in onlyfiles:
            if file_name[0:2] == "st":
                staged_files.append(file_name)
            else:
                main_file = file_name

        pickle_files = [main_file] + staged_files

        for file in pickle_files:
            with open(f"{self.image_embeddings_datastore}/{file}", "rb",) as pkl:
                doc_embeddings = pickle.load(pkl)
            self.doc_embeddings_map.update(doc_embeddings)

        test_embedding = self.doc_embeddings_map[test_image_id]
        # find similarity
        similarities_dict = {}
        for image_id, embedding in self.doc_embeddings_map.items():
            similarity = cosine_similarity([test_embedding], [embedding])[0][0]
            similarities_dict[image_id] = similarity

        # sorted and get the top n similar items
        sorted_similarities = sorted(similarities_dict.items(), key=lambda x: x[1], reverse=True)
        top_n_similarities = sorted_similarities[1:top_n+1]

        database_handler = Read_Database()
        product_id_to_photos_map = await database_handler.get_product_id_to_photos_map()
        image_id_to_product_id_map = {}

        for product_id, photos_ids in product_id_to_photos_map.items():
            for photo_id in photos_ids:
                image_id_to_product_id_map[photo_id] = product_id
        products = []
        for image_id, similarity in top_n_similarities:
            if image_id in image_id_to_product_id_map.keys():
                products.append(image_id_to_product_id_map[image_id])


        return products