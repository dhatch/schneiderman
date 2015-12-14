#data cleaner

#import datetime
import pandas


fileName = "carmelo.csv"
df = pandas.read_csv(fileName)
df.columns =["Rk","G","Date","Age","Tm","Home","Opp","ScoreDiff","GS","MP",
"FG","FGA","FG%","3P","3PA","3P%","FT","FTA","FT%","ORB","DRB","TRB",
"AST","STL","BLK","TOV","PF","PTS",	"GmSc",	"+/-","DFS"]
#get column names correct


df['Home'][pandas.isnull(df['Home'])]=True #Make Home and Away Boolean
df['Home'][df['Home']=='@']=False #Make Home and Away Boolean
df=df[df.Rk != "Rk"] #get rid of extra header columns
df=df[df.GS != "Did Not Play"] #take away games they didn't appear in 
df=df[df.GS != "Inactive"] #take away games they were inactive for 


#df=df.convert_objects(convert_dates=True, convert_numeric=True)
df.Date=pandas.to_datetime(df.Date)

df[["Rk","G","GS","FG","FGA","3P","3PA","FT",
"FTA","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS","+/-"]]=df[["Rk","G","GS","FG","FGA","3P","3PA",
"FT","FTA","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS","+/-"]].astype(int)

df[["FG%","3P%","FT%","GmSc","DFS"]]=df[["FG%","3P%","FT%","GmSc","DFS"]].astype(float)

#add a column for True Shooting Percentage, a better metric for a players shooting ability
df["TS%"]= df["PTS"] / (2 * df["FGA"]+.44*df["FTA"]) 
#add a column for Effective Field Goal Percentage, a better metric for a players shooting ability
df["EFG%"]=(df["FG"]+.5*df["3P"]) / df["FGA"]

df["AgeYear"]=1
df["AgeDays"]=1
for i in df.index:
	ages=str(df["Age"][i]).split("-")
	df.loc[i,"AgeYear"]=int(ages[0])
	df.loc[i,"AgeDays"]=int(ages[1])
	df.loc[i,"MP"]=int(str(df["MP"][i]).split(":")[0])


df.MP=df.MP.astype(int)
#convert minutes played to integers and take away seconds 
#Add Columns for total points up to that game
df["SFG"]  = df.FG.cumsum()-df.FG
df["SFGA"] = df.FGA.cumsum()-df.FGA
df["S3P"]  = df["3P"].cumsum()-df["3P"]
df["S3PA"] = df["3PA"].cumsum()-df["3PA"]
df["SFT"]  = df.FT.cumsum()-df.FT
df["SFTA"] = df.FTA.cumsum()-df.FTA
df["SORB"] = df.ORB.cumsum()-df.ORB
df["SDRB"] = df.DRB.cumsum()-df.DRB
df["STRB"] = df.ORB+df.DRB
df["SAST"] = df.AST.cumsum()-df.AST
df["SSTL"] = df.STL.cumsum()-df.STL
df["SBLK"] = df.BLK.cumsum()-df.BLK
df["STOV"] = df.TOV.cumsum()-df.TOV
df["SPF"]  = df.PF.cumsum()-df.PF
df["SPTS"] = df.PTS.cumsum()-df.PTS
df["SDFS"] = df.DFS.cumsum()-df.DFS

#Add running averages up to that game 
df["AFG"]  = df["SFG"]  / df.G.shift(1)
df["AFGA"] = df["SFGA"] / df.G.shift(1)
df["A3P"]  = df["S3P"]  / df.G.shift(1)
df["A3PA"] = df["S3PA"] / df.G.shift(1)
df["AFT"]  = df["SFT"]  / df.G.shift(1)
df["AFTA"] = df["SFTA"] / df.G.shift(1)
df["AORB"] = df["SORB"] / df.G.shift(1)
df["ADRB"] = df["SDRB"] / df.G.shift(1)
df["ATRB"] = df.AORB+df.ADRB
df["AAST"] = df["SAST"] / df.G.shift(1)
df["ASTL"] = df["SSTL"] / df.G.shift(1)
df["ABLK"] = df["SBLK"] / df.G.shift(1)
df["ATOV"] = df["STOV"] / df.G.shift(1)
df["APF"]  = df["SPF"]  / df.G.shift(1)
df["APTS"] = df["SPTS"] / df.G.shift(1)
df["ADFS"] = df["SDFS"] / df.G.shift(1)
df["Rest"]=(df.Date-df.Date.shift(1))/86400000000000
df.loc[0,"Rest"]=14 #Dummy Variable for start of season
df.Rest=df.Rest.astype(int)

df.to_csv(fileName)
