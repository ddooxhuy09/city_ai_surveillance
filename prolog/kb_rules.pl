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

% Suggest action based on current state
suggest_action(Position, Status, Action, Confidence) :-
    % If not detected, move toward an exit
    Status = undetected,
    exit_point(Exit),
    connected(Position, Exit),
    Action = Exit,
    Confidence = 0.9.

suggest_action(Position, Status, Action, Confidence) :-
    % If detected, try to create a decoy
    Status = detected,
    can_create_decoy(Position),
    Action = create_decoy,
    Confidence = 0.8.

suggest_action(Position, Status, Action, Confidence) :-
    % Choose a random connected location with varied confidence
    Status = undetected,
    connected(Position, Connected),
    not(camera_coverage(_, Connected)),
    Action = Connected,
    random(60, 90, ConfValue),
    Confidence is ConfValue / 100.0.

% Find best escape route
find_best_escape_route(VisitedLocations, [Exit|_], [Exit]) :-
    ai_state(position, CurrentPos),
    connected(CurrentPos, Exit).

find_best_escape_route(VisitedLocations, ExitPoints, [Next|Route]) :-
    ai_state(position, CurrentPos),
    connected(CurrentPos, Next),
    not(member(Next, VisitedLocations)),
    not(camera_coverage(_, Next)),
    find_best_escape_route([Next|VisitedLocations], ExitPoints, Route).
