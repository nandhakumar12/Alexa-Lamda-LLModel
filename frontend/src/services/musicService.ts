// Music Service for Voice Assistant AI
// Handles music playback, library management, and audio controls

export interface Song {
  id: string;
  title: string;
  artist: string;
  genre: string;
  duration: string;
  file: string;
  url: string;
}

export interface MusicLibrary {
  songs: Song[];
}

class MusicService {
  private currentAudio: HTMLAudioElement | null = null;
  private currentSong: Song | null = null;
  private isPlaying: boolean = false;
  private volume: number = 0.7;
  private musicLibrary: Song[] = [];

  constructor() {
    this.loadMusicLibrary();
  }

  // Load music library from S3
  async loadMusicLibrary(): Promise<void> {
    try {
      const response = await fetch('https://voice-assistant-ai-prod-files-qay5floh.s3.amazonaws.com/music/music-library.json');
      const library: MusicLibrary = await response.json();
      this.musicLibrary = library.songs;
      console.log('Music library loaded:', this.musicLibrary.length, 'songs');
    } catch (error) {
      console.error('Failed to load music library:', error);
      // Fallback to default songs
      this.musicLibrary = this.getDefaultSongs();
    }
  }

  // Get default songs if S3 fails
  private getDefaultSongs(): Song[] {
    return [
      {
        id: "1",
        title: "Space Ambient",
        artist: "AI Music",
        genre: "Ambient",
        duration: "4:30",
        file: "space-ambient.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      },
      {
        id: "2",
        title: "Cosmic Journey",
        artist: "AI Music",
        genre: "Electronic",
        duration: "5:15",
        file: "cosmic-journey.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      },
      {
        id: "3",
        title: "Stellar Dreams",
        artist: "AI Music",
        genre: "Cinematic",
        duration: "6:45",
        file: "stellar-dreams.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      },
      {
        id: "4",
        title: "Galactic Waves",
        artist: "AI Music",
        genre: "Ambient",
        duration: "4:20",
        file: "galactic-waves.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      },
      {
        id: "5",
        title: "Interstellar Theme",
        artist: "AI Music",
        genre: "Orchestral",
        duration: "7:30",
        file: "interstellar-theme.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      },
      {
        id: "6",
        title: "Future Bass",
        artist: "AI Music",
        genre: "Electronic",
        duration: "3:45",
        file: "future-bass.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      },
      {
        id: "7",
        title: "Chill Vibes",
        artist: "AI Music",
        genre: "Chill",
        duration: "4:10",
        file: "chill-vibes.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      },
      {
        id: "8",
        title: "Synthwave Night",
        artist: "AI Music",
        genre: "Synthwave",
        duration: "5:00",
        file: "synthwave-night.mp3",
        url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
      }
    ];
  }

  // Search for songs by title, artist, or genre
  searchSongs(query: string): Song[] {
    const searchTerm = query.toLowerCase();
    return this.musicLibrary.filter(song => 
      song.title.toLowerCase().includes(searchTerm) ||
      song.artist.toLowerCase().includes(searchTerm) ||
      song.genre.toLowerCase().includes(searchTerm)
    );
  }

  // Get all songs
  getAllSongs(): Song[] {
    return this.musicLibrary;
  }

  // Get songs by genre
  getSongsByGenre(genre: string): Song[] {
    return this.musicLibrary.filter(song => 
      song.genre.toLowerCase() === genre.toLowerCase()
    );
  }

  // Play a specific song
  async playSong(song: Song): Promise<void> {
    try {
      // Stop current song if playing
      this.stop();

      // Create new audio element
      this.currentAudio = new Audio(song.url);
      this.currentSong = song;
      this.currentAudio.volume = this.volume;

      // Set up event listeners
      this.currentAudio.addEventListener('ended', () => {
        this.isPlaying = false;
        this.currentSong = null;
      });

      this.currentAudio.addEventListener('error', (e) => {
        console.error('Audio playback error:', e);
        throw new Error(`Failed to play ${song.title}`);
      });

      // Play the song
      await this.currentAudio.play();
      this.isPlaying = true;
      
      console.log(`Now playing: ${song.title} by ${song.artist}`);
    } catch (error) {
      console.error('Failed to play song:', error);
      throw error;
    }
  }

  // Play song by title (for voice commands)
  async playSongByTitle(title: string): Promise<string> {
    const songs = this.searchSongs(title);
    
    if (songs.length === 0) {
      return `Sorry, I couldn't find a song called "${title}". Available songs are: ${this.musicLibrary.map(s => s.title).join(', ')}.`;
    }

    const song = songs[0]; // Play first match
    try {
      await this.playSong(song);
      return `Now playing "${song.title}" by ${song.artist}. Enjoy the music! 🎵`;
    } catch (error) {
      return `Sorry, I couldn't play "${song.title}" right now. Please try again.`;
    }
  }

  // Resume current song
  resume(): string {
    if (this.currentAudio && !this.isPlaying) {
      this.currentAudio.play();
      this.isPlaying = true;
      return `▶️ Music resumed.`;
    }
    return `No music to resume. Say "play" followed by a song name to start playing.`;
  }

  // Stop current song
  stop(): string {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
      const stoppedSong = this.currentSong?.title || 'music';
      this.currentSong = null;
      this.isPlaying = false;
      return `🛑 Stopped playing ${stoppedSong}.`;
    }
    return `No music is currently playing.`;
  }

  // Pause current song
  pause(): string {
    if (this.currentAudio && this.isPlaying) {
      this.currentAudio.pause();
      this.isPlaying = false;
      return `⏸️ Music paused. Say "resume" to continue.`;
    }
    return `No music is currently playing.`;
  }

  // Set volume (0-1)
  setVolume(volume: number): void {
    this.volume = Math.max(0, Math.min(1, volume));
    if (this.currentAudio) {
      this.currentAudio.volume = this.volume;
    }
  }

  // Get current playing status
  getPlayingStatus(): { isPlaying: boolean; currentSong: Song | null } {
    return {
      isPlaying: this.isPlaying,
      currentSong: this.currentSong
    };
  }

  // Handle voice commands for music
  async handleMusicCommand(command: string): Promise<string> {
    const lowerCommand = command.toLowerCase();

    // Stop music
    if (lowerCommand.includes('stop')) {
      return this.stop();
    }

    // Pause music
    if (lowerCommand.includes('pause')) {
      return this.pause();
    }

    // Resume music
    if (lowerCommand.includes('resume') || lowerCommand.includes('continue')) {
      return this.resume();
    }

    // Play specific song
    if (lowerCommand.includes('play')) {
      // Extract song name from command
      const playMatch = lowerCommand.match(/play\s+(.+)/);
      if (playMatch) {
        const songName = playMatch[1].replace(/song|music|track/, '').trim();
        return await this.playSongByTitle(songName);
      } else {
        // Play random song
        if (this.musicLibrary.length > 0) {
          const randomSong = this.musicLibrary[Math.floor(Math.random() * this.musicLibrary.length)];
          await this.playSong(randomSong);
          return `🎵 Playing a random song: "${randomSong.title}" by ${randomSong.artist}`;
        }
        return `No songs available to play.`;
      }
    }

    // List available songs
    if (lowerCommand.includes('list') || lowerCommand.includes('songs') || lowerCommand.includes('music')) {
      if (this.musicLibrary.length === 0) {
        return `No songs are currently available.`;
      }
      const songList = this.musicLibrary.map(song => `"${song.title}"`).join(', ');
      return `🎵 Available songs: ${songList}. Say "play" followed by any song title to start playing.`;
    }

    // Default response
    return `🎵 I can help you with music! Try saying: "play [song name]", "stop music", "pause", "resume", or "list songs".`;
  }
}

// Export singleton instance
export const musicService = new MusicService();
export default musicService;
