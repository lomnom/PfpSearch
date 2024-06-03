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
	line=line.split(" ")
	users.append((line[0],int(line[1])))

users.sort(key=lambda user: user[1])

n=0
for user in users:
	n+=user[1]
	percent=round((user[1]/total)*100)
	print(f"{trm.bold}{trm.f256(round(237+(19*(user[1]/total))))}{percent}%{trm.reset}: u/{user[0]} - {user[1]}/{total}")

print(f"In total: {len(users)} users checked")
print(f"Average score is {n/len(users)}, which makes the average percentage {round((n/len(users))*100)}")