"""
Analyze video - Auto-run version (no prompts)
"""
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs

# Load environment variables
load_dotenv()

# Your video ID
VIDEO_ID = "68e20c15f2e53b115e1aef18"

def main():
    """Run comprehensive analysis on the video"""
    print("=" * 60)
    print("TwelveLabs Video Analysis")
    print("=" * 60)
    
    api_key = os.getenv("TWELVELABS_API_KEY") or os.getenv("TL_API_KEY")
    client = TwelveLabs(api_key=api_key)
    
    print(f"\nVideo ID: {VIDEO_ID}")
    print("\nRunning comprehensive analysis...")
    print("This will take 1-2 minutes.\n")
    
    try:
        # 1. Get Gist (Title, Topics, Hashtags)
        print("1. Getting Gist (title, topics, hashtags)...")
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
        for i, chapter in enumerate(chapters_result.chapters[:3], 1):  # Show first 3
            print(f"\n   Chapter {chapter.chapter_number}:")
            print(f"   - Time: {chapter.start_sec}s - {chapter.end_sec}s")
            print(f"   - Title: {chapter.chapter_title}")
            print(f"   - Summary: {chapter.chapter_summary[:150]}...")
        
        if len(chapters_result.chapters) > 3:
            print(f"\n   ... and {len(chapters_result.chapters) - 3} more chapters")
        
        # 4. Get Highlights
        print("\n4. Getting Highlights...")
        highlights_result = client.summarize(video_id=VIDEO_ID, type="highlight")
        
        print(f"\n   Found {len(highlights_result.highlights)} highlights:")
        for i, highlight in enumerate(highlights_result.highlights[:3], 1):  # Show first 3
            print(f"\n   Highlight {i}:")
            print(f"   - Time: {highlight.start_sec}s - {highlight.end_sec}s")
            print(f"   - Description: {highlight.highlight}")
        
        if len(highlights_result.highlights) > 3:
            print(f"\n   ... and {len(highlights_result.highlights) - 3} more highlights")
        
        # 5. Get Detailed Analysis
        print("\n5. Getting Detailed Creative Analysis...")
        print("   (Streaming response - this takes 30-60 seconds...)\n")
        
        analysis_prompt = """Analyze this advertisement/video for creative effectiveness:

1. VISUAL ELEMENTS:
   - Color palette and visual style
   - Key objects, people, and settings
   - Camera work and composition

2. PACING & EDITING:
   - Overall pacing (fast/slow/varied)
   - Editing style and transitions

3. AUDIO & MESSAGING:
   - Music and voiceover characteristics
   - Core message and emotional tone
   - Brand positioning

4. KEY MOMENTS:
   - Most impactful scenes
   - Product/brand reveals
   - Call-to-action effectiveness

5. RECOMMENDATIONS:
   - What works well
   - What could be improved
   - Target audience fit"""
        
        analysis_text = ""
        print("   Analysis: ", end='', flush=True)
        
        text_stream = client.analyze_stream(
            video_id=VIDEO_ID,
            prompt=analysis_prompt
        )
        
        for text in text_stream:
            if text.event_type == "text_generation":
                analysis_text += text.text
                print(text.text, end='', flush=True)
        
        print("\n\n" + "=" * 60)
        print("Analysis Complete!")
        print("=" * 60)
        
        # Save results to file
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
            f.write(f"{summary_result.summary}\n\n")
            
            f.write("CHAPTERS\n")
            f.write("-" * 60 + "\n")
            for chapter in chapters_result.chapters:
                f.write(f"\nChapter {chapter.chapter_number}:\n")
                f.write(f"Time: {chapter.start_sec}s - {chapter.end_sec}s\n")
                f.write(f"Title: {chapter.chapter_title}\n")
                f.write(f"Summary: {chapter.chapter_summary}\n")
            
            f.write("\n\nHIGHLIGHTS\n")
            f.write("-" * 60 + "\n")
            for i, highlight in enumerate(highlights_result.highlights, 1):
                f.write(f"\nHighlight {i}:\n")
                f.write(f"Time: {highlight.start_sec}s - {highlight.end_sec}s\n")
                f.write(f"Description: {highlight.highlight}\n")
            
            f.write("\n\nDETAILED CREATIVE ANALYSIS\n")
            f.write("-" * 60 + "\n")
            f.write(analysis_text)
        
        print(f"\n[OK] Full results saved to: {filename}")
        print("\nYou can now:")
        print("1. Open the results file to view complete analysis")
        print("2. Use this video in the full platform")
        print("3. Create experiments with this video")
        
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "does not exist" in error_msg:
            print("[ERROR] Video not found or not ready yet.")
            print(f"\nYour video ID: {VIDEO_ID}")
            print("\nPlease check:")
            print("1. Video ID is correct")
            print("2. Video has finished indexing")
            print("3. Check dashboard: https://playground.twelvelabs.io/dashboard")
            return False
        else:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    main()
