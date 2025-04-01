% City Map Knowledge Base
% Defines locations and connections between them

% Locations in the city
location(city_center).
location(industrial_zone).
location(residential_area).
location(shopping_mall).
location(park).
location(highway_entrance).
location(port).
location(train_station).

% Roads connecting locations
road(city_center, industrial_zone).
road(city_center, residential_area).
road(industrial_zone, highway_entrance).
road(residential_area, shopping_mall).
road(shopping_mall, park).
road(park, highway_entrance).
road(highway_entrance, port).
road(city_center, train_station).
road(train_station, port).

% Define bidirectional connections
connected(X, Y) :- road(X, Y).
connected(X, Y) :- road(Y, X).

% Define exit points from the city
exit_point(highway_entrance).
exit_point(port).
exit_point(train_station).
