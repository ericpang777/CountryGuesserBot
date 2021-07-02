import boto3
import os

s3 = boto3.resource("s3")
bucket = s3.Bucket("street-view-images")
image_folder = os.path.join(os.curdir, "../data/images")
files = [f for f in os.listdir(image_folder)]
for f in files:
    image = open("../data/images/" + f, "rb")
    bucket.put_object(Key=f, Body=image)