# Atlas

Atlas is a service for finding anything on YouTube.

`notebooks/`: Contains the python notebooks used for exploratory work.

`data/`: Contains data files such as sample transcriptions

For a more detailed breakdown of how Atlas works, see: [Atlas: Find Anything on Youtube](https://atila.ca/blog/tomiwa/atlas)


**Services**
1. [Huggingface Inference Endpoint: video-summarize-and-search](https://ui.endpoints.huggingface.co/tomiwa1a/endpoints/video-summarize-and-search)
2. [Pinecone Index: youtube-search](https://app.pinecone.io/organizations/-NJtg2syoPWRDg1eVwga/projects/ff3f45c0-03c1-4246-8de3-186799f6fbf8/indexes/youtube-search/browser)
3. [Stripe webhook for listening to payments](https://dashboard.stripe.com/webhooks/we_1QMvHBHeg0qPyG6kVxgG4B3z) ([test webhook](https://dashboard.stripe.com/test/webhooks/we_1QNGlxHeg0qPyG6k274l7a2v))

## Quickstart

Test that the [HuggingFace inference endpoint](https://ui.endpoints.huggingface.co/tomiwa1a/endpoints/video-summarize-and-search) is working with cURL

```shell
curl "https://x3s08981hxsn2r2t.us-east-1.aws.endpoints.huggingface.cloud" \
-X POST \
-H "Accept: application/json" \
-H "Authorization: Bearer hf_abc1213" \
-H "Content-Type: application/json" \
-d '{"query": "cookies", "inputs": "https://www.youtube.com/watch?v=m6fnJ6rQPok"}'
```
### Pinecone Index

[View Index in Pinecone](https://app.pinecone.io/organizations/-NJtg2syoPWRDg1eVwga/projects/ff3f45c0-03c1-4246-8de3-186799f6fbf8/indexes/youtube-search/browser)

## Testing Atlas Credits
### Test Buying Credits
1. Replace `data-raw` with json data in `data/payment_intent_succeeded_event.json`
2. Replace URL in prod with:https://atila-core-service-299c222291ba.herokuapp.com/api/atlas/credits/buy

```shell
curl --location --request POST 'http://127.0.0.1:8000/api/atlas/credits/buy' \
--header 'Content-Type: application/json' \
--data-raw '{
    "limit": 10
}'
```


```shell
curl --location --request POST 'https://atila-core-service-299c222291ba.herokuapp.com/api/atlas/credits/buy' \
--header 'Content-Type: application/json' \
--data-raw '{
  "api_version": "2019-10-17",
  "created": 1731891892,
  "data": {
    "object": {
      "amount": 2000,
      "amount_received": 2000,
      "charges": {
        "data": [
          {
            "amount": 2000,
            "amount_captured": 2000,
            "billing_details": {
              "address": {},
              "email": "tomiademidun@gmail.com",
              "name": "Tomiwa Ademidun",
              "phone": null
            }
          }
        ]
      },
      "object": "payment_intent"
    }
  },
  "type": "payment_intent.succeeded"
}'
```

### Test Applying Credits

```shell
curl --location --request POST 'http://127.0.0.1:8000/api/atlas/credits/apply' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "tomiwa@atila.ca",
    "code": "8cw0jshtzy4ae4fk"
}'
```
```shell
curl --location --request POST 'https://atila-core-service-299c222291ba.herokuapp.com/api/atlas/credits/apply' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "tomiwa@atila.ca",
    "code": "8cw0jshtzy4ae4fk"
}'
```