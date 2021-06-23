import discord
#import nest_asyncio
#nest_asyncio.apply()
import requests
from datetime import datetime, timedelta

# =============================================================================
# OpenSea API
# =============================================================================
def get_sales():
	url = "https://api.opensea.io/api/v1/events"
	querystring = {"only_opensea":"true",
	               "offset":"0",
				   "limit":"30", 
	               "asset_contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d", 
	               "occurred_after": (datetime.utcnow() - timedelta(seconds = 5)).replace(microsecond=0).timestamp(),
	               "event_type": "successful"}
	headers = {"Accept": "application/json"}
	print("checking between {} and {}".format(datetime.utcnow().replace(microsecond=0), (datetime.utcnow() - timedelta(hours=0, minutes=0, seconds = 5)).replace(microsecond=0)))
	response = requests.request("GET", url, headers=headers, params=querystring).json()
	dicts = {}
	dicts['sales'] = []
	for i in range(len(response["asset_events"])):
	    ape_sale_price = int(response["asset_events"][i]['total_price']) /1000000000000000000.0
	    ape_num = int(response["asset_events"][i]['asset']['token_id'])
	    ape_img = response["asset_events"][i]['asset']['image_url']
	    ape_link = response["asset_events"][i]['asset']['permalink']
	    keys  = ['ape_sale_price','ape_num','ape_img', 'ape_link']
	    values = [ape_sale_price, ape_num, ape_img, ape_link]
	    sales = dict(zip(keys, values))
	    dicts["sales"].append(sales)
	#check in console what we are returning for debugging
	print(dicts)	
	return(dicts)
	
# =============================================================================
# Discord 
# =============================================================================
from discord.ext import commands, tasks
#doesn't require a command, so use empty string here
client = commands.Bot('')

@client.event
async def on_ready(): 
	print('We have logged in as {0.user}'.format(client))

# =============================================================================
# create background loop task to check for new sales, send message to channel
# =============================================================================
@tasks.loop(seconds=5)
async def ape_sales():
	await client.wait_until_ready()
	#Replace with channel id, right click on channe; to copy this. 
	#Make sure Discord Development Mode is enabled in your account settings 
	channel = client.get_channel(856981719105929321)
	#Call function to hit the OpenSea API
	pulled_sales = get_sales()
	#if len(pulled_sales['sales']) > 0:
	for i in range(len(pulled_sales['sales'])):
		sale_price = pulled_sales['sales'][i]['ape_sale_price']
		number = pulled_sales['sales'][i]['ape_num']
		image = pulled_sales['sales'][i]['ape_img']
		link = pulled_sales['sales'][i]['ape_link']
		title_string = "🚨 BAYC Sale: #{} sold for {} ETH!".format(number,sale_price)
		embed = discord.Embed(title= title_string, url = link, color=discord.Color.blue())
		embed.set_image(url=image)
		await channel.send(embed=embed)
	else:
		return
# =============================================================================
# Start loop
# =============================================================================
ape_sales.start()
# =============================================================================
# run using Discord API token. If running locally, just paste in here. Otherwise, use env. variable
# =============================================================================
client.run(token)
