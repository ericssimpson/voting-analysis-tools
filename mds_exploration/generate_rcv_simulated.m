% set up
a=1:Ncand;
w = [1./randperm(Ncand)];
Nsimvoters=200000;
N = Nsimvoters*numranks; % don't forget to get numranks from someplace

% make some randomly chosen groups of candidates (NYC style)
[~,R] = histc(rand(1,N),cumsum([0;w(:)./sum(w)])); % random indices
R = a(R); % random numbers
selections=reshape(R,Nsimvoters,numranks); % random groups of numranks candidates
clear R

% just make the ballots the same as the selections - toy version to make
% sure mdscale() approach works
% ballots=sort(selections,2); % make each ballot ordered 
% y=datasample([1:Nsimvoters],Nsimvoters/2);
% for i=1:Nsimvoters/2
%    ballots(y(i),:)=flip(selections(y(i),:));
% end

tic
% assume candidates are at 1/(N+1) spacing
candidateposition=a./(Ncand+1);
% pick a random location on [0, 1] axis for voter
voterposition=rand(Nsimvoters,1);
% calculate distance to each candidate
clear ballots
for i=1:Nsimvoters
    dist_to_candidate=abs(voterposition(i)-candidateposition(selections(i,:)));
    [~,preferences]=sort(dist_to_candidate);
    ballots(i,:)=selections(i,preferences);
end
% rank candidates by distance, make that the ballot
toc