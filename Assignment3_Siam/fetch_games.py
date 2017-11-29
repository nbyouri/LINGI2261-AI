#!/usr/local/bin/python3

from lxml.html import parse

RHINO_UP = 'img/20m.gif'
RHINO_RIGHT = 'img/21m.gif'
RHINO_DOWN = 'img/22m.gif'
RHINO_LEFT = 'img/23m.gif'

ELE_UP = 'img/10m.gif'
ELE_RIGHT = 'img/11m.gif'
ELE_DOWN = 'img/12m.gif'
ELE_LEFT = 'img/13m.gif'

ROCK = 'img/minirocher.gif'
EMPTY = 'img/_.gif'

database = {}


def parse_html(id):
    page = parse("pages/www.boiteajeux.net/jeux/sia/historique.php?id="+str(id))
    # rows = page.xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr")
    all_games = page.xpath("/html/body/table")[0].getchildren()[1].getchildren()[0].getchildren()[1].getchildren()
    nb_games = len(all_games)
    # TODO levenshtein compare
    for i in range(1, nb_games):
        game_str = ""
        game = all_games[i].getchildren()[1].getchildren()[0].getchildren()
        for row in game:
            for cell in row.getchildren():
                img = str(cell.getchildren()[0].items()[1][1])
                if img == EMPTY:
                    game_str += "-"
                elif img == ROCK:
                    game_str += "#"
                elif img == RHINO_UP:
                    game_str += "0"
                elif img == RHINO_LEFT:
                    game_str += "1"
                elif img == RHINO_DOWN:
                    game_str += "2"
                elif img == RHINO_RIGHT:
                    game_str += "3"
                elif img == ELE_UP:
                    game_str += "4"
                elif img == ELE_LEFT:
                    game_str += "5"
                elif img == ELE_DOWN:
                    game_str += "6"
                elif img == ELE_RIGHT:
                    game_str += "7"

        if game_str in database:
            database[game_str][0] += (nb_games - i + 1) / nb_games
            database[game_str][1] += 1
        else:
            database[game_str] = [(nb_games - i + 1) / nb_games, 1]


for i in range(2, 18002):
    parse_html(i)

f = open('db.txt', 'w')

f.write("database = {\n")
for k,v in database.items():
    f.write("\t\"%s\" : %s,\n" % (k, v))
f.write("}\n")
f.close()