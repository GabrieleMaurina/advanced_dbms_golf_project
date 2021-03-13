#!/usr/bin/env python

from faker import Faker as F
from random import randrange as rr, sample as sm, random as rf, choice as ch
import sys





# CLUBS ------------------------------------------------------------------------------

def club_data(f,i):
	return f.company(), f.city(), [f.phone_number() for j in range(rr(1,4))], [(rr(2,7), rr(1,10)) for j in range(9)]

def club_cmd(c):
	return "INSERT INTO clubs VALUES ('{}','{}',telephones_set({}),holes_set({}),competitions_set());".format(\
		c[0],
		c[1],
		','.join("'{}'".format(t) for t in c[2]),
		','.join('t_hole({},{})'.format(h[0],h[1]) for h in c[3]))

def gen_clubs(f,n):
	clubs = [club_data(f,i) for i in range(n)]
	clubs_cmds = '\n'.join(club_cmd(c) for c in clubs)+'\n'
	return clubs, clubs_cmds





# PLAYERS ---------------------------------------------------------------------------

def player_data(f,i,n_clubs):
	g = rf() > 0.5
	return (\
		'FC{:0>4}'.format(i),
		f.first_name_male() if g else f.first_name_female(),
		f.last_name(),
		str(f.date_of_birth(minimum_age=10, maximum_age=99)),
		'm' if g else 'f',
		rr(19),
		rr(n_clubs))

def player_cmd(p,clubs):
	return "INSERT INTO players VALUES ('{}','{}','{}',DATE'{}','{}',{},{});".format(\
		p[0],
		p[1],
		p[2],
		p[3],
		p[4],
		p[5],
		"(SELECT REF(c) FROM clubs c WHERE c.name = '{}' AND c.city = '{}')".format(clubs[p[6]][0],clubs[p[6]][1]))

def gen_players(f,n,clubs):
	n_clubs = len(clubs)
	players = [player_data(f, i, n_clubs) for i in range(n)]
	players_cmds = '\n'.join(player_cmd(p, clubs) for p in players)+'\n'
	return players, players_cmds





# COMPETITIONS --------------------------------------------------------------------

def competition_data(f,i,n_clubs,n_players, players):
	reserved = 1 if rf()>0.8 else 0
	club = rr(n_clubs)
	partecipants = list(filter(lambda j: players[j][6]==club if reserved else True, range(n_players)))
	return (\
		i,
		f.company(),
		f.date_between(start_date='-80y'),
		f.company(),
		reserved,
		[([str(rr(1,10)) for k in range(9 if rf() < 0.8 else rr(3,9))],players[j][5],j) for j in sm(partecipants, k=min(len(partecipants),rr(5,21)))],
		3,
		2,
		1,
		ch((0,3)),
		ch((0,3)),
		0,
		5,
		6,
		11,
		12,
		18,
		ch((40, 50, 60)),
		club)

def competition_cmd(c,clubs,players):
	insert_competition = "INSERT INTO competitions VALUES ('{}','{}',DATE'{}','{}','{}',partecipants_set({}),{},{},{},{},{},{},{},{},{},{},{},{});".format(\
		c[0],
		c[1],
		c[2],
		c[3],
		c[4],
		','.join("t_partecipant(strokes_set({}),{},(SELECT REF(p) FROM players p WHERE p.fcn = '{}'))".format(\
			','.join(p[0]),
			p[1],
			players[p[2]][0]) for p in c[5]),
		c[6],
		c[7],
		c[8],
		c[9],
		c[10],
		c[11],
		c[12],
		c[13],
		c[14],
		c[15],
		c[16],
		c[17])
	update_club = "INSERT INTO TABLE (SELECT c.competitions FROM clubs c WHERE c.name='{}' AND c.city='{}') "
	update_club += "VALUES ((SELECT REF(c) FROM competitions c WHERE c.id='{}'));"
	update_club = update_club.format(\
		clubs[c[18]][0],
		clubs[c[18]][1],
		c[0])
	return insert_competition + '\n' + update_club

def gen_competitions(f,n,clubs,players):
	n_clubs = len(clubs)
	n_players = len(players)
	competitions = [competition_data(f,i,n_clubs,n_players,players) for i in range(n)]
	competitions_cmds = '\n'.join(competition_cmd(c,clubs,players) for c in competitions)+'\n'
	return competitions, competitions_cmds





# SAVE  ----------------------------------------------------------------------------

def print_data(out, name, data):
	out.write('-- {}\n'.format(name))
	out.write(data)
	out.write('\n'*5)

def save_data(out,clubs,players,competitions):
	with open(out, 'w') as out:
		print_data(out, 'clubs', clubs)
		print_data(out, 'players', players)
		print_data(out, 'competitions', competitions)





# MAIN -----------------------------------------------------------------------------

def main():
	try:
		out = sys.argv[1]
		n_clubs, n_players, n_competitions = (int(v) for v in sys.argv[2:5])

	except (ValueError, IndexError):
		print('Usage: python gen_data.py <output file> <n clubs> <n players> <n competitions>')

	else:
		f = F()
		clubs, clubs_cmds = gen_clubs(f, n_clubs)
		players, players_cmds = gen_players(f, n_players, clubs)
		competitions, competitions_cmds = gen_competitions(f, n_competitions, clubs, players)
		save_data(out, clubs_cmds, players_cmds, competitions_cmds)

if __name__ == '__main__':
	main()
