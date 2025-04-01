"""
Provides an interface for Python code to interact with Prolog.
"""
import os
import time
import random

class MockProlog:
    """A mock Prolog implementation for development when SWI-Prolog isn't available."""
    def __init__(self):
        self.facts = {}
        self.rules = {}
        print("Khởi tạo MockProlog để thay thế SWI-Prolog")
    
    def query(self, query_string):
        """Mock a Prolog query with reasonable responses."""
        print(f"Mock query: {query_string}")
        
        # Parse query string to provide reasonable responses
        if "location(X)" in query_string:
            locations = ["city_center", "industrial_zone", "residential_area", 
                         "shopping_mall", "park", "highway_entrance", 
                         "port", "train_station"]
            return [{"X": loc} for loc in locations]
        
        elif "connected(" in query_string:
            # Extract location from query
            parts = query_string.split("(")[1].split(",")
            loc1 = parts[0].strip()
            
            if loc1 == "city_center":
                return [{"X": "industrial_zone"}, {"X": "residential_area"}, {"X": "train_station"}]
            elif loc1 == "industrial_zone":
                return [{"X": "city_center"}, {"X": "highway_entrance"}]
            elif loc1 == "residential_area":
                return [{"X": "city_center"}, {"X": "shopping_mall"}]
            elif loc1 == "shopping_mall":
                return [{"X": "residential_area"}, {"X": "park"}]
            elif loc1 == "park":
                return [{"X": "shopping_mall"}, {"X": "highway_entrance"}]
            elif loc1 == "highway_entrance":
                return [{"X": "industrial_zone"}, {"X": "park"}, {"X": "port"}]
            elif loc1 == "port":
                return [{"X": "highway_entrance"}, {"X": "train_station"}]
            elif loc1 == "train_station":
                return [{"X": "city_center"}, {"X": "port"}]
            else:
                return []
        
        elif "exit_point(X)" in query_string:
            return [{"X": "highway_entrance"}, {"X": "port"}, {"X": "train_station"}]
        
        elif "ai_state(position, Pos), ai_state(detected, Status)" in query_string:
            return [{"Pos": "city_center", "Status": "undetected"}]
        
        elif "learn_camera_pattern" in query_string:
            return [{}]  # Success, no return value
        
        else:
            return []  # Default empty response
    
    def assertz(self, fact):
        """Mock asserting a fact."""
        print(f"Mock assertz: {fact}")
        return True
    
    def retract(self, fact):
        """Mock retracting a fact."""
        print(f"Mock retract: {fact}")
        return True
    
    def retractall(self, pattern):
        """Mock retracting all matching facts."""
        print(f"Mock retractall: {pattern}")
        return True

