// Music Service for Voice Assistant AI
// Handles music playback, library management, and audio controls

class MusicService {
  constructor() {
    this.currentAudio = null;
    this.currentSong = null;
    this.isPlaying = false;
    this.volume = 0.7;
    this.musicLibrary = [];
    this.loadMusicLibrary();
  }

  // Load music library from S3
  async loadMusicLibrary() {
    try {
      const response = await fetch('https://voice-assistant-ai-prod-files-qay5floh.s3.amazonaws.com/music/music-library.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const library = await response.json();
      this.musicLibrary = library.songs;
      console.log('Music library loaded from S3:', this.musicLibrary.length, 'songs');
    } catch (error) {
      console.error('Failed to load music library from S3:', error);
      // Fallback to default songs with working URLs
      this.musicLibrary = this.getDefaultSongs();
      console.log('Using default music library:', this.musicLibrary.length, 'songs');
    }
  }

  // Get default songs if S3 fails
  getDefaultSongs() {
    return [
      {
        id: "1",
        title: "Space Ambient",
        artist: "AI Music",
        genre: "Ambient",
        duration: "4:30",
        file: "space-ambient.mp3",
        url: "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3"
      },
      {
        id: "2",
        title: "Cosmic Journey",
        artist: "AI Music",
        genre: "Electronic",
        duration: "5:15",
        file: "cosmic-journey.mp3",
        url: "https://file-examples.com/storage/fe68c1b7c1a9fd42b4c2bb7/2017/11/file_example_MP3_700KB.mp3"
      },
      {
        id: "3",
        title: "Stellar Dreams",
        artist: "AI Music",
        genre: "Cinematic",
        duration: "6:45",
        file: "stellar-dreams.mp3",
        url: "https://file-examples.com/storage/fe68c1b7c1a9fd42b4c2bb7/2017/11/file_example_MP3_1MG.mp3"
      },
      {
        id: "4",
        title: "Galactic Waves",
        artist: "AI Music",
        genre: "Ambient",
        duration: "4:20",
        file: "galactic-waves.mp3",
        url: "https://file-examples.com/storage/fe68c1b7c1a9fd42b4c2bb7/2017/11/file_example_MP3_2MG.mp3"
      },
      {
        id: "5",
        title: "Interstellar Theme",
        artist: "AI Music",
        genre: "Orchestral",
        duration: "7:30",
        file: "interstellar-theme.mp3",
        url: "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3"
      },
      {
        id: "6",
        title: "Future Bass",
        artist: "AI Music",
        genre: "Electronic",
        duration: "3:45",
        file: "future-bass.mp3",
        url: "https://file-examples.com/storage/fe68c1b7c1a9fd42b4c2bb7/2017/11/file_example_MP3_700KB.mp3"
      },
      {
        id: "7",
        title: "Chill Vibes",
        artist: "AI Music",
        genre: "Chill",
        duration: "4:10",
        file: "chill-vibes.mp3",
        url: "https://file-examples.com/storage/fe68c1b7c1a9fd42b4c2bb7/2017/11/file_example_MP3_1MG.mp3"
      },
      {
        id: "8",
        title: "Synthwave Night",
        artist: "AI Music",
        genre: "Synthwave",
        duration: "5:00",
        file: "synthwave-night.mp3",
        url: "https://file-examples.com/storage/fe68c1b7c1a9fd42b4c2bb7/2017/11/file_example_MP3_2MG.mp3"
      }
    ];
  }

  // Search for songs by title, artist, or genre
  searchSongs(query) {
    const searchTerm = query.toLowerCase().trim();
    return this.musicLibrary.filter(song => {
      const title = song.title.toLowerCase();
      const artist = song.artist.toLowerCase();
      const genre = song.genre.toLowerCase();

      // Check for exact matches first
      if (title.includes(searchTerm) || artist.includes(searchTerm) || genre.includes(searchTerm)) {
        return true;
      }

      // Check for partial word matches
      const searchWords = searchTerm.split(' ');
      return searchWords.some(word =>
        title.includes(word) || artist.includes(word) || genre.includes(word)
      );
    });
  }

  // Find song by title with flexible matching
  findSongByTitle(title) {
    const searchTerm = title.toLowerCase().trim();

    // First try exact match
    let song = this.musicLibrary.find(song =>
      song.title.toLowerCase() === searchTerm
    );

    if (song) return song;

    // Then try partial match
    song = this.musicLibrary.find(song =>
      song.title.toLowerCase().includes(searchTerm)
    );

    if (song) return song;

    // Finally try word-by-word matching
    const searchWords = searchTerm.split(' ');
    return this.musicLibrary.find(song => {
      const songTitle = song.title.toLowerCase();
      return searchWords.every(word => songTitle.includes(word));
    });
  }

  // Get all songs
  getAllSongs() {
    return this.musicLibrary;
  }

  // Play a specific song
  async playSong(song) {
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
        console.error('Failed URL:', song.url);
        this.isPlaying = false;
        this.currentSong = null;
        this.currentAudio = null;
      });

