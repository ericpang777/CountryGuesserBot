import io
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import boto3
import json
import numpy
import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

user_table = boto3.resource("dynamodb").Table("user-data")
guild_table = boto3.resource("dynamodb").Table("guild-data")
image_table = boto3.resource("dynamodb").Table("street-view-image-metadata")
num_images = boto3.resource("dynamodb").Table("constants").get_item(Key={"name": "num_images"})["Item"]["val"]
image_bucket = boto3.resource("s3").Bucket("street-view-images")
countries = json.loads(boto3.resource("s3").Bucket("country-data").Object("countries.json").get()["Body"].read().decode("utf-8"))

bot = discord.ext.commands.Bot(command_prefix="")

@bot.command(name="get", aliases=["g", "G", "Get"])
async def get_image_guild(ctx):
    guild_id = ctx.message.guild.id

    try:
        guess_status = guild_table.get_item(Key={"id": str(guild_id)})["Item"]["guess_status"]
    except:
        guess_status = "closed"

    if guess_status == "closed":
        rand = numpy.random.randint(num_images, size=1)[0]
        image_metadata = image_table.get_item(Key={"index": int(rand)})["Item"]
        image_name = image_metadata["name"]
        image_country = image_metadata["country"]
        image_obj = image_bucket.Object(image_name)
        file_stream = io.BytesIO()
        image_obj.download_fileobj(file_stream)

        guild_table.update_item(
            Key={"id": str(guild_id)},
            UpdateExpression="SET guess_status=:guess_status, file_name=:file_name, actual_country=:actual_country, last_updated=:last_updated",
            ExpressionAttributeValues={
                ":guess_status": "open",
                ":file_name": image_name,
                ":actual_country": image_country,
                ":last_updated": str(datetime.datetime.now())
            }
        )
        image_file = discord.File(io.BytesIO(image_obj.get()["Body"].read()), filename=f"place{rand}.jpg")
        await ctx.send(file=image_file)
    else:
        await ctx.send("The server is currently guessing a different image")


@bot.command(name="getself", aliases=["gs", "Gs", "Getself"])
async def get_image_self(ctx):
    user_id = ctx.message.author.id

    try:
        guess_status = user_table.get_item(Key={"id": str(user_id)})["Item"]["guess_status"]
    except:
        guess_status = "closed"

    if guess_status == "closed":
        rand = numpy.random.randint(num_images, size=1)[0]
        image_metadata = image_table.get_item(Key={"index": int(rand)})["Item"]
        image_name = image_metadata["name"]
        image_country = image_metadata["country"]
        image_obj = image_bucket.Object(image_name)
        file_stream = io.BytesIO()
        image_obj.download_fileobj(file_stream)

        user_table.update_item(
            Key={"id": str(user_id)},
            UpdateExpression="SET guess_status=:guess_status, file_name=:file_name, actual_country=:actual_country, last_updated=:last_updated",
            ExpressionAttributeValues={
                ":guess_status": "open",
                ":file_name": image_name,
                ":actual_country": image_country,
                ":last_updated": str(datetime.datetime.now())
            }
        )
        image_file = discord.File(io.BytesIO(image_obj.get()["Body"].read()), filename=f"place{rand}.jpg")
        await ctx.send(file=image_file)
    else:
        await ctx.send("You are currently guessing a different image")

@bot.command("skip", aliases=["s", "S", "Skip"])
async def skip_image_guild(ctx):
    guild_id = ctx.message.guild.id
    guild_data = guild_table.get_item(Key={"id": str(guild_id)})["Item"]
    guess_status = guild_data["guess_status"]

    if guess_status == "open":
        guild_table.update_item(
            Key={"id": str(guild_id)},
            UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
            ExpressionAttributeValues={
                ":guess_status": "closed",
                ":last_updated": str(datetime.datetime.now())
            }
        )
        actual_country = guild_data["actual_country"]
        for c in countries["countries"]:
            if c["alpha_3_code"] == actual_country:
                await ctx.send(f"The answer was {c['name']}, codes: {c['alpha_2_code']}, {c['alpha_3_code']}")
                return
        await ctx.send(f"The answer was {actual_country}")
    else:
        await ctx.send("No image was open")

@bot.command("skipself", aliases=["ss", "Ss", "Skipself"])
async def skip_image_self(ctx):
    user_id = ctx.message.author.id
    user_data = user_table.get_item(Key={"id": str(user_id)})["Item"]
    guess_status = user_data["guess_status"]

    if guess_status == "open":
        user_table.update_item(
            Key={"id": str(user_id)},
            UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
            ExpressionAttributeValues={
                ":guess_status": "closed",
                ":last_updated": str(datetime.datetime.now())
            }
        )
        actual_country = user_data["actual_country"]
        for c in countries["countries"]:
            if c["alpha_3_code"] == actual_country:
                await ctx.send(f"The answer was {c['name']}, codes: {c['alpha_2_code']}, {c['alpha_3_code']}")
                return
        await ctx.send(f"The answer was {actual_country}")
    else:
        await ctx.send("No image was open")