class PrologConnector:
    def __init__(self, use_mock=False):
        """Initialize the Prolog connector."""
        self.use_mock = use_mock
        
        if use_mock:
            self.prolog = MockProlog()
        else:
            try:
                from pyswip import Prolog
                self.prolog = Prolog()
                print("Sử dụng SWI-Prolog thực")
            except Exception as e:
                print(f"Không thể khởi tạo SWI-Prolog: {e}")
                print("Chuyển sang sử dụng MockProlog")
                self.prolog = MockProlog()
                self.use_mock = True
        
    def load_knowledge_base(self):
        """Load all Prolog knowledge base files."""
        prolog_dir = "prolog"
        
        # Kiểm tra thư mục tồn tại
        if not os.path.exists(prolog_dir):
            os.makedirs(prolog_dir)
            print(f"Đã tạo thư mục {prolog_dir}")
            # Tạo các file Prolog nếu chưa tồn tại
            self._create_prolog_files(prolog_dir)
        
        # Kiểm tra các file tồn tại
        required_files = ["kb_city.pl", "kb_surveillance.pl", "kb_ai_behavior.pl", "kb_rules.pl"]
        for file in required_files:
            file_path = os.path.join(prolog_dir, file)
            if not os.path.exists(file_path):
                print(f"Tạo file {file_path} vì không tồn tại")
                self._create_prolog_file(file_path, file)
        
        # Nạp các file Prolog
        try:
            if not self.use_mock:
                self.consult(os.path.join(prolog_dir, "kb_city.pl"))
                self.consult(os.path.join(prolog_dir, "kb_surveillance.pl"))
                self.consult(os.path.join(prolog_dir, "kb_ai_behavior.pl"))
                self.consult(os.path.join(prolog_dir, "kb_rules.pl"))
            
            # Khởi tạo trạng thái ban đầu
            self.assertz("ai_state(position, city_center)")
            self.assertz("ai_state(detected, undetected)")
            self.assertz("ai_state(known_cameras, [])")
            self.assertz("ai_state(escape_plan, [])")
        except Exception as e:
            print(f"Lỗi khi nạp cơ sở tri thức: {e}")
    
    def _create_prolog_files(self, prolog_dir):
        """Create Prolog files with default content if they don't exist."""
        self._create_prolog_file(os.path.join(prolog_dir, "kb_city.pl"), "kb_city.pl")
        self._create_prolog_file(os.path.join(prolog_dir, "kb_surveillance.pl"), "kb_surveillance.pl")
        self._create_prolog_file(os.path.join(prolog_dir, "kb_ai_behavior.pl"), "kb_ai_behavior.pl")
        self._create_prolog_file(os.path.join(prolog_dir, "kb_rules.pl"), "kb_rules.pl")
    
    def _create_prolog_file(self, file_path, file_type):
        """Create a specific Prolog file with appropriate content."""
        content = ""
        
        if "kb_city.pl" in file_type:
            content = """% City Map Knowledge Base
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
"""
        elif "kb_surveillance.pl" in file_type:
            content = """% Surveillance System Knowledge Base
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
"""
        elif "kb_ai_behavior.pl" in file_type:
            content = """% AI Behavior Knowledge Base
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
"""
        elif "kb_rules.pl" in file_type:
            content = """% Advanced Rules for AI Learning and Adaptation
% Defines learning mechanisms and strategic decision-making

% Learning from camera detection
learn_camera_pattern(CameraID) :-
    ai_state(known_cameras, KnownCameras),
    not(member(CameraID, KnownCameras)),
    camera(CameraID, Location, Range),
    append(KnownCameras, [CameraID], UpdatedCameras),
    retract(ai_state(known_cameras, KnownCameras)),
    assertz(ai_state(known_cameras, UpdatedCameras)).

% Rules for creating false signals
create_false_signal(Location) :-
    ai_state(position, CurrentPos),
    can_create_decoy(CurrentPos),
    location(Location),
    Location \\= CurrentPos,
    assertz(decoy_signal(Location, 75)).

% Evaluate effectiveness of a decoy
evaluate_decoy_effectiveness(Location, Effectiveness) :-
    decoy_signal(Location, Strength),
    findall(C, (camera_coverage(C, Location)), CoveringCameras),
    length(CoveringCameras, NumCameras),
    Effectiveness is Strength * NumCameras.
"""
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def consult(self, filename):
        """Load a Prolog file with proper path handling."""
        if self.use_mock:
            print(f"Giả lập nạp file: {filename}")
            return True
        
        try:
            # Thay thế backslash bằng forward slash
            normalized_path = filename.replace('\\', '/')
            
            print(f"Đang tải file Prolog: {normalized_path}")
            
            # Đọc nội dung file thay vì dùng consult
            with open(normalized_path, 'r') as f:
                content = f.read()
            
            # Tách các mệnh đề và xử lý từng mệnh đề
            for clause in content.split('.'):
                clause = clause.strip()
                if clause and not clause.startswith('%'):  # Bỏ qua comment và dòng trống
                    try:
                        self.prolog.assertz(clause)
                    except Exception as e:
                        print(f"Lỗi khi thêm mệnh đề: {clause}, lỗi: {e}")
            
            return True
        except Exception as e:
            print(f"Lỗi khi tải file Prolog {filename}: {e}")
            return False
    
    def query(self, query_string, **kwargs):
        """Run a Prolog query."""
        return self.prolog.query(query_string, **kwargs)
    
    def assertz(self, fact):
        """Assert a new fact to the Prolog database."""
        return self.prolog.assertz(fact)
    
    def retract(self, fact):
        """Retract a fact from the Prolog database."""
        return self.prolog.retract(fact)
    
    def retractall(self, pattern):
        """Retract all facts matching a pattern."""
        return self.prolog.retractall(pattern)
    
    def reset_ai_state(self):
        """Reset the AI state in the Prolog knowledge base."""
        # Retract all AI state facts
        try:
            list(self.query("retractall(ai_state(_, _))"))
            
            # Reinitialize AI state
            self.assertz("ai_state(position, city_center)")
            self.assertz("ai_state(detected, undetected)")
            self.assertz("ai_state(known_cameras, [])")
            self.assertz("ai_state(escape_plan, [])")
            
            # Remove decoy signals
            list(self.query("retractall(decoy_signal(_, _))"))
        except Exception as e:
            print(f"Lỗi khi reset trạng thái AI: {e}")
