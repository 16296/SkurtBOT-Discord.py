#bot.py
print("Loading...\n")
import os
import discord
import json as filereader
import random as dice
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print("Connecting...\n")
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(intents=intents,command_prefix=">")

class Candidate():
	def __init__(self,name,backers):
		self.name = name
		self.backers = backers

	def getName(self):
		return self.name
	def getBackers(self):
		return self.backers
	
	def addBacker(self,backerRef):
		self.backers = self.backers.append(backerRef)
	
	def createDict(self):
		return {"name":self.name,"backers":self.backers}

class Party():
	def __init__(self,name,members,extrapoints):
		self.name = name
		self.members = members
		self.extrapoints = extrapoints
		self.points = (members*5) + extrapoints
		self.roleId =  None

	def getName(self):
		return self.name
	def getMembers(self):
		return self.members
	def getPoints(self):
		return self.points
	def getExtras(self):
		return self.extrapoints

	def setExtras(self,newExtra):
		self.extrapoints = newExtra
		self.__init__(self.name,self.members,self.extrapoints)

	def setMembers(self,newMembers):
		self.members = newMembers
		self.__init__(self.name,self.members,self.extrapoints)

	def createDict(self):
		return {"name":self.name,"members":self.members,"extrapoints":self.extrapoints}

def saveCandidates():
	newDict = {}
	for i in candidateRefs:
		newDict[i] = candidateRefs[i].createDict()
	with open("candidates.json","w",encoding="utf-8") as file:
		filereader.dump(newDict,file,ensure_ascii=False,indent=4)

def createCandidates():
	global candidates
	global candidateRefs
	with open("candidates.json","r") as candidateFile:
		candidateDict = filereader.load(candidateFile)
	candidateRefs = list(candidateDict.keys())
	candidates = {}
	for i,j in zip(range(len(candidateRefs)),candidateRefs):
		temp = candidateDict[candidateRefs[i]].values()
		valueArray = list(temp)
		candidates[j] = Candidate(*valueArray)

def saveObjects():
	newDict = {}
	for i in partyRefs:
		newDict[i] = partyObjects[i].createDict()
	with open("parties.json","w",encoding="utf-8") as file:
		filereader.dump(newDict,file,ensure_ascii=False,indent=4) 	

def createObjects():
	global partyObjects
	global partyRefs
	with open("parties.json","r") as partyFile:
		partyDict = filereader.load(partyFile)
	#partyDict is a two-dimensional dictionary
	partyRefs = list(partyDict.keys())
	partyObjects = {}
	for i,j in zip(range(len(partyRefs)),partyRefs):
		temp = partyDict[partyRefs[i]].values()
		valueArray = list(temp)
		partyObjects[j] = Party(*valueArray) #partyObjects["mp"] for example is the name of the Minarchy Party object and can be called as such

