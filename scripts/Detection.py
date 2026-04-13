from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class Detection:
    """Represents a single bird species detection from BirdNet"""
    
    species: str
    confidence: float
    time_start: float
    time_end: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date: Optional[str] = None
    location_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def duration(self) -> float:
        """Get detection duration in seconds"""
        return self.time_end - self.time_start
    
    def to_dict(self) -> Dict:
        """Convert detection to dictionary"""
        return {
            'species': self.species,
            'confidence': self.confidence,
            'time_start': self.time_start,
            'time_end': self.time_end,
            'duration': self.duration(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'date': self.date,
            'location_name': self.location_name,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert detection to JSON string"""
        return json.dumps(self.to_dict())
    
    def __repr__(self) -> str:
        return f"Detection({self.species}, conf={self.confidence:.3f}, {self.time_start:.1f}s-{self.time_end:.1f}s)"
    


@dataclass
class Detections:
    """Represents a collection of bird species detections"""
    
    detections: List[Detection] = field(default_factory=list)
    filename: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date: Optional[str] = None
    
    def add_detection(self, detection: Detection) -> None:
        """Add a single detection"""
        self.detections.append(detection)
    
    def add_from_dict(self, detect_dict: Dict) -> None:
        """Add a detection from dictionary"""
        detection = Detection(
            species=detect_dict.get('species'),
            confidence=detect_dict.get('confidence', 0.0),
            time_start=detect_dict.get('time_start', 0.0),
            time_end=detect_dict.get('time_end', 0.0),
            latitude=detect_dict.get('latitude', self.latitude),
            longitude=detect_dict.get('longitude', self.longitude),
            date=detect_dict.get('date', self.date),
            location_name=detect_dict.get('location_name', self.location_name),
            metadata=detect_dict.get('metadata', {})
        )
        self.add_detection(detection)
    
    def add_multiple(self, detections: List[Detection]) -> None:
        """Add multiple detections"""
        self.detections.extend(detections)
    
    def filter_by_confidence(self, min_confidence: float) -> 'Detections':
        """Filter detections by minimum confidence threshold"""
        filtered = Detections(
            filename=self.filename,
            location_name=self.location_name,
            latitude=self.latitude,
            longitude=self.longitude,
            date=self.date
        )
        filtered.detections = [d for d in self.detections if d.confidence >= min_confidence]
        return filtered
    
    def filter_by_species(self, species: str) -> 'Detections':
        """Filter detections by species name"""
        filtered = Detections(
            filename=self.filename,
            location_name=self.location_name,
            latitude=self.latitude,
            longitude=self.longitude,
            date=self.date
        )
        species_lower = species.lower()
        filtered.detections = [d for d in self.detections if species_lower in d.species.lower()]
        return filtered
    
    def filter_by_time_range(self, start_time: float, end_time: float) -> 'Detections':
        """Filter detections by time range (in seconds)"""
        filtered = Detections(
            filename=self.filename,
            location_name=self.location_name,
            latitude=self.latitude,
            longitude=self.longitude,
            date=self.date
        )
        filtered.detections = [
            d for d in self.detections 
            if not (d.time_end < start_time or d.time_start > end_time)
        ]
        return filtered
    
    def sort_by_confidence(self, descending: bool = True) -> 'Detections':
        """Sort detections by confidence score"""
        sorted_detections = Detections(
            filename=self.filename,
            location_name=self.location_name,
            latitude=self.latitude,
            longitude=self.longitude,
            date=self.date
        )
        sorted_detections.detections = sorted(
            self.detections,
            key=lambda d: d.confidence,
            reverse=descending
        )
        return sorted_detections
    
    def sort_by_time(self, ascending: bool = True) -> 'Detections':
        """Sort detections by start time"""
        sorted_detections = Detections(
            filename=self.filename,
            location_name=self.location_name,
            latitude=self.latitude,
            longitude=self.longitude,
            date=self.date
        )
        sorted_detections.detections = sorted(
            self.detections,
            key=lambda d: d.time_start,
            reverse=not ascending
        )
        return sorted_detections
    
    def sort_by_species(self, reverse: bool = False) -> 'Detections':
        """Sort detections alphabetically by species"""
        sorted_detections = Detections(
            filename=self.filename,
            location_name=self.location_name,
            latitude=self.latitude,
            longitude=self.longitude,
            date=self.date
        )
        sorted_detections.detections = sorted(
            self.detections,
            key=lambda d: d.species,
            reverse=reverse
        )
        return sorted_detections
    
    def get_unique_species(self) -> List[str]:
        """Get list of unique species detected"""
        return list(set(d.species for d in self.detections))
    
    def get_species_count(self) -> Dict[str, int]:
        """Get count of detections per species"""
        counts = {}
        for detection in self.detections:
            counts[detection.species] = counts.get(detection.species, 0) + 1
        return counts
    
    def get_average_confidence(self) -> float:
        """Get average confidence across all detections"""
        if not self.detections:
            return 0.0
        return sum(d.confidence for d in self.detections) / len(self.detections)
    
    def get_max_confidence(self) -> Optional[float]:
        """Get maximum confidence score"""
        return max((d.confidence for d in self.detections), default=None)
    
    def get_min_confidence(self) -> Optional[float]:
        """Get minimum confidence score"""
        return min((d.confidence for d in self.detections), default=None)
    
    def get_total_duration(self) -> float:
        """Get total duration of all detections in seconds"""
        return sum(d.duration() for d in self.detections)
    
    def to_list_of_dicts(self) -> List[Dict]:
        """Convert all detections to list of dictionaries"""
        return [d.to_dict() for d in self.detections]
    
    def to_json(self, pretty: bool = True) -> str:
        """Convert detections to JSON string"""
        data = {
            'filename': self.filename,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'date': self.date,
            'detections': [d.to_dict() for d in self.detections],
            'summary': {
                'total_detections': len(self.detections),
                'unique_species': len(self.get_unique_species()),
                'average_confidence': self.get_average_confidence(),
                'max_confidence': self.get_max_confidence(),
                'min_confidence': self.get_min_confidence(),
                'total_duration': self.get_total_duration()
            }
        }
        
        if pretty:
            return json.dumps(data, indent=2)
        else:
            return json.dumps(data)
    
    def __len__(self) -> int:
        """Return number of detections"""
        return len(self.detections)
    
    def __getitem__(self, index: int) -> Detection:
        """Allow indexing into detections"""
        return self.detections[index]
    
    def __repr__(self) -> str:
        return f"Detections({len(self.detections)} detections, {len(self.get_unique_species())} species)"
    
    def __str__(self) -> str:
        summary = self.__repr__()
        species_count = self.get_species_count()
        species_str = "\n  ".join([f"{sp}: {count}" for sp, count in sorted(species_count.items())])
        return f"{summary}\n  {species_str}"


# Example usage
if __name__ == "__main__":
    # Create a detections collection
    detections = Detections(
        filename="recording.wav",
        location_name="Field A",
        latitude=42.0347,
        longitude=-93.6199,
        date="2024-04-12"
    )
    
    # Add some detections
    detections.add_detection(Detection(
        species="American Robin",
        confidence=0.95,
        time_start=5.2,
        time_end=8.3
    ))
    
    detections.add_detection(Detection(
        species="Northern Mockingbird",
        confidence=0.87,
        time_start=12.1,
        time_end=15.4
    ))
    
    detections.add_detection(Detection(
        species="American Robin",
        confidence=0.72,
        time_start=20.5,
        time_end=23.8
    ))
    
    # Print summary
    print(detections)
    print(f"\nTotal detections: {len(detections)}")
    print(f"Species: {detections.get_unique_species()}")
    print(f"Average confidence: {detections.get_average_confidence():.3f}")
    
    # Filter by confidence
    high_conf = detections.filter_by_confidence(0.85)
    print(f"\nHigh confidence (>0.85): {len(high_conf)} detections")
    
    # Filter by species
    robins = detections.filter_by_species("Robin")
    print(f"Robins: {len(robins)} detections")
    
    # Print JSON
    print("\n" + detections.to_json())
