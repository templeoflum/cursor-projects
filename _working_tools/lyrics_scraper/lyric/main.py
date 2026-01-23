import os
import sys
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///lyrics.db')
Session = sessionmaker(bind=engine)

class Song(Base):
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True)
    artist = Column(String(100))
    title = Column(String(200))
    lyrics = Column(Text)
    url = Column(String(500))

Base.metadata.create_all(engine)

class GeniusLyricsScraper:
    def __init__(self):
        self.api_token = os.getenv('GENIUS_API_TOKEN')
        if not self.api_token:
            print("Error: GENIUS_API_TOKEN not found in .env file")
            sys.exit(1)
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.genius.com'
        self.session = Session()

    def search_artist(self, query: str) -> List[Dict]:
        """Search for an artist on Genius."""
        search_url = f"{self.base_url}/search"
        params = {'q': query}
        
        response = requests.get(search_url, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"Error searching for artist: {response.status_code}")
            return []
        
        data = response.json()
        hits = data['response']['hits']
        
        # Filter for artist results only
        artists = []
        for hit in hits:
            if hit['type'] == 'artist':
                artists.append({
                    'id': hit['result']['id'],
                    'name': hit['result']['name'],
                    'url': hit['result']['url']
                })
        return artists

    def get_artist_songs(self, artist_id: int) -> List[Dict]:
        """Get all songs for an artist."""
        songs_url = f"{self.base_url}/artists/{artist_id}/songs"
        params = {'per_page': 50}
        
        response = requests.get(songs_url, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"Error getting artist songs: {response.status_code}")
            return []
        
        data = response.json()
        return data['response']['songs']

    def scrape_lyrics(self, url: str) -> str:
        """Scrape lyrics from a Genius song page."""
        response = requests.get(url)
        if response.status_code != 200:
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics_div = soup.find('div', {'class': 'Lyrics__Container-sc-1ynbvzw-1'})
        
        if not lyrics_div:
            return ""
        
        # Extract and clean lyrics
        lyrics = []
        for line in lyrics_div.stripped_strings:
            if line and not line.startswith('[') and not line.endswith(']'):
                lyrics.append(line)
        
        return '\n'.join(lyrics)

    def save_lyrics(self, artist: str, title: str, lyrics: str, url: str):
        """Save lyrics to the database."""
        song = Song(
            artist=artist,
            title=title,
            lyrics=lyrics,
            url=url
        )
        self.session.add(song)
        self.session.commit()

    def get_stored_lyrics(self, artist: str = None) -> List[Song]:
        """Retrieve stored lyrics from the database."""
        query = self.session.query(Song)
        if artist:
            query = query.filter(Song.artist.ilike(f"%{artist}%"))
        return query.all()

def main():
    scraper = GeniusLyricsScraper()
    
    while True:
        print("\n1. Search for an artist")
        print("2. View stored lyrics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            artist_name = input("Enter artist name: ")
            artists = scraper.search_artist(artist_name)
            
            if not artists:
                print("No artists found.")
                continue
            
            print("\nFound artists:")
            for i, artist in enumerate(artists, 1):
                print(f"{i}. {artist['name']}")
            
            artist_choice = int(input("\nSelect an artist (number): ")) - 1
            if artist_choice < 0 or artist_choice >= len(artists):
                print("Invalid selection.")
                continue
            
            selected_artist = artists[artist_choice]
            songs = scraper.get_artist_songs(selected_artist['id'])
            
            print(f"\nFound {len(songs)} songs for {selected_artist['name']}")
            for i, song in enumerate(songs[:10], 1):
                print(f"{i}. {song['title']}")
            
            song_choice = int(input("\nSelect a song to scrape (number): ")) - 1
            if song_choice < 0 or song_choice >= len(songs):
                print("Invalid selection.")
                continue
            
            selected_song = songs[song_choice]
            print(f"\nScraping lyrics for {selected_song['title']}...")
            
            lyrics = scraper.scrape_lyrics(selected_song['url'])
            if lyrics:
                scraper.save_lyrics(
                    selected_artist['name'],
                    selected_song['title'],
                    lyrics,
                    selected_song['url']
                )
                print("Lyrics saved successfully!")
            else:
                print("Failed to scrape lyrics.")
        
        elif choice == '2':
            artist_filter = input("Enter artist name to filter (or press Enter for all): ")
            songs = scraper.get_stored_lyrics(artist_filter)
            
            if not songs:
                print("No stored lyrics found.")
                continue
            
            print("\nStored lyrics:")
            for i, song in enumerate(songs, 1):
                print(f"{i}. {song.artist} - {song.title}")
            
            song_choice = int(input("\nSelect a song to view lyrics (number): ")) - 1
            if song_choice < 0 or song_choice >= len(songs):
                print("Invalid selection.")
                continue
            
            print("\nLyrics:")
            print(songs[song_choice].lyrics)
        
        elif choice == '3':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 