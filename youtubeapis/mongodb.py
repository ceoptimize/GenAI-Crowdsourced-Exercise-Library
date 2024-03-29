from pymongo import MongoClient

class MongoDBManager:
    
    """Encapsulates MongoDB interactions."""

    def __init__(self, uri, db_name, gpt_entries_coll, unsent_question_maps_coll):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.gpt_entries_coll = self.db[gpt_entries_coll]
        self.unsent_question_maps_coll = self.db[unsent_question_maps_coll]

    def insert_gpt_entry(self, entry):
        """Inserts a new document into the GPT entries collection."""
        return self.gpt_entries_coll.insert_one(entry)

    def find_gpt_entry(self, query):
        """Finds documents in the GPT entries collection."""
        return self.gpt_entries_coll.find(query)

    def update_gpt_entry(self, query, update):
        """Updates documents in the GPT entries collection."""
        return self.gpt_entries_coll.update_many(query, update)

    def delete_gpt_entry(self, query):
        """Deletes documents from the GPT entries collection."""
        return self.gpt_entries_coll.delete_many(query)

    def insert_unsent_question_map(self, entry):
        """Inserts a new document into the unsent question maps collection."""
        return self.unsent_question_maps_coll.insert_one(entry)

    def find_unsent_question_map(self, query):
        """Finds documents in the unsent question maps collection."""
        return self.unsent_question_maps_coll.find(query)

    def update_unsent_question_map(self, query, update):
        """Updates documents in the unsent question maps collection."""
        return self.unsent_question_maps_coll.update_many(query, update)

    def delete_unsent_question_map(self, query):
        """Deletes documents from the unsent question maps collection."""
        return self.unsent_question_maps_coll.delete_many(query)