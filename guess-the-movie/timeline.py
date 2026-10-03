# -*- coding: utf-8 -*-
"""Single source of truth for the 60-second "خمن الفيلم" video.

Every other output (subtitles, overlays, SFX, the shot plan, the final edit)
is generated from the data in this file, so timing never drifts between them.
"""

DURATION = 60.0
W, H, FPS = 1080, 1920, 30

ME, AI = "me", "ai"

# Dialogue: (start, end, speaker, text). Times are in seconds on the master timeline.
LINES = [
    (0.30, 5.80, ME, "النهارده الـAI اختارلي فيلم… وأنا عندي دقيقة واحدة بس عشان أخمّنه. يلا نشوف هعرفه ولا لأ!"),
    (8.10, 9.70, ME, "أول سؤال… الفيلم مصري؟"),
    (9.95, 11.70, AI, "أيوه، مصري طبعًا."),
    (12.10, 13.30, ME, "قديم ولا حديث؟"),
    (13.55, 16.60, AI, "قديم نسبيًا… من الأفلام اللي لسه الناس بتتكلم عنها."),
    (16.90, 18.40, ME, "طيب هو فيلم كوميدي؟"),
    (18.65, 21.10, AI, "كوميدي… بس وراه موضوع تقيل شوية."),
    (21.30, 22.50, ME, "آه… فهمتك."),
    (22.70, 24.60, ME, "هل الفيلم بيناقش قضية اجتماعية؟"),
    (24.85, 27.20, AI, "جداً… وبيعمل ده بطريقة ساخرة."),
    (27.50, 29.00, ME, "هل فيه علاقة بالمخدرات؟"),
    (29.20, 29.90, AI, "أيوه."),
    (30.15, 32.00, ME, "استنى كده… إحنا بنقرب."),
    (32.30, 35.40, ME, "هل البطل بيحاول يفهم أو يتعامل مع موضوع المخدرات بطريقة مختلفة؟"),
    (35.65, 38.00, AI, "بالضبط… وده أساس كبير من أحداث الفيلم."),
    (38.30, 39.80, ME, "طب فيه محمود عبدالعزيز؟"),
    (40.00, 40.70, AI, "أيوه."),
    (40.90, 42.80, ME, "تمام… كده الموضوع بقى واضح."),
    (43.10, 44.40, ME, "ويحيى الفخراني كمان؟"),
    (44.60, 45.20, AI, "أيوه."),
    (45.40, 46.50, ME, "يا نهار أبيض!"),
    # Guess: 1.8 s of held silence and a push-in first, then the line, then a beat.
    (48.40, 51.00, ME, "طب الفيلم اسمه… الكيف؟"),
    (52.00, 53.20, AI, "أيووووه!"),
    (54.00, 56.40, ME, "كنت عارفها من أول محمود عبدالعزيز أصلاً!"),
    (56.55, 58.60, AI, "لا يا عم، إنت كنت بتستجوبني مش بتخمّن!"),
    (58.75, 59.75, ME, "المهم إني جبتها!"),
]

# Question counter: (start, end, n). The 9th question (the guess) deliberately has no counter.
COUNTER = [
    (8.0, 12.0, 1), (12.0, 16.8, 2), (16.8, 22.6, 3), (22.6, 27.4, 4),
    (27.4, 32.2, 5), (32.2, 38.2, 6), (38.2, 43.0, 7), (43.0, 46.6, 8),
]

TITLE_CARD = (5.9, 8.0)        # "خمن الفيلم / 60 ثانية"
GUESS = (46.6, 52.0)           # music drop, push-in, silence
REVEAL = 52.0                  # AI "أيووووه!" + title "الكيف"
TIMER = (5.9, 52.0)            # on-screen countdown runs until the reveal

