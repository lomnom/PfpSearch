import asyncpraw as praw
import asyncio
import Terminal
import yaml

tasks=[]
runningtasks=[]
async def main():
	await init()
	for task in tasks:
		runningtasks.append(asyncio.create_task(task))
	for task in runningtasks:
		await task
	await reddit.close()

async def init():
	global reddit
	config=yaml.safe_load(open("cfg.yaml",'r').read())
	reddit=praw.Reddit(
		client_id=config[client_id],
		client_secret=config[client_secret],
		user_agent="ahem."
	)
	pass

async def usernames():
	redditor=await reddit.redditor("dalithop",fetch=True)
	print(redditor.icon_img)
tasks.append(testpfp())

asyncio.run(main())