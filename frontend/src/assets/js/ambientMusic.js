/**
 * Ambient Music Player
 * Handles ambient music playback for meditation and relaxation profiles
 */

class AmbientMusicPlayer {
    constructor() {
        this.audio = null;
        this.isPlaying = false;
        this.currentTrack = null;
        this.volume = 0.3; // Default volume (30%)
        this.availableTracks = [
            { name: 'Background Ambient', file: 'AudioCoffee - Background Ambient Music.mp3' },
            { name: 'Clouds (Ambient)', file: 'Alex-Productions - Ambient Background music_ Clouds.mp3' }
        ];
        this.audioBasePath = '/assets/audio/';

        // Initialize UI elements
        this.initializePlayer();
    }

    initializePlayer() {
        // Create audio element
        this.audio = new Audio();
        this.audio.loop = true;
        this.audio.volume = this.volume;

        // Event listeners
        this.audio.addEventListener('ended', () => {
            console.log('Track ended (should not happen with loop)');
        });

        this.audio.addEventListener('error', (e) => {
            console.error('Audio error:', e);
            this.handleAudioError();
        });

        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayButton();
        });

        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayButton();
        });

        // Setup event listeners for existing player in DOM
        this.setupEventListeners();
        this.populateTrackList();

        // Autoplay first track after a brief delay
        setTimeout(() => {
            if (this.availableTracks.length > 0) {
                const trackSelect = document.getElementById('ambient-track-select');
                if (trackSelect) {
                    trackSelect.value = this.availableTracks[0].file;
                    //this.loadTrack(this.availableTracks[0].file);
                }
            }
        }, 1000);
    }

    // No longer needed - player exists in HTML
    createPlayerUI() {
        // Player UI exists in HTML, nothing to create
    }

    populateTrackList() {
        const trackSelect = document.getElementById('ambient-track-select');
        const mobileTrackSelect = document.getElementById('mobile-ambient-track-select');

        // Populate desktop player
        if (trackSelect) {
            this.availableTracks.forEach(track => {
                const option = document.createElement('option');
                option.value = track.file;
                option.textContent = track.name;
                trackSelect.appendChild(option);
            });
        }

        // Populate mobile player
        if (mobileTrackSelect) {
            this.availableTracks.forEach(track => {
                const option = document.createElement('option');
                option.value = track.file;
                option.textContent = track.name;
                mobileTrackSelect.appendChild(option);
            });
        }
    }

    setupEventListeners() {
        // Desktop player controls
        const playPauseBtn = document.getElementById('ambient-play-pause');
        const trackSelect = document.getElementById('ambient-track-select');
        const volumeSlider = document.getElementById('ambient-volume');
        const closeBtn = document.getElementById('ambient-close');

        // Mobile player controls
        const mobilePlayPauseBtn = document.getElementById('mobile-ambient-play-pause');
        const mobileTrackSelect = document.getElementById('mobile-ambient-track-select');

        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        }

        if (mobilePlayPauseBtn) {
            mobilePlayPauseBtn.addEventListener('click', () => this.togglePlayPause());
        }

        if (trackSelect) {
            trackSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadTrack(e.target.value);
                    // Sync mobile select
                    if (mobileTrackSelect) {
                        mobileTrackSelect.value = e.target.value;
                    }
                }
            });
        }

        if (mobileTrackSelect) {
            mobileTrackSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadTrack(e.target.value);
                    // Sync desktop select
                    if (trackSelect) {
                        trackSelect.value = e.target.value;
                    }
                }
            });
        }

        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                this.setVolume(e.target.value / 100);
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hidePlayer());
        }
    }

    loadTrack(trackFile) {
        const trackPath = this.audioBasePath + trackFile;

        // Try to load the track
        this.audio.src = trackPath;
        this.currentTrack = trackFile;

        // Update track info display
        this.updateTrackInfo(trackFile);

        // Auto-play when track is selected
        const playPromise = this.audio.play();

        if (playPromise !== undefined) {
            playPromise.then(() => {
                console.log('Track loaded and playing:', trackFile);
            }).catch(error => {
                console.warn('Autoplay prevented. User must click play.', error);
                // Browser prevented autoplay - user must click play
            });
        }
    }

    updateTrackInfo(trackFile) {
        // Parse track info from filename
        let trackName = 'Unknown Track';
        let artistName = '';

        const track = this.availableTracks.find(t => t.file === trackFile);
        if (track) {
            trackName = track.name;
            // Extract artist from filename
            if (trackFile.includes('Alex-Productions')) {
                artistName = 'Alex Productions';
            } else if (trackFile.includes('AudioCoffee')) {
                artistName = 'AudioCoffee';
            }
        }

        // Update desktop player
        const trackNameEl = document.getElementById('ambient-track-name');
        const artistNameEl = document.getElementById('ambient-artist-name');
        if (trackNameEl) trackNameEl.textContent = trackName;
        if (artistNameEl) artistNameEl.textContent = artistName;

        // Update mobile player
        const mobileTrackNameEl = document.getElementById('mobile-ambient-track-name');
        const mobileArtistNameEl = document.getElementById('mobile-ambient-artist-name');
        if (mobileTrackNameEl) mobileTrackNameEl.textContent = trackName;
        if (mobileArtistNameEl) mobileArtistNameEl.textContent = artistName;
    }

    togglePlayPause() {
        if (!this.currentTrack) {
            // No track selected, select first available
            const trackSelect = document.getElementById('ambient-track-select');
            if (trackSelect && this.availableTracks.length > 0) {
                trackSelect.value = this.availableTracks[0].file;
                this.loadTrack(this.availableTracks[0].file);
            }
            return;
        }

        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    play() {
        if (this.audio && this.currentTrack) {
            const playPromise = this.audio.play();

            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('Playing ambient music');
                }).catch(error => {
                    console.error('Play failed:', error);
                    this.handleAudioError();
                });
            }
        }
    }

    pause() {
        if (this.audio) {
            this.audio.pause();
        }
    }

    stop() {
        if (this.audio) {
            this.audio.pause();
            this.audio.currentTime = 0;
        }
    }

    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        if (this.audio) {
            this.audio.volume = this.volume;
        }
    }

    updatePlayButton() {
        // Update all play/pause icons (desktop and mobile)
        const playIcons = document.querySelectorAll('#ambient-play-pause .play-icon, #mobile-ambient-play-pause .play-icon');
        const pauseIcons = document.querySelectorAll('#ambient-play-pause .pause-icon, #mobile-ambient-play-pause .pause-icon');

        playIcons.forEach(icon => {
            if (this.isPlaying) {
                icon.style.setProperty('display', 'none', 'important');
            } else {
                icon.style.setProperty('display', 'flex', 'important');
            }
        });

        pauseIcons.forEach(icon => {
            if (this.isPlaying) {
                icon.style.setProperty('display', 'flex', 'important');
            } else {
                icon.style.setProperty('display', 'none', 'important');
            }
        });
    }

    showPlayer() {
        // Player is always visible in HTML now, nothing to do
    }

    hidePlayer() {
        // Player is always visible, just stop playing
        this.stop();
    }

    handleAudioError() {
        console.warn('Could not load ambient music file. Make sure audio files are in /assets/audio/');
        // Show user-friendly message
        const trackSelect = document.getElementById('ambient-track-select');
        if (trackSelect) {
            const currentOption = trackSelect.options[trackSelect.selectedIndex];
            if (currentOption) {
                currentOption.textContent = currentOption.textContent + ' (unavailable)';
            }
        }
    }

    // Show music player for all characters
    isEnabledForCharacter(characterName) {
        // Music player is available for all characters
        return true;
    }
}

// Export for use in other modules
window.AmbientMusicPlayer = AmbientMusicPlayer;