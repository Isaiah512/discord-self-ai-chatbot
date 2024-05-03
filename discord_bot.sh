#!/bin/bash

source .env

while true; do
  NONCE=$(python3 -c "import random; print(random.randint(1018, 1018 + 2*(10**17)))")

  RESPONSE=$(curl -s "https://discord.com/api/v9/channels/$CHANNEL_ID/messages" \
    -H "authorization: $AUTH_KEY" \
    -H 'content-type: application/json')

  if [ -z "$RESPONSE" ]; then
    echo "No messages"
  else
    LAST_MESSAGE=$(echo "$RESPONSE" | jq -r '.[0].content')

    if [ -z "$LAST_MESSAGE" ]; then
      echo "Last message is empty"
    else
      if [[ $LAST_MESSAGE == "-a"* ]]; then
        echo "Found message starting with '-a': $LAST_MESSAGE"
        
        MESSAGE_CONTENT="${LAST_MESSAGE#'-a'}"

        MESSAGE_CONTENT=$(python3 - <<END
import google.generativeai as genai

genai.configure(api_key="$TOKEN")

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 500,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
])

convo.send_message("$MESSAGE_CONTENT")
print(convo.last.text)
END
)
        if [ -z "$MESSAGE_CONTENT" ]; then
          echo "Generated message is empty"
        else
          curl "https://discord.com/api/v9/channels/$CHANNEL_ID/messages" \
            -H "authorization: $AUTH_KEY" \
            -H 'content-type: application/json' \
            --data-raw "{\"mobile_network_type\":\"unknown\",\"content\":\"$MESSAGE_CONTENT\",\"nonce\":\"$NONCE\"}"
        fi
      else
        echo "Message does not start with '-a': $LAST_MESSAGE"
      fi
    fi
  fi
 
  # every 5 seconds it checks if there is a new message
  sleep 5
done
