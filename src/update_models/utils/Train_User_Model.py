import os
import tempfile

import tensorflow as tf
import tensorflow_recommenders as tfrs

from src.update_models.utils.process_dataset_for_user_model import process_data
from src.update_models.utils.User_Models import RecommendationModel


def train(output_dir, ratings_path, product_path):
    """# Compiling Model"""
    (
        products,
        train,
        test,
        unique_user_ids,
        unique_regions,
        unique_ratings,
        unique_user_product_ids,
        unique_product_ids,
    ) = process_data(ratings_path, product_path)
    model = RecommendationModel(
        [
            [unique_user_ids, unique_regions, unique_ratings, unique_user_product_ids],
            unique_product_ids,
        ],
        products=products,
    )
    model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

    cached_train = train.shuffle(120000).batch(10000).cache()
    cached_test = test.batch(10000).cache()

    """# Training Model"""

    history = model.fit(cached_train, epochs=15)

    """# Prediction on Single Query"""

    # Create a model that takes in raw query features, and
    index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
    # recommends movies out of the entire movies dataset.
    index.index_from_dataset(
        tf.data.Dataset.zip(
            (products.batch(1000), products.batch(1000).map(model.product_model))
        )
    )
    # out = index(
    #     {
    #         "reviewerID": tf.constant(["645a8408b559b8644e5baa5f"]),
    #         "region": tf.constant(["Islamabad"]),
    #         "overall": tf.constant(["5"]),
    #         "asin": tf.constant(["6463f5091c50b9d1ed194150"]),
    #     }
    # )
    # print(out)
    # Export the query model.
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(output_dir, "model")

    # Save the index.
    tf.saved_model.save(index, path)