# Shared look for every generated clip — pasted into each prompt verbatim.
IDENTITY = (
    "The man is EXACTLY the person in the attached reference photos: same face shape, jaw, chin, nose, "
    "dark brown eyes, eyebrows, lips, warm brown skin tone, short curly black hair with a receding hairline, "
    "short trimmed beard and moustache, same age (mid-30s) and facial proportions, same small mole on the cheek beside the nose, exactly as in the references. "
    "Do not beautify, de-age, swap, or morph the face."
)
WARDROBE = "Wardrobe (identical in every clip): cream ribbed turtleneck under a dusty-pink fine-check blazer, as in the reference photos."
SET = (
    "Set (identical in every clip): dark modern studio, matte charcoal walls, a few warm practical lamps and a soft "
    "teal LED strip far out of focus in the background. Lighting: cinematic key light camera-left at 45°, soft fill, "
    "subtle warm rim light on hair and shoulders, natural shadows, realistic skin texture and pores. "
    "Shot on a cinema camera, 35mm-equivalent lens, shallow depth of field, 9:16 vertical, 1080x1920, 30 fps."
)
AUDIO_RULE = (
    "Audio: only his own voice, natural conversational Egyptian Arabic (Cairene), relaxed and playful, not formal "
    "Arabic and not an advert read; perfectly lip-synced. No music, no sound effects, no on-screen text or captions."
)
NEGATIVE = (
    "face swap, face morphing, identity change, different person, plastic skin, waxy skin, beauty filter, "
    "unnatural eyes, flicker, warped teeth, extra fingers, deformed hands, changing clothes, changing hair, "
    "changing beard, age change, different studio, lip-sync drift, exaggerated expressions, robotic movement, "
    "text, subtitles, watermark"
)

