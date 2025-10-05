"""
Simplified TwelveLabs test - only tests TwelveLabs API
No other dependencies required
"""
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs
from twelvelabs.indexes import IndexesCreateRequestModelsItem
from twelvelabs.tasks import TasksRetrieveResponse

# Load environment variables
load_dotenv()

def test_connection():
    """Test TwelveLabs API connection"""
    print("=" * 60)
    print("TwelveLabs API Connection Test")
    print("=" * 60)
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    if not api_key or api_key == "your_twelvelabs_api_key_here":
        print("\nERROR: No API key found!")
        print("Please add your TwelveLabs API key to .env file:")
        print("  TWELVELABS_API_KEY=tlk_your_actual_key_here")
        return False
    
    try:
        print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")
        print("\nInitializing TwelveLabs client...")
        client = TwelveLabs(api_key=api_key)
        print("[OK] Client initialized successfully!")
        
        # Test: List existing indexes
        print("\nFetching existing indexes...")
        indexes = client.indexes.list()
        print(f"[OK] Found {len(list(indexes))} existing indexes")
        
        # Test: Create or get index
        print("\nCreating/getting test index...")
        index_name = "test_index"
        
        # Check if index exists
        indexes = client.indexes.list()
        existing_index = None
        for idx in indexes:
            # Check if index has the name we're looking for
            idx_name = getattr(idx, 'index_name', getattr(idx, 'name', None))
            if idx_name == index_name:
                existing_index = idx
                break
        
        if existing_index:
            print(f"[OK] Using existing index: {existing_index.id}")
            index_id = existing_index.id
        else:
            print(f"Creating new index: {index_name}")
            index = client.indexes.create(
                index_name=index_name,
                models=[
                    IndexesCreateRequestModelsItem(
                        model_name="pegasus1.2",
                        model_options=["visual", "audio"]
                    )
                ]
            )
            print(f"[OK] Created new index: {index.id}")
            index_id = index.id
        
        print("\n" + "=" * 60)
        print("SUCCESS! TwelveLabs API is working correctly!")
        print("=" * 60)
        print(f"\nYour index ID: {index_id}")
        print("\nNext steps:")
        print("1. You can now upload videos to this index")
        print("2. Run the full platform to analyze videos")
        print("3. See QUICK_START.md for more details")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR: Connection failed!")
        print("=" * 60)
        print(f"\nError message: {str(e)}")
        print("\nPossible issues:")
        print("1. Invalid API key - check your key at:")
        print("   https://playground.twelvelabs.io/dashboard/api-key")
        print("2. No internet connection")
        print("3. API quota exceeded (check your dashboard)")
        return False


def test_video_upload():
    """Test video upload (optional)"""
    print("\n" + "=" * 60)
    print("Video Upload Test (Optional)")
    print("=" * 60)
    
    test_video = input("\nEnter video URL to test (or press Enter to skip): ").strip()
    
    if not test_video:
        print("Skipping video upload test")
        return
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    client = TwelveLabs(api_key=api_key)
    
    try:
        # Get or create index
        index_name = "test_index"
        indexes = client.indexes.list()
        index_id = None
        for idx in indexes:
            if idx.name == index_name:
                index_id = idx.id
                break
        
        if not index_id:
            print("ERROR: No index found. Run connection test first.")
            return
        
        print(f"\nUploading video: {test_video}")
        print("This may take a few minutes...")
        
        # Create task
        task = client.tasks.create(
            index_id=index_id,
            video_url=test_video
        )
        print(f"Task created: {task.id}")
        
        # Monitor progress
        def on_update(t: TasksRetrieveResponse):
            print(f"  Status: {t.status}")
        
        task = client.tasks.wait_for_done(
            task_id=task.id,
            sleep_interval=5,
            callback=on_update
        )
        
        if task.status == "ready":
            print(f"\n[OK] Video uploaded successfully!")
            print(f"  Video ID: {task.video_id}")
            
            # Test analysis
            print("\nTesting analysis APIs...")
            
            # Gist
            print("  Getting gist...")
            gist = client.gist(video_id=task.video_id, types=["title", "topic"])
            print(f"  [OK] Title: {gist.title}")
            print(f"  [OK] Topics: {gist.topics}")
            
            # Summary
            print("  Getting summary...")
            summary = client.summarize(video_id=task.video_id, type="summary")
            print(f"  [OK] Summary: {summary.summary[:100]}...")
            
            print("\n[OK] All tests passed!")
        else:
            print(f"\nERROR: Upload failed with status: {task.status}")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test 1: Connection
    if test_connection():
        # Test 2: Video upload (optional)
        test_video_upload()
    else:
        print("\nPlease fix the connection issue before proceeding.")
