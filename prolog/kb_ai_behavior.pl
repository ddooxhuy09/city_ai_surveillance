% AI Behavior Knowledge Base
% Defines AI state and behavior rules

% AI state predicates
:- dynamic ai_state/2.

% Decoy signal predicates
:- dynamic decoy_signal/2.

% Power sources for creating decoys
power_source(industrial_zone).
power_source(shopping_mall).
power_source(train_station).

% Check if AI can create a decoy at current location
can_create_decoy(Location) :- 
    ai_state(position, Location), 
    power_source(Location).

% Risk level assessment
risk_level(Location, high) :- 
    camera_coverage(_, Location), 
    sensor(_, Location, _).
risk_level(Location, medium) :- 
    camera_coverage(_, Location); 
    sensor(_, Location, _).
risk_level(Location, low) :- 
    blind_spot(Location).

% Safe path finding between locations
safe_path(Start, End, Path) :- 
    find_path(Start, End, [Start], Path, low).

% Path finding with risk assessment
find_path(End, End, Visited, [End], _).
find_path(Current, End, Visited, [Current|Path], MaxRisk) :-
    connected(Current, Next),
    not(member(Next, Visited)),
    risk_level(Next, Risk),
    risk_acceptable(Risk, MaxRisk),
    find_path(Next, End, [Next|Visited], Path, MaxRisk).

% Risk level acceptability
risk_acceptable(low, _).
risk_acceptable(medium, medium).
risk_acceptable(medium, high).
risk_acceptable(high, high).
