"""Prompts. The key is the name you type on the command line: python main.py <name>."""

PROMPTS = {
    # 1 person in the video, 1 or more images of the SAME person (more angles = better match)
    "one-person": """Use Video 1 as the base. Replace the person in Video 1 with the person
from the reference images. Use that image to reproduce that person's exact face, facial features, hairstyle,
natural skin tone and body type.

The face must match the reference image closely and stay consistent and
recognizable in every frame, from every angle. Keep the clothing from Video 1
unless the reference images clearly show the full outfit.

Keep the exact motion from Video 1: the same body movements, gestures, head turns,
facial expressions, lip movements, eye direction and timing. Keep the same pose,
position, scale and framing as in Video 1. If a part of the body becomes visible
that isn't shown in the reference images, reconstruct it naturally to match.

Keep the same background, objects, lighting, camera angle, camera movement and
overall composition as Video 1. Make the replacement look completely natural and
photorealistic, with realistic lighting, shadows, skin texture and proportions,
seamless blending and no flickering or face morphing.""",

    # 4 people in the video, 1 image per person (Image 1 = 1st person from the left)
    "four-people": """Use Video 1 as the base. Replace the four people in Video 1 with the people
from the reference images, ordered from left to right as they appear in Video 1:
- the 1st person from the left becomes the person from Image 1,
- the 2nd person from the left becomes the person from Image 2,
- the 3rd person from the left becomes the person from Image 3,
- the 4th person from the left becomes the person from Image 4.

Preserve each person's exact face, facial features, hairstyle, natural skin tone,
body type and clothing from their respective reference image. Each face must
match its reference image closely and stay consistent and recognizable in every
frame, from every angle.

Keep the exact motion from Video 1 for each person: the same body movements,
gestures, head turns, facial expressions, lip movements, eye direction and timing.
Keep the same poses, positions, scale, framing and amount of each person visible
as in Video 1. Do not show significantly more or less of any person than in the
original. If a part of their body or clothing becomes visible but isn't shown in
their reference image, naturally reconstruct it to match their outfit and appearance.

Keep the same background, objects, lighting, camera angle, camera movement,
cuts and overall composition as Video 1. Make the replacements look completely
natural and photorealistic, with realistic lighting, shadows, skin texture,
proportions and seamless blending, with no flickering or face morphing.""",
}

DEFAULT_PROMPT = "one-person"
