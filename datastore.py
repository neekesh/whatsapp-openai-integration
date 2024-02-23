
# Imports the Google Cloud client library
from google.cloud import datastore



class Datastore:
# Instantiates a client
    def __init__(self) -> None:
        self.client = datastore.Client()
        self.kind = "ChatDetails"

    def create(self, chat_details ):

        name = chat_details["phone_no"]
        create_key = self.client.key(self.kind, name)
        entity = datastore.Entity(key=create_key)
        entity["description"] = {
            "thread_id": chat_details["thread_id"],
            
        }
        self.client.put(entity)
        return "Created"

    def get(self, phone_no):
        filter_Key = self.client.key(self.kind,phone_no)
    
        query = self.client.query(kind=self.kind)
        query.add_filter('__key__', '=', filter_Key)
    
        results = list(query.fetch(limit=1))
        if results:
            entity = results[0]
            thread_id = entity['description']['thread_id']
            return thread_id
        else:
            return 


if __name__ == "__main__":
    ds = Datastore()