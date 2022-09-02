% reborn :-	move(A,L):-	reposition(L):-	visited(X,Y):-	wumpus(X,Y)
% confundus(X,Y)	tingle(X,Y)		glitter(X,Y)		stench(X,Y)	safe(X,Y)
% wall(X,Y)	explore(L):-	current(0,0,rNorth).	current(X,Y,D)	hasarrow.


% define dynamic data.
:- dynamic visited/2.
:- dynamic wumpus/2.
:- dynamic confundus/2.
:- dynamic tingle/2.
:- dynamic glitter/2.
:- dynamic stench/2.
:- dynamic wall/2.
:- dynamic current/3.
:- dynamic hasarrow/0.
hasarrow.
:- dynamic visible/2.
:- dynamic exception/0.
:- dynamic variable/0.
:- dynamic virtual_current/3.
:- dynamic bump/0.
:- dynamic virtual_visited/2.
:- dynamic value/3.

%define adjacent cells, find the adj_cell (X_i,Y_i) of (X,Y).
adj_cell(X_i,Y_i,X,Y):-
	X_i is X-1, Y_i is Y;
	X_i is X+1, Y_i is Y;
	X_i is X, Y_i is Y+1;
	X_i is X, Y_i is Y-1.

%define rules for safe cells.
safe(X,Y):-
	visible(X,Y),
	not(wumpus(X,Y)),
	not(confundus(X,Y)).

%implement reborn function.
reborn:-
	retractall(visited(_,_)),
	retractall(visible(_,_)),
	retractall(wumpus(_,_)),
	retractall(confundus(_,_)),
	retractall(tingle(_,_)),
	retractall(glitter(_,_)),
	retractall(stench(_,_)),
	retractall(wall(_,_)),
	retractall(current(_,_,_)),
	retractall(virtual_current(_,_,_)),
	retractall(virtual_visited(_,_)),
	asserta(current(0,0,rnorth)),
	asserta(visited(0,0)),
	asserta(visible(0,0)),
	set_visible(0,0),
	asserta(hasarrow),!.

%set the cells adj to (X,Y) into visible.
set_visible(X,Y):-
	adj_cell(X_i,Y_i,X,Y),
	not(visible(X_i,Y_i)),
	asserta(visible(X_i,Y_i)),
	fail;

	true.


%implement reposition function.
reposition(L):-
	retractall(visited(_,_)),
	retractall(visible(_,_)),
	retractall(wumpus(_,_)),
	retractall(confundus(_,_)),
	retractall(tingle(_,_)),
	retractall(glitter(_,_)),
	retractall(stench(_,_)),
	retractall(wall(_,_)),
	retractall(current(_,_,_)),
	retractall(virtual_current(_,_,_)),
	retractall(virtual_visited(_,_)),
	asserta(current(0,0,rnorth)),
	asserta(visited(0,0)),
	unzip_sensory_data(L,_Confounded_i,Stench_i,Tingle_i,Glitter_i,_Bump_i,_Scream_i),
	asserta(visible(0,0)),
	set_visible(0,0),
	set_stench(0,0,Stench_i),
	set_tingle(0,0,Tingle_i),
	set_glitter(0,0,Glitter_i),!.

%implement move function.
move(A,L):-
	L=[], %if empty, the agent has stepped into wumpus.
	!;

	%first make sure A is a valid action.
	A=turnleft, turn_left,!;
	A=turnright, turn_right,!;
	A=shoot, shoot(L),!;
	A=pickup, pick_up(L),!;
	A=moveforward,
	unzip_sensory_data(L,Confounded_i,Stench_i,Tingle_i,Glitter_i,Bump_i,Scream_i),
	move_forward(L,Confounded_i,Stench_i,Tingle_i,Glitter_i,Bump_i,Scream_i),!.

unzip_sensory_data(L,Confounded_i,Stench_i,Tingle_i,Glitter_i,Bump_i,Scream_i):-
	%extract information from L and check for validity.
	%Confounded_i temporarily hold indicator for confounded, etc.
	%Ln means the sensory without first n indicators.
	[Confounded_i | L1] = L,
	[Stench_i | L2] = L1,
	[Tingle_i | L3] = L2,
	[Glitter_i | L4] = L3,
	[Bump_i | L5] = L4,
	[Scream_i] = L5.

turn_left:-
	current(X,Y,D),
	(D=rnorth, retractall(current(_,_,_)), asserta(current(X,Y,rwest));
	D=rwest, retractall(current(_,_,_)), asserta(current(X,Y,rsouth));
	D=rsouth, retractall(current(_,_,_)), asserta(current(X,Y,reast));
	D=reast, retractall(current(_,_,_)), asserta(current(X,Y,rnorth))).
