from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from products.models import Product


@registry.register_document
class ProductDocument(Document):
    # Adding completion field for autocomplete suggestions
    name = fields.TextField(
        fields={
            "raw": fields.KeywordField(),  # For exact matches
            "suggest": fields.CompletionField(),  # For autocomplete suggestions
        }
    )
    # Searchable fields
    hashtags = fields.ObjectField(
        properties={
            "keyword": fields.KeywordField(),
        }
    )
    description = fields.TextField()
    condition = fields.KeywordField()

    class Index:
        name = "products"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "ngram_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "ngram_filter"],
                    }
                },
                "filter": {
                    "ngram_filter": {"type": "ngram", "min_gram": 2, "max_gram": 3}
                },
            },
        }

    class Django:
        model = Product
        fields = ["id"]
