import numpy as np
import pandas as pd
import tensorflow as tf

"""# Reading Dataset"""

ratings_path = ""
product_path = ""

def process_data(ratings_path, product_path):
  # Reading Datasets
  ratings_dataset = pd.read_csv(ratings_path).astype(
      "str")
  product_dataset = pd.read_csv(product_path).astype(
      "str")


  ratings_dataset_tensor = tf.data.Dataset.from_tensor_slices(
      dict(ratings_dataset))
  product_dataset_tensor = tf.data.Dataset.from_tensor_slices(
      dict(product_dataset))

  """# Taking Required Featues from Data"""

  users_data = ratings_dataset_tensor.map(lambda x: {
      "reviewerID": x["reviewerID"],
      "asin": x["asin"],
      "overall": x['overall'],
      'region': x['region']
  })
  products = product_dataset_tensor.map(lambda x: x["asin"])


  """# Splitting the data into Train and Test"""

  tf.random.set_seed(42)
  shuffled = users_data.shuffle(150000, seed=42, reshuffle_each_iteration=False)

  train = shuffled.take(120000)
  test = shuffled.skip(120000).take(30000)

  products_batch = products.batch(10000)
  user_ids = users_data.batch(10000).map(lambda x: x["reviewerID"])
  ratings = users_data.batch(10000).map(lambda x: x["overall"])
  regions = users_data.batch(10000).map(lambda x: x["region"])
  user_product_ids = users_data.batch(10000).map(lambda x: x["asin"])

  """# Finding Unique Elements"""

  unique_product_ids = np.unique(np.concatenate(list(products_batch)))
  unique_user_ids = np.unique(np.concatenate(list(user_ids)))
  unique_ratings = np.unique(np.concatenate(list(ratings)))
  unique_ratings = np.unique(np.concatenate(list(regions)))
  unique_user_product_ids = np.unique(np.concatenate(list(user_product_ids)))

  return products, train, test, unique_product_ids, unique_user_ids, unique_ratings, unique_ratings, unique_user_product_ids