turn_right:-
	current(X,Y,rnorth), retractall(current(_,_,_)), asserta(current(X,Y,reast));
	current(X,Y,reast), retractall(current(_,_,_)), asserta(current(X,Y,rsouth));
	current(X,Y,rsouth), retractall(current(_,_,_)), asserta(current(X,Y,rwest));
	current(X,Y,rwest), retractall(current(_,_,_)), asserta(current(X,Y,rnorth)).

shoot(L):-
	not(hasarrow);

	hasarrow,
	retract(hasarrow),
	unzip_sensory_data(L,_Confounded_i,_Stench_i,_Tingle_i,_Glitter_i,_Bump_i,Scream_i),
	Scream_i = on,
	reason_shoot_true,
	retractall(wumpus(_,_)),
	retractall(stench(_,_));

	true.

reason_shoot_true:-
	wumpus(X_i,Y_i),
	not(is_ahead(X_i,Y_i)),
	retractall(wumpus(X_i,Y_i)),
	fail;

	reason_wumpus.

is_ahead(X_i,Y_i):-
	current(X,Y,D),
	(D=rnorth, X_i=X, Y_i>Y;
	D=rsouth, X_i=X, Y_i<Y;
	D=rwest, Y_i=Y, X_i<X;
	D=reast, Y_i=Y, X_i>X).

reason_wumpus:-
	count(wumpus(_X,_Y),Count),
	Count=1,
	wumpus(X_i,Y_i),
	retractall(confundus(X_i,Y_i)), !;

	true.

count(P,Count):-
	findall(1,P,L),
	length(L,Count).

pick_up(L):-
	current(X,Y,_D),
	glitter(X,Y),
	unzip_sensory_data(L,_Confounded_i,_Stench_i,_Tingle_i,Glitter_i,_Bump_i,_Scream_i),
	Glitter_i = on,
	fail;

	current(X,Y,_D),
	glitter(X,Y),
	unzip_sensory_data(L,_Confounded_i,_Stench_i,_Tingle_i,Glitter_i,_Bump_i,_Scream_i),
	Glitter_i = off,
	retractall(glitter(X,Y));

	current(X,Y,_D),
	not(glitter(X,Y)).

move_forward(L,Confounded_i,Stench_i,Tingle_i,Glitter_i,Bump_i,_Scream_i):-
	Bump_i = on, next_cell(X,Y), asserta(wall(X,Y)),retractall(wumpus(X,Y)),retractall(confundus(X,Y)),reason_wumpus;

	Confounded_i=on, reposition(L);

	next_cell(X,Y),
	current(_X0,_Y0,D),
	retractall(current(_,_,_)),
	retractall(confundus(X,Y)),
	retractall(wumpus(X,Y)),
	asserta(current(X,Y,D)),
	(visited(X,Y);
	asserta(visited(X,Y))),
	set_stench(X,Y,Stench_i),
	reason_wumpus,
	set_tingle(X,Y,Tingle_i),
	set_glitter(X,Y,Glitter_i),
	set_visible(X,Y).

next_cell(X,Y):-
	(current(X0,Y0,D),
	(D = rnorth, X is X0, Y is Y0+1;
	D = rwest, X is X0-1, Y is Y0;
	D = reast, X is X0+1, Y is Y0;
	D = rsouth, X is X0, Y is Y0-1)).

set_stench(X,Y,Stench_i):-
	Stench_i = on, asserta(stench(X,Y)), reason_stench_true(X,Y);
	Stench_i = off, retractall(stench(X,Y)), reason_stench_false(X,Y).
set_tingle(X,Y,Tingle_i):-
	Tingle_i = on, asserta(tingle(X,Y)), reason_tingle_true(X,Y);
	Tingle_i = off, retractall(tingle(X,Y)), reason_tingle_false(X,Y).
set_glitter(X,Y,Glitter_i):-
	Glitter_i = on, asserta(glitter(X,Y));
	Glitter_i = off, retractall(glitter(X,Y)).

reason_stench_false(X,Y):-
	adj_cell(X_i,Y_i,X,Y), retractall(wumpus(X_i,Y_i)), fail;

	true.

reason_stench_true(X,Y):-
	wumpus(X_i,Y_i),
	not(adj_cell(X_i,Y_i,X,Y)),
	retractall(wumpus(X_i,Y_i)),
	fail;

	adj_cell(X_i,Y_i,X,Y), %find the adj_cell satisfying the following conditions.
	not(visited(X_i,Y_i)), % 1. not visited.
	not(wall(X_i,Y_i)),	%2. not inhabited by wall.
	adj_are_all_stench(X_i,Y_i), % 3. its adjacent cells all have stench if it's visited.
	adj_to_all_stench(X_i,Y_i), %4. adjacent to all the stench cells.
	fail;

	true.

