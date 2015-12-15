#draft kings cleaner

import pandas

fileName="DKSalaries.csv"
df = pandas.read_csv(fileName)
for i in df.index:
		games=str(df["GameInfo"][i]).replace('@',' ').split()
		df.loc[i,"HomeTeam"]=games[0]
		df.loc[i,"AwayTeam"]=games[1]

df["Home"] = df.teamAbbrev==df.HomeTeam
df.to_csv(fileName)

