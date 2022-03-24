import discord
import requests
import json

TOKEN = '*********************'
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.endswith('?'):
        coin = message.content.split('?')[0].upper()
        url = 'https://api.binance.com/api/v3/ticker/24hr?symbol={}USDT'.format(coin)
        req = requests.get(url)
        res = json.loads(req.content)
        lastPrice = float(res['lastPrice'])
        priceChangePercent = float(res['priceChangePercent'])

        if priceChangePercent > 0:
            bot_color = 0x2ecc71
        elif priceChangePercent == 0:
            bot_color = 0x3498db
        else: 
            bot_color = 0xe74c3c

        embedVar = discord.Embed(title='币种:{}'.format(b),color=bot_color,description='现价:{}$\n涨跌幅:{}%'.format(lastPrice,priceChangePercent))
        await message.channel.send(embed=embedVar)  
    

client.run(TOKEN)