adj_are_all_stench(X,Y):-
	adj_cell(X_i,Y_i,X,Y),
	visited(X_i,Y_i),
	not(stench(X_i,Y_i)),
	asserta(exception),
	fail;

	not(exception);

	exception, retractall(exception), fail.

adj_to_all_stench(X,Y):-
	%this predicate will check all stench cells,
	%if all stench sell are adjacent to X,Y, it will fail.
	%if there is exception, it will pass and will not assert any wumpus(X,Y).
	stench(X_i,Y_i),
	not(adj_cell(X_i,Y_i,X,Y)),!;

	%this will be executed if the above predicate fails.
	wumpus(X,Y),!;
	asserta(wumpus(X,Y)).

reason_tingle_false(X,Y):-
	adj_cell(X_i,Y_i,X,Y),
	retractall(confundus(X_i,Y_i)),
	fail;
	true.


reason_tingle_true(X,Y):-
	adj_cell(X_i,Y_i,X,Y), %find the adj_cell satisfying the following conditions.
	not(visited(X_i,Y_i)), % 1. not visited.
	not(wall(X_i,Y_i)),	%2. not inhabited by wall.
	adj_are_all_tingle(X_i,Y_i), % 3. its adjacent cells all have tingle if it's visited.
	fail;

	true.

adj_are_all_tingle(X,Y):-
	adj_cell(X_i,Y_i,X,Y),
	visited(X_i,Y_i),
	not(tingle(X_i,Y_i)),
	asserta(exception),
	fail;

	exception, retractall(exception),!;
	asserta(confundus(X,Y)).

% implement explore function.
explore(L):-
	%first determine whether L is a variable.
	retractall(variable),
	[H|_T] = L,
	H = invalid_action,
	asserta(variable),
	fail;

	not(variable),
	[A|T] = L,
	current(X,Y,D),
	asserta(virtual_current(X,Y,D)),%initialize virtual location.
	take_virtual_action(A,T);

	variable, retractall(variable),
	find_path(L).


take_virtual_action(A, L):-
	(A=turnLeft, turn_left_virtual,!;
	A=turnRight, turn_right_virtual,!;
	A=shoot, shoot_virtual,!;
	A=pickup, pick_up_virtual,!;
	A=moveforward, move_forward_virtual(L),!),
	%this will be false until L is an empty list
	%therefore it will return fail when L is empty.
	[A_i|T] = L,
	take_virtual_action(A_i,T);

	virtual_current(X,Y,_D),
	safe(X,Y),
	not(visited(X,Y)),
	retractall(virtual_current(_,_,_));

	virtual_current(0,0,_D),
	retractall(virtual_current(_,_,_)),
	not(glitter(_,_)),
	no_safe_unvisited_cell;

	retractall(virtual_current(_,_,_)).

no_safe_unvisited_cell:-
	safe(X,Y),
	not(visited(X,Y)),
	not(wall(X,Y)),
	asserta(exception),
	fail;

	not(exception);

	exception, retractall(exception), fail.

turn_left_virtual:-
	virtual_current(X,Y,rnorth), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,rwest));
	virtual_current(X,Y,reast), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,rnorth));
	virtual_current(X,Y,rwest), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,rsouth));
	virtual_current(X,Y,rsouth), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,reast)).

turn_right_virtual:-
	virtual_current(X,Y,rnorth), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,reast));
	virtual_current(X,Y,reast), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,rsouth));
	virtual_current(X,Y,rwest), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,rnorth));
	virtual_current(X,Y,rsouth), retractall(virtual_current(_,_,_)), asserta(virtual_current(X,Y,rwest)).

shoot_virtual.

pick_up_virtual:-
	virtual_current(X,Y,_D),
	glitter(X,Y);

	true.

move_forward_virtual(L):-
	next_cell_virtual(X,Y,_D),
	(wumpus(X,Y), asserta(exception);
	confundus(X,Y), asserta(exception);
	wall(X,Y), asserta(bump)),
	fail;

	not(exception),		%if the cell is safe.
	(
	bump, retractall(bump);		%not accessible.
	next_cell_virtual(X,Y,D),	%accessible then change virtual location,
	retractall(virtual_current(_,_,_)),
	asserta(virtual_current(X,Y,D))
	),
	(
	% check if the new cell is unvisited.
	visited(X,Y);	%if visited, nothing happens.
	%if not visited, check if there are still actions in the list.
	[_H|_T] = L, fail
	);

	exception, retractall(exception), fail.

