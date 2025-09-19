# save_dataset.py
import pandas as pd
import tensorflow as tf
import os

#  1) Load your Excel file 
file_path = "Updated Data.xlsx"
df = pd.read_excel(file_path)

# # Keep only rows with both age + gender
# df = df.dropna(subset=["Birth date", "Gender"])

# # Age calculation (assuming Birth date = year of birth)
# CURRENT_YEAR = 2025
# df["AgeYears"] = CURRENT_YEAR - df["Birth date"].astype(int)

# # Only keep valid rows
# df = df[(df["AgeYears"] > 0) & (df["AgeYears"] < 120)]

# print(" Cleaned data shape:", df.shape)

# # 2) TensorFlow Dataset from DataFrame 
# def df_to_dataset(df):
#     paths = df["image_path"].values
#     genders = df["Gender"].astype(int).values
#     ages = df["AgeYears"].astype(float).values

#     def load_image(path, gender, age):
#         img = tf.io.read_file(path)
#         img = tf.image.decode_jpeg(img, channels=3)
#         img = tf.image.resize(img, [224, 224]) / 255.0  # normalize
#         return img, {"gender": gender, "age": age}

#     ds = tf.data.Dataset.from_tensor_slices((paths, genders, ages))
#     ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
#     return ds

# dataset = df_to_dataset(df)

# # 3) Serialize TFRecord 


# def serialize_example(image, gender, age):
#     feature = {
#         "image": tf.train.Feature(
#             bytes_list=tf.train.BytesList(
#                 value=[tf.io.encode_jpeg(tf.cast(image*255, tf.uint8)).numpy()]
#             )
#         ),
#         "gender": tf.train.Feature(int64_list=tf.train.Int64List(value=[int(gender)])),
#         "age": tf.train.Feature(float_list=tf.train.FloatList(value=[float(age)])),
#     }
#     example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
#     return example_proto.SerializeToString()

# os.makedirs("tfrecords", exist_ok=True)
# tfrecord_file = "tfrecords/dataset.tfrecord"

# with tf.io.TFRecordWriter(tfrecord_file) as writer:
#     for img, labels in dataset:
#         example = serialize_example(img, labels["gender"], labels["age"])
#         writer.write(example)

# print(" Saved dataset to:", tfrecord_file)



# #  4) Load back TFRecord (example) 
# def parse_example(example_proto):
#     feature_description = {
#         "image": tf.io.FixedLenFeature([], tf.string),
#         "gender": tf.io.FixedLenFeature([], tf.int64),
#         "age": tf.io.FixedLenFeature([], tf.float32),
#     }
#     parsed = tf.io.parse_single_example(example_proto, feature_description)
#     image = tf.image.decode_jpeg(parsed["image"], channels=3)
#     image = tf.image.resize(image, [224, 224]) / 255.0
#     return image, {"gender": parsed["gender"], "age": parsed["age"]}

# raw_dataset = tf.data.TFRecordDataset(tfrecord_file)
# parsed_dataset = raw_dataset.map(parse_example)

# print(" Reloaded TFRecord example:")
# for img, labels in parsed_dataset.take(1):
#     print("Image shape:", img.shape, "Labels:", labels)


import os

#Check which files are missing
missing_files = df[~df["image_path"].apply(os.path.exists)]

print(f"Missing files count: {len(missing_files)}")
print(missing_files[["image_path"]].head(20))

