import sqlite3
import os
import datetime
import argparse
import subprocess

video_dir="/home/spirou/Videos"

def initdb():

    conn = sqlite3.connect("movie.db")
    c = conn.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' and
      name='movies' ''')

    if c.fetchone()[0] == 1:
        print('Table exists')
        print('Dropping it')
        c.execute('''DROP TABLE movies''')
        c.execute('''CREATE TABLE movies (name text, year integer, path text) ''')
        conn.commit()

    else:
        c.execute('''CREATE TABLE movies (name text, year integer, path text) ''')
        conn.commit()

    conn.close()


def check_if_movie_exists(full_path):
    conn = sqlite3.connect("movie.db")
    c = conn.cursor()
    c.execute("SELECT * from movies where path=?", (full_path,))
    data = c.fetchall()

    if len(data) == 0:
        return False
    else:
        return True


def search_for_movies(movie_dir):

    listofmovies = []
    carry_on = True
    for root, dirs, files in os.walk(movie_dir):
        for file in files:
            full_path = os.path.join(root, file)
            condition_1 = file.endswith(".mp4")
            condition_2 = not check_if_movie_exists(full_path)
            if condition_1 and condition_2:
                listofmovies.append(
                    prompt_user(root, file))

                carry_on = input("Do you want to continue : ").lower() == "y"

                if not carry_on:
                    append_db(listofmovies)
                    return listofmovies

    append_db(listofmovies)
    return listofmovies


def prompt_user(root, file):
    print(file)
    statbuf = os.stat(os.path.join(root, file))
    mod_timestamp = datetime.datetime.fromtimestamp(
        statbuf.st_mtime)
    print("Modification time: {}".format(mod_timestamp))
    # todo use modification time

    name = input("What is the name of this movie : ")
    year_released = input("What is the date of this movie : ")

    movie = {}
    movie["name"] = name
    movie["year"] = year_released
    movie["filepath"] = os.path.join(root, file)
    return movie


def append_db(listofmovies):
    conn = sqlite3.connect("movie.db")
    c = conn.cursor()
    for movie in listofmovies:
        c.execute('insert into movies (name, year, path) values (?,?,?)',
                  (movie["name"], movie["year"], movie["filepath"]))

    conn.commit()
    c.close()


def scandb():
    conn = sqlite3.connect("movie.db")
    c = conn.cursor()
    for row in c.execute('SELECT * from movies'):
        print(row)
    c.close()

def show_movies():
    conn = sqlite3.connect("movie.db")
    c = conn.cursor()
    for row in c.execute('SELECT * from movies'):
      print(f'{row[0]}  ({row[1]})')
    c.close()

def prompt_user_for_movie():
    name_of_request = input("what is the name of the movie : ")
    conn = sqlite3.connect("movie.db")
    c = conn.cursor()
    c.execute("SELECT * from movies where name=?", (name_of_request,))
    data = c.fetchall()[0]
    filepath = data[2]
    return filepath



def main():

  parser = argparse.ArgumentParser()
  parser.add_argument('action')
  args = parser.parse_args()

  if args.action == "scan" :
    scandb()

  if args.action == "search" :
    search_for_movies(video_dir)

  if args.action == "watch":
    show_movies()
    filepath = prompt_user_for_movie()
    subprocess.call(['vlc',filepath])

if __name__ == "__main__":
  main()


