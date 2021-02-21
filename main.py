from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

user_input = input('Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ')

CHROME_DRIVER_PATH = r"C:\Users\bpham\Documents\chromedriver"
URL_SCRAPE = f"https://www.billboard.com/charts/hot-100/{user_input}"

CLIENT_ID = "----------INSERT YOUR OWN---------------"
CLIENT_SECRET = "----------INSERT YOUR OWN---------------"

# Spotipy Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://127.0.0.1:9090/",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

with open("token.txt") as file:
    data = json.load(file)
    token = (data["access_token"])

# AUTHROIZATION CODE
AUTHORIZATION = f"----------INSERT YOUR OWN---------------"

# Run not headless
# driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)

# Run headless
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options, executable_path=CHROME_DRIVER_PATH)

# Get site data
driver.get(URL_SCRAPE)

# Grab Song Name & Put into a list
song_name = driver.find_elements_by_class_name("chart-element__information__song")
song_name_list = [i.text for i in song_name]

# Grab Artist Name
artist_name = driver.find_elements_by_class_name("chart-element__information__artist")
artist_name_list = [i.text for i in artist_name]

# Remove the "Featuring" string as it doesn't search well with Spotify API
artist_name_feature_removed = []
for i in artist_name_list:
    if "Featuring" in i:
        artist_name_feature_removed.append((i).replace('Featuring', ''))
    else:
        artist_name_feature_removed.append(i)
artist_name_feature_removed.pop()

# Create playlist params
request_body = json.dumps({
    "name": f"{user_input} Billboard 100",
    "description": "",
    "public": True
})
# Create playlist response
response = requests.post(url="https://api.spotify.com/v1/users/bphamt/playlists", data=request_body,
                         headers={"Content-Type": "application/json", "Authorization": AUTHORIZATION})
print(response)
# Convert playlist data into json
data = response.json()
# Grab playlist ID
PLAYLIST_ID = (data['external_urls']['spotify']).split("/")[4]

for i in range(len(song_name_list) - 1):
    try:
      # # Grab song ID
      grab_params = {
          "q": f"{song_name_list[i]} {artist_name_feature_removed[i]}",
          "type": "track,artist"
      }
      response = requests.get(url="https://api.spotify.com/v1/search", params=grab_params,
                              headers={"Content-Type": "application/json", "Authorization": AUTHORIZATION})
      data = response.json()
      TRACK_ID = (data['tracks']['items'][0]['uri'])

      # # Add song to playlist
      add_params = {
          "playlist_id": PLAYLIST_ID,
          "uris": TRACK_ID
      }
      response = requests.post(url=f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks", params=add_params,
                               headers={"Content-Type": "application/json", "Authorization": AUTHORIZATION})
    except:
      pass

driver.quit()
