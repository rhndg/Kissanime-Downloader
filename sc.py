#!/usr/bin/python

import requests
import bs4
import urllib
from time import strftime
from urllib.request import urlopen
import re, os, sys


root_url = 'http://www.kissanime.com';
anime_list = "anime_list.txt";
current_dir = os.path.dirname(os.path.realpath(__file__));

def d ():
  return "[" + strftime("%H:%M:%S") + "]";

def get_video_list (anime):
  res = requests.get(root_url + '/Anime/' + anime);
  soup = bs4.BeautifulSoup(res.text);
  links = soup.select('table a[href^=/Anime/' + anime + '/]');
  hrefs = [a.attrs.get('href') for a in links]
  #vids['t'] = re.split("-", re.split("\?", vids['l'][0])[0])[-1];
  #print vids['t'];
  return hrefs;

def get_video_data (video_page_url):
  video_data = {};
  res = requests.get(root_url + video_page_url);
  soup = bs4.BeautifulSoup(res.text);
  video_data['dls'] = soup.select('div#divDownload a')[0];
  video_data['l'] = video_data['dls'].attrs.get('href');
  #print video_data['l'];
  return video_data;

def download (anime, url, i_, _d):
  anime = anime.replace("-", " ");
  _dir = current_dir + "\\" + anime + "\\";
  if not os.path.isdir(_dir):
    os.makedirs(_dir);
  i = i_ + ".mp4";
  i = i.replace("!", "");
  i = i.replace("-", " ");
  if os.path.isfile(_dir + i):
    if os.path.getsize(_dir + i) <= 1:
      print (d(), "[Deleting]", i);
    else:
      #print ("[Skipping]", i, "(Already exists)");
      return False;
  #urllib.urlretrieve(url['l'], i)
  if not _d:
    print (d(), "[Anime]", anime);
  print (d(), "[Downloading]", i);
  file = open(_dir + i,'wb');
  file.write(urlopen(get_video_data(url)['l']).read());
  file.close();
  file.close();
  return True;

def download_anime (anime):
  #Download anime
  #(Skipping special episodes and episodes outside of range)
  s = -1;
  f = 99999999;
  if '#' in anime:
    range = anime.split("#")[-1];
    anime = anime.split("#")[0];
    if "-" in range:
      s = int(range.split("-")[0]);
      f = int(range.split("-")[1]);
    else:
      s = int(range);

  if s > f:
    print (d(), "[Error]", "Starting range cannot be higher than ending range!");
    print (d(), "[Skipping]", anime);
    return;
  
  video_list = get_video_list(anime);
  i = 0;
  _d = False;
  for a in reversed(video_list):
    if not "Episode" in a:
      continue;
    i += 1;
    if s >= 0:
      if i < s:
        #print (d(), "Skipping Episode", i);
        continue;
    if i > f:
      #print (d(), "Skipping Episode", i);
      continue;
    t = a.split('?')[0].split('-')[-1];
    try:
      if download(anime, a, anime + '-' + t, _d):
        _d = True;
    except IOError:
      print (d(), "Error");
  if not _d:
    print (d(), "[Complete]", anime);

def get_anime_list ():
  #Read list of anime from file
  alf = open (anime_list, 'r');
  for line in alf:
    line = line.replace("\n", '');
    if line == "":
      continue;
    if line.startswith("#"):
      continue;
    download_anime(line);
  alf.close();

def sort_anime_list ():
  unsortedFile = open("b_" + anime_list, "r");
  sortedFile = open(anime_list, "w+");
  
  sortedFile.write("# anime_list.txt - generated from bookmarks file\n\n");
  sortedFile.write("# NOTE: Lines starting with a '#' symbol will be ignored.\n");
  sortedFile.write("# Adding a '#' symbol after the anime name will allow you to specify the range to download\n");
  sortedFile.write("# The format for this is: Anime#firstEpisode-LastEpisode\n");
  sortedFile.write("# If the '-' symbol is omited, all remaining episodes will be downloaded\n\n");
  for line in sorted(unsortedFile, key = str.lower):
    sortedFile.write(line);
  unsortedFile.close();
  sortedFile.close();
  os.remove("b_" + anime_list);

def find (name):
  for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
    for file in files:
      if name in file:
        return file;
  return name;

def parse_bookmarks (bookmark_file):
  print ("Parsing", bookmark_file, "\n");
  b = open (bookmark_file, 'r');
  f = open ("b_" + anime_list, 'w');
  for line in b:
    line = line.replace("\n", '');
    if line == "":
      continue;
    if "kissanime.com" in line:
      line = line.split("Anime/")[1].split("\"")[0];
      print ("[Bookmark]", line);
      f.write(line + '\n');
  b.close();
  f.close();
  sort_anime_list();
  print ();
  print ("Finished parsing bookmarks. \nDelete", bookmark_file, "to start downloading from", anime_list);

def run ():
  if os.path.isfile(find("bookmarks")):
    parse_bookmarks(find("bookmarks"));
  elif os.path.isfile(anime_list):
    print(d(), "[System Start]");
    get_anime_list();
  else:
    print ("[Error]", anime_list, "does not exist!");
    sys.exit();

run();
