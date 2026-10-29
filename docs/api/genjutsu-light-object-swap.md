# Genjutsu Light

> Replace objects, characters or clothes using reference images. Uses the first 15 seconds of the source video and preserves source audio.

## Overview

- **Endpoint**: `https://api.higgsfield.ai/higgsfield/genjutsu-light/object-swap/v1.0`
- **Model ID**: `higgsfield/genjutsu-light/object-swap/v1.0`
- **Category**: video2video
- **Kind**: inference
- **Tags**: featured, trending

## Pricing

Priced per total second by resolution: 480p $0.05, 720p $0.10, or 1080p $0.20. Rates shown are before any applicable customer discount. Billable seconds = output duration + the sum of input reference video durations. Input video durations are measured during preprocessing; without video references, only output duration is billed. Genjutsu Light trims the source to 15 seconds; output duration is rounded up to whole seconds before billing.

## Authentication

Keep credentials in server-side environment variables. The SDKs accept the same `KEY_ID:KEY_SECRET` value under their documented variable names.

```bash
export HF_CREDENTIALS="YOUR_KEY_ID:YOUR_KEY_SECRET" # TypeScript
export HF_KEY="YOUR_KEY_ID:YOUR_KEY_SECRET"         # Python and cURL
```

The official SDKs configure the authorization header. Keep credentials server-side; the TypeScript SDK blocks browser use.

## API Information

Use `subscribe` to submit the model request and wait for a terminal result. TypeScript performs automatic polling with `withPolling: true`; Python's synchronous `subscribe` call also waits.

### Input Parameters

- **`prompt`** (`string`, _optional_):
  - Default: `""`

- **`video_url`** (`string`, _required_):

- **`image_urls`** (`list<string>`, _required_):

- **`resolution`** (`string`, _optional_):
  - Default: `"720p"`
  - Options: `720p`, `480p`, `1080p`

### Input JSON Schema

```json
{
  "type": "object",
  "title": "ObjectSwapParams",
  "required": [
    "video_url",
    "image_urls"
  ],
  "properties": {
    "prompt": {
      "type": "string",
      "title": "Prompt",
      "default": "",
      "maxLength": 10000
    },
    "video_url": {
      "type": "string",
      "title": "Video Url",
      "format": "uri",
      "maxLength": 2083,
      "minLength": 1
    },
    "image_urls": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uri",
        "maxLength": 2083,
        "minLength": 1
      },
      "title": "Image Urls",
      "maxItems": 8,
      "minItems": 1
    },
    "resolution": {
      "enum": [
        "720p",
        "480p",
        "1080p"
      ],
      "type": "string",
      "title": "Resolution",
      "default": "720p"
    }
  },
  "additionalProperties": true
}
```

### Required Parameters Example

```json
{
  "prompt": "",
  "video_url": "https://example.com/input.mp4",
  "image_urls": [
    "https://example.com/input.jpg"
  ],
  "resolution": "720p"
}
```

### Output Schema

The shared polling endpoint returns one of the following status shapes:

```json
{
  "title": "RequestStatus",
  "oneOf": [
    {
      "title": "PendingRequestStatus",
      "type": "object",
      "properties": {
        "request_id": {
          "type": "string",
          "format": "uuid"
        },
        "status_url": {
          "type": "string",
          "format": "uri"
        },
        "cancel_url": {
          "type": "string",
          "format": "uri"
        },
        "status": {
          "type": "string",
          "enum": [
            "queued",
            "in_progress",
            "nsfw",
            "canceled"
          ]
        }
      },
      "required": [
        "status",
        "request_id"
      ]
    },
    {
      "title": "FailedRequestStatus",
      "type": "object",
      "properties": {
        "request_id": {
          "type": "string",
          "format": "uuid"
        },
        "status_url": {
          "type": "string",
          "format": "uri"
        },
        "cancel_url": {
          "type": "string",
          "format": "uri"
        },
        "status": {
          "type": "string",
          "const": "failed"
        },
        "error": {
          "type": "string"
        }
      },
      "required": [
        "status",
        "request_id",
        "error"
      ]
    },
    {
      "title": "CompletedRequestStatus",
      "type": "object",
      "properties": {
        "request_id": {
          "type": "string",
          "format": "uuid"
        },
        "status_url": {
          "type": "string",
          "format": "uri"
        },
        "cancel_url": {
          "type": "string",
          "format": "uri"
        },
        "status": {
          "type": "string",
          "const": "completed"
        },
        "video": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            }
          },
          "required": [
            "url"
          ]
        },
        "zip": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            }
          },
          "required": [
            "url"
          ]
        },
        "mov": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            }
          },
          "required": [
            "url"
          ]
        },
        "jsx": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            }
          },
          "required": [
            "url"
          ]
        },
        "fbx": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            }
          },
          "required": [
            "url"
          ]
        },
        "ply": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            }
          },
          "required": [
            "url"
          ]
        }
      },
      "required": [
        "status",
        "request_id",
        "video"
      ]
    }
  ]
}
```

## SDK Installation

Install one of the official server-side SDKs:

```bash
npm install @higgsfield/client
# or
pip install higgsfield-client
```

## Usage Examples

### TypeScript

```typescript
import { config, higgsfield } from "@higgsfield/client/v2";

config({
  credentials: process.env.HF_CREDENTIALS,
});

const result = await higgsfield.subscribe(
  "higgsfield/genjutsu-light/object-swap/v1.0",
  {
    input: {
      "prompt": "",
      "video_url": "https://example.com/input.mp4",
      "image_urls": [
        "https://example.com/input.jpg"
      ],
      "resolution": "720p"
    },
    withPolling: true,
  },
);

console.log(result);
```

### Python

```python
import higgsfield_client

result = higgsfield_client.subscribe(
    'higgsfield/genjutsu-light/object-swap/v1.0',
    arguments={'prompt': '',
         'video_url': 'https://example.com/input.mp4',
         'image_urls': ['https://example.com/input.jpg'],
         'resolution': '720p'},
)

print(result)
```

### cURL

```bash
curl --request POST \
  --url 'https://api.higgsfield.ai/higgsfield/genjutsu-light/object-swap/v1.0' \
  --header "Authorization: Key $HF_KEY" \
  --header "Content-Type: application/json" \
  --data @- <<'JSON'
{
  "prompt": "",
  "video_url": "https://example.com/input.mp4",
  "image_urls": [
    "https://example.com/input.jpg"
  ],
  "resolution": "720p"
}
JSON
```

## Additional Resources

- [Model page](https://console.higgsfield.ai/models/higgsfield/genjutsu-light/object-swap/v1.0)
- [This LLM-readable document](https://dash.higgsfield.ai/models/higgsfield/genjutsu-light/object-swap/v1.0/llms.txt)

## Documentation Index

- [Complete Higgsfield documentation](https://docs.higgsfield.ai/docs/llms.txt)
