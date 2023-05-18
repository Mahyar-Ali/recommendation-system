import tensorflow as tf
import tensorflow_recommenders as tfrs


class UserModel(tf.keras.Model):
    def __init__(
        self, unique_user_ids, unique_regions, unique_ratings, unique_user_product_ids
    ):
        super().__init__()

        # Define embeddings for user ID, region, and rating
        self.user_id_embedding = tf.keras.Sequential(
            [
                tf.keras.layers.StringLookup(
                    vocabulary=unique_user_ids, mask_token=None
                ),
                tf.keras.layers.Embedding(len(unique_user_ids) + 1, 32),
            ]
        )

        self.region_embedding = tf.keras.Sequential(
            [
                tf.keras.layers.StringLookup(
                    vocabulary=unique_regions, mask_token=None
                ),
                tf.keras.layers.Embedding(len(unique_regions) + 1, 32),
            ]
        )

        self.rating_embedding = tf.keras.Sequential(
            [
                tf.keras.layers.StringLookup(
                    vocabulary=unique_ratings, mask_token=None
                ),
                tf.keras.layers.Embedding(len(unique_ratings) + 1, 32),
            ]
        )

        self.product_id_embedding = tf.keras.Sequential(
            [
                tf.keras.layers.StringLookup(
                    vocabulary=unique_user_product_ids, mask_token=None
                ),
                tf.keras.layers.Embedding(len(unique_ratings) + 1, 32),
            ]
        )

    def call(self, inputs):
        # Split input features into user ID, region, and rating
        user_id = inputs["reviewerID"]
        region = inputs["region"]
        rating = inputs["overall"]
        product_ids = inputs["asin"]

        # Compute embeddings for user ID, region, and rating
        user_id_embed = self.user_id_embedding(user_id)
        region_embed = self.region_embedding(region)
        rating_embed = self.rating_embedding(rating)
        product_id_embed = self.product_id_embedding(product_ids)

        # Concatenate embeddings
        concatenated = tf.concat(
            [user_id_embed, region_embed, rating_embed, product_id_embed], axis=1
        )

        return concatenated


"""# Candidate or Product Model"""


class ProductModel(tf.keras.Model):
    def __init__(self, unique_product_ids):
        super().__init__()

        self.productId_embedding = tf.keras.Sequential(
            [
                tf.keras.layers.StringLookup(
                    vocabulary=unique_product_ids, mask_token=None
                ),
                tf.keras.layers.Embedding(len(unique_product_ids) + 1, 128),
            ]
        )

    def call(self, asin):
        return self.productId_embedding(asin)


"""# Combining User and Product Model with Task"""


class RecommendationModel(tfrs.models.Model):
    def __init__(self, inputs, products):
        super().__init__()
        user_inputs, product_input = inputs
        self.user_model = UserModel(*user_inputs)
        self.product_model = ProductModel(product_input)

        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=products.batch(1000).map(self.product_model),
            ),
        )

    def compute_loss(self, features, training=False):
        # We only pass the user id and timestamp features into the query model. This
        # is to ensure that the training inputs would have the same keys as the
        # query inputs. Otherwise the discrepancy in input structure would cause an
        # error when loading the query model after saving it.
        user_features = {
            "reviewerID": features["reviewerID"],
            "region": features["region"],
            # Cast rating to int and then string
            "overall": features["overall"],
            "asin": features["asin"],
        }
        user_embeddings = self.user_model(user_features)
        product_embeddings = self.product_model(features["asin"])

        return self.task(user_embeddings, product_embeddings)
