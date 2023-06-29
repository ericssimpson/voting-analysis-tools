import pandas as pd
import numpy as np
import csv

print("Welcome to Election Module. Please input as asked.")

#Input data, candidate list--
print("Please arrange the castvote/simulated-vote record into a csv file as an array in the manner described below:- \n 1) Each column from the very first corresponds to a rank, in ascending order from left to right. \n 2) Each row from the very first corresponds to a particular voter's choice(s) \n 3) If a voter has not assigned a particular rank to any candidate, mark 'undervote' in the cell identified by the row corresponding to said voter and the column correspnding to the particular rank.\n 4) If a voter has assigned a particular rank to multiple candidates, mark 'overvote' in the cell identified by the row corresponding to said voter and the column correspnding to the particular rank.\n 5) Separate columns by space/tab and rows by line.")
data=pd.read_csv(str(input("Please enter the data-filename without quotes. (Eg: data.csv) :- ")), header=None) #Only works with instructions above followed to the letter
n=int(input("Enter number of contestants:- "))
cand=[]
u=0
while u<n:
	cand.append(str(input("Please enter candidate name/ID, as designated in the voting data provided:- ")))
	u+=1
cand=np.array(cand)
nranks=data.shape[1]#max no. of ranks assigned 
nvotes=data.shape[0]
#----------------------------
def clean(data):
#-----------------------
	data=data.replace(['undervote'],-1)
	data=data.replace(['overvote'],0)
	return data
	#Now Undervotes are designated as -1 and Overvotes as 0
#----------------------

#print("Contesting Candidates are :", cand)

def irv(data, cand): #Input Data Array, Cand Array
	data=clean(data)
	nranks=data.shape[1]#max no. of ranks assigned 
	nvotes=data.shape[0]
	
	labelstodrop=[]
	for i in range(nvotes):
		for j in range(nranks - 1):
			k=j+1
			if int(data.iloc[i,j])==-1 & int(data.iloc[i,k])==-1:
				labelstodrop.append(i)
	data.drop(labels=labelstodrop, axis=0, inplace=True)
#Dropping votes with 2 consecutive undervotes as per Alaska IRV Law

	data.drop(data.loc[(data[0]==0)].index, inplace=True)#Votes where candidate has voted atleast 2 candidates as Rank 1 are invalidated as per Alaska IRV Law
	nranks=data.shape[1]#max no. of ranks assigned 
	nvotes=data.shape[0]

	for i in range(nvotes):
		for j in range(nranks):
			if data.iloc[i,j]==-1:
				for k in range(j,nranks):
					if k<nranks-1:
						data.iloc[i,k]=data.iloc[i,k+1] #Taking next rank assigned candidate if current rank assigned to none. 
					if k==nranks-1:
						data.iloc[i,k]=-1

	j=0
	i=1

	while j==0 & i<(nranks):
		#print("Round %i | Contesting Candidates are :"%i, cand)
		counts =(data.drop(data.loc[(data[0]==-1)|(data[0]==0)].index, inplace=False))[0].value_counts()
		winner = counts.idxmax()
		majority=counts.max()
		total=0
		for u in range(len(cand)):
			total+=data[0].value_counts()[cand[u]]

		#print("The Round %i counting is as follows:"%i)
		#print("Candidate ID | Votes")
		#print(counts)
		#Majority
		if majority>(total/2.):
		#	print("Candidate", winner, "wins with a",(100.0*(majority/total)),"majority in Round %i. \n"%i)
			j=1

		#No majority
		else:
			minority=counts.min()
			loser=counts.idxmin()
		#	print("Candidate", loser, "is eliminated in Round %i. Moving on to next round... \n"%i)
			b = np.array([loser])
			cand = np.setdiff1d(cand,b)
		#	print('Remaining Candidates are :', cand)
			#Remove eliminated candidate from Rank 1 and replace them with next non loser choice as per voter's ranking
			for u in (data.loc[(data[i-1]==loser)].index):
				for l in range(i,nranks):
					if data.at[u,l]!=loser:
						(data.at[u,i-1])=(data.at[u,l])
						break
			#if (data.at[u,i])!=loser:
			#	(data.at[u,i-1])=(data.at[u,i])
			#else:
			#	if (data.at[u,i+1])!=loser:
			#		(data.at[u,i-1])=(data.at[u,i+1])
			#else:
			#		if (data.at[u,i+2])!=loser:
						#(data.at[u,i-1])=(data.at[u,'Rank 4'])
			#		else:
			#			(data.at[u,'Rank 1'])=-1
			data=data.replace([loser],0)
			i+=1
	return winner

print(irv(data,cand))
	

