
import tmdbsimple as tmdb
import sys
from googlesearch import search as googlesearch
from bs4 import BeautifulSoup
from moviepy.editor import (VideoFileClip,concatenate_videoclips)
from pathvalidate import sanitize_filename
from yt_dlp import YoutubeDL
import glob
import os
import requests



tmdb.API_KEY = "******"
query = sys.argv[-1]
print("[Pre-show Generator] Movie", query)

search = tmdb.Search()
search.movie(query=query)

upcoming = tmdb.Movies()
response = upcoming.upcoming()

similar_movies = []
for movie in response['results']:
    if search.results[0]['genre_ids'][0] in movie['genre_ids']:
        similar_movies.append(movie)

print('[Pre-show Generator] Which movies seem interesting?\
      Type the indexes like this: 3,4,6 \n')
for c, movie in enumerate(similar_movies):
    print(c+1, ".",movie['title'])

select_movies = input('[Pre-show Generator] Ans: ')
select_movies = [int(index)-1 for index in select_movies.split(',')]
final_movie_list = [similar_movies[index] for index in select_movies]

print('[Pre-show Generator] Searching trailers')

yt_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio',
    'outtmpl': '__trailer__.mp4',
    'quiet': True,
    'progress': True,
}

file_name_dict = {movie['title']: sanitize_filename(f"{movie['title']}-trailer.mp4") for movie in final_movie_list}

trailer_urls = []
for movie in final_movie_list:
    for film_url in googlesearch('site:tv.apple.com '+ movie['title'], stop=10):
        break
    req = requests.get(film_url)
    soup = BeautifulSoup(req.content, 'html.parser')
    trailer_urls.append(soup.find(property="og:video").attrs['content'])
    filename = file_name_dict[movie['title']]

    if os.path.isfile(filename):
        print(' --- Skipped - file exists')
        continue
    
    with YoutubeDL(yt_opts) as ydl:
        result = ydl.download([trailer_urls[-1]])
        if result == 0:
            found = glob.glob('./__trailer__.*')
            if len(found):
                
                os.rename(found[0], filename)
                print(' --- Ok - {}'.format(filename))
            else:
                print(' --- Error - download not found')
        else:
            print(' --- Error - download failed')

print('[Pre-show Generator] Combining trailers')

trailer_clips = [VideoFileClip(file_name_dict[movie['title']]) for movie in final_movie_list]

# Find a countdown movie and download it
yt_opts = {
    'outtmpl': 'countdown_timer.mp4',
    'quiet': True,
    'progress': True,
}

req = requests.get("https://www.videvo.net/video/futuristic-countdown-timer/45/")
soup = BeautifulSoup(req.content, 'html.parser')

videos = soup.findAll('video')
source = videos[0].findAll('source')

print(source[0]['src'])

with YoutubeDL(yt_opts) as ydl:
        result = ydl.download(source[0]['src'])

trailer_clips.append(VideoFileClip('countdown_timer.mp4'))
final_clip = concatenate_videoclips(trailer_clips, method="compose")
final_clip.write_videofile("combined_trailers.mp4")


    

# print(final_movie_list)