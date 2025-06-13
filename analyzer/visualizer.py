# analyzer/visualizer.py
"""
Simple visualization extension for AudioAnalyzer
Adds visualization capabilities using Essentia for consistency
"""

import numpy as np
import cv2
import math
import os
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
    
    def generate_sacred_geometry_frame(self, features: Dict, time_progress: float) -> np.ndarray:
        """Generate complex sacred geometry mandala like the original screenshot"""
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Extract and scale features
        bass = min(features['bass'] * 500, 1.0)
        mid = min(features['mid'] * 300, 1.0)
        treble = min(features['treble'] * 200, 1.0)
        amplitude = min(features['amplitude'] * 100, 1.0)
        mel_bands = features['mel_bands']
        
        colors = self.color_palettes['neon']
        center_x, center_y = self.center
        
        # Base parameters for sacred geometry
        rotation = (time_progress * 8 + mid * 10) % 360
        base_radius = 50 + amplitude * 120  # 50-170 pixel radius
        
        # Layer 1: Outermost geometric ring - Complex interlocking patterns
        outer_segments = 24  # More segments for complexity
        outer_radius = base_radius * 1.0
        
        for i in range(outer_segments):
            angle = (360 / outer_segments) * i + rotation
            angle_rad = math.radians(angle)
            
            # Color cycling
            color_idx = i % len(colors)
            color = colors[color_idx]
            brightness = min(1.0, 0.6 + amplitude * 0.4)
            color = tuple(int(c * brightness) for c in color)
            
            # Create interlocking geometric shapes
            # Outer points
            outer_x = int(center_x + math.cos(angle_rad) * outer_radius)
            outer_y = int(center_y + math.sin(angle_rad) * outer_radius)
            
            # Inner points for this segment
            inner_radius = outer_radius * 0.75
            inner_x = int(center_x + math.cos(angle_rad) * inner_radius)
            inner_y = int(center_y + math.sin(angle_rad) * inner_radius)
            
            # Create connecting lines to multiple other points (sacred geometry)
            for connection in [3, 5, 8, 12]:  # Connect to various other points
                if i + connection < outer_segments:
                    connect_angle = (360 / outer_segments) * (i + connection) + rotation
                    connect_rad = math.radians(connect_angle)
                    connect_x = int(center_x + math.cos(connect_rad) * inner_radius)
                    connect_y = int(center_y + math.sin(connect_rad) * inner_radius)
                    
                    # Draw connecting line
                    cv2.line(img, (inner_x, inner_y), (connect_x, connect_y), 
                             tuple(int(c * 0.7) for c in color), 1)
            
            # Draw main radial line
            cv2.line(img, (inner_x, inner_y), (outer_x, outer_y), color, 3)
            
            # Add geometric nodes
            cv2.circle(img, (outer_x, outer_y), 3, color, -1)
        
        # Layer 2: Middle geometric pattern - Star polygons
        mid_segments = 12
        mid_radius = base_radius * 0.7
        
        for i in range(mid_segments):
            angle = (360 / mid_segments) * i + rotation * 0.7
            
            # Create star polygon points
            for star_layer in range(3):
                star_angle = angle + star_layer * 120  # 3-fold symmetry
                star_rad = math.radians(star_angle)
                
                # Variable radius based on mel bands
                mel_idx = (i + star_layer) % len(mel_bands)
                radius_var = mid_radius * (0.8 + mel_bands[mel_idx] * 0.4)
                
                star_x = int(center_x + math.cos(star_rad) * radius_var)
                star_y = int(center_y + math.sin(star_rad) * radius_var)
                
                # Color for this star layer
                color = colors[(i + star_layer) % len(colors)]
                brightness = min(1.0, 0.5 + mid * 0.5)
                color = tuple(int(c * brightness) for c in color)
                
                # Draw star points
                cv2.circle(img, (star_x, star_y), 4, color, -1)
                
                # Connect star points to form triangles
                next_star_angle = star_angle + 120
                next_star_rad = math.radians(next_star_angle)
                next_star_x = int(center_x + math.cos(next_star_rad) * radius_var)
                next_star_y = int(center_y + math.sin(next_star_rad) * radius_var)
                
                cv2.line(img, (star_x, star_y), (next_star_x, next_star_y), color, 2)
        
        # Layer 3: Inner geometric ring - Complex polygons
        inner_segments = 8  # Octagonal base
        inner_radius = base_radius * 0.45
        
        for i in range(inner_segments):
            angle = (360 / inner_segments) * i + rotation * -0.5
            angle_rad = math.radians(angle)
            
            # Create multiple geometric shapes per segment
            for shape_type in range(2):
                shape_radius = inner_radius * (0.8 + shape_type * 0.3)
                
                # Create polygon vertices
                polygon_sides = 6 if shape_type == 0 else 4  # Hexagons and squares
                polygon_points = []
                
                for vertex in range(polygon_sides):
                    vertex_angle = angle + (360 / polygon_sides) * vertex
                    vertex_rad = math.radians(vertex_angle)
                    vertex_x = int(center_x + math.cos(vertex_rad) * shape_radius)
                    vertex_y = int(center_y + math.sin(vertex_rad) * shape_radius)
                    polygon_points.append([vertex_x, vertex_y])
                
                # Color and draw polygon
                color = colors[i % len(colors)]
                brightness = min(1.0, 0.4 + treble * 0.6)
                color = tuple(int(c * brightness) for c in color)
                
                polygon_points = np.array(polygon_points, dtype=np.int32)
                cv2.polylines(img, [polygon_points], True, color, 2)
                
                # Fill with semi-transparent color
                fill_color = tuple(int(c * 0.3) for c in color)
                cv2.fillPoly(img, [polygon_points], fill_color)
        
        # Layer 4: Sacred geometry center - Flower of Life inspired
        center_radius = base_radius * 0.25
        
        # Create overlapping circles (Flower of Life pattern)
        for circle_ring in range(3):
            ring_radius = center_radius * (0.4 + circle_ring * 0.2)
            circles_in_ring = 6 if circle_ring > 0 else 1  # Center + 6 around
            
            for circle_idx in range(circles_in_ring):
                if circle_ring == 0:  # Center circle
                    circle_x, circle_y = center_x, center_y
                else:
                    circle_angle = (360 / circles_in_ring) * circle_idx + rotation * 0.2
                    circle_rad = math.radians(circle_angle)
                    offset_radius = ring_radius * 0.6
                    circle_x = int(center_x + math.cos(circle_rad) * offset_radius)
                    circle_y = int(center_y + math.sin(circle_rad) * offset_radius)
                
                # Color based on ring and audio
                color = colors[circle_ring % len(colors)]
                brightness = min(1.0, 0.5 + amplitude * 0.5)
                color = tuple(int(c * brightness) for c in color)
                
                # Draw circle outline
                cv2.circle(img, (circle_x, circle_y), int(ring_radius * 0.4), color, 2)
        
        # Layer 5: Geometric connecting lines - Sacred geometry intersections
        connection_radius = base_radius * 0.6
        num_connections = 12
        
        for i in range(num_connections):
            # Create geometric star patterns
            for multiplier in [2, 3, 5]:  # Different geometric ratios
                angle1 = (360 / num_connections) * i + rotation
                angle2 = (360 / num_connections) * ((i * multiplier) % num_connections) + rotation
                
                angle1_rad = math.radians(angle1)
                angle2_rad = math.radians(angle2)
                
                x1 = int(center_x + math.cos(angle1_rad) * connection_radius)
                y1 = int(center_y + math.sin(angle1_rad) * connection_radius)
                x2 = int(center_x + math.cos(angle2_rad) * connection_radius)
                y2 = int(center_y + math.sin(angle2_rad) * connection_radius)
                
                # Color based on connection type
                color = colors[multiplier % len(colors)]
                alpha_brightness = 0.3 + (bass * 0.3)
                color = tuple(int(c * alpha_brightness) for c in color)
                
                cv2.line(img, (x1, y1), (x2, y2), color, 1)
        
        # Final center point - The sacred center
        center_size = max(3, int(5 + amplitude * 8))
        center_color = colors[0]
        cv2.circle(img, (center_x, center_y), center_size, (255, 255, 255), -1)  # White center
        cv2.circle(img, (center_x, center_y), center_size + 2, center_color, 2)  # Colored ring
        
        return img
    
    def generate_mandala_frame(self, features: Dict, time_progress: float) -> np.ndarray:
        """Generate true radial symmetry pattern with organic curved petals like preview.webp"""
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Extract and scale features
        bass = min(features['bass'] * 500, 1.0)
        mid = min(features['mid'] * 300, 1.0)
        treble = min(features['treble'] * 200, 1.0)
        amplitude = min(features['amplitude'] * 100, 1.0)
        mel_bands = features['mel_bands']
        
        colors = self.color_palettes['neon']
        center_x, center_y = self.center
        
        # Parameters for the organic radial pattern
        num_main_petals = 8 + int(bass * 4)  # 8-12 main petals
        rotation = (time_progress * 5 + mid * 3) % 360  # Slower rotation
        base_radius = 80 + amplitude * 100  # Base size
        
        # Create the characteristic curved organic petal pattern like preview.webp
        for symmetry_order in range(4, 0, -1):  # Create 4 layers, largest first
            layer_scale = 0.3 + symmetry_order * 0.2  # 0.5, 0.7, 0.9, 1.1
            layer_radius = base_radius * layer_scale
            layer_rotation = rotation + symmetry_order * 8  # Each layer rotates slightly
            
            # Number of petals for this layer (higher order = more petals)
            petals_in_layer = num_main_petals * symmetry_order // 2
            
            # Color for this layer
            layer_color = colors[(symmetry_order - 1) % len(colors)]
            brightness = min(1.0, 0.3 + amplitude * 0.5 + symmetry_order * 0.1)
            layer_color = tuple(int(c * brightness) for c in layer_color)
            
            # Create the organic flowing petals
            for petal in range(petals_in_layer):
                petal_angle = (360 / petals_in_layer) * petal + layer_rotation
                
                # Use mel bands to create variation in petal shapes
                mel_idx = petal % len(mel_bands)
                mel_influence = mel_bands[mel_idx]
                
                # Create organic flowing petal shape with multiple curves
                petal_points = []
                
                # Generate smooth organic petal outline
                for curve_step in range(36):  # 36 points for very smooth curves
                    t = curve_step / 35.0  # Parameter from 0 to 1 along petal
                    
                    # Organic radius function - creates the flowing curved shape
                    base_curve = math.sin(t * math.pi)  # Basic petal shape
                    organic_modifier = (
                        math.sin(t * math.pi * 3 + petal_angle * 0.01) * 0.15 +  # High freq ripples
                        math.cos(t * math.pi * 2 + time_progress * 0.1) * 0.1 +   # Breathing effect
                        mel_influence * 0.3  # Audio reactivity
                    )
                    
                    # Radius varies organically along the petal
                    point_radius = layer_radius * (0.2 + 0.8 * t) * (base_curve + organic_modifier)
                    
                    # Angular width of petal - wider at base, narrower at tip
                    petal_width = math.sin(t * math.pi) * 0.8  # Width function
                    
                    # Create the flowing organic outline
                    for side in [-1, 1]:  # Left and right sides of petal
                        side_angle = math.radians(petal_angle + side * petal_width * 15)  # 15 degrees max width
                        side_x = int(center_x + math.cos(side_angle) * point_radius)
                        side_y = int(center_y + math.sin(side_angle) * point_radius)
                        
                        # Only add every other point to avoid overcrowding
                        if curve_step % 2 == side % 2:
                            petal_points.append([side_x, side_y])
                
                # Create filled organic petal shape
                if len(petal_points) >= 3:
                    petal_points = np.array(petal_points, dtype=np.int32)
                    
                    # Fill the organic petal
                    cv2.fillPoly(img, [petal_points], layer_color)
                    
                    # Add subtle outline for definition
                    outline_color = tuple(min(255, int(c * 1.2)) for c in layer_color)
                    cv2.polylines(img, [petal_points], True, outline_color, 1)
        
        # Add the characteristic gradient/flowing effect like in preview.webp
        overlay = img.copy()
        
        # Create flowing radial gradient effect
        for radius_step in range(20, int(base_radius * 1.2), 8):
            for angle_step in range(0, 360, 3):
                angle_rad = math.radians(angle_step + rotation * 0.1)
                
                # Create flowing effect with audio reactivity
                flow_influence = (
                    math.sin(angle_step * 0.05 + time_progress * 0.2) * 0.3 +
                    math.cos(radius_step * 0.03 + time_progress * 0.15) * 0.2
                )
                
                effective_radius = radius_step * (1 + flow_influence * amplitude)
                
                x = int(center_x + math.cos(angle_rad) * effective_radius)
                y = int(center_y + math.sin(angle_rad) * effective_radius)
                
                # Check if we're inside the pattern
                if 0 <= x < self.width and 0 <= y < self.height:
                    if np.any(img[y, x] > 0):  # If there's already color here
                        # Add flowing gradient effect
                        gradient_intensity = 1.0 - (radius_step / (base_radius * 1.2))
                        for color_channel in range(3):
                            enhancement = int(gradient_intensity * 30 * amplitude)
                            overlay[y, x, color_channel] = min(255, overlay[y, x, color_channel] + enhancement)
        
        # Blend the gradient overlay
        img = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)
        
        # Add the characteristic center pattern
        center_radius = int(15 + amplitude * 25)
        
        # Create concentric center like in preview.webp
        for center_ring in range(5):
            ring_radius = center_radius - center_ring * 3
            if ring_radius > 0:
                ring_color = colors[center_ring % len(colors)]
                ring_brightness = 1.0 - center_ring * 0.15
                ring_color = tuple(int(c * ring_brightness) for c in ring_color)
                
                # Alternate between filled and outline rings
                if center_ring % 2 == 0:
                    cv2.circle(img, (center_x, center_y), ring_radius, ring_color, -1)  # Filled
                else:
                    cv2.circle(img, (center_x, center_y), ring_radius, ring_color, 2)   # Outline
        
        # Final bright center point
        cv2.circle(img, (center_x, center_y), 2, (255, 255, 255), -1)
        
        # Apply slight blur for organic smoothness like in preview.webp
        img = cv2.GaussianBlur(img, (3, 3), 0.8)
        
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
        
        # Setup video writer with fallback codecs
        fourcc_options = [
            ('mp4v', 'mp4'),
            ('XVID', 'avi'), 
            ('MJPG', 'avi'),
            ('X264', 'mp4')
        ]
        
        video_writer = None
        actual_output_file = output_file
        
        for fourcc_code, extension in fourcc_options:
            try:
                # Adjust output filename extension if needed
                if not output_file.lower().endswith(f'.{extension}'):
                    base_name = os.path.splitext(output_file)[0]
                    actual_output_file = f"{base_name}.{extension}"
                
                fourcc = cv2.VideoWriter_fourcc(*fourcc_code)
                video_writer = cv2.VideoWriter(actual_output_file, fourcc, fps, (self.width, self.height))
                
                if video_writer.isOpened():
                    print(f"Using codec: {fourcc_code}, output: {actual_output_file}")
                    break
                else:
                    video_writer.release()
                    video_writer = None
            except Exception as e:
                print(f"Failed to create video writer with {fourcc_code}: {e}")
                if video_writer:
                    video_writer.release()
                    video_writer = None
        
        if not video_writer or not video_writer.isOpened():
            print("Error: Could not open video writer with any codec")
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
                elif features['mid'] > features['bass']:
                    use_sacred = True   # Sacred geometry for mid-heavy sections
                else:
                    use_mandala = False  # Kaleidoscope for treble-heavy sections
            elif style == "mandala":
                use_mandala = True
                use_sacred = False
            elif style == "sacred_geometry":
                use_mandala = False
                use_sacred = True
            else:  # kaleidoscope
                use_mandala = False
                use_sacred = False
            
            # Generate frame
            if style == "sacred_geometry" or (style == "mixed" and 'use_sacred' in locals() and use_sacred):
                frame = self.generate_sacred_geometry_frame(features, time_progress * 10)
            elif use_mandala:
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
        print(f"Visualization saved as {actual_output_file}")
        
        return actual_output_file
