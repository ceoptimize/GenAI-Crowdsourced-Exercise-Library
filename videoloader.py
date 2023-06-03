from youtube import Youtube
from postgres import PostgresDatabase



class VideoLoader:
    def __init__(self):
        self.postgres = PostgresDatabase()
        self.youtube = Youtube()

    def load_videos_to_youtubevideo_table(self, printresults = True):
        self.youtube.insert_all_channel_ids_to_postgres()
        print("done")
        if(printresults):
            query = """
                SELECT *
                FROM youtubevideo
                LIMIT 5;
                """
            result = self.postgres.fetch_query(query)
            print("First 5 rows of the YoutubeVideo table:")
            for row in result:
                print(row)


