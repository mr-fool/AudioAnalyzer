# analyzer/visualizer.py
"""
Simple visualization extension for AudioAnalyzer
Adds visualization capabilities using Essentia for consistency
"""

import numpy as np
import cv2
import math
from typing import Dict, Optional
import essentia.standard as es

class VisualizationGenerator:
    """
    Visualization generator using Essentia for consistency with existing AudioAnalyzer
    """
    
    def __init__(self, width: int = 512, height: int = 512):
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        
        # Initialize Essentia algorithms (consistent with your existing code)
        # Note: MonoLoader will be created per-file in create_visualization_video
        self.windowing = es.Windowing(type='hann')
        self.spectrum = es.Spectrum()
        self.mel_bands = es.MelBands()
        self.mfcc = es.MFCC()
        
        # Color palettes for different styles
        self.color_palettes = {
            'neon': [(255, 0, 255), (0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 128), (128, 255, 0)],
            'plasma': [(255, 0, 100), (255, 100, 0), (100, 255, 0), (0, 100, 255), (255, 150, 50), (150, 50, 255)]
        }
    
    def extract_frame_features(self, audio: np.ndarray, frame_start: int, frame_size: int = 2048) -> Dict:
        """Extract audio features using Essentia for consistency"""
        frame_end = min(frame_start + frame_size, len(audio))
        frame_audio = audio[frame_start:frame_end]
        
        if len(frame_audio) < frame_size:
            frame_audio = np.pad(frame_audio, (0, frame_size - len(frame_audio)))
        
        # Apply windowing and get spectrum using Essentia
        windowed = self.windowing(frame_audio)
        spectrum = self.spectrum(windowed)
        
        # Get mel bands for frequency analysis
        try:
            mel_bands = self.mel_bands(spectrum)
            mfcc_bands, mfcc_coeffs = self.mfcc(spectrum)
        except Exception:
            # Fallback if Essentia fails
            mel_bands = np.zeros(40)
            mfcc_coeffs = np.zeros(13)
        
        # Extract meaningful frequency bands
        spectrum_size = len(spectrum)
        if spectrum_size > 0:
            # Define frequency ranges as spectrum indices
            bass_end = int(spectrum_size * 0.1)  # Low frequencies
            mid_start = bass_end
            mid_end = int(spectrum_size * 0.4)   # Mid frequencies  
            treble_start = mid_end               # High frequencies
            
            bass_energy = np.mean(spectrum[:bass_end]) if bass_end > 0 else 0
            mid_energy = np.mean(spectrum[mid_start:mid_end]) if mid_end > mid_start else 0
            treble_energy = np.mean(spectrum[treble_start:]) if treble_start < spectrum_size else 0
        else:
            bass_energy = mid_energy = treble_energy = 0
        
        return {
            'bass': bass_energy,
            'mid': mid_energy, 
            'treble': treble_energy,
            'amplitude': np.mean(np.abs(frame_audio)),
            'mel_bands': mel_bands,
            'mfcc': mfcc_coeffs,
            'spectrum': spectrum
        }
    
    def generate_mandala_frame(self, features: Dict, time_progress: float) -> np.ndarray:
        """Generate complex geometric mandala with intricate patterns"""
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Extract and scale features for better visibility
        bass = min(features['bass'] * 500, 1.0)
        mid = min(features['mid'] * 300, 1.0)
        treble = min(features['treble'] * 200, 1.0)
        amplitude = min(features['amplitude'] * 100, 1.0)
        mel_bands = features['mel_bands']
        
        colors = self.color_palettes['neon']
        center_x, center_y = self.center
        
        # Geometric mandala parameters
        base_segments = 12 + int(bass * 12)  # 12-24 primary segments
        rotation = (time_progress * 10 + mid * 15) % 360
        base_radius = 60 + amplitude * 100  # 60-160 pixel base radius
        
        # Layer 1: Outer geometric ring with complex patterns
        for segment in range(base_segments):
            segment_angle = (360 / base_segments) * segment + rotation
            angle_rad = math.radians(segment_angle)
            
            # Mel band influence for this segment
            mel_idx = segment % len(mel_bands)
            mel_influence = 1.0 + mel_bands[mel_idx] * 2
            
            # Color cycling
            color_idx = (segment + int(treble * 10)) % len(colors)
            color = colors[color_idx]
            brightness = min(1.0, 0.4 + amplitude * 0.6 + mel_bands[mel_idx] * 0.3)
            color = tuple(int(c * brightness) for c in color)
            
            # Outer radius with variation
            outer_radius = base_radius * mel_influence
            inner_radius = outer_radius * 0.7
            
            # Calculate segment points
            outer_x = int(center_x + math.cos(angle_rad) * outer_radius)
            outer_y = int(center_y + math.sin(angle_rad) * outer_radius)
            inner_x = int(center_x + math.cos(angle_rad) * inner_radius)
            inner_y = int(center_y + math.sin(angle_rad) * inner_radius)
            
            # Create geometric segment with angular sides
            next_segment_angle = (360 / base_segments) * ((segment + 1) % base_segments) + rotation
            next_angle_rad = math.radians(next_segment_angle)
            
            next_outer_x = int(center_x + math.cos(next_angle_rad) * outer_radius)
            next_outer_y = int(center_y + math.sin(next_angle_rad) * outer_radius)
            next_inner_x = int(center_x + math.cos(next_angle_rad) * inner_radius)
            next_inner_y = int(center_y + math.sin(next_angle_rad) * inner_radius)
            
            # Draw geometric segment as polygon
            segment_points = np.array([
                [inner_x, inner_y],
                [outer_x, outer_y],
                [next_outer_x, next_outer_y],
                [next_inner_x, next_inner_y]
            ], dtype=np.int32)
            
            cv2.fillPoly(img, [segment_points], color)
            cv2.polylines(img, [segment_points], True, tuple(min(255, int(c * 1.3)) for c in color), 1)
        
        # Layer 2: Middle geometric pattern - star shapes
        mid_segments = base_segments * 2  # Double the segments for finer detail
        mid_radius = base_radius * 0.6
        
        for segment in range(0, mid_segments, 2):  # Every other segment for star pattern
            segment_angle = (360 / mid_segments) * segment + rotation * 0.5
            angle_rad = math.radians(segment_angle)
            
            color_idx = (segment // 2) % len(colors)
            color = colors[color_idx]
            brightness = min(1.0, 0.5 + mid * 0.5)
            color = tuple(int(c * brightness) for c in color)
            
            # Star point geometry
            point_radius = mid_radius * (1.0 + mel_bands[segment % len(mel_bands)])
            point_x = int(center_x + math.cos(angle_rad) * point_radius)
            point_y = int(center_y + math.sin(angle_rad) * point_radius)
            
            # Create star points with connecting lines
            base_radius_inner = mid_radius * 0.4
            base_x = int(center_x + math.cos(angle_rad) * base_radius_inner)
            base_y = int(center_y + math.sin(angle_rad) * base_radius_inner)
            
            # Side points for triangular star points
            side_angle_offset = math.radians(360 / mid_segments)
            left_angle = angle_rad - side_angle_offset * 0.3
            right_angle = angle_rad + side_angle_offset * 0.3
            
            left_x = int(center_x + math.cos(left_angle) * base_radius_inner)
            left_y = int(center_y + math.sin(left_angle) * base_radius_inner)
            right_x = int(center_x + math.cos(right_angle) * base_radius_inner)
            right_y = int(center_y + math.sin(right_angle) * base_radius_inner)
            
            # Draw triangular star point
            star_points = np.array([
                [base_x, base_y],
                [left_x, left_y],
                [point_x, point_y],
                [right_x, right_y]
            ], dtype=np.int32)
            
            cv2.fillPoly(img, [star_points], color)
            cv2.polylines(img, [star_points], True, tuple(min(255, int(c * 1.4)) for c in color), 2)
        
        # Layer 3: Inner geometric ring - hexagonal/octagonal patterns
        inner_segments = 8  # Fixed geometric symmetry
        inner_radius = base_radius * 0.35
        
        for segment in range(inner_segments):
            segment_angle = (360 / inner_segments) * segment + rotation * -0.3
            angle_rad = math.radians(segment_angle)
            
            color_idx = segment % len(colors)
            color = colors[color_idx]
            brightness = min(1.0, 0.6 + treble * 0.4)
            color = tuple(int(c * brightness) for c in color)
            
            # Create geometric shapes (hexagons/diamonds)
            shape_radius = inner_radius * (0.8 + mel_bands[segment % len(mel_bands)] * 0.4)
            
            # Generate regular polygon points
            polygon_sides = 6  # Hexagon
            polygon_points = []
            
            for poly_point in range(polygon_sides):
                poly_angle = angle_rad + math.radians((360 / polygon_sides) * poly_point)
                poly_x = int(center_x + math.cos(poly_angle) * shape_radius)
                poly_y = int(center_y + math.sin(poly_angle) * shape_radius)
                polygon_points.append([poly_x, poly_y])
            
            polygon_points = np.array(polygon_points, dtype=np.int32)
            cv2.fillPoly(img, [polygon_points], color)
            cv2.polylines(img, [polygon_points], True, 
                         tuple(min(255, int(c * 1.5)) for c in color), 2)
        
        # Layer 4: Geometric connecting lines - sacred geometry
        connection_radius = base_radius * 0.8
        num_connections = base_segments
        
        for i in range(num_connections):
            angle1 = math.radians((360 / num_connections) * i + rotation)
            angle2 = math.radians((360 / num_connections) * ((i + 3) % num_connections) + rotation)  # Connect every 3rd point
            
            x1 = int(center_x + math.cos(angle1) * connection_radius)
            y1 = int(center_y + math.sin(angle1) * connection_radius)
            x2 = int(center_x + math.cos(angle2) * connection_radius)
            y2 = int(center_y + math.sin(angle2) * connection_radius)
            
            color_idx = i % len(colors)
            color = colors[color_idx]
            alpha = min(255, int(100 + amplitude * 155))  # Semi-transparent connecting lines
            color = tuple(int(c * 0.6) for c in color)  # Dimmer for background lines
            
            cv2.line(img, (x1, y1), (x2, y2), color, 1)
        
        # Central mandala core - complex geometric center
        core_radius = int(20 + amplitude * 20)
        
        # Multiple concentric geometric shapes in center
        for core_ring in range(4):
            ring_radius = core_radius - core_ring * 4
            if ring_radius > 0:
                color = colors[core_ring % len(colors)]
                brightness = 1.0 - core_ring * 0.2
                color = tuple(int(c * brightness) for c in color)
                
                # Draw geometric center shapes
                if core_ring % 2 == 0:
                    # Circles
                    cv2.circle(img, (center_x, center_y), ring_radius, color, 2)
                else:
                    # Squares/diamonds
                    square_points = []
                    for corner in range(4):
                        corner_angle = math.radians(45 + 90 * corner + rotation * 0.1)
                        corner_x = int(center_x + math.cos(corner_angle) * ring_radius)
                        corner_y = int(center_y + math.sin(corner_angle) * ring_radius)
                        square_points.append([corner_x, corner_y])
                    
                    square_points = np.array(square_points, dtype=np.int32)
                    cv2.polylines(img, [square_points], True, color, 2)
        
        # Final center point
        cv2.circle(img, (center_x, center_y), 3, (255, 255, 255), -1)
        
        return img
    
    def generate_kaleidoscope_frame(self, features: Dict, time_progress: float) -> np.ndarray:
        """Generate true kaleidoscope visualization with organic flowing patterns"""
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        bass = features['bass'] * 100
        mid = features['mid'] * 100
        treble = features['treble'] * 100
        amplitude = features['amplitude'] * 50
        mel_bands = features['mel_bands']
        
        colors = self.color_palettes['plasma']
        
        # Kaleidoscope with flowing organic segments
        num_segments = 64  # More segments for smoother kaleidoscope
        base_radius = 80
        
        for i in range(num_segments):
            segment_angle = (360 / num_segments) * i
            
            # Create organic flowing radius using multiple wave functions
            wave1 = math.sin(time_progress * 2 + i * 0.1)
            wave2 = math.cos(time_progress * 1.5 + i * 0.15)
            wave3 = math.sin(time_progress * 3 + i * 0.05)
            
            # Mel band influence on radius
            mel_idx = min(i % len(mel_bands), len(mel_bands) - 1)
            mel_influence = mel_bands[mel_idx] * 3
            
            # Complex radius calculation for organic feel
            radius_variation = base_radius * (
                0.5 +                           # Base
                bass * 0.008 +                  # Bass influence
                wave1 * 0.3 +                   # Primary wave
                wave2 * 0.2 +                   # Secondary wave  
                wave3 * 0.1 +                   # Tertiary wave
                mel_influence * 0.3 +           # Mel band influence
                amplitude * 0.01                # Amplitude influence
            )
            
            # Multiple depth layers for kaleidoscope effect
            for depth in range(6):
                depth_scale = 0.2 + depth * 0.16  # 0.2, 0.36, 0.52, 0.68, 0.84, 1.0
                layer_radius = radius_variation * depth_scale
                
                # Color cycling with time and depth
                color_phase = (time_progress * 0.3 + i * 0.02 + depth * 0.1) % 1
                color_idx = int(color_phase * len(colors))
                base_color = colors[color_idx % len(colors)]
                
                # Dynamic brightness based on audio
                brightness = min(1.0, 0.2 + mid * 0.01 + treble * 0.008 + depth * 0.1)
                color = tuple(int(c * brightness) for c in base_color)
                
                # Calculate flowing positions with multiple wave offsets
                wave_offset_x = (math.sin(time_progress * 1.8 + i * 0.25 + depth * 0.1) * 
                               (5 + bass * 0.1))
                wave_offset_y = (math.cos(time_progress * 2.2 + i * 0.3 + depth * 0.15) * 
                               (5 + mid * 0.1))
                
                angle_rad = math.radians(segment_angle + time_progress * 10)
                x = int(self.center[0] + math.cos(angle_rad) * layer_radius + wave_offset_x)
                y = int(self.center[1] + math.sin(angle_rad) * layer_radius + wave_offset_y)
                
                # Create flowing connections
                next_segment = (i + 1) % num_segments
                next_angle_rad = math.radians((360 / num_segments) * next_segment + time_progress * 10)
                next_x = int(self.center[0] + math.cos(next_angle_rad) * layer_radius + wave_offset_x)
                next_y = int(self.center[1] + math.sin(next_angle_rad) * layer_radius + wave_offset_y)
                
                # Draw flowing curves
                thickness = max(1, int(1 + treble * 0.05 + depth * 0.5))
                cv2.line(img, (x, y), (next_x, next_y), color, thickness)
                
                # Add organic particles/nodes
                particle_size = max(1, int(1 + amplitude * 0.1 + depth * 0.3))  # Always define particle_size
                if amplitude > 2:
                    cv2.circle(img, (x, y), particle_size, color, -1)
                
                # Create symmetric kaleidoscope effect by mirroring
                if depth % 2 == 0:  # Mirror every other layer
                    mirror_x = self.width - x
                    mirror_y = self.height - y
                    if 0 <= mirror_x < self.width and 0 <= mirror_y < self.height:
                        cv2.circle(img, (mirror_x, mirror_y), particle_size, color, -1)
        
        # Apply slight blur for organic flow effect
        img = cv2.GaussianBlur(img, (3, 3), 0.5)
        
        return img
    
    def create_visualization_video(self, audio_file: str, output_file: str = "visualization.mp4",
                                 duration: float = 10.0, fps: int = 24, style: str = "mixed") -> Optional[str]:
        """
        Create MP4 visualization directly from audio file using Essentia
        """
        print(f"Loading audio from {audio_file}")
        
        try:
            # Load audio using Essentia (consistent with your existing code)
            # Configure the loader with the filename, then call it
            loader = es.MonoLoader(filename=audio_file, sampleRate=44100)
            audio = loader()
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None
        
        print(f"Audio loaded: {len(audio)/44100:.2f}s duration")
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_file, fourcc, fps, (self.width, self.height))
        
        if not video_writer.isOpened():
            print("Error: Could not open video writer")
            return None
        
        # Calculate frame parameters
        total_frames = int(duration * fps)
        frame_size = 2048
        hop_size = int(44100 / fps)  # Samples per video frame
        
        print(f"Generating {total_frames} frames at {fps} FPS")
        
        for frame_idx in range(total_frames):
            # Calculate audio position
            time_progress = (frame_idx / total_frames) * duration
            audio_sample_idx = int(time_progress * 44100)
            
            # Extract features using Essentia
            features = self.extract_frame_features(audio, audio_sample_idx, frame_size)
            
            # Choose visualization style
            if style == "mixed":
                # Switch based on audio characteristics
                if features['bass'] > features['treble']:
                    use_mandala = True  # Mandala for bass-heavy sections
                else:
                    use_mandala = False  # Kaleidoscope for treble-heavy sections
            elif style == "mandala":
                use_mandala = True
            else:  # kaleidoscope
                use_mandala = False
            
            # Generate frame
            if use_mandala:
                frame = self.generate_mandala_frame(features, time_progress * 10)
            else:
                frame = self.generate_kaleidoscope_frame(features, time_progress * 10)
            
            # Write frame to video
            video_writer.write(frame)
            
            # Progress update
            if (frame_idx + 1) % 30 == 0:
                progress = (frame_idx + 1) / total_frames * 100
                print(f"Progress: {progress:.1f}% ({frame_idx + 1}/{total_frames})")
        
        video_writer.release()
        print(f"Visualization saved as {output_file}")
        
        return output_file