from elasticsearch import Elasticsearch
from dotenv import dotenv_values
from pprint import pprint

config = dotenv_values(".env")

class ElasticSearchConfig:
    def __init__(self):
        es_port = config.get("es-port")
        self.ES_PORT = int(es_port) if es_port else 9200
        self.DOMAIN = config.get("es-domain")
        self.USERNAME = config.get("es-username")
        self.ELASTIC_PASSWORD = config.get("es-password")
        
    def setup_elasticsearch(self) -> Elasticsearch:
        if not self.DOMAIN or not self.USERNAME or not self.ELASTIC_PASSWORD:
            raise ValueError("Elasticsearch config incomplete")
        
        client = Elasticsearch(
            hosts=[{
                "host": self.DOMAIN,
                "port": self.ES_PORT,
                "scheme": "http"  # important!
            }],
            basic_auth=(self.USERNAME, self.ELASTIC_PASSWORD)
        )
        return client

    @staticmethod
    def get_es_instance() -> Elasticsearch:
        """
        Creates and returns an instance of Elasticsearch using the configuration provided by ElasticSearchConfig.

        Returns:
            Elasticsearch: An initialized Elasticsearch client instance.
        """
        config = ElasticSearchConfig()
        return config.setup_elasticsearch()

if __name__ == "__main__":
    client = ElasticSearchConfig.get_es_instance()
    try:
        info = client.info()
        pprint(info)
    except Exception as e:
        print("Connection failed:", e)
