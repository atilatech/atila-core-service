# Atlas Chatbot


Message on WhatsApp:

1. Send a message `start` to https://wa.me/12896703567

Messave on WhatsApp via `curl`:

```shell
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=help&WaId=19058758867&ProfileName=Tomiwa[CURL]" \
  http://127.0.0.1:8001/api/chatbot/handle-incoming-message/
```