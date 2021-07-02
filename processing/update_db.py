import boto3
import os

dynamodb = boto3.resource("dynamodb")
image_table = dynamodb.Table("street-view-image-metadata")

image_folder = os.path.join(os.curdir, "../data/images")
files = [f for f in os.listdir(image_folder)]

with image_table.batch_writer() as batch:
    for i in range(len(files)):
        batch.put_item(
            Item={
                "index": i,
                "name": files[i],
                "country": files[i][:files[i].find("_")],
            }
        )


constants_table = dynamodb.Table("constants")
constants_table.put_item(
    Item={
        "name": "num_images",
        "val": len(files)
    }
)