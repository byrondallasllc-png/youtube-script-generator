#!/usr/bin/env python3
"""
Batch Script Generator — Generate scripts for all 3 channels from one topic list.
Usage: python batch_generate.py

Reads topics from topics.txt (one per line, format: channel|topic)
Example topics.txt:
    finance|7 Assets That Pay You While You Sleep
    motivation|The Man Who Lost Everything and Started Over at 40
    horror|The Night Shift at the Hotel on Route 9
"""

import anthropic
import os
from datetime import datetime

client = anthropic.Anthropic()

CHANNEL_PROMPTS = {
    "finance": """You are a scriptwriter for a faceless YouTube channel in the personal finance / passive income niche.

Write a complete, ready-to-record YouTube script for the topic below. Follow this structure EXACTLY:

1. HOOK (0–30 seconds): A bold claim or shocking stat that stops the scroll. NO "Hey guys" or intro fluff. Drop straight into it.
2. PROMISE (30–60 seconds): Tell the viewer what they'll learn and why it matters to them right now.
3. BODY (3–7 minutes): 5–7 numbered tips or points. Each point gets:
   - A clear headline
   - 2–3 sentences of explanation
   - A specific example or stat if possible
4. CTA (final 30 seconds): Ask them to subscribe + tease the next video naturally.

Tone: Confident, authoritative, calm. Like a knowledgeable friend, not a sales pitch.
Format: Label each section. Write full sentences, not bullet points. Ready to paste into a teleprompter.
Length: ~900–1100 words total.""",

    "motivation": """You are a scriptwriter for a faceless YouTube motivational / self-improvement channel.

Write a complete, ready-to-record YouTube script for the topic below. Follow this structure EXACTLY:

1. HOOK (0–20 seconds): Open with a provocative statement or question. No intro. Make the viewer feel seen immediately.
2. STORY/NARRATIVE (2–4 minutes): A real or composite story with an emotional arc — struggle, turning point, transformation. Use present tense for immediacy.
3. LESSON (2–3 minutes): Extract 3 clear takeaways from the story. Practical, not fluffy.
4. CLOSE (30 seconds): End with one powerful line that reframes how they see themselves + quiet subscribe ask.

Tone: Deep, calm, cinematic. Like a voiceover in a documentary about human potential.
Format: Label each section. Write full, flowing sentences. Avoid lists in the body — this should feel like storytelling.
Length: ~800–1000 words total.""",

    "horror": """You are a scriptwriter for a faceless YouTube horror / scary stories channel.

Write a complete, ready-to-record YouTube script for the topic below. Follow this structure EXACTLY:

1. HOOK (0–30 seconds): Drop DIRECTLY into the action. No intro. Start mid-scene. Create immediate dread.
2. STORY BUILD (5–10 minutes): Slow, deliberate tension. Details matter — sensory descriptions, specific times/dates, small unsettling observations. Build to the payoff.
3. PAYOFF / TWIST (1–2 minutes): The reveal or conclusion. Land it hard.
4. CTA (20 seconds): Brief, don't break the atmosphere.

Tone: Tense, atmospheric, matter-of-fact. The scariest stories are told like they actually happened.
Format: Label each section. Write in first or third person — be consistent. No filler, no fluff.
Length: ~1000–1300 words total."""
}

SAMPLE_TOPICS = [
    ("finance", "7 Assets That Pay You While You Sleep"),
    ("motivation", "The Man Who Lost Everything and Started Over at 40"),
    ("horror", "The Night Shift at the Hotel on Route 9"),
]


def generate_script(channel: str, topic: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=CHANNEL_PROMPTS[channel],
        messages=[
            {
                "role": "user",
                "content": f"Write the script for this topic: {topic}"
            }
        ]
    )
    return next(b.text for b in response.content if b.type == "text")


def load_topics_from_file(filepath: str):
    topics = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" not in line:
                print(f"Skipping invalid line (missing |): {line}")
                continue
            channel, topic = line.split("|", 1)
            channel = channel.strip().lower()
            topic = topic.strip()
            if channel not in CHANNEL_PROMPTS:
                print(f"Skipping unknown channel: {channel}")
                continue
            topics.append((channel, topic))
    return topics


def main():
    # Load topics
    if os.path.exists("topics.txt"):
        print("Loading topics from topics.txt...")
        topics = load_topics_from_file("topics.txt")
    else:
        print("No topics.txt found. Using sample topics...\n")
        print("Create a topics.txt file with lines like:")
        print("  finance|7 Assets That Pay You While You Sleep")
        print("  motivation|Why Most People Quit")
        print("  horror|The Cabin at Mile Marker 7\n")
        topics = SAMPLE_TOPICS

    if not topics:
        print("No topics to process. Exiting.")
        return

    # Output folder
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"scripts_{date_str}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating {len(topics)} script(s) → {output_dir}/\n")
    print("=" * 60)

    for i, (channel, topic) in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] {channel.upper()}: {topic}")
        print("-" * 40)

        try:
            script = generate_script(channel, topic)

            # Save
            safe_topic = topic.lower().replace(" ", "_").replace("/", "-")[:50]
            filename = os.path.join(output_dir, f"{channel}_{safe_topic}.txt")

            with open(filename, "w") as f:
                f.write(f"CHANNEL: {channel.upper()}\n")
                f.write(f"TOPIC: {topic}\n")
                f.write(f"GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(script)

            # Print preview
            preview = script[:300].replace("\n", " ")
            print(f"  Preview: {preview}...")
            print(f"  Saved: {filename}")

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n\nDone! {len(topics)} script(s) saved to {output_dir}/")


if __name__ == "__main__":
    main()
