import boto3
import os

s3 = boto3.resource("s3")
for bucket in s3.buckets.all():
    image_folder = os.path.join(os.curdir, "../data/images")
    files = [f for f in os.listdir(image_folder)]
    for f in files:
        image = open("../data/images/" + f, "rb")
        s3.Bucket("street-view-images").put_object(Key=f, Body=image)