# The shot plan. Each clip is generated separately (≤ 8 s each, so any current
# image-to-video model with audio can make it), then the edit stitches them.
# During AI lines the man is silent and reacts; the AI host is a graphic overlay
# added in the edit, so generated clips only ever contain him.
CLIPS = [
    dict(id="C01", start=0.0, end=5.9, shot="Medium close-up, chest up, centred",
         camera="Very slow push-in (about 5%)",
         face="Bright, confident half-smile; eyebrows lift on 'دقيقة واحدة'; grins on 'يلا'",
         body="Small open-hand gesture at chest height on 'اختارلي فيلم', settles back",
         sfx="Soft riser into the title card", music="Upbeat cinematic pulse starts at 0.0",
         onscreen="Subtitles only",
         ref=("c12567e0", 0.487, 0.32, 0.62, 1.00, 1.05)),
    dict(id="C02", start=5.9, end=8.0, shot="Same framing, slightly wider",
         camera="Locked off; the edit punches in on the title card",
         face="Rubs hands together, playful 'challenge accepted' smile, no dialogue",
         body="Rubs palms once, looks at camera",
         sfx="Whoosh + bass hit as the title lands", music="Pulse continues",
         onscreen="Title card: خمن الفيلم — 60 ثانية; countdown timer appears",
         ref=("c12567e0", 0.487, 0.35, 0.80, 1.06, 1.00)),
    dict(id="C03", start=8.0, end=12.0, shot="Close-up, slight 3/4 to camera-right (looking at the AI)",
         camera="Subtle arc left-to-right (a few degrees)",
         face="Curious squint on the question; nods with a small smile while the AI answers",
         body="Leans in slightly on 'أول سؤال'",
         sfx="Whoosh in; ding on the AI answer", music="Pulse",
         onscreen="Counter: السؤال 1 / 9; AI host panel while AI speaks",
         ref=("fbf29834", 0.51, 0.40, 0.50, 1.00, 1.04)),
    dict(id="C04", start=12.0, end=16.8, shot="Medium close-up, centred",
         camera="Locked off, tiny handheld float",
         face="Raises one eyebrow on 'قديم ولا حديث'; thoughtful 'hmm' face while listening",
         body="Tilts head slightly",
         sfx="Jump-cut whoosh; ding on answer", music="Pulse",
         onscreen="Counter: السؤال 2 / 9; AI host panel",
         ref=("257ea5bf", 0.50, 0.43, 0.55, 1.04, 1.00)),
    dict(id="C05", start=16.8, end=22.6, shot="Close-up",
         camera="Slow push-in",
         face="Hopeful smile on 'كوميدي؟'; smile fades to knowing look; says 'آه… فهمتك' with a slow nod",
         body="Index finger points lightly at the AI on 'فهمتك'",
         sfx="Whoosh; ding", music="Pulse, add light suspense layer",
         onscreen="Counter: السؤال 3 / 9; AI host panel",
         ref=("44cdb7f8", 0.46, 0.43, 0.52, 1.00, 1.06)),
    dict(id="C06", start=22.6, end=27.4, shot="Over-the-shoulder from behind the AI screen (his face fully visible)",
         camera="Locked off, slow rack focus from screen edge to his face",
         face="Serious, analytical; narrows eyes while listening",
         body="Rests chin briefly on knuckles",
         sfx="Whoosh; ding", music="Pulse",
         onscreen="Counter: السؤال 4 / 9; AI host panel",
         ref=("c12567e0", 0.487, 0.33, 0.70, 1.00, 1.03)),
    dict(id="C07", start=27.4, end=32.2, shot="Close-up",
         camera="Quick small push-in on 'استنى كده'",
         face="Lowered voice and half-whisper on the question; eyes widen at 'أيوه.'; raises palm 'wait' on 'استنى كده'",
         body="Palm up toward camera on 'استنى كده'",
         sfx="Whoosh; ding; low tension hit on 'بنقرب'", music="Suspense layer up",
         onscreen="Counter: السؤال 5 / 9; AI host panel",
         ref=("fbf29834", 0.51, 0.40, 0.46, 1.00, 1.08)),
    dict(id="C08", start=32.2, end=38.2, shot="Medium close-up, slight low angle",
         camera="Subtle arc right-to-left",
         face="Talks it through, slightly faster; satisfied nod at 'بالضبط'",
         body="Hands describe a small circle as he thinks aloud",
         sfx="Whoosh; ding", music="Suspense",
         onscreen="Counter: السؤال 6 / 9; AI host panel",
         ref=("257ea5bf", 0.50, 0.43, 0.62, 1.03, 1.00)),
    dict(id="C09", start=38.2, end=43.0, shot="Close-up",
         camera="Locked off, tiny push-in on 'واضح'",
         face="Confident smirk on 'محمود عبدالعزيز'; leans back satisfied on 'كده الموضوع بقى واضح'",
         body="Leans back, crosses arms loosely",
         sfx="Whoosh; ding; low impact", music="Suspense, building",
         onscreen="Counter: السؤال 7 / 9; AI host panel",
         ref=("44cdb7f8", 0.46, 0.43, 0.50, 1.00, 1.05)),
    dict(id="C10", start=43.0, end=46.6, shot="Medium close-up",
         camera="Locked off",
         face="Quick question; on 'يا نهار أبيض!' slaps forehead lightly, laughs",
         body="Hand to forehead, then drops",
         sfx="Whoosh; ding; small comic 'boing' optional", music="Peak of the build, then cut",
         onscreen="Counter: السؤال 8 / 9; AI host panel",
         ref=("98eb40df", 0.46, 0.44, 0.60, 1.00, 1.03)),
    dict(id="C11", start=46.6, end=52.0, shot="Close-up → extreme close-up",
         camera="Slow continuous push-in (about 25%), ends on eyes and mouth",
         face="Thinking, then a 1.8 s pause looking straight into the lens; says the guess slowly; holds still after 'الكيف؟'",
         body="Completely still",
         sfx="Music drops; low impact; heartbeat; 1 s of near-silence after 'الكيف؟'", music="Ducked to near silence",
         onscreen="No counter; timer flashes red; letterbox bars slide in",
         ref=("29edb565", 0.48, 0.42, 0.62, 1.00, 1.28)),
    dict(id="C12", start=52.0, end=60.0, shot="Medium close-up, centred",
         camera="Snap back wide on the reveal, then locked off",
         face="Bursts out laughing at 'أيووووه'; proud, cheeky on 'كنت عارفها'; mock-offended then laughing at the AI's comeback; big grin on 'المهم إني جبتها!'",
         body="Fist pump on the reveal; points at himself on 'جبتها'",
         sfx="Celebration hit + sparkle at 52.0; whoosh out", music="Bright, major-key return; out at 60.0",
         onscreen="Big title: الكيف; AI host panel; end card",
         ref=("e670b6be", 0.30, 0.36, 0.62, 1.00, 1.04)),
]
