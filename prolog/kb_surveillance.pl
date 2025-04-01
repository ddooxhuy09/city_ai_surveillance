% Surveillance System Knowledge Base
% Defines cameras, sensors and their properties

% Camera predicates
% camera(ID, Location, Range)
:- dynamic camera/3.

% Sensor predicates
% sensor(ID, Location, Type)
:- dynamic sensor/3.

% Camera coverage calculation
camera_coverage(CameraID, Location) :- 
    camera(CameraID, CamLoc, Range), 
    path_within_range(CamLoc, Location, Range).

% Path within range calculations
path_within_range(Loc, Loc, _).
path_within_range(Start, End, Range) :-
    Range > 0,
    connected(Start, Mid),
    NewRange is Range - 1,
    path_within_range(Mid, End, NewRange).

% Blind spots in the surveillance system
blind_spot(Location) :- 
    location(Location), 
    not(any_camera_coverage(Location)).

any_camera_coverage(Location) :- 
    camera(_, _, _), 
    camera_coverage(_, Location).
