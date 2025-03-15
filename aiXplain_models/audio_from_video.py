import time
from aixplain.factories import ModelFactory

def extract_audio_from_video(video_data, model_id="653684e161ddee7e38347e7b", poll_interval=5):
    """
    Extracts audio from a given video using the specified AI model asynchronously.

    Parameters:
    - video_data (str): The video file data or file path.
    - model_id (str): The AI model ID to use for audio extraction.
    - poll_interval (int): Time (in seconds) to wait before polling for results.

    Returns:
    - dict: The extracted audio data if successful, None otherwise.
    """
    try:
        model = ModelFactory.get(model_id)

        # Start the asynchronous request
        start_response = model.run_async({"video": video_data})

        # Extract the polling URL from the response
        poll_url = start_response.get("poll_url")

        if not poll_url:
            print("Polling URL not found in response.")
            return None

        # Polling loop: Check the completion status periodically
        while True:
            result = model.poll(poll_url)
            if result.get("completed"):
                return result  # Return the extracted audio data
            else:
                time.sleep(poll_interval)  # Wait before polling again

    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage
video_file_path = "<VIDEO_VIDEO_DATA>"  # Replace with actual video data or file path
audio_result = extract_audio_from_video(video_file_path)

if audio_result:
    print(audio_result)