      this.currentAudio.addEventListener('loadstart', () => {
        console.log('Audio loading started for:', song.title);
      });

      this.currentAudio.addEventListener('canplay', () => {
        console.log('Audio ready to play:', song.title);
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
  async playSongByTitle(title) {
    // First try to find exact or close match
    let song = this.findSongByTitle(title);

    // If no direct match, try searching
    if (!song) {
      const songs = this.searchSongs(title);
      if (songs.length > 0) {
        song = songs[0]; // Use the first search result
      }
    }

    if (!song) {
      const songList = this.musicLibrary.map((s, index) => `${index + 1}. "${s.title}"`).join('\n');
      return `Sorry, I couldn't find a song called "${title}" in Nandhakumar's favorites.\n\n🎵 Available songs:\n${songList}\n\nTry saying "play" followed by one of these song names!`;
    }

    try {
      await this.playSong(song);
      return `🎵 Now playing "${song.title}" by ${song.artist}. Enjoy the music!`;
    } catch (error) {
      return `Sorry, I couldn't play "${song.title}" right now. Please try again.`;
    }
  }

  // Stop current song
  stop() {
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
  pause() {
    if (this.currentAudio && this.isPlaying) {
      this.currentAudio.pause();
      this.isPlaying = false;
      return `⏸️ Music paused. Say "resume" to continue.`;
    }
    return `No music is currently playing.`;
  }

  // Resume current song
  resume() {
    if (this.currentAudio && !this.isPlaying) {
      this.currentAudio.play();
      this.isPlaying = true;
      return `▶️ Music resumed.`;
    }
    return `No music to resume. Say "play" followed by a song name to start playing.`;
  }

  // Get current playing status
  getPlayingStatus() {
    return {
      isPlaying: this.isPlaying,
      currentSong: this.currentSong
    };
  }

  // Handle voice commands for music
  async handleMusicCommand(command) {
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

    // List songs first (before play command to avoid conflicts)
    if (lowerCommand.includes('list') || (lowerCommand.includes('songs') && !lowerCommand.includes('play')) ||
        lowerCommand.includes('what songs') || lowerCommand.includes('show songs') || lowerCommand.includes('available')) {
      if (this.musicLibrary.length === 0) {
        return `No songs are currently available.`;
      }
      const songList = this.musicLibrary.map((song, index) => `${index + 1}. "${song.title}" by ${song.artist} (${song.genre})`).join('\n');
      return `🎵 Here are Nandhakumar's favorite songs:\n\n${songList}\n\nWhich one would you like me to play? Just say "play" followed by the song name!`;
    }

    // Play specific song or random
    if (lowerCommand.includes('play')) {
      // Check if it's just "play" or "play music" without specific song
      if (lowerCommand.trim() === 'play' || lowerCommand.trim() === 'play music' ||
          lowerCommand.trim() === 'play song' || lowerCommand.trim() === 'play a song') {
        // Play random song from Nandhakumar's favorites
        if (this.musicLibrary.length > 0) {
          const randomSong = this.musicLibrary[Math.floor(Math.random() * this.musicLibrary.length)];
          await this.playSong(randomSong);
          return `🎵 Playing one of Nandhakumar's favorites: "${randomSong.title}" by ${randomSong.artist}. Enjoy the music!`;
        }
        return `No songs available to play.`;
      }

      // Extract song name from command
      const playMatch = lowerCommand.match(/play\s+(.+)/);
      if (playMatch) {
        const songName = playMatch[1].replace(/song|music|track|the/, '').trim();
        return await this.playSongByTitle(songName);
      }
    }

    // Handle general music requests
    if (lowerCommand.includes('music') && !lowerCommand.includes('stop') && !lowerCommand.includes('pause')) {
      if (this.musicLibrary.length > 0) {
        const randomSong = this.musicLibrary[Math.floor(Math.random() * this.musicLibrary.length)];
        await this.playSong(randomSong);
        return `🎵 Playing one of Nandhakumar's favorites: "${randomSong.title}" by ${randomSong.artist}. Say "list songs" to see all available tracks!`;
      }
      return `No songs available to play.`;
    }

    // Default response
    return `🎵 I can help you with Nandhakumar's music collection! Try saying:\n• "play music" - for a random favorite\n• "play [song name]" - for a specific song\n• "list songs" - to see all favorites\n• "stop", "pause", or "resume" - to control playback`;
  }
}

// Export singleton instance
const musicService = new MusicService();
export default musicService;
