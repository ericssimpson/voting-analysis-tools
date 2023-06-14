import pandas as pd
import numpy as np

print("Welcome to Election Module. Please input as asked.")


#Input data, candidate list
data=pd.read_csv(str(input("Please enter the voting data filename. Ensure that the data only is an array of Ranks assigned as columns and individual voters' choices as Rows:- ")))
n=int(input("Enter number of contestants:- "))
cand=[]
u=0
while u<n:
	cand.append(str(input("Please enter candidate name/ID, as designated in the voting data provided:- ")))
	u+=1
cand=np.array(cand)

#Number of ranks assigned
nranks=data.shape[1]

#Clean data
data=data.replace(['undervote'],-1)
data=data.replace(['overvote'],0)
#Now Undervotes are designated as -1 and Overvotes as 0
data.drop(data.loc[(data['Rank 1']==-1) & (data['Rank 2']==-1)].index, inplace=True)
data.drop(data.loc[(data['Rank 1']==0)].index, inplace=True)
#Blanks dropped

j=0
i=1
while j==0 & i<(nranks):
	if i==1:
		print("Contesting Candidates are :", cand)
	
	counts =(data.drop(data.loc[(data['Rank 1']==-1)|(data['Rank 1']==0)].index, inplace=False))['Rank 1'].value_counts()
	winner = counts.idxmax()
	majority=counts.max()
	total=0
	for u in range(len(cand)):
		total+=data['Rank 1'].value_counts()[cand[u]]
	
	#Majority
	if majority>(total/2.):
		print("The Round %i counting is as follows:"%i)
		print("Candidate ID | Votes")
		print(counts)
		print("Candidate", winner, "wins with a",(100.0*(majority/total)),"majority in Round %i. \n"%i)
		j=1

	#No majority
	else:
		minority=counts.min()
		loser=counts.idxmin()
		print("The Round %i counting is as follows:"%i)
		print("Candidate ID | Votes")
		print(counts)
		print("Candidate", loser, "is eliminated in Round %i. Moving on to next round... \n"%i)
		b = np.array([loser])
		cand = np.setdiff1d(cand,b)
		print('Remaining Candidates are :', cand)
		#Remove eliminated candidate from Rank 1 and replace them with next non loser choice as per voter's ranking
		for u in (data.loc[(data['Rank 1']==loser)].index):
			if (data.at[u,'Rank 2'])!=loser:
				(data.at[u,'Rank 1'])=(data.at[u,'Rank 2'])
			else:
				if (data.at[u,'Rank 3'])!=loser:
					(data.at[u,'Rank 1'])=(data.at[u,'Rank 3'])
				else:
					if (data.at[u,'Rank 4'])!=loser:
						(data.at[u,'Rank 1'])=(data.at[u,'Rank 4'])
					else:
						(data.at[u,'Rank 1'])=-1
		data=data.replace([loser],0)
		i+=1
	
	

	

