function [winner,method]=election(pref,method,varargin)
% ELECTION - determine the election winner(s) under various methods
%
%   winner = election(pref)
%   winner = election(pref,method)
%   winner = election(pref,method,p1,...)
%   [winner,method] = election(pref,'all')
%
% Inputs:
%   pref is an array with one row per voter listing the voter's order of 
%     preferences of candidates 1 to N.  For voters with incomplete preferences,
%     the row can be filled with zeros or NaN or inf values as required.
%     For methods that depend only on the primary votes (first preferences), the
%     array can be a column vector.
%
%     Any invalid votes are ignored (definition of valid depends on the method,
%     but unless otherwise specified the primary-vote-based methods require only
%     the first preference to be a positive integer, and the preference-based 
%     methods also require the row to have no repeats).
%
%   method is a string with the name of the election method to use (see below). 
%     The names are case-insensitive and can be abbreviated to the first 3
%     letters of the name (except for the minimax methods abbreviated
%     'mmw','mmm','mmv' respectively, and Schwartz/Schulze abbreviated 'scw'
%     and 'scu' respectively).
%
%     Multiple methods can be used by making method a cell array of names; also
%     specifying method='all' is equivalent to specifying the list of all
%     supported methods (see below).
%
%   p1,... are optional parameters to be passed to the specific method (not
%     supported if method='all' or method is a cell array).
%
% Outputs:
%   winner is an array containing the list of equally-ranked winners of the 
%     election using the specified method, or if several methods were specified 
%     then the result is a cell array with one entry per method.  Many of the
%     methods do not always produce a single result, and the result can be empty
%     for example if there are no valid votes.
%
%   methods returns the list of methods that were used if 'all' was specified, 
%     otherwise it is identical to the input method.
%
% Supported election methods:
%
%   Primary votes:
%
%     'dictator' - voter 1 determines the winner (no winner if their first
%       preference is not valid).
%
%     'hat' - randomly selected according to number of primary votes.
%
%     'FPP' - first past the post: winner has the most primary votes.
%
%     'runoff' - (also known as two-round system or ballotage): if no candidate
%       has an absolute majority of the primary vote then returns the two
%       candidates with the most primary votes.  This is obviously called 
%       two-round because if no single winner is determined then a second 
%       election must be conducted using the two winners of the first.
%
%     'runoff', P1 - if input P1 is provided, then if no absolute winner occurs 
%       all candidates with less than a fraction p1 of the vote are excluded.
%
%     'exhaustive' - similar to runoff, but only the candidate(s) with the least
%       number of primary votes are excluded.
%
%   non-Condorcet Preferential:
%
%     'pref' - preferential voting (also known as instant runoff, alternative
%       vote, single transferable vote): loser's votes are allocated to their
%       voters next preferences, until an absolute majority is attained.
%
%     'contingent' - same as 'runoff' but automatically performs the second 
%       round based on the full set of preferences.
%
%     'Coombs' - a method similar to the instant runoff preferential method,
%       where if there is no majority then the candidate to be excluded is the
%       one that is ranked at the bottom of the preferences by the most voters.
%
%     'Borda' - (Borda count): candidates score according to their rank in the 
%       preferences, for example with 5 candidates, each candidate gets 5 points
%       for a primary vote, 4 for a secondary, down to 1 point for a lowest-rank
%       preference.  If PREF has M columns and M<N (N is the number of 
%       candidates) then each vote gives [M,...,1] points.  The candidate(s) 
%       with the most points wins.
%
%     'Borda', P1 - if parameter P1 is specified as a function handle, then 
%       a position K in a voter's preferences will give P1(K) points.  The
%       function can also be of the form P1(K,M) where M is the number of
%       preferences each voter is allowed (the default is P1=@(k,m)m+1-k).  
%       Other examples are P1=@(k)1./k (Nauru), and 
%       s=[12,10,8:-1:1];P1=@(k)reshape(s(k),size(k)); (Eurovision contest).
%
%     'Nanson', P1 - a variation of the Borda method, where the candidates with
%       a score at or below the average score are removed from the ballot and
%       the scores are recalculated, repeating until a winner is obtained.  See
%       Borda method for description of input P1.  For simplicity it is assumed
%       that every vote must fully specify preferences.
%
%     'Baldwin', P1 - a variation of the Borda method, where the candidate with
%       the lowest scores is eliminated from the ballot and the scores are
%       recalculated, repeating until a single winner is obtained. For
%       simplicity it is assumed that every vote must fully specify preferences.
%
%     'Bucklin' - a method where if there is no clear majority in the first
%       round then all the second preferences are added to the vote, and
%       continuing until at least one candidate has a "majority" (defined
%       relative to the number of voters).  At the second and subsequent rounds,
%       if there are several candidates with a majority then the one with the
%       highest majority becomes the winner.
%
%   Condorcet (based on pairwise runoffs from preferences - for these, we
%     consider the matrix C where C(I,J) is the number of voters that prefer I 
%     to J (with the voter's unstated preferences ranked equal worst).
%     If C(I,J) > C(J,I) then I wins the pairwise runoff against J.  
%     Condorcet methods are those that produce the "Condorcet winner" (the
%     candidate that pairwise beats all other candidates) if one exists.
%
%     'Smith' - determines the Smith set, which is the smallest set of 
%       candidates that beat all other candidates outside the set.
%
%     'Schwartz' - the union of all minimal sets of candidates that are
%       unbeatable (i.e. win or possibly tie) by any candidate outside the sets.
%
%     'Landau' - (also known as uncovered set or Fishburn set): the set of 
%       candidates that beat or tie with all other candidates, or for any they
%       don't, beat/tie with a third candidate that beats/ties with the other.
%       In other words, I is a winner if for all J, I=J or C(I,J)>=C(J,I) or
%       C(I,K)>=C(K,I) and C(K,J)>=C(J,K) for some K.
%
%     'Copeland' - The winner(s) are those win the most pairwise runoffs.
%
%     'minimaxwinvote' - A minimax method, where the winner is the candidate
%       with the least worst score against it.  If the score S(I,J) is the score
%       of I against J, then J wins if max_I{S(I,J)} is not more than that for
%       any other candidate.  For this version, the score is the  number of 
%       "winning votes": S(I,J) = C(I,J) if C(I,J)>C(J,I), or zero otherwise.
%
%     'minimaxmargin' - A minimax method similar to minimaxwinvote, except the
%       score is determined as S(I,J) = C(I,J)-C(J,I).
%
%     'minimaxvote' - (also known as pairwise opposition): a minimax method, 
%       where the score is simply S(I,J)=C(I,J), however this method is not 
%       strictly Condorcet.
%
%     'Kemeny-Young' - finds the preference sequence that maximizes the 
%       Kemeny-Young score.  For a sequence (K1,...,KN), the Kemeny-Young score
%       is the sum of C(Ki,Kj) over all 1<=i<j<=N.  This counts the number of
%       voters whose preferences of I over J match that of the sequence, for all
%       possible combinations I, J.  The winner is the first member of the
%       sequence with maximum score (or winners, if there are several).
%
%     'rankedpairs' - (also known as the Tideman method): sort all the pairs
%       (I,J) where I beats J (i.e. C(I,J) > C(J,I)) in the order such that 
%       (I,J) > (K,L) if C(I,J) > C(K,L) (comparing I,K or J,L if a tie).  Then 
%       use the pairs (I,J) to determine the final ordering of the candidates, 
%       by taking them in the given order and rejecting any that would lead to a
%       cycle.  The winner is the first in the final order. Under this ordering
%       some of the pairs could still be equivalent, so to avoid ambiguities we
%       check all permutations of the equivalent orderings and include a
%       candidate as a winner if any of the permutations makes them a winner.
%
%     'Schulze' - this method uses the concept of indirect defeats.  If there is
%       a path from I to J where each member of the path defeats the next in the
%       path in a pairwise comparison, then the strength of that path is the 
%       lowest number of winning votes along that path.  I indirectly defeats J
%       if the maximum strength of a path from I to J is greater than J to I.
%       The Schulze winner(s) can also be determined by considering a directed
%       graph with edges I to J with weight C(I,J) if I defeats J.  At each
%       step, a vertex J is removed if there is a path from I to J but not J to
%       I, otherwise if none can be found then the lowest weight edge is
%       removed; the remaining vertices correspond to the winners.
%
%
%
% Examples:
%
%   election([1,2,3;1,2,3;2,3,1],'pref') % returns 1
%   election([1,2,3;3,1,2;2,3,1],'pref') % returns [1,2,3]
%
%   % different methods can have different results
%   [winner,method]=election([1,2,3; 1,2,3; 2,3,1; 3,2,1],'all');
%   fmt = '%-20s%s\n';
%   fprintf(1,fmt,'Method:','Winner(s):');
%   for i=1:numel(winner)
%     fprintf(1,fmt,method{i},mat2str(winner{i}));
%   end;

% Author: Ben Petschel 21/8/2010
%
% Version history:
%   21/8/2010 - first release

if nargin==0
  error('election:nargin:noargs','at least one input argument required');
elseif nargin==1
  method = 'pref';
elseif isequal(method,'all')
  method = {'dictator','hat','FPP','runoff','exhaustive','pref','contingent',...
  'Coombs','Borda','Nanson','Baldwin','Bucklin','Smith','Schwartz','Landau',...
  'Copeland','minimaxwinvote','minimaxmargin','minimaxvote','Kemeny-Young',...
  'rankedpairs','Schulze'};
end;

if iscell(method)
  winner = cell(size(method));
  for i=1:numel(method)
    winner{i} = election(pref,method{i}); % params ignored for cell array method
  end;
  return
end;

if isempty(pref)
  % all methods will assume pref is non-empty
  winner = [];
  return
end;

switch lower(method)

  case {'dic','dictator'}
    winner = dictator(pref);

  case 'hat'
    winner = hat(pref);

  case 'fpp'
    winner = fpp(pref);

  case {'run','runoff'}
    winner = runoff(pref,varargin{:});

  case {'exh','exhaustive'}
    winner = exhaustive(pref,varargin{:});

  case {'pre','pref'}
    winner = prefelim(pref,1); % pref elimtype = 1 for preferential system

  case {'con','contingent'}
    winner = prefelim(pref,2,varargin{:}); % pref elimtype = 2 for contingent

  case {'coo','coombs'}
    winner = prefelim(pref,3); % pref elimtype = 3 for Coombs

  case {'bor','borda'}
    winner = bordaelim(pref,0,varargin{:}); % elimtype = 0 for Borda method

  case {'nan','nanson'}
    winner = bordaelim(pref,1,varargin{:}); % elimtype = 1 for Nanson method

  case {'bal','baldwin'}
    winner = bordaelim(pref,2,varargin{:}); % elimtype = 2 for Baldwin method

  case {'buc','bucklin'}
    winner = bucklin(pref);

  case {'smi','smith'}
    winner = smith(pref);

  case {'scw','schwartz'}
    winner = schwartz(pref);

  case {'lan','landau'}
    winner = landau(pref);

  case {'cop','copeland'}
    winner = copeland(pref);

  case {'mmw','minimaxwinvote'}
    winner = minimaxscore(pref,1); % scoretype = 1 for winvote

  case {'mmm','minimaxmargin'}
    winner = minimaxscore(pref,2); % scoretype = 2 for margin

  case {'mmv','minimaxvote'}
    winner = minimaxscore(pref,3); % scoretype = 3 for vote count

  case {'kem','kemeny-young'}
    winner = kemeny(pref);

  case {'ran','rankedpairs'}
    winner = rankedpairs(pref);

  case {'scu','schulze'}
    winner = schulze(pref);

  otherwise
    error('election:method:badmethod','election method not recognized');
end;

end % main function election(...)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% election method implementations
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function winner = dictator(pref)
% voter 1 determines the winner.

if ~isposint(pref(1))
  winner = [];
else
  winner = pref(1);
end;

end % function dictator(...)


function winner = hat(pref)
% randomly selected according to number of primary votes.
% (any invalid primary votes are ignored)

vc = votecount(pref(:,1));
if any(vc)
  winner = find(rand<=cumsum(vc)/sum(vc),1,'first');
else
  winner = [];
end; % if any(vc) ... else ...

end % function hat(...)


function winner = fpp(pref)
% first past the post: winner has the most primary votes.

vc = votecount(pref(:,1));
if any(vc)
  winner = find(vc==max(vc));
else
  winner = [];
end; % if any(vc) ... else ...

end % function fpp(...)


function winner = runoff(pref,p1)
% (also known as two-round system or ballotage): if no candidate has an absolute
% majority of the primary vote then returns the two candidates with the most
% primary votes.
%
% If input P1 is provided, then if no absolute winner occurs all candidates with
% less than a fraction p1 of the vote are excluded.

if nargin<2
  p1 = [];
end;

vc = votecount(pref(:,1));
if ~any(vc)
  winner = []; % no valid votes
else
  vc = vc/sum(vc);
  if max(vc) > 1/2
    % have a majority
    winner = find(vc==max(vc));
  else
    % no majority, choose either the top 2 candidates or exclude the candidates
    % with less than the fraction P1 of the vote
    if isempty(p1)
      svc = sort(vc);
      p1 = svc(end-1); % can't have length 1 or this would be picked up already
    end;
    winner = find(vc>=p1);
  end; % if max(vc)>1/2 ... else ...
end; % if ~any(vc) ... else ...

end % function runoff(...)


function winner = exhaustive(pref)
% similar to runoff, but only the candidate(s) with the least number of primary
% votes are excluded.

vc = votecount(pref(:,1));
if ~any(vc)
  winner = []; % no valid votes
else
  vc = vc/sum(vc);
  if max(vc) > 1/2
    % have a majority
    winner = find(vc==max(vc));
  else
    % no majority, exclude the bottom candidate(s) (unless all equal)
    winner = find(vc>min(vc));
    if isempty(winner)
      winner = (1:numel(vc));
    end;
  end; % if max(vc)>1/2 ... else ...
end; % if ~any(vc) ... else ...

end % function exhaustive(...)


function winner = prefelim(pref,elimtype,p1)
% preferential system elimination: elimtype is one of
%  1: standard (instant runoff: losers at each stage have least votes)
%  2: contingent (losers determined by runoff, either top two or percentage)
%  3: Coombs (loser is the one with the most lowest-preference votes)

pvalid = pref(hasnorepeats(pref),:); % ignore votes with repeats
N = max(pvalid(isposint(pvalid))); % number of candidates
if elimtype == 3
  % valid votes must have full set of preferences
  if size(pvalid,2)~=N
    pvalid=[];
  else
    pvalid = pvalid(all(isposint(pvalid),2), :);
  end;
else
  if elimtype == 2 && nargin<3
    p1 = [];
  end;
end; % if elimtype==3 ... else ...

winner = [];
losers = [];
while ~isempty(pvalid)
  vc = votecount(pvalid(:,1),N);
  if ~any(vc)
    % no valid votes remain
    pvalid = [];
  else
    vc = vc/sum(vc);
    if max(vc) > 1/2
      % have a majority
      winner = find(vc==max(vc));
      pvalid = [];
    else
      % no majority, so check for a tie or exclude the bottom candidate(s) among
      % the current winners and go to their next preferences
      winner = setdiff((1:N),losers); % allows a tie to occur
      % determine the candidates to exclude
      switch elimtype
        case 1
          % exclude the candidate with the least votes
          newlosers = find(vc==min(vc(winner)));

        case 2
          % if p1 specified, exclude any below p1,
          % otherwise exclude all but the top two (or more if tie)
          if isempty(p1)
            p2 = sort(vc);
            p2 = p2(end-1); % case where vc has 1 element already caught
          else
            p2 = p1;
          end;
          newlosers = find(vc<p2);

        case 3
          % exclude the candidate with the most lowest-preference votes
          % need to locate all the preferences that are still in the running
          np = size(pvalid,1);
          winpref = ismember(pvalid,winner); % all votes for potential winners
          % use bsxfun to mark position of votes for possible winners
          % take maximum to find the position of lowest preferences
          % (lowpos values should all be positive)
          lowpos=max(bsxfun(@times,winpref,1:size(pvalid,2)),[],2);
          % convert column numbers to array indices and get the lowest
          % preferences
          lowpref = pvalid((1:np)'+np*(lowpos-1));
          newlosers = fpp(lowpref);

        otherwise
          error('election:prefelim:badelimtype','Internal error (elimtype not recognized)');
      end; % switch elimtype
      newlosers = setdiff(newlosers,losers);
      if isempty(newlosers)
        % cannot reduce any further, so keep the current set of winners
        pvalid = [];
      else
        % remove the losers from the preferences
        losers = sort([losers,newlosers]);
        loservote = ismember(pvalid(:,1),losers);
        while any(loservote)
          pvalid(loservote,1:end-1) = pvalid(loservote,2:end);
          pvalid(loservote,end) = 0;
          loservote = ismember(pvalid(:,1),losers);
        end;
      end; % if isempty(newlosers) ... else ...
    end; % if max(vc) > 1/2 ... else ...
  end; % if ~any(vc) ... else ...
end; % while ~isempty(pvalid)

end % function prefelim(...)


function winner = bordaelim(pref,elimtype,fun)
% sequential elimination based on Borda counts
%
% Borda counts is score according to their rank in the preferences, for example
% with 5 candidates, each candidate gets 5 points for a primary vote, 4 for a
% secondary, down to 1 point for a lowest-rank preference.  If PREF has M
% columns and M<N (N is the number of candidates) then each vote gives [M,...,1]
% points.
%
% If parameter FUN is specified as a function handle, then a position K in a
% voter's preferences will give FUN(K) points. For example, FUN=@(k)1./k gives
% (1,1/2,1/3,...) points.
%
% Invalid votes are those that have repeats or contain non positive integers
%
% elimtype is one of:
%  0: Borda (those with highest score at round 1 are the winners)
%  1: Nanson (any below the average score are eliminated)
%  2: Baldwin (lowest scoring candidate is eliminated)
% For simplicity it is assumed that every vote must fully specify preferences.

if nargin<3
  fun = @(k,m)m+1-k;
elseif nargin(fun)==1
  % add a dummy argument
  fun = @(k,m)fun(k);
end;

N = max(pref(isposint(pref))); % number of candidates
if size(pref,2)~=N
  % the vote is not fully specified
  winner = [];
  return;
end;

% remove votes that repeat or misspecify candidates
pvalid = pref(all(isposint(pref),2) & hasnorepeats(pref), :);
M=N; % M will decrease in size
n=size(pvalid,1);
pvalid = pvalid'; % require transpose

% cycle through eliminations until winner found
winner = [];
losers = [];
while ~isempty(pvalid)
  % calculate the borda score
  winner = setdiff((1:N),losers);
  scores = accumarray(pvalid(:),repmat(fun((1:M)',M),n,1))'; % gets row vector
  switch elimtype
    case 0
      %  0: Borda with no elimination (1 step only, so calculate winner here)
      %  winners are those that attain the maximum score
      newlosers = [];
      winner = find(scores==max(scores));
      pvalid = [];
    case 1
      %  1: Nanson (any below the average score are eliminated)
      newlosers = find(scores<mean(scores(winner)));
    case 2
      %  2: Baldwin (lowest scoring candidate(s) are eliminated)
      newlosers = find(scores==min(scores(winner))&scores<max(scores(winner)));
    otherwise
      error('election:bordaelim:badelimtype','Internal error (elimtype not recognized)');
  end;
  newlosers = setdiff(newlosers,losers); % only consider new losers
  if isempty(newlosers)
    pvalid = []; % have a tie between the current winners
  else
    losers = sort([losers,newlosers]);
    M = M - numel(newlosers);
    % remove new losers from the ballot; know that each appears once in each col
    pvalid = reshape(pvalid(~ismember(pvalid,newlosers)),M,n);
  end; % if isempty(newlosers) ... else ...
end; % while ~isempty(pvalid)

end % function bordaelim(...)


function winner = bucklin(pref)
% Bucklin method: if there is no clear majority in the first round then all the
% second preferences are added to the vote, and continuing until at least one
% candidate has a "majority" (defined relative to the number of voters).  At the
% second and subsequent rounds, if there are several candidates with a majority
% then the one with the highest majority becomes the winner.
%
% Every voter must list the same number of preferences.

if ~all(isposint(pref(:)))
  winner = [];
else
  n = size(pref,1); % number of voters
  M = size(pref,2); % number of preferences
  N = max(pref(:)); % number of candidates
  m=0; % current number of preferences to use
  winner = 1:N;
  while numel(winner)>1 && m<M
    m = m+1;
    vc = votecount(pref(:,1:m));
    if any(vc>n/2)
      winner = find(vc==max(vc));
    end;
  end; % while ...
end; % if ~all(...) ... else ...

end % function bucklin(...)


function winner = smith(pref)
% determines the Smith set, which is the smallest set of candidates that beat
% all other candidates outside the set, based on C (see Cmatrix)

B = beatmatrix(pref); % pairwise wins
N = size(B,1); % number of candidates

if isempty(B)
  winner = [];
  return
end;

% Search by brute-force: try candidates 1 to N until minimal set found.
% If candidate I is in smith set, then any candidate they don't beat must also.
winner = 1:N;
i=1;
while i<=N && numel(winner)>1
  % (stops if a single winner is found that beats all other candidates
  S = i; % elements of current Smith set candidate
  Scheck = i;
  while ~isempty(Scheck) && numel(S)<numel(winner)
    % add to S any candidate not beaten by one in the set (until exceed maximum)
    j = Scheck(1);
    Snew = setdiff(find(~B(j,:)),S); % candidates not beaten by j, not already in S
    S = sort([S,Snew]);
    Scheck = sort([Scheck(2:end),Snew]); % now check all new candidates except j
  end; % while ~isempty(Scheck) && ...
  if numel(S)<numel(winner)
    winner = sort(S);
  end;
  i=i+1;
end; % while i<=N && ...

end % function smith(...)


function winner = schwartz(pref)
% determines Schwartz set - the union of all minimal sets of candidates that are
% unbeatable (i.e. win or possibly tie) by any candidate outside the sets.

B = beatmatrix(pref); % pairwise wins/ties
N = size(B,1); % number of candidates

if isempty(B)
  winner = [];
  return
end;

% Search by brute-force: for each candidates I, find minimal unbeaten set S{I}
% that contains I.  Each S{I} is minimal if it includes no other S{J} as a 
% proper subset.
Scell = cell(1,N); % collection of possible Schwartz components
for i=1:N
  % find the minimal unbeaten set that contains candidate i
  S = i;
  Scheck = i;
  while ~isempty(Scheck)
    % add to S any candidate that beats a member of S
    j = Scheck(1);
    Snew = setdiff(find(B(:,j)'),S); % candidates that beat j, not already in S
    S = sort([S,Snew]);
    Scheck = sort([Scheck(2:end),Snew]); % now check all new candidates except j
  end; % while ~isempty(Scheck)
  Scell{i} = S;
end; % for i=1:N ...
% sort components in order of size, and drop any that contain another as a
% proper subset
[~,ord]=sort(cellfun(@numel,Scell));
Scell = Scell(ord);
i=1;
while i<numel(Scell)
  j=i+1;
  while j<=numel(Scell)
    if all(ismember(Scell{i},Scell{j}))
      Scell(j)=[]; % delete because it is either identical copy or non-minimal
    else
      j=j+1; % lookat next
    end;
  end; % while j<=numel(Scell)
  i=i+1;
end; % while i<numel(Scell)
% take union of all sets
winner = unique(cell2mat(Scell));

end % function schwartz(...)


function winner = landau(pref)
% 'Landau' - (also known as uncovered set or Fishburn set): a set of candidates
% that beats or ties all other candidates, or for any they don't, beats/ties
% with a third candidate that beats/ties with the other.  In other words, I is a
% winner if for all J, C(I,J)>=C(J,I) or C(I,K)>=C(K,I) and C(K,J)>=C(J,K) for 
% some K.

B = beattiematrix(pref);

if isempty(B)
  winner = []; % no valid votes
  return
end;

% matrix B + B^2 is positive if B(i,j) or B(i,k)&B(k,j) is true for some k
winner = find(all((B+B^2)>0, 2)');

end % function landau(...)


function winner = copeland(pref)
% Copeland: the winner(s) are those win the most pairwise runoffs.

B = beatmatrix(pref);
if isempty(B)
  winner = [];
  return;
end;

nwins = sum(B,2)'; % row sum is number of pairwise wins
winner = find(nwins==max(nwins));

end % function copeland(...)


function winner = minimaxscore(pref,scoretype)
% minimax method, where the winner is the candidate with the least worst score
% against it.  If the score S(I,J) is the score of I against J, then J wins if
% max_I{S(I,J)} is not more than that for any other candidate.
%
% scoretype is one of:
%  1: number of winning votes: S(I,J)=C(I,J) if C(I,J)>C(J,I), or 0 otherwise
%  2: vote margin: S(I,J) = C(I,J)-C(J,I)
%  3: number of votes: S(I,J) = C(I,J)

C = Cmatrix(pref);
if isempty(C)
  winner = [];
  return
end;

switch scoretype
  case 1
    S = C.*(C>C');
  case 2
    S = C - C';
  case 3
    S = C;
  otherwise
    error('election:minimaxscore:badscoretype','Internal error (scoretype not recognized');
end; % switch scoretype

Sworst = max(S,[],1); % column-wise maximum is max score against each candidate
winner = find(Sworst==min(Sworst));

end % function minimaxscore(...)


function winner = kemeny(pref)
% finds the preference sequence that maximizes the Kemeny-Young score.  For a
% sequence (K1,...,KN), the Kemeny-Young score is the sum of C(Ki,Kj) over all
% 1<=i<j<=N.  This counts the number of voters whose preferences of I over J
% match that of the sequence, for all possible combinations I, J.  The winner is
% the first member of the sequence with maximum score (or winners, if there are
% several).

C = Cmatrix(pref);
if isempty(C)
  winner = []; % no valid votes given
  return;
end;

N = size(C,1);
if N>10
  warning('election:kemeny:numcand',...
    'Too many candidates: for %d candidates up to %d combinations need to be checked',...
    N,factorial(N));
end;

% recursive implementation
ordlist = kemenyrecur(C);

winner = unique(ordlist(:,1)'); % each row of ord is a top-scoring ordering of the candidates

end % function kemeny(...)

function [ordlist,score]=kemenyrecur(C,firstfew,rest,bestsofar)
% finds the optimal sum of the upper triangular part of C
% over all permutations of C
%
% all entries of C must be non-negative.
%
% does a depth-first search with pruning based on best value so far

N = size(C,1); % number of candidates to check
if nargin==1
  % top-level recursion
  firstfew = []; % first few vertices in the permutation
  rest = 1:N; % vertices not yet put in the permutation
  bestsofar = 0; % best score so far
end;

if N==1
  % C is 1x1
  if numel(rest)~=1
    error('election:kemenyrecur:badsize','Internal error (input vector REST has wrong size)');
  end;
  ordlist = rest;
  score = C; % usually zero, but keep it general
  return
end;

% check that matrix can possibly beat bestsofar
% upper tri part has N(N-1)/2 elements
Csort = sort(C(:),'descend');
ulim = sum(Csort(1:N*(N-1)/2));

if ulim < bestsofar
  % cannot improve current best, so don't search any further
  score = -inf; % to no problems if matrix has all zeros
  ordlist = [];
  return
end;

% now try vertices in decreasing order of their row sum
[Csum,tryorder] = sort(sum(C,2),'descend');
score = -inf;
ordlist = [];
for i=1:N
  newtry = tryorder(i); % index into "rest"
  newCind = [1:(newtry-1),(newtry+1):N];
  newC = C(newCind,newCind);
  newfirst = [firstfew,i];
  newrest = rest(newCind);
  newbest = bestsofar - Csum(i);
  [newordlist,newscore] = kemenyrecur(newC,newfirst,newrest,newbest);
  if newscore > newbest
    % have a new best, create new list
    bestsofar = Csum(i)+newscore;
    score = bestsofar;
    ordlist=[repmat(rest(newtry),size(newordlist,1),1), newordlist];
  elseif newscore == newbest
    % have another equal best, append this to the list
    score = bestsofar;
    ordlist=[ordlist; repmat(rest(newtry),size(newordlist,1),1), newordlist]; %#ok<AGROW>
  end;
end; % for i=1:N


end % function kemenyrecur(...)


function winner = rankedpairs(pref)
% Ranked Pairs (also known as the Tideman method): sort all the pairs (I,J)
% where I beats J (i.e. C(I,J) > C(J,I)) in the order such that (I,J) > (K,L) if
% C(I,J) > C(K,L) (comparing I,K or J,L if a tie).  Then use the pairs (I,J) to
% determine the final ordering of the candidates, by taking them in the given
% order and rejecting any that would lead to a cycle.  The winner is the first
% in the final order.
%
% Under this ordering some of the pairs could still be equivalent, so to avoid
% ambiguities we check all permutations of the equivalent orderings and include
% a candidate as a winner if any of the permutations makes them a winner.

C = Cmatrix(pref);
N = size(C,1); % number of candidates

if N==0
  % no valid votes
  winner = [];
  return
elseif N==1
  winner = 1;
  return
end; % if N==0 elseif ...

% N>=2, so construct sorted list of all pairs (I,J) where C(I,J)>C(J,I)
[ii,jj] = find(C>C');
[pairsorted,equiv] = sortpairs([ii,jj],C); % pairs sorted in descending order
nequiv = numel(equiv)-1; % number of equivalence classes
szequiv = diff(equiv); % size of each equivalence class
ncomb = prod(factorial(szequiv));

% Now for each possible ordering among the equivalence classes, build up the 
% list of ranked pairs, rejecting any that create a cycle.
if ncomb > 1e5
  warning('election:rankedpairs:largencomb','with the %d candidates there are %d combinations to check',N,ncomb);
end;
permlist = cell(1,nequiv);
for i=1:nequiv
  permlist{i} = equiv(i):(equiv(i+1)-1);
end;
winner = []; % will fill the array with the winners
while ~isempty(permlist)
  % add the relations I>J in the specified order, rejecting any that produce a
  % cycle
  addord = cell2mat(permlist);
  B = false(size(C)); % this will be the "beat matrix" defining the partial order
  for k=1:numel(addord)
    % add relation I>J if it does not produce a cycle, maintaining transitive 
    % property at every step so that I>J and J>K -> I>K always
    % hence we only need to check if J>I
    i = pairsorted(addord(k),1);
    j = pairsorted(addord(k),2);
    if ~B(j,i)
      % add relation I>J to the partial order, so for all K>I add K>J etc
      B(:,j) = B(:,j) | B(:,i); % for all K>I add K>J
      B(i,:) = B(i,:) | B(j,:); % for all J>K add I>K
      B(i,j) = true; % add I>J
    end; % if ~B(j,i)
  end; % for i=1:numel(addord) ...
  % now eliminate the candidates that are beaten by some other
  % all(~B(:,j)) is true if no candidate beats J (equiv to ~any(B))
  winner = union(winner,find(all(~B)));
  permlist = nextmultiperm(permlist);
end; % while ~isempty(permlist) ...

end % function rankedpairs(...)


function [L,equiv]=sortpairs(pairlist,C)
% helper function for RANKEDPAIRS
%
% sorts L into descending order using the ranked pair comparison
% also returns array equiv marking the start of each equivalence class 
% (if any are equal) with the last element being size(pairlist,1)+1

% use mergesort
n = size(pairlist,1);
if n==1
  L = pairlist;
  equiv = [1;2];
elseif n==2
  y = paircompare(pairlist(1,1),pairlist(1,2),pairlist(2,1),pairlist(2,2),C);
  if y==1
    L = pairlist;
    equiv = [1;2;3];
  elseif y==0
    L = pairlist;
    equiv = [1;3];
  else
    L = pairlist([2,1],:);
    equiv = [1;2;3];
  end;
else
  % mergesort the two parts of the list
  [L1,eq1] = sortpairs(pairlist(1:floor(n/2),:),C);
  neq1 = numel(eq1)-1;
  [L2,eq2] = sortpairs(pairlist(1:(floor(n/2)+1),:),C);
  neq2 = numel(eq2)-1;
  L = zeros(n,2);
  equiv = zeros(neq1+neq2+1,1);
  equiv(1) = 1;
  i1=1; % current equivalence class of L1
  i2=1; % current equivalence class of L2
  j=1; % current row of L
  i=1; % current equivalence class of L
  while i1<=neq1 || i2<=neq2
    % compare equivalence classes of L1 and L2 and insert the larger one first
    j1 = eq1(i1); % first row of i1th equiv class of L1
    j2 = eq2(i2); % same but for L2
    if i1<=neq1 && i2<=neq2
      % compare the two equivalence classes (returns 1 if L1(j1,:)>L2(j2,:))
      y = paircompare(L1(j1,1),L1(j1,2),L2(j2,2),L2(j2,2),C);
    elseif i1<=neq1
      % L2 is finished, so automatically insert L1
      y = 1;
    else
      % L1 is finished, so automatically insert L2
      y = -1;
    end; % if i1<=neq1 ... elseif ...
    % now insert one or the other (or both) depending on y
    if y>=0
      % insert L1's equiv class first and increment i1
      k1 = eq1(i1+1)-1; % last row of equiv class in L1
      k = j+k1-j1; % last row of equiv class in L
      L(j:k,:) = L1(j1:k1,:);
      i1 = i1+1; % next equiv class in L1
      j = k+1; % next row of L
    end; % if y>=0 ...
    if y<=0
      % insert L2's equiv class and increment i2
      k2 = eq2(i2+1)-1; % last row of equiv class in L2
      k = j+k2-j2; % last row of equiv class in L
      L(j:k,:) = L2(j2:k2,:);
      i2 = i2+1; % next equiv class in L2
      j = k+1; % next row of L
    end; % if y<=0 ...
    % now update the equivalence classes
    i = i+1;
    equiv(i) = j;
  end; % while i1<=neq1 || ...
  % now finished, only need first i rows of equiv
  equiv = equiv(1:i);
end; % if n==1 ... elseif ... else ...

end % function sortpairs(...)


function y=paircompare(i,j,k,l,C)
% helper function for RANKEDPAIRS and SORTPAIRS
%
% compares (i,j) and (k,l) using matrix C:
% (i,j) > (k,l) if C(i,j) > C(k,l) or (if tie) C(i,k)>C(k,i) or C(j,l)>C(l,j)
% returns 1 if (i,j)>(k,l), -1 if (i,j)<(k,l) or 0 otherwise

y = sign(C(i,j)-C(k,l)); % compares C(i,j) with C(k,l)
if y==0
  y = sign(C(i,k)-C(k,i)); % if equal, compares C(i,k) with C(k,i)
end;
if y==0
  y = sign(C(j,l)-C(l,j)); % if still equal, compares C(j,l) with C(l,j)
end;

end % function paircompare(...)


function winner = schulze(pref)
% The Schulze method uses the concept of indirect defeats.  If there is a path
% from I to J where each member of the path defeats the next in the path in a
% pairwise comparison, then the strength of that path is the lowest number of
% winning votes along that path.  I indirectly defeats J if the maximum strength
% of a path from I to J is greater than J to I.
%
% The Schulze winner(s) can also be determined by considering a directed graph
% with edges I to J with weight C(I,J) if I defeats J.  At each step, a vertex J
% is removed if there is a path from I to J but not J to I, otherwise if none
% can be found then the lowest weight edge is removed; the remaining vertices
% correspond to the winners.

C = Cmatrix(pref);
N = size(C,1); % number of candidates

if isempty(N)
  winner = [];
  return
end;

% calculate the edge weight matrix, where weight is C(I,J) if C(I,J)>C(J,I)
C = C.*(C>C');
winner = 1:N;
keepgoing = true;
while keepgoing
  % find the connectivity matrix, by finding where (I+C)^(N-1) > 0
  % (I+C)^n is number of paths of length n including possibly I->I
  % shortest path from I to J has length at most N-1, so find the first 2^k>=N-1
  % and calculate (I+C)^(2^k) by successive squaring
  B = (eye(N,N)+C)>0;
  for i=1:ceil(log2(N-1))
    B = (B^2)>0; % avoids overflow
  end;
  % if B(I,J) is true and B(J,I) is false for some I then J is a loser
  losers = find(any(B & ~B')); % column-wise
  if ~isempty(losers)
    % expunge the losers from the vote
    C(:,losers)=0;
    C(losers,:)=0;
    winner = setdiff(winner,losers);
  else
    % no direct losers, so find a minimum-weight edge
    if any(C>0)
      minedge = find(C==min(C(C>0)));
    else
      minedge = [];
    end; % if any(C>0) ... else ...
    if isempty(minedge)
      % can go no further
      keepgoing = false;
    else
      % remove the minimum-weight edge(s)
      C(minedge)=0;
    end; % if isempty(minedge) ... else ...
  end; % if ~isempty(losers) ... else ...
end; % while keepgoing

end % function schulze(...)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% helper functions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function y=votecount(x,N)
% counts the number of votes for each candidate (shape of x ignored)
% returns row array or empty array otherwise
% optional input N specifies the minimum size of y (default 0)

if nargin==1
  N = 0;
end;
valid = isposint(x);
if any(valid)
  % accumarray fails for empty input
  y = accumarray(x(valid),1)'; % returns row array
else
  y = [];
end;
if N>numel(y)
  y(end+1:N)=0;
end;

end % function votecount(...)


function y=isposint(x)
% returns logical array with y(i)=true if x(i) is a positive integer

y = isfinite(x) & (x>0) & (x==floor(x));

end % function isposint(...)


function y=hasnorepeats(x)
% returns logical array with y(i)=true if x(i,:) has no repeated positive ints

if size(x,2)==1
  % only first preferences were given
  y = true(size(x,1),1);
else
  % check for repeats (where row-wise sorted differences are zero)
  sx = sort(x,2);
  y = all(diff(sx,1,2)~=0 | ~isposint(sx(:,2:end)), 2);
end; % if size(pref,2)==1 ... else ...

end % function hasnorepeats(...)


function C=Cmatrix(pref)
% Determines the matrix where C(i,j) is the number of voters that prefer i to j.
% Any candidates not listed by a voter are assumed to be equal least preferred.
%
% Any vote with repeats or non-candidates out of order (non-positive-integers 
% listed before the last listed positive integer) are ignored.

N = max(pref(isposint(pref))); % number of candidates
C = zeros(N,N);
for k=1:size(pref,1)
  thisvote = pref(k,:);
  iscand = isposint(thisvote);
  lastcand = find(iscand,1,'last');
  firstnon = find(~iscand,1,'first');
  if ~isempty(lastcand) && (isempty(firstnon) || lastcand>firstnon)
    % valid vote must have candidates and no non-candidates out of order
    thisvote = thisvote(1:lastcand);
    nopref = setdiff(1:N,thisvote); % candidates not expressed in preferences
    for i=1:numel(thisvote)
      % add vote for every candidate less prefered than the i'th
      C(thisvote(i),thisvote(i+1:end))=C(thisvote(i),thisvote(i+1:end))+1;
      % add vote for every candidate not explicitly listed
      C(thisvote(i),nopref) = C(thisvote(i),nopref)+1;
    end; % for i=1:numel(thisvote)
  end; % if ~isempty(...)
end; % for k=1:size(pref,1)

end % function Cmatrix(...)


function B=beatmatrix(pref)
% Calculates the matrix B where B(i,j) is true if C(i,j)>C(j,i) where C is the
% matrix with the number of voters that prefer i to j (see Cmatrix for details),
% i.e. B(i,j) is true if candidate i beats candidate j.

C = Cmatrix(pref);
B = C>C';

end % function beatmatrix(...)


function B=beattiematrix(pref)
% Calculates the matrix B where B(i,j) is true if C(i,j)>=C(j,i) where C is the
% matrix with the number of voters that prefer i to j (see Cmatrix for details),
% i.e. B(i,j) is true if candidate i beats or ties with candidate j.

C = Cmatrix(pref);
B = C>=C';

end % function beattiematrix(...)


function cout = nextmultiperm(c)
% NEXTMULTIPERM  increments the right-most permutation, in a list of
% permutations, or returns [] otherwise.
%
% Used by RANKEDPAIRS

cout = c;
n = numel(c);

keepgoing = true;
while keepgoing && n>0
  % increment c{n} if possible, or reset c{n}
  cout{n} = nextperm(c{n});
  if isempty(cout{n})
    cout{n} = sort(c{n});
    n = n-1;
  else
    keepgoing = false;
  end;
end; % while keepgoing && n>0 ...
if n==0
  % have reached the last permutation
  cout = [];
end;

end % function nextmultiperm(...)


function vout=nextperm(v)
%NEXTPERM  determine the next permutation of a row vector
% (cut-down version of the file in the NextVector toolbox FEX #24757)
%
% returns the next permutation of V by lexical ordering (see below)
% or [] if there is none.  Elements of v can be any value except NaN.
%
% based on NEXTPERM in the NextVector toolbox (FEX #24757)

vout = v;

% find the rightmost element that is smaller than its successor
ind = find(diff(v)>0,1,'last');

if isempty(ind),
  % v is in descending order, so it is the last vector
  vout = [];
else
  % swap v(ind) with the next smallest value to the right
  this=v(ind);
  tail=v(ind+1:end);
  [next,pos]=min(tail+0./(tail>this)); % find the smallest larger value by using NaN's
  tail(pos)=this;
  vout(ind)=next;
  % sort the remaining values
  vout(ind+1:end)=sort(tail);
end;

end % function nextperm(...)
