"""
Check video indexing status and run analysis
"""
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs
import time

# Load environment variables
load_dotenv()

# Your video ID
VIDEO_ID = "68e20c15f2e53b115e1aef18"

def check_video_status():
    """Check if video indexing is complete"""
    print("=" * 60)
    print("Checking Video Status")
    print("=" * 60)
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    client = TwelveLabs(api_key=api_key)
    
    print(f"\nVideo ID: {VIDEO_ID}")
    print("\nChecking status...")
    
    try:
        # Try to run a simple gist query
        # If video is ready, this will succeed
        # If video is still indexing, this will fail
        gist = client.gist(video_id=VIDEO_ID, types=["title"])
        
        print(f"[OK] Video is ready!")
        print(f"  Video ID: {VIDEO_ID}")
        print(f"  Title: {gist.title}")
        print(f"  Status: Ready for analysis")
        
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "does not exist" in error_msg:
            print("[ERROR] Video not found. Please check your video ID.")
            print(f"\nYour video ID: {VIDEO_ID}")
            print("\nDouble-check this ID in your TwelveLabs dashboard:")
            print("https://playground.twelvelabs.io/dashboard")
            return False
        elif "processing" in error_msg or "indexing" in error_msg or "not ready" in error_msg:
            print("[WAIT] Video is still indexing...")
            print("       Please wait a few more minutes and try again.")
            print("\nYou can check progress at:")
            print("https://playground.twelvelabs.io/dashboard")
            return False
        else:
            # Try anyway - might just be a different error
            print(f"[WARNING] Status check returned: {e}")
            print("\nTrying to proceed with analysis anyway...")
            return True


def run_analysis():
    """Run comprehensive analysis on the video"""
    print("\n" + "=" * 60)
    print("Running Video Analysis")
    print("=" * 60)
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    client = TwelveLabs(api_key=api_key)
    
    try:
        # 1. Get Gist (Title, Topics, Hashtags)
        print("\n1. Getting Gist (title, topics, hashtags)...")
        gist = client.gist(video_id=VIDEO_ID, types=["title", "topic", "hashtag"])
        
        print(f"\n   Title: {gist.title}")
        print(f"   Topics: {', '.join(gist.topics)}")
        print(f"   Hashtags: {', '.join(gist.hashtags)}")
        
        # 2. Get Summary
        print("\n2. Getting Summary...")
        summary_result = client.summarize(video_id=VIDEO_ID, type="summary")
        
        print(f"\n   Summary:")
        print(f"   {summary_result.summary}")
        
        # 3. Get Chapters
        print("\n3. Getting Chapters...")
        chapters_result = client.summarize(video_id=VIDEO_ID, type="chapter")
        
        print(f"\n   Found {len(chapters_result.chapters)} chapters:")
        for i, chapter in enumerate(chapters_result.chapters[:5], 1):  # Show first 5
            print(f"\n   Chapter {chapter.chapter_number}:")
            print(f"   - Time: {chapter.start_sec}s - {chapter.end_sec}s")
            print(f"   - Title: {chapter.chapter_title}")
            print(f"   - Summary: {chapter.chapter_summary[:100]}...")
        
        if len(chapters_result.chapters) > 5:
            print(f"\n   ... and {len(chapters_result.chapters) - 5} more chapters")
        
        # 4. Get Highlights
        print("\n4. Getting Highlights...")
        highlights_result = client.summarize(video_id=VIDEO_ID, type="highlight")
        
        print(f"\n   Found {len(highlights_result.highlights)} highlights:")
        for i, highlight in enumerate(highlights_result.highlights[:5], 1):  # Show first 5
            print(f"\n   Highlight {i}:")
            print(f"   - Time: {highlight.start_sec}s - {highlight.end_sec}s")
            print(f"   - Description: {highlight.highlight}")
        
        if len(highlights_result.highlights) > 5:
            print(f"\n   ... and {len(highlights_result.highlights) - 5} more highlights")
        
        # 5. Get Detailed Analysis
        print("\n5. Getting Detailed Analysis...")
        print("   (This may take 30-60 seconds...)")
        
        analysis_prompt = """Provide a detailed analysis of this video including:
        - Visual style and composition
        - Key themes and messages
        - Emotional tone
        - Target audience
        - Overall effectiveness"""
        
        analysis_text = ""
        text_stream = client.analyze_stream(
            video_id=VIDEO_ID,
            prompt=analysis_prompt
        )
        
        print("\n   Detailed Analysis:")
        for text in text_stream:
            if text.event_type == "text_generation":
                analysis_text += text.text
                print(text.text, end='', flush=True)
        
        print("\n\n" + "=" * 60)
        print("Analysis Complete!")
        print("=" * 60)
        
        # Save results to file
        save_results(gist, summary_result, chapters_result, highlights_result, analysis_text)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_results(gist, summary, chapters, highlights, analysis):
    """Save analysis results to a text file"""
    filename = f"analysis_results_{VIDEO_ID}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("VIDEO ANALYSIS RESULTS\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Video ID: {VIDEO_ID}\n\n")
        
        f.write("GIST\n")
        f.write("-" * 60 + "\n")
        f.write(f"Title: {gist.title}\n")
        f.write(f"Topics: {', '.join(gist.topics)}\n")
        f.write(f"Hashtags: {', '.join(gist.hashtags)}\n\n")
        
        f.write("SUMMARY\n")
        f.write("-" * 60 + "\n")
        f.write(f"{summary.summary}\n\n")
        
        f.write("CHAPTERS\n")
        f.write("-" * 60 + "\n")
        for chapter in chapters.chapters:
            f.write(f"\nChapter {chapter.chapter_number}:\n")
            f.write(f"Time: {chapter.start_sec}s - {chapter.end_sec}s\n")
            f.write(f"Title: {chapter.chapter_title}\n")
            f.write(f"Summary: {chapter.chapter_summary}\n")
        
        f.write("\n\nHIGHLIGHTS\n")
        f.write("-" * 60 + "\n")
        for i, highlight in enumerate(highlights.highlights, 1):
            f.write(f"\nHighlight {i}:\n")
            f.write(f"Time: {highlight.start_sec}s - {highlight.end_sec}s\n")
            f.write(f"Description: {highlight.highlight}\n")
        
        f.write("\n\nDETAILED ANALYSIS\n")
        f.write("-" * 60 + "\n")
        f.write(analysis)
    
    print(f"\n[OK] Results saved to: {filename}")


if __name__ == "__main__":
    # Just check status (no interactive prompts)
    if check_video_status():
        print("\n[OK] Video is ready for analysis!")
        print("\nTo run full analysis, use:")
        print("   py analyze_video.py")
    else:
        print("\n[INFO] Video is not ready yet.")
        print("\nOptions:")
        print("1. Wait a few more minutes and run this script again")
        print("2. Check status in TwelveLabs dashboard:")
        print("   https://playground.twelvelabs.io/dashboard")
        print("\nTo check again, run:")
        print("   py check_and_analyze.py")
