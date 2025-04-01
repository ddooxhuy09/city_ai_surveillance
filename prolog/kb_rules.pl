% Advanced Rules for AI Learning and Adaptation
% Defines learning mechanisms and strategic decision-making

% Learning from camera detection
learn_camera_pattern(CameraID) :-
    ai_state(known_cameras, KnownCameras),
    not(member(CameraID, KnownCameras)),
    camera(CameraID, Location, Range),
    append(KnownCameras, [CameraID], UpdatedCameras),
    retract(ai_state(known_cameras, KnownCameras)),
    assertz(ai_state(known_cameras, UpdatedCameras)).

% Create a random number between Min and Max
random(Min, Max, Result) :-
    Range is Max - Min,
    Result is Min + random(Range).

% Rules for creating false signals
create_false_signal(Location) :-
    ai_state(position, CurrentPos),
    can_create_decoy(CurrentPos),
    location(Location),
    Location \= CurrentPos,
    random(50, 100, Strength),
    assertz(decoy_signal(Location, Strength)).

% Evaluate effectiveness of a decoy
evaluate_decoy_effectiveness(Location, Effectiveness) :-
    decoy_signal(Location, Strength),
    findall(C, (camera_coverage(C, Location)), CoveringCameras),
    length(CoveringCameras, NumCameras),
    Effectiveness is Strength * NumCameras.
