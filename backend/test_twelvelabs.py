"""
Test script for TwelveLabs integration
Run this to verify your API key and test video upload/analysis
Based on official TwelveLabs quickstart
"""
import os
from dotenv import load_dotenv
from integrations.twelvelabs_client import TwelveLabsClient

# Load environment variables
load_dotenv()

def test_twelvelabs_connection():
    """Test TwelveLabs API connection"""
    print("Testing TwelveLabs API connection...")
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    if not api_key:
        print("❌ TWELVELABS_API_KEY or TL_API_KEY not found in .env file")
        return False
    
    try:
        client = TwelveLabsClient(api_key=api_key)
        print("✅ TwelveLabs client initialized")
        
        # Test: Create or get index
        print("\nTesting index creation/retrieval...")
        index_id = client.create_or_get_index("test_index")
        print(f"✅ Index ID: {index_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_video_upload(video_url: str):
    """Test video upload and indexing"""
    print(f"\nTesting video upload: {video_url}")
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    client = TwelveLabsClient(api_key=api_key)
    
    try:
        # Upload video
        print("Uploading video to TwelveLabs...")
        print("(This may take a few minutes depending on video length)")
        result = client.upload_video(
            video_url=video_url,
            video_title="Test Video"
        )
        
        print(f"\n✅ Video uploaded successfully!")
        print(f"   Video ID: {result['video_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Duration: {result.get('duration', 'N/A')} seconds")
        
        # Analyze video
        print("\nAnalyzing video creative elements...")
        print("(Using gist, summarize, and analyze APIs)")
        analysis = client.analyze_creative_elements(result['video_id'])
        
        print(f"\n✅ Analysis complete!")
        print(f"\n   Title: {analysis['analysis'].get('title', 'N/A')}")
        print(f"   Topics: {analysis['analysis'].get('topics', [])}")
        print(f"   Summary: {analysis['analysis'].get('summary', 'N/A')[:200]}...")
        
        return result['video_id']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_video_segments(video_id: str):
    """Test getting video segments (chapters)"""
    print(f"\nTesting video segmentation for video ID: {video_id}")
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    client = TwelveLabsClient(api_key=api_key)
    
    try:
        scenes = client.get_video_segments(video_id)
        
        print(f"✅ Found {len(scenes)} chapters/scenes")
        if scenes:
            print("\nFirst chapter:")
            print(f"   Title: {scenes[0].get('title', 'N/A')}")
            print(f"   Start: {scenes[0]['start_time']}s")
            print(f"   End: {scenes[0]['end_time']}s")
            print(f"   Summary: {scenes[0].get('description', 'N/A')[:100]}...")
        
        # Also test key moments
        print("\nTesting key moments/highlights...")
        key_moments = client.get_key_moments(video_id)
        print(f"✅ Found {len(key_moments)} key moments")
        if key_moments:
            print(f"\nFirst highlight: {key_moments[0]['description']}")
        
        return scenes
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("TwelveLabs Integration Test")
    print("=" * 60)
    
    # Test 1: Connection
    if not test_twelvelabs_connection():
        print("\n⚠️  Connection test failed. Please check your API key.")
        exit(1)
    
    # Test 2: Video Upload (optional - provide a video URL)
    print("\n" + "=" * 60)
    print("Video Upload Test (Optional)")
    print("=" * 60)
    
    # Example video URL - replace with your own or skip
    test_video_url = input("\nEnter a video URL to test (or press Enter to skip): ").strip()
    
    if test_video_url:
        video_id = test_video_upload(test_video_url)
        
        if video_id:
            # Test 3: Video Segmentation
            print("\n" + "=" * 60)
            print("Video Segmentation Test")
            print("=" * 60)
            test_video_segments(video_id)
    else:
        print("\n⏭️  Skipping video upload test")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
