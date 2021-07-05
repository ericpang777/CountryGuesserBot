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
country_list = boto3.resource("s3").Bucket("country-data").Object("country_list.txt").get()["Body"].read().decode("utf-8")
valid_commands = {c : 1 for c in ["get", "g", "G", "Get",
                                  "Getself", "gs", "Gs", "Getself",
                                  "skip", "s", "S", "Skip",
                                  "skipself", "ss", "Ss", "Skipself",
                                  "try", "t", "T", "Try",
                                  "tryself", "ts", "Ts", "Tryself",
                                  "curr", "c", "C", "Curr",
                                  "currself", "cs", "Cs", "Currself",
                                  "list", "l" , "L", "List"]}

bot = discord.ext.commands.Bot(command_prefix="")

@bot.event
async def on_message(message):
    if message.content.split(" ")[0] in valid_commands:
        await bot.process_commands(message)

async def get_image(ctx, table, id):
    try:
        guess_status = table.get_item(Key={"id": str(id)})["Item"]["guess_status"]
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

        table.update_item(
            Key={"id": str(id)},
            UpdateExpression="SET guess_status=:guess_status, file_name=:file_name, actual_country=:actual_country, last_updated=:last_updated",
            ExpressionAttributeValues={
                ":guess_status": "open",
                ":file_name": image_name,
                ":actual_country": image_country,
                ":last_updated": str(datetime.datetime.now())
            }
        )
        image_file = discord.File(io.BytesIO(image_obj.get()["Body"].read()), filename="place1.jpg")
        await ctx.send(file=image_file)
    else:
        await ctx.send("Currently guessing a different image")


@bot.command(name="get", aliases=["g", "G", "Get"])
async def get_image_guild(ctx):
    await get_image(ctx, guild_table, ctx.message.guild.id)


@bot.command(name="getself", aliases=["gs", "Gs", "Getself"])
async def get_image_self(ctx):
    await get_image(ctx, user_table, ctx.message.author.id)


async def skip_image(ctx, table, id):
    data = table.get_item(Key={"id": str(id)})["Item"]
    guess_status = data["guess_status"]

    if guess_status == "open":
        table.update_item(
            Key={"id": str(id)},
            UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
            ExpressionAttributeValues={
                ":guess_status": "closed",
                ":last_updated": str(datetime.datetime.now())
            }
        )
        actual_country = data["actual_country"]
        for c in countries["countries"]:
            if c["alpha_3_code"] == actual_country:
                await ctx.send(f"The answer was {c['name']}, codes: {c['alpha_2_code']}, {c['alpha_3_code']}")
                return
        await ctx.send(f"The answer was {actual_country}")
    else:
        await ctx.send("No image was open")


@bot.command("skip", aliases=["s", "S", "Skip"])
async def skip_image_guild(ctx):
    await skip_image(ctx, guild_table, ctx.message.guild.id)


@bot.command("skipself", aliases=["ss", "Ss", "Skipself"])
async def skip_image_self(ctx):
    await skip_image(ctx, user_table, ctx.message.author.id)


async def try_guess(ctx, table, id):
    data = table.get_item(Key={"id": str(id)})["Item"]
    guess_status = data["guess_status"]

    if guess_status == "closed":
        await ctx.send("No image currently open")
    else:
        message = ctx.message.content.strip().lower()
        message = message[message.find(" "):].strip()
        actual_country = data["actual_country"].lower()

        if actual_country == message:
            table.update_item(
                Key={"id": str(id)},
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
                    table.update_item(
                        Key={"id": str(id)},
                        UpdateExpression="SET guess_status=:guess_status, last_updated=:last_updated",
                        ExpressionAttributeValues={
                            ":guess_status": "closed",
                            ":last_updated": str(datetime.datetime.now())
                        }
                    )
                    await ctx.send(f"Correct, {c['name']}, codes: {c['alpha_2_code']}, {c['alpha_3_code']}")
                    return
        await ctx.send("Incorrect")


@bot.command("try", aliases=["t", "T", "Try"])
async def try_guess_guild(ctx):
    await try_guess(ctx, guild_table, ctx.message.guild.id)


@bot.command("tryself", aliases=["ts", "Ts", "Tryself"])
async def try_guess_self(ctx):
    await try_guess(ctx, user_table, ctx.message.author.id)


async def get_curr(ctx, table, id):
    try:
        guess_status = table.get_item(Key={"id": str(id)})["Item"]["guess_status"]
        if guess_status == "open":
            image_name = table.get_item(Key={"id": str(id)})["Item"]["file_name"]
            image_obj = image_bucket.Object(image_name)
            file_stream = io.BytesIO()
            image_obj.download_fileobj(file_stream)
            image_file = discord.File(io.BytesIO(image_obj.get()["Body"].read()), filename=f"place1.jpg")
            await ctx.send(file=image_file)
    except:
        await ctx.send("Something went wrong")

@bot.command("curr", aliases=["c", "C", "Curr"])
async def get_curr_guild(ctx):
    await get_curr(ctx, guild_table, ctx.message.guild.id)

@bot.command("currself", aliases=["cs", "Cs", "Currself"])
async def get_curr_self(ctx):
    await get_curr(ctx, user_table, ctx.message.author.id)

@bot.command("list", aliases=["l", "L", "List"])
async def list_countries(ctx):
    await ctx.send(country_list[:1492])
    await ctx.send(country_list[1492:3009])
    await ctx.send(country_list[3009:])

bot.run(TOKEN)