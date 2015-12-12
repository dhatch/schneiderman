#data cleaner

import datetime
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

df[['PTS', 'FGA','FTA',"FG","3P"]] = df[['PTS', 'FGA','FTA',"FG","3P"]].astype(int)
df["TS%"]= df["PTS"] / (2 * df["FGA"]+.44*df["FTA"])
df["EFG%"]=(df["FG"]+.5*df["3P"]) / df["FGA"]

df["Age Year"]=1
df["Age Days"]=1
for i in df.index:
	ages=str(df["Age"][i]).split("-")
	df.loc[i,"Age Year"]=int(ages[0])
	df.loc[i,"Age Days"]=int(ages[1])