next_cell_virtual(X,Y,D):-
	virtual_current(X0,Y0,D),
	(D = rnorth, X is X0, Y is Y0+1;
	D = rwest, X is X0-1, Y is Y0;
	D = reast, X is X0+1, Y is Y0;
	D = rsouth, X is X0, Y is Y0-1).

find_path(L):-
	% first case, there is no safe accessible unvisited cells and may or maynot have coins.
	% should go to origin.
	no_safe_unvisited_cell,
	%not(glitter(X,Y)),
	current(X,Y,D),
	Route = [virtual_current(X,Y,D)],
	asserta(virtual_visited(X,Y)),
	path_to_origin(L,Route),	%this will generate an action list that return to origin.
	retractall(virtual_visited(_,_)), !;


	%second, normal case, generate a path to a new cell.
	current(X,Y,D),
	Route = [virtual_current(X,Y,D)],
	asserta(virtual_visited(X,Y)),
	path_to_newcell(L_i,Route),
	(glitter(X,Y), append([pickup],L_i,L);
	append([],L_i,L)),
	retractall(virtual_visited(_,_)), !.

path_to_origin(L,Route):-
	[Current|_Previous] = Route,
	Current = virtual_current(0,0,_D),
	L =[],!.

path_to_origin(L,Route):-
	[virtual_current(X,Y,_D)|_Previous] = Route,
	adj_cell(X_i,Y_i,X,Y),
	not(virtual_visited(X_i,Y_i)),
	safe(X_i,Y_i),
	not(wall(X_i,Y_i)),
	generate_action_list(X_i,Y_i,D_i,L_i,Route),
	asserta(virtual_visited(X_i,Y_i)),
	Route_i = [virtual_current(X_i,Y_i,D_i)|Route],
	path_to_origin(L_ii,Route_i),
	append(L_i,L_ii,L).

path_to_newcell(L,Route):-
	[virtual_current(X,Y,_D)|_Previous] = Route,
	safe(X,Y),
	not(visited(X,Y)),
	L = [], !.

path_to_newcell(L,Route):-
	[virtual_current(X,Y,_D)|_Previous] = Route,
	adj_cell(X_i,Y_i,X,Y),
	not(virtual_visited(X_i,Y_i)),
	safe(X_i,Y_i),
	not(wall(X_i,Y_i)),
	generate_action_list(X_i,Y_i,D_i,L_i,Route),
	asserta(virtual_visited(X_i,Y_i)),
	Route_i = [virtual_current(X_i,Y_i,D_i)|Route],
	path_to_newcell(L_ii,Route_i),
	append(L_i,L_ii,L).

ini_assign_value:-
	visible(X,Y),
	not(visited(X,Y)),
	(safe(X,Y), asserta(value(X,Y,1.0));
	not(safe(X,Y)), asserta(value(X,Y,-1.0))),
	assign_value.

assign_value:-
	all_have_value,!.
assign_value:-
	value(_X,_Y,_V),
	assign_value.

generate_action_list(X_i,Y_i,D_i,L_i,Route):-
	Route = [virtual_current(X,Y,D)|_Previous],
	(X_i=X, Y_i is Y+1, move_up(D,L_i), D_i=rnorth;
	X_i=X, Y_i is Y-1, move_down(D,L_i), D_i=rsouth;
	X_i is X-1, Y_i=Y, move_left(D,L_i), D_i=rwest;
	X_i is X+1, Y_i=Y, move_right(D,L_i), D_i=reast).
move_up(D,L):-
	D=rnorth, L=[moveforward];
	D=reast, L=[turnleft, moveforward];
	D=rwest, L=[turnright, moveforward];
	D=rsouth, L=[turnright, turnright, moveforward].
move_down(D,L):-
	D=rnorth, L=[turnright, turnright, moveforward];
	D=reast, L=[turnright, moveforward];
	D=rwest, L=[turnleft, moveforward];
	D=rsouth, L=[moveforward].
move_left(D,L):-
	D=rnorth, L=[turnleft, moveforward];
	D=reast, L=[turnleft, turnleft, moveforward];
	D=rwest, L=[moveforward];
	D=rsouth, L=[turnright, moveforward].
move_right(D,L):-
	D=rnorth, L=[turnright, moveforward];
	D=reast, L=[moveforward];
	D=rwest, L=[turnright, turnright, moveforward];
	D=rsouth, L=[turnleft, moveforward].
