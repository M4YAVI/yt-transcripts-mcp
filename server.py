import multiprocessing  # Import multiprocessing
import re

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError  # Import ToolError from fastmcp.exceptions
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

# --- Create the MCP Server ---
mcp = FastMCP(name="YouTube Transcript Extractor 🎬")


def _extract_video_id(video_url: str) -> str | None:
    """Helper function to extract the video ID from various YouTube URL formats."""
    # Standard watch URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
    match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", video_url)
    if match:
        return match.group(1)

    # Shortened youtu.be URL: https://youtu.be/dQw4w9WgXcQ
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", video_url)
    if match:
        return match.group(1)

    # Shorts URL: https://www.youtube.com/shorts/your_video_id
    match = re.search(r"shorts/([a-zA-Z0-9_-]{11})", video_url)
    if match:
        return match.group(1)

    return None


@mcp.tool
def get_youtube_transcript(video_url: str) -> str:
    """
    Fetches the full text transcript for a given YouTube video URL.
    The video must have transcripts enabled and available.
    """
    print(f"Received request to get transcript for: {video_url}")

    video_id = _extract_video_id(video_url)

    if not video_id:
        raise ToolError(
            f"Could not extract a valid YouTube video ID from the URL: '{video_url}'"
        )

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join(item["text"] for item in transcript_list)
        print(f"Successfully fetched transcript for video ID: {video_id}")
        return full_transcript

    except TranscriptsDisabled:
        raise ToolError(f"Transcripts are disabled for the video with ID: {video_id}")
    except NoTranscriptFound:
        raise ToolError(
            f"No transcript could be found for the video with ID: {video_id}. It may not be available in any language."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise ToolError(
            f"An unexpected error occurred while fetching the transcript: {str(e)}"
        )


if __name__ == "__main__":
    # Add this line for better Windows compatibility
    multiprocessing.freeze_support()

    print("🚀 Starting YouTube Transcript MCP Server...")
    # Change this line to use HTTP transport
    mcp.run(transport="http", host="127.0.0.1", port=8000)
