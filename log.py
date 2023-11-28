import datetime


def log_aggregate_results(successes, unlikely_videos, detail_failures, json_load_failures):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"Timestamp: {timestamp}\n"
            f"Total Successful Inserts: {successes}\n"
            f"Total Unlikely Exercise Videos: {unlikely_videos}\n"
            f"Total Failures Getting Exercise Details: {detail_failures}\n"
            f"Total Failures Loading JSON: {json_load_failures}\n\n"
        )
        try:
            with open("logs/aggregate_log.txt", "a") as log_file:
                log_file.write(log_message)
        except IOError as e:
            print(f"An I/O error occurred while writing to the aggregate log file: {str(e)}")

def log_error(video_id, video_title, likely_score, error_message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = (
        f"Timestamp: {timestamp}\n"
        f"Video ID: {video_id}\n"
        f"Video Title: {video_title}\n"
        f"Likely/Unlikely Score: {likely_score}\n"
        f"Error: {error_message}\n\n"
    )
    try:
        with open("logs/error_log.txt", "a") as log_file:
            log_file.write(log_message)
    except IOError as e:
        print(f"An I/O error occurred while writing to the log file: {str(e)}")


def log_counter(exercise, video_id, video_title, likely_score, video_counter):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = (
        f"Timestamp: {timestamp}\n"
        f"ExercisePrompt: {exercise}\n"
        f"Video ID: {video_id}\n"
        f"Video Title: {video_title}\n"
        f"Likely/Unlikely Score: {likely_score}\n"
        f"Count: {video_counter}\n\n"
    )
    try:
        with open("logs/success_log.txt", "a") as log_file:
            log_file.write(log_message)
    except IOError as e:
        print(f"An I/O error occurred while writing to the log file: {str(e)}")




