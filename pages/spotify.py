from pages.base import BasePage, ResourceCache

class SpotifyPage(BasePage):
    def __init__(self, display, spotify_service, font_path='fonts/FSEX300.ttf'):
        super().__init__(display, font_path)
        self.spotify_service = spotify_service
        self.current_track = None

    def update(self):
        try:
            self.current_track = self.spotify_service.get_playing()
        except Exception as e:
            print(f"Erro Spotify: {e}")
            self.current_track = None

    def should_show(self):
        return self.current_track is not None

    def render(self):
        if not self.current_track: return
        
        self.display.clear()
        
        # Logo do Spotify
        spotify_icon_url = "https://cdn-icons-png.flaticon.com/512/174/174872.png"
        icon_spot = ResourceCache.get_icon(spotify_icon_url, size=(16, 16))
        if icon_spot:
            self.display.draw_image(icon_spot, (-1, 20))
            
        self.display.draw_text_centered("SPOTIFY", 38, self.font_path, 14, fill=(30, 255, 120))
        self.display.draw_line(50, margin=30, fill=(30, 255, 120))
        
        music_name = self.current_track['music']
        if len(music_name) > 16: music_name = music_name[:14] + ".."
        self.display.draw_text_centered(music_name.upper(), 65, self.font_path, 18, fill=(255, 255, 255))
        
        artist_name = self.current_track['artists']
        if len(artist_name) > 22: artist_name = artist_name[:20] + ".."
        self.display.draw_text_centered(artist_name, 90, self.font_path, 14, fill=(255, 255, 255))
        
        self.display.draw_progress_bar(0.65, 115, height=3, color=(30, 255, 120))
        
        status_text = "REPRODUZINDO" if self.current_track.get('playing') else "PAUSADO"
        self.display.draw_text_centered(status_text, 132, self.font_path, 14, fill=(255, 255, 255))

    def get_duration(self):
        return 10