@client.command()
async def sim_votes(ctx,candidate1=None,candidate2=None,humanvotes=None):
	role = discord.utils.find(lambda r: r.name == 'Eternal Press Secretary', ctx.message.guild.roles)
	if role in ctx.author.roles:
		if candidate1 != None and candidate2 != None and humanvotes != None and humanvotes.isdigit():
			totalvotes = (int(humanvotes)//3)*2
			candidate1 = candidate1.title()
			candidate2 = candidate2.title() 
			#formats candidate references
			pop1 = 0
			pop2 = 0
			for j in candidates[candidate1].getBackers():
				points = partyObjects[j].getPoints()
				pop1 += points
			for j in candidates[candidate2].getBackers():
				points = partyObjects[j].getPoints()
				pop2 += points
			#sums total popularity points of backing parties
			if pop1 < pop2:
				temp = pop1
				pop1 = pop2
				pop2 = temp
				temp = candidate1
				candidate1 = candidate2
				candidate2 = temp
			#swaps candidates so that candidate1 and pop1 are the larger number
			votes1 = 0
			votes2 = 0
			for i in range(totalvotes*4):
				#runs the trial 4 times for precision, mitigates outliers
				d100 = dice.randint(1,100)
				#rolls a d100
				if d100 < (pop1/(pop1+pop2))*100:
					#if the d100 result is less than the ratio of pop2 to pop1, candidate 1 gains a vote
					votes1 += 1
				elif d100 >= (pop1/(pop1+pop2))*100:
					#if the d100 result is greater than the ratio of pop2 to pop1, candidate 2 gains a vote
					votes2 += 1
			votes1 = votes1 // 4
			votes2 = votes2 // 4
			#divides by 4 to get an average
			await ctx.send(f"{candidates[candidate1].getName()} won {votes1} simulated votes.\n{candidates[candidate2].getName()} won {votes2} simulated votes.")
			#output
		else:
			await ctx.send("Two valid candidate names and a total number of votes must be provided (>sim_votes [Name] [Name] [Integer])")
	else:
		await ctx.send(f"Hey {ctx.author.mention}! You can't use this command. Only users with the {role.name} role may use this command!")

@client.command()
async def info(ctx,reference=None):
	if reference != None:
		reference = reference.lower()
		print(f"Command >info running in {ctx.guild.name}...")
		if reference in list(partyObjects.keys()):
			popularity = partyObjects[reference].getPoints()			
			for i in client.emojis:
				if i.name == reference.upper():
					msgEmoji = i.id
			if popularity > 0 and popularity <=49:
				popPhrase = "disliked"
			elif popularity > 49 and popularity <= 70:
				popPhrase = "obscure"
			elif popularity > 70 and popularity <=100:
				popPhrase = "somewhat popular"
			elif popularity > 100 and popularity <=140:
				popPhrase = "popular"
			elif popularity > 140 and popularity <= 200:
				popPhrase = "very popular"
			elif popularity > 200:
				popPhrase = "overwhelmingly popular"
			await ctx.send(f"The {partyObjects[reference].getName()} Party had {partyObjects[reference].getMembers()} counted members in the last midterm election.\n\nThe {partyObjects[reference].getName()} Party is currently {popPhrase}. <:{reference}:{msgEmoji}>")
		else:
			await ctx.send("A valid reference must be provided (e.g. MP, UCP, NUP).")
	else:
		await ctx.send("A reference must be provided (e.g. MP, UCP, NUP).")

@client.command()
async def house(ctx,reference=None):
	if reference != None:
		reference = reference.lower()
		print(f"Command >house running in {ctx.guild.name}...")
		if reference in list(partyObjects.keys()):
			house = (partyObjects[reference].getPoints() // 20) + 1
			await ctx.send(f"Based on data taken in the most recent midterm and current popularity figures, the {partyObjects[reference].getName()} Party should have {house} seats in the House of Representatives.")
		else:
			await ctx.send("A valid reference must be provided (e.g. MP, UCP, NUP).")
	else:
		await ctx.send("A reference must be provided (e.g. MP, UCP, NUP).")

@client.command()
async def popularity(ctx,reference=None):
	role = discord.utils.find(lambda r: r.name == 'Eternal Press Secretary', ctx.message.guild.roles)
	if role in ctx.author.roles: ###CHANGE ABOVE TO ADMINISTRATOR
		if reference != None:
			reference = reference.lower()
			print(f"Command >popularity running in {ctx.guild.name}...")
			if reference in list(partyObjects.keys()):
				await ctx.send(f"The {partyObjects[reference].getName()} Party has {partyObjects[reference].getPoints()} Popularity points, {partyObjects[reference].getExtras()} of which are bonus.")
			else:
				await ctx.send("A valid reference must be provided (e.g. MP, UCP, NUP).")
		else:
			await ctx.send("A reference must be provided (e.g. MP, UCP, NUP).")
	else:
		await ctx.send(f"Hey, {ctx.author.mention}! You can't run this command! Only users with the {role.name} role may use this command.")

@client.command()
async def members(ctx,reference=None,newMembers=None):
	role = discord.utils.find(lambda r: r.name == 'Eternal Press Secretary', ctx.message.guild.roles)
	if role in ctx.author.roles: ###CHANGE ABOVE TO ADMINISTRATOR
		if reference and newMembers != None:
			reference = reference.lower()
			print(f"Command >members running in {ctx.guild.name}...")
			if reference in list(partyObjects.keys()):
				if newMembers.isdigit():
					partyObjects[reference].setMembers(int(newMembers))
				else:
					await ctx.send("An integer must be specified.")
				saveObjects()
				createObjects()
				await ctx.send(f"The {partyObjects[reference].getName()} Party now has {partyObjects[reference].getMembers()} counted members.")
			else:
				await ctx.send("A valid integer value and reference must be provided (>members [reference] [integer]).")
		else:
			await ctx.send("A valid integer value and reference must be provided (>members  [reference] [integer]).")
	else:
		await ctx.send(f"Hey, {ctx.author.mention}! You can't run this command! Only users with the {role.name} role may use this command.")

@client.command()
async def addpoints(ctx,reference=None,points=None):
	role = discord.utils.find(lambda r: r.name == 'Eternal Press Secretary', ctx.message.guild.roles)
	if role in ctx.author.roles: ###CHANGE ABOVE TO ADMINISTRATOR
		if reference and points != None:
			reference = reference.lower()
			print(f"Command >addpoints running in {ctx.guild.name}...")
			if reference in list(partyObjects.keys()):
				if points.isdigit():
					points = int(points)
					currentPoints = partyObjects[reference].getExtras()
					newPoints = currentPoints + points
					partyObjects[reference].setExtras(newPoints)
				else:
					await ctx.send("An integer must be specified.")
				saveObjects()
				createObjects()
				await ctx.send(f"The {partyObjects[reference].getName()} Party now has {partyObjects[reference].getPoints()} popularity points.")
			else:
				await ctx.send("A valid integer value and reference must be provided (>points [reference] [integer]).")
		else:
			await ctx.send("A valid integer value and reference must be provided (>points  [reference] [integer]).")
	else:
		await ctx.send(f"Hey, {ctx.author.mention}! You can't run this command! Only users with the {role.name} role may use this command.")

@client.command()
async def removepoints(ctx,reference=None,points=None):
	role = discord.utils.find(lambda r: r.name == 'Eternal Press Secretary', ctx.message.guild.roles)
	if role in ctx.author.roles: ###CHANGE ABOVE TO ADMINISTRATOR
		if reference and points != None:
			reference = reference.lower()
			print(f"Command >removepoints running in {ctx.guild.name}...")
			if reference in list(partyObjects.keys()):
				if points.isdigit():
					points = int(points)
					currentPoints = partyObjects[reference].getExtras()
					if currentPoints < points:
						newPoints = 0
					else:
						newPoints = currentPoints - points
					partyObjects[reference].setExtras(newPoints)
				else:
					await ctx.send("An integer must be specified.")
				saveObjects()
				createObjects()
				await ctx.send(f"The {partyObjects[reference].getName()} Party now has {partyObjects[reference].getPoints()} popularity points.")
			else:
				await ctx.send("A valid integer value and reference must be provided (>points [reference] [integer]).")
		else:
			await ctx.send("A valid integer value and reference must be provided (>points  [reference] [integer]).")
	else:
		await ctx.send(f"Hey, {ctx.author.mention}! You can't run this command! Only users with the {role.name} role may use this command.")

@client.command()
async def newparty(ctx,newReference=None,newName=None):
	role = discord.utils.find(lambda r: r.name == 'Eternal Press Secretary', ctx.message.guild.roles)
	if role in ctx.author.roles:
		if (newReference and newName != None) and not (newReference in list(partyObjects.keys() ) ):
			newName = newName.title()
			newReference = newReference.lower()
			partyRefs.append(newReference)
			partyObjects[newReference] = Party(newName,0,50)
			saveObjects()
			await ctx.send(f"The {newName} Party has been added with party reference {newReference}.")
		else:
			await ctx.send("A valid reference and name must be provided (>newparty [reference] [name]).")	
	else:
		await ctx.send(f"Hey, {ctx.author.mention}! You can't run this command! Only users with the {role.name} role may use this command.")

@client.command()
async def election(ctx,reference):
	reference = reference.lower()
	print(f"Command >election running in {ctx.guild.name}...")
	if reference in list(partyObjects.keys()):
		message = await ctx.send(f'React to this message to vote for the\n\n{partyObjects[reference].getName().upper()} PARTY\n\nin the House of Representatives.')
		msgEmoji = ""
		for i in client.emojis:
			if i.name == reference.upper():
				msgEmoji = i.id
		await message.add_reaction(f"<:{reference}:{msgEmoji}>")
	else:
		await ctx.send(f'Invalid party reference! Oopsie!')

messageReplyFunnys = {
	"ok":"https://media.discordapp.net/attachments/602932168783822860/912776326405054464/ok.gif",
	"ok and?":"https://tenor.com/view/ok-and-ok-and-caption-trade-gif-21164436",
	"ping":"PONG!",
	"doin ya mom":"https://tenor.com/view/ass-funny-mom-doin-your-mom-ray-william-johnson-gif-19785274",
	"bruhhh":"https://tenor.com/view/bruh-nawh-no-way-fr-gif-22615915",
	"woman moment":"https://tenor.com/view/crungo-woman-moment-gif-18206520",
	"cum":"https://tenor.com/view/mulan-cum-mouth-full-load-gif-18600334",
	"sneed":"https://tenor.com/view/sneed-cat-based-nae-nae-dancing-dance-gif-16884764",
	"squid game":"https://tenor.com/view/gihun-gihun-smile-smile-fades-squid-game-jung-jae-gif-23380735",
	"<@!398909858847391755>":"https://tenor.com/view/rule49-goku-goku-rules-mods-ping-gif-23408530",
	"flashbang out":"https://tenor.com/view/think-fast-flashbang-gif-19261198",
	"nice cock":"https://tenor.com/view/chicken-cock-play-with-my-cock-cock-swing-steady-head-gif-17954343",
	"i am the press secretary":"<@!398909858847391755>",
	"cunny":"https://tenor.com/view/cunny-gif-20668002",
	"hi":"https://tenor.com/view/hi-cat-meme-shit-yourself-gif-20847548",
	"hello":"https://tenor.com/view/doom-eternal-hello-chat-doom-gif-23180044",
	"fnf":"https://tenor.com/view/rule2no-friday-night-funkin-fnf-friday-night-funkin-goku-dbs-gif-22463804",
	"jew":"https://tenor.com/view/cool-it-cool-it-with-the-antisemetic-remarks-patrick-bateman-american-psycho-anti-semetic-gif-21354111",
	"bot broken":"https://cdn.discordapp.com/attachments/888185052435972126/892036063621677076/473525ed-dd94-41d4-8a7b-643edd14da46.gif",
	"grandma":"https://media.discordapp.net/attachments/387370085108547605/908046108721307668/IMG_0824.gif",
	"begone":"https://media.discordapp.net/attachments/456352116269907968/913191179124867072/C23A36FE-94DC-485C-9F67-CD2754696041.gif",
	"mod hat":"https://tenor.com/view/discord-mod-life-of-a-discord-mod-discord-moderator-family-guy-gif-22385062",
	"oorah":"https://tenor.com/view/sir-yes-sir-oorah-oorah-marine-twerk-army-gif-22931251",
	"xd":"https://cdn.discordapp.com/attachments/821222063901245440/915641492431831060/XDXDXDXD.jpg",
	"real":"NOT FAKE"
}

messageBlacklist = ["McCorkle Jones Simp","Beatrice","SkurtBOT","Xenomorth"]

@client.event
async def on_message(message):
	for i in list(messageReplyFunnys.keys()):
		if message.content.lower() == i and message.author.name not in messageBlacklist:
			print(f"ayo {message.author.name.lower()} just said {i}")
			await message.channel.send(messageReplyFunnys[i])
			break
		elif message.content.lower() == i and message.author.name in messageBlacklist:
			print(f"lmao {message.author.name.lower()} just tried to say something funny")
			await message.channel.send("unfunny meme please leave the server")
	await client.process_commands(message)

@client.command()
async def funny(ctx):
	random = dice.randint(0,len(messageReplyFunnys)-1)
	await ctx.send(list(messageReplyFunnys.values())[random])

@client.event
async def on_ready():
	createObjects()
	createCandidates()
	print(f'{client.user} is ready for action!')

client.run(TOKEN)