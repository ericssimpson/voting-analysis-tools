N=1000; voters=0:1/(N-1):1;
fw=0.3;
Ncand=3;
% I realize I should be able to do this analytically but I am lame today
% My excuse is that someday I will do this for some other distribution, or
% for a 2-D voter landscape.
%
% For running the election, this script calls election.m by Ben Petschel
% https://www.mathworks.com/matlabcentral/fileexchange/28521-election?s_tid=mwa_osa_a

fpp_rcv_match=0;
for j=1:200
    candidates=sort(rand(1,Ncand))*0.7+0.15;
    for i=1:N
        candidate_perceived=candidates+rand(1,Ncand)*fw-fw/2; %add random numbers to get voter perception
        dists=abs(voters(i)-candidate_perceived);
        [b,castvote(i,:)]=sort(dists); % generate cast vote record
        falsevote(i,:)=castvote(i,:);
        if falsevote(i,1)==Ncand 
            foo=rand;
            if foo<0.5
                falsevote(i,2:Ncand)=[1:(Ncand-1)]; % generate a ranking where farthest opponent gets ranked second
            end
        end
    end
    firstpast(j,:)=histcounts(castvote(:,1),[0.5:1:Ncand+0.5]); % first-past-the-post counts
    [plurality(j),fptp_winner(j)]=max(firstpast(j,:));
    [foo,method]=election(castvote,'FPP'); fpp_winner(j)=foo;
    [foo2,method]=election(castvote,'pref'); rcv_winner(j)=foo2;
    [foo3,method]=election(falsevote,'pref'); false_winner(j)=foo3;
    if foo==foo2
        fpp_rcv_match=fpp_rcv_match+1;
    end 
end

[b,ind]=sort(plurality);
for k=1:5
    matches(k)=0;falsematches(k)=0;
    avg_fpp(k)=mean(plurality(ind((k-1)*40+1:(k*40-1))));
    for kk=1:40
        ii=kk+k*40-40;
        if fpp_winner(ind(ii))==rcv_winner(ind(ii))
            matches(k)=matches(k)+1;
        end
        if false_winner(ind(ii))~=rcv_winner(ind(ii))
            falsematches(k)=falsematches(k)+1;
        end
    end
end

plot(avg_fpp/10,matches/40,'o-k')
hold on
axis([33 58 0 1.05])
grid on
xlabel('First-choice finisher''s vote share (%)')
ylabel('Probability of being Condorcet winner')
title('True-positive rate')

plot(avg_fpp/10,falsematches/40,'o-r')
hold on
axis([33 58 0 0.25])
grid on
xlabel('First-choice finisher''s vote share (%)')
ylabel('Probability that extreme candidate can game election')
title('False-positive rate')