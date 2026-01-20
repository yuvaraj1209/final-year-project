#!/usr/bin/env python3
"""
Test script for nose-based gesture control system.
This script verifies that the nose tracking implementation is working correctly.
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from movements import HeadMovementDetector, FaceDetector
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("NoseControlTest")

def test_nose_movement_detector():
    """Test the nose movement detector functionality"""
    print("🧪 Testing Nose Movement Detector...")
    
    detector = HeadMovementDetector()
    
    # Test initialization
    assert detector.nose_center_x is None, "Initial nose center should be None"
    assert detector.movement_threshold == 0.025, "Movement threshold should be 0.025"
    assert detector.calibration_needed == True, "Should need calibration initially"
    
    print("✅ Initialization test passed")
    
    # Test recalibration
    detector.recalibrate_center()
    assert detector.calibration_needed == True, "Should need calibration after reset"
    assert detector.calibration_frames == 0, "Calibration frames should be reset"
    assert detector.nose_center_x is None, "Nose center should be reset to None"
    
    print("✅ Recalibration test passed")
    
    print("🎉 All nose movement detector tests passed!")
    return True

def test_face_detector():
    """Test the face detector functionality"""
    print("🧪 Testing Face Detector...")
    
    detector = FaceDetector()
    
    # Test with no MediaPipe (simulation mode)
    result = detector.detect_faces("fake_image_data")
    
    # Should return simulated response
    assert result['status'] == 'simulated', "Should return simulated status when MediaPipe not available"
    assert 'face_count' in result, "Should include face_count in result"
    
    print("✅ Face detector simulation test passed")
    print("🎉 Face detector tests passed!")
    return True

def display_usage_instructions():
    """Display usage instructions for nose-based controls"""
    print("\n" + "="*60)
    print("🎯 NOSE-BASED WHEELCHAIR CONTROL SYSTEM")
    print("="*60)
    print()
    print("📋 CONTROL INSTRUCTIONS:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("👃 Nose Controls (when in WHEELCHAIR mode):")
    print("  • Move NOSE LEFT   → UI shows LEFT")
    print("  • Move NOSE RIGHT  → UI shows RIGHT") 
    print("  • Move HEAD UP     → UI shows FORWARD")
    print("  • Move HEAD DOWN   → UI shows BACKWARD")
    print()
    print("👁️ Eye Controls (mode switching):")
    print("  • SINGLE BLINK     → Enter WHEELCHAIR mode")
    print("  • DOUBLE BLINK     → Enter PLACE selection mode") 
    print("  • LONG BLINK       → Return to STOP mode")
    print()
    print("🔧 Calibration:")
    print("  • Click 'Calibrate Nose' button to reset center position")
    print("  • System auto-calibrates nose center on startup")
    print()
    print("⚡ Quick Start:")
    print("  1. Look at the camera")
    print("  2. Single blink to activate wheelchair controls")
    print("  3. Move your nose to control direction")
    print("  4. Long blink to stop")
    print()
    print("="*60)

async def main():
    """Main test function"""
    print("🚀 Starting Nose-Based Gesture Control Tests...")
    print()
    
    # Run tests
    try:
        test_nose_movement_detector()
        test_face_detector()
        print()
        print("✅ ALL TESTS PASSED!")
        
        # Display instructions
        display_usage_instructions()
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())