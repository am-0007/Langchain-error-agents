
from elastic_transport import ObjectApiResponse
from _ElasticSearch.ElasticSearchConfig import ElasticSearchConfig
from elasticsearch import Elasticsearch
import re


class EsUtils:        
    @staticmethod
    def get_index_mappings(indices: list[str]) -> list[dict]:
        es_instance: Elasticsearch = ElasticSearchConfig.get_es_instance()
        if indices is None or len(indices) == 0:
            print("No indices provided, fetching all indices.")
            cat_indices = es_instance.cat.indices(format="json")
            print(f"cat_indices: {cat_indices}")

            # Use the helper to filter indices with size > 0 and exclude system indices
            indices = EsUtils.get_index_name_with_size_greater_than_zero(cat_indices=cat_indices)

        mappings = []
        fields = []
        properties = {}
        for index in indices:
            resp : ObjectApiResponse = es_instance.indices.get_mapping(index=index)

            mapping = {}
            if resp.body is not None:
                for key in resp.body:
                    index_mapping_value = resp.body[key]
                    mapping[index] = index_mapping_value
                    properties = index_mapping_value['mappings']['properties']
                    if properties is None:
                        print(f"Warning: index '{index}' has no 'properties' in its mapping, skipping.")
                        continue 
                    fields = list(properties.keys())    
                                   
            mappings.append({
                "fields": fields,
                "description": f"Mapping and Fields in index '{index}'",
                "mapping": {'properties': properties}
            })
            
        return mappings


    @staticmethod
    def get_index_name_with_size_greater_than_zero(cat_indices: list[dict]) -> list[str]:
        """
        Returns a list of index names from the provided cat_indices list
        where the index store size is greater than zero and the index
        name does NOT start with '.' (system indices excluded).
        """
        indices_with_size = []
        for index_info in cat_indices:
            # Use 'pri.store.size' (likely typo fix from 'pre.store.size')
            size_str = index_info.get("pri.store.size", "0")  # size as string like "57.4kb" or "0"
            
            # Convert size string to bytes for numeric comparison
            size_in_bytes = EsUtils.__parse_size_to_bytes(size_str)

            index_name = index_info.get("index", "")
            if size_in_bytes > 0 and not index_name.startswith('.'):
                indices_with_size.append(index_name)
        return indices_with_size


    @staticmethod
    def __parse_size_to_bytes(size_str: str) -> int:
        """
        Converts Elasticsearch size string (e.g., '57.4kb', '1gb') to bytes as integer.
        """
        size_str = size_str.strip().lower()
        units = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4}

        match = re.match(r"([\d.]+)([a-z]*)", size_str)
        if not match:
            return 0
        number, unit = match.groups()
        number = float(number)
        multiplier = units.get(unit, 1)
        return int(number * multiplier)

    
    
if __name__ == "__main__":
    mappings = EsUtils.get_index_mappings(["cigna", "uhc"])
    print(mappings)