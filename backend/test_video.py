from dotenv import load_dotenv
import os
from twelvelabs import TwelveLabs

load_dotenv()
client = TwelveLabs(api_key=os.getenv("TWELVELABS_API_KEY"))

# Use sample video
video_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
index_id = "68e20573f2e53b115e1aee13"  # Your index ID

print("Uploading video...")
task = client.tasks.create(index_id=index_id, video_url=video_url)
print(f"Task ID: {task.id}")
print("Waiting for indexing... (this takes a few minutes)")

task = client.tasks.wait_for_done(task_id=task.id, sleep_interval=5)
print(f"Video ID: {task.video_id}")

print("\nGetting analysis...")
gist = client.gist(video_id=task.video_id, types=["title", "topic"])
print(f"Title: {gist.title}")
print(f"Topics: {gist.topics}")