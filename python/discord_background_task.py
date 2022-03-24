import discord
import asyncio
from discord.ext import tasks
from requests_html import HTMLSession



TOKEN = '*************'
client = discord.Client()

@tasks.loop(seconds=600)
async def background_task():
    await client.wait_until_ready()
    url = 'https://api-manager.upbit.com/api/v1/notices?page=1&per_page=10&thread_name=general'
    session = HTMLSession()
    result= session.get(url).html.search('[거래] KRW, BTC 마켓 디지털 자산 추가 ({})')
    # result= session.get(url).html.search('리플({})')
    if result is not  None:
        await client.get_channel(905687015578824747).send('检测到upbit公告添加币种:{}'.format(result[0]))
        await client.get_channel(905356266686279691).send('检测到upbit公告添加币种:{}'.format(result[0]))
    else:
        # await client.get_channel(905687015578824747).send('没有检测到上币信息')
        # await client.get_channel(905356266686279691).send('没有检测到上币信息')
        print('没有检测到上币信息')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('---------------')

background_task.start()
client.run(TOKEN)