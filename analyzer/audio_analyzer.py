import numpy as np
import essentia
import essentia.standard as es
import os

class AudioAnalyzer:
    def __init__(self):
        self.sample_rate = 44100
        self.results = {}
        
    def load_audio(self, file_path):
        """Load audio file using Essentia"""
        try:
            # Load audio file
            audio = es.MonoLoader(filename=file_path, sampleRate=self.sample_rate)()
            return audio
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None
            
    def analyze_audio(self, file_path):
        """Analyze audio using Essentia"""
        results = {}
        
        # Load audio
        audio = self.load_audio(file_path)
        if audio is None:
            raise Exception("Failed to load audio file")
        
        # Ensure audio array has even length for FFT
        if len(audio) % 2 != 0:
            audio = audio[:-1]  # Remove last sample to make it even
            
        # Calculate Nyquist frequency based on sample rate
        nyquist_freq = self.sample_rate / 2
        high_freq_bound = min(22000, nyquist_freq - 50)  # Set high bound safely below Nyquist
            
        # Initialize algorithms
        spectrum = es.Spectrum()
        melBands = es.MelBands(inputSize=len(audio) // 2 + 1, 
                              highFrequencyBound=high_freq_bound)  # Set high freq safely
        mfcc = es.MFCC(inputSize=len(audio) // 2 + 1, 
                      highFrequencyBound=high_freq_bound)  # Set high freq safely
        key = es.Key()
        bpm = es.RhythmExtractor2013()
        loudness = es.Loudness()
        dissonance = es.Dissonance()
        
        # Initialize HPCP with the required algorithms
        spectralPeaks = es.SpectralPeaks()
        hpcp = es.HPCP()
        
        # Extract features with error handling
        try:
            spec = spectrum(audio)
            mel_bands = melBands(spec)
            mfcc_bands = mfcc(spec)[1]
            
            # Calculate HPCP by first getting the spectral peaks
            freqs, mags = spectralPeaks(spec)
            hpcp_output = hpcp(freqs, mags)
            
            # Dissonance also needs spectral peaks
            diss = dissonance(freqs, mags)  # Pass both frequencies and magnitudes
            
            # Get key with error handling
            try:
                key_data = key(hpcp_output)
            except Exception as e:
                print(f"Warning: Key detection error: {e}")
                # Use default key if detection fails
                key_data = ("C major", "major")  # Default to C major
                
            rhythm_data = bpm(audio)
            loud = loudness(audio)
        except Exception as e:
            print(f"Warning: Feature extraction error: {e}")
            # Use default values if extraction fails
            spec = np.zeros(1025)  # Default empty spectrum
            mel_bands = np.zeros(40)  # Default mel bands
            mfcc_bands = np.zeros(13)  # Default MFCC bands
            key_data = ("C major", "major")  # Default to C major
            rhythm_data = (120, np.array([0]), np.array([0]), np.array([0]))  # Default 120 BPM
            loud = -20  # Default loudness
            diss = 0.5  # Default dissonance
        
        # Instrument detection using MusicExtractor
        try:
            music_extractor = es.MusicExtractor(lowlevelStats=['mean', 'stdev'],
                                              rhythmStats=['mean', 'stdev'],
                                              tonalStats=['mean', 'stdev'])
            features = music_extractor(file_path)
            
            # Debug: Print the features structure
            print(f"MusicExtractor features type: {type(features)}")
            if isinstance(features, tuple):
                print(f"Features tuple length: {len(features)}")
                if features and len(features) > 0:
                    print(f"First element type: {type(features[0])}")
            
            # Process Pool object from MusicExtractor
            if isinstance(features, tuple) and features:
                first_element = features[0]
                # Check if it's a Pool object (has descriptorNames method)
                if hasattr(first_element, 'descriptorNames') and callable(getattr(first_element, 'descriptorNames', None)):
                    print("First element is a Pool, converting to dictionary")
                    # Convert Pool to dictionary
                    features_dict = {}
                    for name in first_element.descriptorNames():
                        try:
                            features_dict[name] = first_element[name]
                        except Exception as e:
                            print(f"Error accessing Pool descriptor {name}: {e}")
                elif isinstance(first_element, dict):
                    features_dict = first_element
                else:
                    print(f"Unknown first element type: {type(first_element)}, using default features")
                    features_dict = self._create_default_features()
            else:
                features_dict = features
                
        except Exception as e:
            print(f"Warning: MusicExtractor error: {e}")
            # Create a minimal features dict with defaults
            features_dict = self._create_default_features()
        
        # Mood detection based on features
        # Using simple rules based on key, tempo and spectral features
        mood = self._detect_mood(key_data[0], rhythm_data[0], loud, mfcc_bands, mel_bands)
        
        # Instrument detection
        instruments = self._detect_instruments(features_dict)
        
        # Store results
        results["key"] = f"{key_data[0]} {key_data[1]}"  # Key name and scale
        results["bpm"] = round(rhythm_data[0], 1)  # BPM value
        results["loudness"] = round(loud, 2)  # Loudness in dB
        results["dissonance"] = round(diss, 2)  # Dissonance value
        results["mood"] = mood  # Detected mood
        results["instruments"] = instruments  # Detected instruments
        results["advanced_features"] = features_dict  # All extracted features
        results["audio"] = audio  # Store audio for visualization
        results["file_name"] = os.path.basename(file_path)  # Store filename for reference
        
        # Debug: Print structure of the features_dict
        print(f"Feature dictionary structure: {type(features_dict)}")
        if isinstance(features_dict, dict):
            print(f"Feature dictionary keys sample: {list(features_dict.keys())[:5] if features_dict else []}")
        
        self.results = results
        return results
    
    def _create_default_features(self):
        """Create default features dict in case MusicExtractor fails"""
        features = {
            'lowlevel.dynamic_complexity': 0.3,
            'rhythm.danceability': 0.5,
            'tonal.chords_number': 3,
            'rhythm.beats_loudness.mean': 0.4,
            'lowlevel.spectral_energy_band_ratio_0.mean': 0.3,
            'lowlevel.spectral_energy_band_ratio_1.mean': 0.2,
            'lowlevel.spectral_energy_band_ratio_2.mean': 0.2,
            'lowlevel.spectral_energy_band_ratio_3.mean': 0.1,
            'lowlevel.spectral_contrast_coeffs_0.mean': 0.1,
            'lowlevel.mfcc_bands.mean': 0.4,
            'lowlevel.spectral_centroid.mean': 1200,
            'lowlevel.spectral_rolloff.mean': 2000,
            'lowlevel.spectral_flatness_db.mean': -35
        }
        return features
    
    def _detect_mood(self, key, bpm, loudness, mfcc_bands, mel_bands):
        """Detect mood of the audio based on extracted features"""
        moods = []
        
        # Tempo based mood detection
        if bpm < 70:
            moods.append("slow")
            moods.append("relaxed")
        elif bpm < 100:
            moods.append("moderate")
            moods.append("steady")
        elif bpm < 120:
            moods.append("upbeat")
        else:
            moods.append("energetic")
            moods.append("fast")
        
        # Loudness based mood
        if loudness < -20:
            moods.append("soft")
            moods.append("intimate")
        elif loudness < -10:
            moods.append("balanced")
        else:
            moods.append("loud")
            moods.append("intense")
        
        # Key based mood (simplified)
        major_keys = ["C major", "G major", "D major", "A major", "E major", "B major", "F# major"]
        minor_keys = ["A minor", "E minor", "B minor", "F# minor", "C# minor", "G# minor", "D# minor"]
        
        if key in major_keys:
            moods.append("happy")
            moods.append("bright")
        elif key in minor_keys:
            moods.append("melancholic")
            moods.append("somber")
        
        # Spectral features for additional mood detection
        # High energy in higher mel bands often indicates brightness
        try:
            high_energy = np.mean(mel_bands[15:]) > np.mean(mel_bands[:15])
            if high_energy:
                moods.append("bright")
                moods.append("sharp")
            else:
                moods.append("warm")
                moods.append("deep")
        except:
            # Default values if calculation fails
            moods.append("balanced")
        
        # Use MFCC for texture
        try:
            mfcc_std = np.std(mfcc_bands)
            if mfcc_std > 15:
                moods.append("complex")
                moods.append("textured")
            else:
                moods.append("simple")
                moods.append("clean")
        except:
            # Default values if calculation fails
            moods.append("textured")
        
        # Remove duplicates and return
        return list(set(moods))
    
    def _detect_instruments(self, features):
        """Detect instruments in the audio based on extracted features"""
        instruments = []
        
        try:
            # Check if features is a Pool object
            if hasattr(features, 'descriptorNames') and callable(getattr(features, 'descriptorNames', None)):
                # Check for percussion
                if 'rhythm.beats_loudness.mean' in features.descriptorNames() and features['rhythm.beats_loudness.mean'] > 0.5:
                    instruments.append("drums")
                
                # Check for bass
                if 'lowlevel.spectral_energy_band_ratio_0.mean' in features.descriptorNames() and features['lowlevel.spectral_energy_band_ratio_0.mean'] > 0.4:
                    instruments.append("bass")
                
                # Check for guitar or strings
                if 'lowlevel.spectral_energy_band_ratio_2.mean' in features.descriptorNames() and features['lowlevel.spectral_energy_band_ratio_2.mean'] > 0.3:
                    if 'lowlevel.spectral_centroid.mean' in features.descriptorNames() and features['lowlevel.spectral_centroid.mean'] < 1500:
                        instruments.append("guitar")
                    else:
                        instruments.append("strings")
                
                # Check for piano
                if ('lowlevel.spectral_energy_band_ratio_1.mean' in features.descriptorNames() and 
                    'lowlevel.spectral_contrast_coeffs_0.mean' in features.descriptorNames() and
                    features['lowlevel.spectral_energy_band_ratio_1.mean'] > 0.25 and 
                    features['lowlevel.spectral_contrast_coeffs_0.mean'] > 0.2):
                    instruments.append("piano")
                
                # Check for vocals
                if 'lowlevel.mfcc_bands.mean' in features.descriptorNames() and features['lowlevel.mfcc_bands.mean'] > 0.5:
                    instruments.append("vocals")
                
                # Check for brass
                if ('lowlevel.spectral_energy_band_ratio_3.mean' in features.descriptorNames() and
                    'lowlevel.spectral_rolloff.mean' in features.descriptorNames() and
                    features['lowlevel.spectral_energy_band_ratio_3.mean'] > 0.2 and 
                    features['lowlevel.spectral_rolloff.mean'] > 3000):
                    instruments.append("brass")
                
                # Check for synthesizers
                if 'lowlevel.spectral_flatness_db.mean' in features.descriptorNames() and features['lowlevel.spectral_flatness_db.mean'] > -30:
                    instruments.append("synthesizer")
                    
            # Check if features is a tuple (some versions of Essentia return tuples)
            elif isinstance(features, tuple):
                # It's likely that the first element is the actual features dict
                if features and isinstance(features[0], dict):
                    features = features[0]
                    
                    # Now process as dictionary
                    if features.get('rhythm.beats_loudness.mean', 0) > 0.5:
                        instruments.append("drums")
                    
                    if features.get('lowlevel.spectral_energy_band_ratio_0.mean', 0) > 0.4:
                        instruments.append("bass")
                    
                    if features.get('lowlevel.spectral_energy_band_ratio_2.mean', 0) > 0.3:
                        if features.get('lowlevel.spectral_centroid.mean', 0) < 1500:
                            instruments.append("guitar")
                        else:
                            instruments.append("strings")
                    
                    if (features.get('lowlevel.spectral_energy_band_ratio_1.mean', 0) > 0.25 and 
                        features.get('lowlevel.spectral_contrast_coeffs_0.mean', 0) > 0.2):
                        instruments.append("piano")
                    
                    if features.get('lowlevel.mfcc_bands.mean', 0) > 0.5:
                        instruments.append("vocals")
                    
                    if (features.get('lowlevel.spectral_energy_band_ratio_3.mean', 0) > 0.2 and 
                        features.get('lowlevel.spectral_rolloff.mean', 0) > 3000):
                        instruments.append("brass")
                    
                    if features.get('lowlevel.spectral_flatness_db.mean', -50) > -30:
                        instruments.append("synthesizer")
                else:
                    # Fallback to default features if structure is unexpected
                    return ["mixed instruments"]
            # If features is a dictionary        
            elif isinstance(features, dict):
                # Check for percussion
                if features.get('rhythm.beats_loudness.mean', 0) > 0.5:
                    instruments.append("drums")
                
                # Check for bass
                if features.get('lowlevel.spectral_energy_band_ratio_0.mean', 0) > 0.4:
                    instruments.append("bass")
                
                # Check for guitar or strings
                if features.get('lowlevel.spectral_energy_band_ratio_2.mean', 0) > 0.3:
                    if features.get('lowlevel.spectral_centroid.mean', 0) < 1500:
                        instruments.append("guitar")
                    else:
                        instruments.append("strings")
                
                # Check for piano
                if (features.get('lowlevel.spectral_energy_band_ratio_1.mean', 0) > 0.25 and 
                    features.get('lowlevel.spectral_contrast_coeffs_0.mean', 0) > 0.2):
                    instruments.append("piano")
                
                # Check for vocals
                if features.get('lowlevel.mfcc_bands.mean', 0) > 0.5:
                    instruments.append("vocals")
                
                # Check for brass
                if (features.get('lowlevel.spectral_energy_band_ratio_3.mean', 0) > 0.2 and 
                    features.get('lowlevel.spectral_rolloff.mean', 0) > 3000):
                    instruments.append("brass")
                
                # Check for synthesizers
                if features.get('lowlevel.spectral_flatness_db.mean', -50) > -30:
                    instruments.append("synthesizer")
        except Exception as e:
            print(f"Warning: Instrument detection error: {e}")
        
        # If no instruments detected, add some fallbacks based on general features
        if not instruments:
            try:
                # For Pool object
                if hasattr(features, 'descriptorNames') and callable(getattr(features, 'descriptorNames', None)):
                    if 'lowlevel.spectral_centroid.mean' in features.descriptorNames():
                        if features['lowlevel.spectral_centroid.mean'] < 1000:
                            instruments.append("bass-heavy instruments")
                        elif features['lowlevel.spectral_centroid.mean'] < 2000:
                            instruments.append("mid-range instruments")
                        else:
                            instruments.append("high-range instruments")
                # For dictionary
                elif isinstance(features, dict):
                    if features.get('lowlevel.spectral_centroid.mean', 0) < 1000:
                        instruments.append("bass-heavy instruments")
                    elif features.get('lowlevel.spectral_centroid.mean', 0) < 2000:
                        instruments.append("mid-range instruments")
                    else:
                        instruments.append("high-range instruments")
            except:
                # Most generic fallback
                instruments.append("mixed instruments")
        
        if not instruments:
            instruments.append("mixed instruments")
        
        return instruments
    
    def generate_description(self):
        """Generate a detailed description of the audio for LLM input"""
        if not self.results:
            return "No analysis results available."
        
        r = self.results
        
        # Create a descriptive text about the audio
        description = f"This audio track is in {r['key']} with a tempo of {r['bpm']} BPM. "
        description += f"The overall loudness is {r['loudness']} dB, which makes it a "
        
        # Add mood description
        if r['mood']:
            description += f"{', '.join(r['mood'][:3])} piece. "
        
        # Add instruments
        if r['instruments']:
            description += f"The main instruments detected are {', '.join(r['instruments'])}. "
        
        # Add additional characteristics
        if 'advanced_features' in r:
            try:
                f = r['advanced_features']
                
                # More robust structure checking for features
                valid_features = False
                
                # Check if f is a Pool object
                if hasattr(f, 'descriptorNames') and callable(getattr(f, 'descriptorNames', None)):
                    valid_features = True
                    # Dynamics
                    if 'lowlevel.dynamic_complexity' in f.descriptorNames() and f['lowlevel.dynamic_complexity'] > 0.5:
                        description += "It has varied dynamics with significant changes in intensity. "
                    else:
                        description += "It maintains a relatively consistent dynamic level throughout. "
                    
                    # Rhythm
                    if 'rhythm.danceability' in f.descriptorNames() and f['rhythm.danceability'] > 0.6:
                        description += "The rhythm is highly danceable and groovy. "
                    else:
                        description += "The rhythm is more complex and less dance-oriented. "
                        
                    # Harmony
                    if 'tonal.chords_number' in f.descriptorNames() and f['tonal.chords_number'] > 4:
                        description += "It has a rich harmonic progression with multiple chord changes. "
                    else:
                        description += "It has a simpler harmonic structure with fewer chord changes. "
                
                # If features is a tuple, try to extract the dictionary
                elif isinstance(f, tuple):
                    if f and hasattr(f[0], 'descriptorNames') and callable(getattr(f[0], 'descriptorNames', None)):
                        valid_features = True
                        pool = f[0]
                        # Dynamics
                        if 'lowlevel.dynamic_complexity' in pool.descriptorNames() and pool['lowlevel.dynamic_complexity'] > 0.5:
                            description += "It has varied dynamics with significant changes in intensity. "
                        else:
                            description += "It maintains a relatively consistent dynamic level throughout. "
                        
                        # Rhythm
                        if 'rhythm.danceability' in pool.descriptorNames() and pool['rhythm.danceability'] > 0.6:
                            description += "The rhythm is highly danceable and groovy. "
                        else:
                            description += "The rhythm is more complex and less dance-oriented. "
                            
                        # Harmony
                        if 'tonal.chords_number' in pool.descriptorNames() and pool['tonal.chords_number'] > 4:
                            description += "It has a rich harmonic progression with multiple chord changes. "
                        else:
                            description += "It has a simpler harmonic structure with fewer chord changes. "
                    elif f and isinstance(f[0], dict):
                        valid_features = True
                        dict_f = f[0]
                        # Dynamics
                        if dict_f.get('lowlevel.dynamic_complexity', 0) > 0.5:
                            description += "It has varied dynamics with significant changes in intensity. "
                        else:
                            description += "It maintains a relatively consistent dynamic level throughout. "
                        
                        # Rhythm
                        if dict_f.get('rhythm.danceability', 0) > 0.6:
                            description += "The rhythm is highly danceable and groovy. "
                        else:
                            description += "The rhythm is more complex and less dance-oriented. "
                            
                        # Harmony
                        if dict_f.get('tonal.chords_number', 0) > 4:
                            description += "It has a rich harmonic progression with multiple chord changes. "
                        else:
                            description += "It has a simpler harmonic structure with fewer chord changes. "
                # If features is already a dictionary
                elif isinstance(f, dict):
                    valid_features = True
                    # Dynamics
                    if f.get('lowlevel.dynamic_complexity', 0) > 0.5:
                        description += "It has varied dynamics with significant changes in intensity. "
                    else:
                        description += "It maintains a relatively consistent dynamic level throughout. "
                    
                    # Rhythm
                    if f.get('rhythm.danceability', 0) > 0.6:
                        description += "The rhythm is highly danceable and groovy. "
                    else:
                        description += "The rhythm is more complex and less dance-oriented. "
                        
                    # Harmony
                    if f.get('tonal.chords_number', 0) > 4:
                        description += "It has a rich harmonic progression with multiple chord changes. "
                    else:
                        description += "It has a simpler harmonic structure with fewer chord changes. "
                
                # If no valid features structure found
                if not valid_features:
                    # Use generic description if structure is unexpected
                    description += "It has a distinctive sonic character. "
            except Exception as e:
                print(f"Warning: Error generating additional characteristics: {e}")
                # Add generic description if we can't get specific features
                description += "It has a distinctive sonic character. "
        
        # Summary for lyrics suggestions
        description += "\n\nLyrics for this track should reflect its "
        if r['mood']:
            description += f"{', '.join(r['mood'][:2])} atmosphere"
        else:
            description += "distinctive atmosphere"
            
        description += " and could explore themes that complement its "
        
        # Suggest themes based on mood
        themes = []
        moods = r.get('mood', [])
        
        if any(m in moods for m in ["happy", "bright", "energetic"]):
            themes.extend(["celebration", "optimism", "adventure"])
        elif any(m in moods for m in ["melancholic", "somber", "soft"]):
            themes.extend(["reflection", "longing", "memory"])
        elif any(m in moods for m in ["intense", "complex", "fast"]):
            themes.extend(["struggle", "determination", "passion"])
        else:
            themes.extend(["journey", "transformation", "connection"])
            
        description += f"{', '.join(themes)} themes."
        
        return description

    def export_results_to_json(self, file_path):
        """Export analysis results to a JSON file"""
        if not self.results:
            print("No results available to export")
            return False
            
        try:
            import json
            # Create a copy of results without the audio data (which can't be serialized)
            export_data = self.results.copy()
            if 'audio' in export_data:
                del export_data['audio']
                
            # Convert numpy arrays to lists for JSON serialization
            for key, value in export_data.items():
                if isinstance(value, np.ndarray):
                    export_data[key] = value.tolist()
                    
            # Handle advanced features
            if 'advanced_features' in export_data:
                advanced_features = export_data['advanced_features']
                # If it's a Pool object, convert to dict
                if hasattr(advanced_features, 'descriptorNames'):
                    feature_dict = {}
                    for name in advanced_features.descriptorNames():
                        try:
                            # Convert numpy arrays to lists
                            value = advanced_features[name]
                            if isinstance(value, np.ndarray):
                                feature_dict[name] = value.tolist()
                            else:
                                feature_dict[name] = value
                        except:
                            pass
                    export_data['advanced_features'] = feature_dict
            
            # Write to JSON file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            print(f"Results exported to {file_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False
            
    def batch_analyze(self, file_list, callback=None):
        """Analyze multiple audio files in batch mode"""
        results = []
        
        for i, file_path in enumerate(file_list):
            try:
                print(f"Analyzing file {i+1}/{len(file_list)}: {os.path.basename(file_path)}")
                file_results = self.analyze_audio(file_path)
                results.append({
                    'file_path': file_path,
                    'results': file_results
                })
                
                # Call the callback if provided
                if callback:
                    callback(i+1, len(file_list), file_path, file_results)
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                results.append({
                    'file_path': file_path,
                    'error': str(e)
                })
                
                # Call the callback with error
                if callback:
                    callback(i+1, len(file_list), file_path, None, str(e))
        
        return results