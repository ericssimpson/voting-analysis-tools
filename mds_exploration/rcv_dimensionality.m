% setup for particular election



%Ncand=length(find(choices<50)); % look in choices

%NYC
load('NYCspace.mat')
names=["Adams" "Wiley" "Donovan" "Stringer" "Garcia" "Morales" "Prince" "Yang" "McGuire" "Taylor" "Chang" "Foldenauer" "Wright" "skipped" "overvote" "writein"];
choices=[1,2,3,4,5,6,7,8,9,10,11,12,13,97,98,99];
%Ncand=9; % restrict to better-known candidates

%Maine
%choices=[1,2,3,4,97,98,99];
%names=["Poliquin" "Golden" "Bond" "Hoar" "skipped" "overvote" "writein"];
%Ncand=4; % restrict to better-known candidates

%counts=zeros(Ncand);
% done with setup for particular election

%%%%%%%%%%%%%%%%%%%%%%%%%

% now start working with cast vote records
numballots=size(ballots,1); numranks=size(ballots,2);

% ranked candidates 1...C; other codes count down from 99
% get rid of zeros to simplify later calculations
for i=1:numballots
    for j=1:numranks
        if ballots(i,j)==0
            ballots(i,j)=97;
        end
    end
end

% count up frequencies of consecutive-pair ballot choices
for i=1:numballots
    for j=1:numranks-1
        if and(ballots(i,j)<=Ncand,ballots(i,j+1)<=Ncand)
            counts(ballots(i,j),ballots(i,j+1))=counts(ballots(i,j),ballots(i,j+1))+1;
        end
    end
end

% how many ballots contain a particular pair of preferences anywhere in list?
% this is not efficient but who said I was good at algorithm efficiency
mentioned_together=zeros(Ncand);
for i=1:numballots
    for j=1:numranks
        for k=1:numranks
            if and(ballots(i,j)<=Ncand,ballots(i,k)<=Ncand)
                mentioned_together(ballots(i,j),ballots(i,k))=mentioned_together(ballots(i,j),ballots(i,k))+1;
            end
        end
    end
end

% normalize to frequencies relative to votes cast for the two candidates
freq=counts./mentioned_together;

% combine freq in either direction to create symmetric matrix
% self-self pairs are zeroed out
clear freq_upptri
for i=1:Ncand
    for j=i+1:Ncand
        freq_upptri(i,j)=(freq(i,j)+freq(j,i))/2;
        freq_upptri(j,i)=freq_upptri(i,j);
    end      
end

[maxpairs,inds]=max(freq_upptri)
foo=min(freq_upptri(freq_upptri>0));

d=1./freq_upptri.^0.5; % this is our distrance metric. 1/freq works for randomly generated polarized ballots
% seems robust to ^k, where ^2 causes some distortion, ^0.5 is fine

for i=1:Ncand
    for j=1:Ncand
        if isnan(d(i,j))
            d(i,j)=2/foo;
        end
        if isinf(d(i,j))
            d(i,j)=2/foo;
        end
    end
end
for i=1:1:Ncand
    d(i,i)=0;
end
    
% 1 dimension
YY=mdscale(d,1);
scatter(YY.*0,YY)
hold on
axrange=[min(YY,[],'all') max(YY,[],'all')];
for i=1:Ncand
   text(0.2,YY(i),names(i));
%    text(0.2,YY(i),num2str(i));
end
axis([-1 1.5 axrange*1.2]);

%%%%%%%%%%%%%%%%%%%%%%%%%


% 2 dimensions
Y = mdscale(d,2);
scatter(Y(:,1),Y(:,2))
hold on
axrange=[min(Y,[],'all') max(Y,[],'all')];
foo=abs(axrange(2)-axrange(1))/80;
for i=1:Ncand
   text(Y(i,1)+foo,Y(i,2)+foo,names(i));
   % text(Y(i,1)+foo,Y(i,2)+foo,num2str(i));
end
clear foo
axis([axrange*1.2 axrange*1.2]);
grid on

