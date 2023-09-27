from youtube import Youtube
from postgres import PostgresDatabase



class VideoLoader:
    def __init__(self):
        self.postgres = PostgresDatabase()
        self.youtube = Youtube()

    def load_videos_to_youtubevideo_table(self, printresults = False, enable_limit=True):
        self.youtube.insert_all_channel_ids_to_postgres(enable_limit)
        if(printresults):
            query = """
                SELECT *
                FROM youtubevideo
                LIMIT 5;
                """
            result = self.postgres.fetch_query(query)
           


