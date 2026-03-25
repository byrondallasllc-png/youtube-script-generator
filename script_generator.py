#!/usr/bin/env python3
"""
YouTube Script Generator — Finance, Motivation, Horror channels
Usage: python script_generator.py
"""

import anthropic
import sys

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
4. CTA (20 seconds): Brief, don't break the atmosphere. Something like "More stories in the description. Subscribe if you made it this far."

Tone: Tense, atmospheric, matter-of-fact. The scariest stories are told like they actually happened.
Format: Label each section. Write in first or third person — be consistent. No filler, no fluff.
Length: ~1000–1300 words total."""
}

def generate_script(channel: str, topic: str) -> str:
    system_prompt = CHANNEL_PROMPTS[channel]

    print(f"\n Generating {channel.upper()} script for: \"{topic}\"\n")
    print("=" * 60)

    full_script = ""

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Write the script for this topic: {topic}"
            }
        ]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_script += text

    print("\n" + "=" * 60)
    return full_script


def save_script(channel: str, topic: str, script: str):
    safe_topic = topic.lower().replace(" ", "_").replace("/", "-")[:40]
    filename = f"{channel}_{safe_topic}.txt"

    with open(filename, "w") as f:
        f.write(f"CHANNEL: {channel.upper()}\n")
        f.write(f"TOPIC: {topic}\n")
        f.write("=" * 60 + "\n\n")
        f.write(script)

    print(f"\n Script saved to: {filename}")
    return filename


def main():
    print("\n YOUTUBE SCRIPT GENERATOR")
    print(" Finance | Motivation | Horror\n")

    # Select channel
    print("Select channel:")
    print("  1. Finance")
    print("  2. Motivation")
    print("  3. Horror")

    while True:
        choice = input("\nEnter 1, 2, or 3: ").strip()
        channel_map = {"1": "finance", "2": "motivation", "3": "horror"}
        if choice in channel_map:
            channel = channel_map[choice]
            break
        print("Invalid choice. Enter 1, 2, or 3.")

    # Enter topic
    topic = input(f"\nEnter topic for {channel.upper()} script: ").strip()
    if not topic:
        print("No topic entered. Exiting.")
        sys.exit(1)

    # Generate
    script = generate_script(channel, topic)

    # Save
    save = input("\n\nSave script to file? (y/n): ").strip().lower()
    if save == "y":
        save_script(channel, topic, script)


if __name__ == "__main__":
    main()
