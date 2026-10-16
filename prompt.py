PROMPT="""Use Video 1 as the base. Replace the four people in Video 1 with the people
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
proportions and seamless blending, with no flickering or face morphing."""