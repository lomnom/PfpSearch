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

def log(*messages,newline=True):
	trm.fprint(trm.dim+f"[{time.ctime()}]"+trm.reset,*map(str,messages))
	if newline:
		trm.fprint("\n")

imageQueue=queue.Queue()
def imageShower():
	while True:
		item=imageQueue.get()
		if item is None:
			return
		title,image=item
		cv2.imshow(title, image)
		cv2.waitKey(1)

def showImage(title,image):
	imageQueue.put((title,image))

sift=cv2.SIFT_create()
flann=cv2.FlannBasedMatcher({"algorithm":0, "trees":5}, {})

tasks=[]
async def main():
	await init()
	await asyncio.gather(*tasks)
	await reddit.close()

#NOTE: execution cannot be resumed from where it was last halted.
async def init():
	global reddit, target, targetSift, subs, beginning, userObjects,outfile
	config=yaml.safe_load(open("cfg.yaml",'r').read())
	reddit=praw.Reddit(
		client_id=config['client_id'],
		client_secret=config['client_secret'],
		user_agent="ahem."
	)
	subs=finput("Enter the subreddits to scrape from as a space-seperated list:")
	subs=subs.split(" ")

	outfile=finput("Name the output file:")
	open(outfile,'w').close()
	outfile=open(outfile,'a')

	target=cv2.imread(finput("Enter the path to the target image:"),cv2.IMREAD_COLOR)
	targetSift=sift.detectAndCompute(target, None)
	showImage("Target", target)

	outfile.write(str(len(targetSift[1]))+'\n')

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
	#await userObjects.put(await reddit.redditor("")) #DEBUF
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
			if user is None:
				break
			await user.load()
			if not hasattr(user,"icon_img"):
				continue
			if "avatar_default" in user.icon_img:
				if user.icon_img not in defaultAvatarCache:
					async with session.get(user.icon_img) as response:
						defaultAvatarCache[user.icon_img]=await response.read()
					log(f"Cached {user.icon_img}")
				icons.put((defaultAvatarCache[user.icon_img],user.name))
			else:	
				async with session.get(user.icon_img) as response:
					icons.put((await response.read(),user.name))
		icons.put(None)
tasks.append(pfps())

icons=queue.Queue()
def crunchPics():
	count=0
	while True:
		icon,name=icons.get()
		if icon is None:
			return
		file=np.frombuffer(icon, np.uint8)
		img=cv2.imdecode(file, cv2.IMREAD_COLOR)
		kp,desc=sift.detectAndCompute(img, None)
		# what we really want is most features matched, not most number of matches found.
		matches=flann.knnMatch(desc,targetSift[1],k=2) #img is querydescriptor and target is traindescriptor.
		result=[]
		ratio=0.7
		for m,n in matches:
			if m.distance < ratio*n.distance:
				result.append(m)

		indicesFound=set()
		for m in result:
			indicesFound.add(m.trainIdx)
		log(name,len(indicesFound),len(targetSift[1]),trm.bold+str(round((len(indicesFound)/len(targetSift[1]))*100))+"%"+trm.reset)
		outfile.write(name+" "+str(len(indicesFound))+"\n")
		outfile.flush()
		count+=1
		if count%100==0:
			log(f"{count} users evaluated!")

		# render=cv2.drawMatches(img,kp,target,targetSift[0],result,None)
		# showImage(name, render)
		# log(len(result))
		# log(kp)
		# log(targetSift[0])
		# log(result)

cruncher=threading.Thread(target=crunchPics)

def redditStuff():
	asyncio.run(main())
redditThread=threading.Thread(target=redditStuff)

redditThread.start()
cruncher.start()
imageShower() 
cruncher.join()
redditThread.join()

log("Do a keystroke in an image window to end.")
cv2.waitKey(0)