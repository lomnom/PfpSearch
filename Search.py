import asyncpraw as praw
import asyncio, aiohttp
import threading, queue #yes this is an unholy marraige
import Terminal as trm
import cv2
import numpy as np
import time
import yaml

def finput(prompt):
	return input(trm.bold+prompt+" "+trm.reset)

def log(message,newline=True):
	trm.fprint(trm.dim+f"[{time.ctime()}]"+trm.reset,str(message))
	if newline:
		trm.fprint("\n")

def showImage(title,image):
	cv2.imshow("Target", target)
	cv2.waitKey(1)

sift=cv2.SIFT_create()
flann=cv2.FlannBasedMatcher({"algorithm":0, "trees":5}, {})

tasks=[]
async def main():
	await init()
	await asyncio.gather(*tasks)
	await reddit.close()

#NOTE: execution cannot be resumed from where it was last halted.
async def init():
	global reddit, target, targetSift, subs, beginning, userObjects
	config=yaml.safe_load(open("cfg.yaml",'r').read())
	reddit=praw.Reddit(
		client_id=config['client_id'],
		client_secret=config['client_secret'],
		user_agent="ahem."
	)
	target=cv2.imread(finput("Enter the path to the target image:"),cv2.IMREAD_COLOR)
	targetSift=sift.detectAndCompute(target, None)
	showImage("Target", target)

	subs=finput("Enter the subreddits to scrape from as a space-seperated list:")
	subs=subs.split(" ")

	userObjects=asyncio.Queue(256)

users=set()

async def addAuthor(item):
	if item.author is None:
		return
	if item.author.name not in users:
		users.add(item.author.name)
		if len(users)%250==0:
			log(f"{len(users)} users discovered.")
		await userObjects.put(item.author)

async def submissions():
	global posts
	posts=asyncio.Queue(128)
	for sub in subs:
		sub=await reddit.subreddit(sub)
		log(f"Scraping {sub.display_name}")
		n=0
		async for post in sub.hot(limit=None):
			n+=1
			await addAuthor(post)
			await posts.put(post)
			if n%100==0:
				log(f"Scraped {n} submissions from {sub.display_name}")
	await posts.put(None) #means that its done
	log("Scraped all submissions!")
tasks.append(submissions())

async def comments():
	while True:
		post=await posts.get()
		await post.load()
		if post is None:
			break
		comments=post.comments
		log(f"Getting comments of {post.id}",newline=False)
		while True:
			remaining=await comments.replace_more(limit=5, threshold=0)
			trm.fprint(f".")
			if remaining==[]:
				break
		trm.fprint("\n")
		for comment in list(comments):
			await addAuthor(comment)
	log("Scraped all comments!")
	await userObjects.put(None)
tasks.append(comments())

defaultAvatarCache={}
async def pfps():
	async with aiohttp.ClientSession() as session:
		while True:
			user=await userObjects.get()
			await user.load()
			if "avatar_default" in user.icon_img:
				if user.icon_img not in defaultAvatarCache:
					async with session.get(user.icon_img) as response:
						defaultAvatarCache[user.icon_img]=await response.read()
					log(f"Cached {user.icon_img}")
				icons.put(defaultAvatarCache[user.icon_img])
			else:	
				async with session.get(user.icon_img) as response:
					icons.put(await response.read())
tasks.append(pfps())

icons=queue.Queue()
def crunchPics():
	while True:
		icon=icons.get()
		if icon is None:
			return
		log("Icon received!!")
cruncher=threading.Thread(target=crunchPics)

cruncher.start()
asyncio.run(main())
cruncher.join()
log("Do a keystroke in an image window to end.")
cv2.waitKey(0)