@bot.command("try", aliases=["t", "T", "Try"])
async def try_guess_guild(ctx):
    guild_id = ctx.message.guild.id
    guild_data = guild_table.get_item(Key={"id": str(guild_id)})["Item"]
    guess_status = guild_data["guess_status"]

    if guess_status == "closed":
        await ctx.send("No image currently open")
    else:
        message = ctx.message.content.strip().lower()
        message = message[message.find(" "):].strip()
        actual_country = guild_data["actual_country"].lower()

        if actual_country == message:
            guild_table.update_item(
                Key={"id": str(guild_id)},
                UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
                ExpressionAttributeValues={
                    ":guess_status": "closed",
                    ":last_updated": str(datetime.datetime.now())
                }
            )
            await ctx.send("Correct")
            return

        for c in countries["countries"]:
            if c["alpha_3_code"].lower() == actual_country:
                if c["name"].lower() == message or c["alpha_2_code"].lower() == message or c["alpha_3_code"].lower() == message:
                    guild_table.update_item(
                        Key={"id": str(guild_id)},
                        UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
                        ExpressionAttributeValues={
                            ":guess_status": "closed",
                            ":last_updated": str(datetime.datetime.now())
                        }
                    )
                    await ctx.send(f"Correct, {c['name']}, codes: {c['alpha_2_code']}, {c['alpha_3_code']}")
                    return
        await ctx.send("Incorrect")

@bot.command("tryself", aliases=["ts", "Ts", "Tryself"])
async def try_guess_self(ctx):
    user_id = ctx.message.author.id
    user_data = user_table.get_item(Key={"id": str(user_id)})["Item"]
    guess_status = user_data["guess_status"]

    if guess_status == "closed":
        await ctx.send("No image currently open")
    else:
        message = ctx.message.content.strip().lower()
        message = message[message.find(" "):].strip()
        actual_country = user_data["actual_country"].lower()

        if actual_country == message:
            user_table.update_item(
                Key={"id": str(user_id)},
                UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
                ExpressionAttributeValues={
                    ":guess_status": "closed",
                    ":last_updated": str(datetime.datetime.now())
                }
            )
            await ctx.send("Correct")
            return

        for c in countries["countries"]:
            if c["alpha_3_code"].lower() == actual_country:
                if c["name"].lower() == message or c["alpha_2_code"].lower() == message or c["alpha_3_code"].lower() == message:
                    user_table.update_item(
                        Key={"id": str(user_id)},
                        UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
                        ExpressionAttributeValues={
                            ":guess_status": "closed",
                            ":last_updated": str(datetime.datetime.now())
                        }
                    )
                    await ctx.send(f"Correct, {c['name']}, codes: {c['alpha_2_code']}, {c['alpha_3_code']}")
                    return
        await ctx.send("Incorrect")

@bot.command("curr", aliases=["c", "C", "Curr"])
async def get_curr_guild(ctx):
    guild_id = ctx.message.guild.id

    try:
        guess_status = guild_table.get_item(Key={"id": str(guild_id)})["Item"]["guess_status"]
        if guess_status == "open":
            image_name = guild_table.get_item(Key={"id": str(guild_id)})["Item"]["file_name"]
            image_obj = image_bucket.Object(image_name)
            file_stream = io.BytesIO()
            image_obj.download_fileobj(file_stream)
            image_file = discord.File(io.BytesIO(image_obj.get()["Body"].read()), filename=f"place1.jpg")
            await ctx.send(file=image_file)
    except:
        await ctx.send("Something went wrong")

@bot.command("currself", aliases=["cs", "Cs", "Currself"])
async def get_curr_self(ctx):
    user_id = ctx.message.author.id

    try:
        guess_status = user_table.get_item(Key={"id": str(user_id)})["Item"]["guess_status"]
        if guess_status == "open":
            image_name = user_table.get_item(Key={"id": str(user_id)})["Item"]["file_name"]
            image_obj = image_bucket.Object(image_name)
            file_stream = io.BytesIO()
            image_obj.download_fileobj(file_stream)
            image_file = discord.File(io.BytesIO(image_obj.get()["Body"].read()), filename=f"place1.jpg")
            await ctx.send(file=image_file)
    except:
        await ctx.send("Something went wrong")


bot.run(TOKEN)