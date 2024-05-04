#!/bin/bash

source .env

while true; do
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
      if [[ $LAST_MESSAGE == "-help" ]]; then
        echo "Received '-help'"
        MESSAGE_RESPONSE="For text prompt: -a\nFor vision prompt: -i"

        NONCE=$(python3 -c "import random; print(random.randint(1018, 1018 + 2*(10**17)))")

        MESSAGE_RESPONSE=$(echo "$MESSAGE_RESPONSE" | sed -e 's/"/\\"/g' -e 's/  */ /g' -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g')

        echo "Sending generated message:"
        echo "{\"mobile_network_type\": \"unknown\", \"content\": \"$MESSAGE_RESPONSE\", \"nonce\": \"$NONCE\"}"

        curl "https://discord.com/api/v9/channels/$CHANNEL_ID/messages" \
          -H "authorization: $AUTH_KEY" \
          -H 'content-type: application/json' \
          --data-raw "{\"mobile_network_type\": \"unknown\", \"content\": \"$MESSAGE_RESPONSE\", \"nonce\": \"$NONCE\"}"

        echo "Generated message: $MESSAGE_RESPONSE"
      elif [[ $LAST_MESSAGE == "-i"* ]]; then
        echo "Received '-i'"

        ATTACHMENTS_COUNT=$(echo "$RESPONSE" | jq '.[0].attachments | length')
        if [[ $ATTACHMENTS_COUNT -gt 0 ]]; then
          echo "Message contains attachments"

          IMG_URL=$(echo "$RESPONSE" | jq -r '.[0].attachments[0].url')
          echo "Extracted image URL: $IMG_URL"

          MESSAGE_CONTENT=$(echo "$LAST_MESSAGE" | sed 's/^-i//')

          IMAGE_FILE="discord_image.jpg"
          curl -o "$IMAGE_FILE" "$IMG_URL"
          echo "Image downloaded to: $IMAGE_FILE"

          MESSAGE_RESPONSE=$(python3 - <<END
import google.generativeai as genai
from PIL import Image

genai.configure(api_key="$TOKEN")

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]

model = genai.GenerativeModel('gemini-pro-vision',
                              safety_settings=safety_settings)

img = Image.open("$IMAGE_FILE")

try:
  response = model.generate_content(["$MESSAGE_CONTENT", img], stream=True)
  response.resolve()
except Exception as e:
  MESSAGE_RESPONSE = e

print(response.text)
END
          )
          rm "$IMAGE_FILE"

          if [ -z "$MESSAGE_RESPONSE" ]; then
            echo "Generated message is empty"
          else
            MESSAGE_RESPONSE=$(echo "$MESSAGE_RESPONSE" | sed -e 's/"/\\"/g' -e 's/  */ /g' -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g')

            NONCE=$(python3 -c "import random; print(random.randint(1018, 1018 + 2*(10**17)))")

            echo "Sending generated message:"
            echo "{\"mobile_network_type\": \"unknown\", \"content\": \"$MESSAGE_RESPONSE\", \"nonce\": \"$NONCE\"}"

            curl "https://discord.com/api/v9/channels/$CHANNEL_ID/messages" \
              -H "authorization: $AUTH_KEY" \
              -H 'content-type: application/json' \
              --data-raw "{\"mobile_network_type\": \"unknown\", \"content\": \"$MESSAGE_RESPONSE\", \"nonce\": \"$NONCE\"}"

            echo "Generated message: $MESSAGE_RESPONSE"
          fi
        else
          echo "No attachments found in the last message"
        fi
      elif [[ $LAST_MESSAGE == "-a"* ]]; then
        echo "Found message starting with '-a': $LAST_MESSAGE"

        MESSAGE_CONTENT="${LAST_MESSAGE#'-a'}"

        MESSAGE_RESPONSE=$(python3 - <<END
import google.generativeai as genai

genai.configure(api_key="$TOKEN")

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 500,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

try:
    convo = model.start_chat(history=[])
    convo.send_message("$MESSAGE_CONTENT")
    MESSAGE_RESPONSE = convo.last.text
except Exception as e:
    MESSAGE_RESPONSE = "Generated message: ERROR: Safety violation detected"

print(MESSAGE_RESPONSE)
END
        )

        if [ -z "$MESSAGE_RESPONSE" ]; then
          echo "Generated message is empty"
        else
          MESSAGE_RESPONSE=$(echo "$MESSAGE_RESPONSE" | sed -e 's/"/\\"/g' -e 's/  */ /g' -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g')

          NONCE=$(python3 -c "import random; print(random.randint(1018, 1018 + 2*(10**17)))")

          echo "Sending generated message:"
          echo "{\"mobile_network_type\": \"unknown\", \"content\": \"$MESSAGE_RESPONSE\", \"nonce\": \"$NONCE\"}"

          curl "https://discord.com/api/v9/channels/$CHANNEL_ID/messages" \
            -H "authorization: $AUTH_KEY" \
            -H 'content-type: application/json' \
            --data-raw "{\"mobile_network_type\": \"unknown\", \"content\": \"$MESSAGE_RESPONSE\", \"nonce\": \"$NONCE\"}"

          echo "Generated message: $MESSAGE_RESPONSE"
        fi
      else
        echo "Message does not start with '-a': $LAST_MESSAGE"
      fi
    fi
  fi

  sleep 2
done

