import Terminal as trm
def finput(prompt):
	return input(trm.bold+prompt+" "+trm.reset)

filename=finput("Enter path to result file:")
file=open(filename,'r')
data=file.read()
file.close()
data=data.split("\n")

total=int(data[0])
data=data[1:]

users=[]
for line in data:
	if line=='':
		continue
	name,matches=line.split(":")
	matches=list(map(int,matches.split(",")[:-1]))
	users.append((name,len(matches),matches))

compare=finput("Enter a positive braille diagram or trait list to compare against (press enter if none):")

if compare=='':
	comparison=lambda user: -user[1]
else:
	if compare[0].isnumeric():
		compare=list(map(int,compare.split(",")[:-1]))
	else:
		result=[]
		for n,char in enumerate(compare):
			char=trm.fromCharacter(char)
			for i in range(8):
				if trm.readPixel(char,i)==True:
					result.append(n*8+i)
		compare=result
	print("Comparing to this trait list:",','.join(map(str,compare))+',')
	compare=set(compare)
	def distance(user):
		matches=set(user[2])
		return len(compare ^ matches)
	comparison=distance
	maxDist=max(distance(user) for user in users)

users.sort(key=comparison,reverse=True)

ceil=lambda n:round(n+0.5)
def brailleChart(total,matches):
	characters=[0]*ceil(total/8)
	for match in matches:
		characters[match//8]=trm.addPixel(characters[match//8],match%8)
	return "".join(map(trm.toCharacter,characters))

n=0
for i,user in enumerate(users):
	name,matchesN,matches=user
	n+=matchesN
	percent=round((matchesN/total)*100)
	colour=trm.f256(round(237+(19*(matchesN/total))))

	if compare=='':
		middleText=f"{matchesN}/{total}: "
	else:
		dist=distance(user)
		middleText=trm.f256(round(255-(19*(dist/maxDist))))+f"d={dist} "+trm.reset

	print(f"{trm.bold}{colour}{percent}%{trm.reset},\t"\
		f"{trm.inverse if i%2==0 else ''}" \
		f"[{brailleChart(total,matches)}]{trm.reset} "+ \
		middleText + \
		f"https://reddit.com/u/{trm.bold}{name}{trm.reset}"
	)

print(f"In total: {len(users)} users checked")
print(f"Average score is {round((n/len(users))*100)/100}, which makes the average percentage {round(((n/len(users))/total)*10000)/100}%")