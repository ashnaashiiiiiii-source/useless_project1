import html
import json
import random
import time
from collections import Counter
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Search & Regret AI", page_icon="🤖", layout="wide")

DEFAULTS = {
	"history": [], "xp": 0, "score": 0, "answer": "", "reaction": "happy",
	"mode": "NORMAL", "streak": 0, "energy": 100, "achievements": [],
	"last_category": "🔎 General", "last_confidence": 0, "last_brain": "🧠 Fully Operational",
	"challenge": "", "challenge_done": False, "event": "", "random_question": "",
	"clear_armed": False, "battle_result": "", "roast": "",
}
for key, value in DEFAULTS.items():
	if key not in st.session_state:
		st.session_state[key] = value.copy() if isinstance(value, list) else value


# 100 playful local responses: ten categories with ten contextual lines each.
RESPONSES = {
	"💻 Programming": [
		"Your code isn't broken. Your relationship with semicolons is.", "The compiler read your code and chose professional silence.",
		"You are not debugging; you are negotiating with a machine.", "One more print statement and this becomes a documentary.",
		"Your IDE has seen enough and is considering a career change.", "A missing bracket has defeated modern engineering again.",
		"Your algorithm has entered its experimental jazz phase.", "The stack trace is longer than your attention span. Relatable.",
		"Python is not angry. It is simply specific about whitespace.", "C has no garbage collection because it expects character development.",
	],
	"📚 Academics": [
		"You opened the syllabus today? Bold strategy.", "You have converted a semester into a speedrun.",
		"The professor said important and you heard optional.", "Your notes are aesthetically pleasing and academically unemployed.",
		"The syllabus is not going to absorb itself through proximity.", "Your brain is buffering, but at least the panic has 5G.",
		"You are learning through vibes, which is statistically dramatic.", "The assignment is due soon, and suddenly every ceiling fan is fascinating.",
		"Mathematics saw your shortcuts and requested adult supervision.", "This is revision by hostage negotiation with tomorrow's deadline.",
	],
	"💼 Career": [
		"Your resume has more blank space than your knowledge of DSA.", "Your portfolio is currently a mood board with ambition.",
		"LinkedIn has detected ambition and is preparing motivational posts.", "Your resume says team player. Your group chat says otherwise.",
		"Career panic is ambition wearing a fake moustache.", "The interview is a polite boss battle.",
		"Your five-year plan is mostly five tabs and a dream.", "You are one focused weekend away from dangerous employability.",
		"The recruiter wants clarity. Your cover letter has plot twists.", "Your future is bright. Please add one finished project to it.",
	],
	"❤️ Life": [
		"Your life is not a bug. It is a feature-rich beta release.", "You are overthinking so efficiently it almost qualifies as cardio.",
		"Your feelings have opened seventeen tabs and none are responding.", "Love is suspiciously similar to debugging: tiny clues, huge consequences.",
		"Your social battery is at 3 percent and still accepting invitations.", "The meaning of life is currently in maintenance mode.",
		"Your personal growth arc needs fewer dramatic cliffhangers.", "A friendship problem cannot be solved by refreshing the chat.",
		"You are doing better than your midnight search history suggests.", "Your 3 AM conclusions require peer review.",
	],
	"🛠️ Tech & Devices": [
		"Your laptop becomes slow exactly when your deadline becomes fast.", "The Wi-Fi has entered witness protection.",
		"Your battery percentage is now a suspense thriller.", "Your laptop fan is composing an industrial album.",
		"You have 47 browser tabs and the confidence of a person with none.", "Restarting is not magic, but it has an excellent success rate.",
		"Your screen time report is a documentary nobody asked to watch.", "Your charger has become the most important relationship in the house.",
		"Technology has advanced dramatically. Your cable management has not.", "Your device is running on hope and a warm battery.",
	],
	"💰 Money": [
		"Your budget is less of a plan and more of a creative writing exercise.", "Your bank account just whispered, be serious.",
		"The sale is not saving money if you did not need the item.", "Your spending habits have more plot twists than your career plan.",
		"Your wallet has entered airplane mode.", "You checked your balance with the bravery of a horror protagonist.",
		"Every small purchase is harmless until they form a committee.", "Your budget has beautiful intentions and no enforcement mechanism.",
		"You are one unnecessary subscription from a board meeting.", "Your money is not gone. It has become experiences and delivery fees.",
	],
	"🎮 Gaming": [
		"You cannot defeat the boss because the boss has been studying too.", "Your gaming chair has more career stability than you do.",
		"One more match is how the sun becomes a rumor.", "Your skill issue has excellent graphics.",
		"The tutorial warned you. You skipped it with confidence.", "You are not addicted; you are conducting extremely long research.",
		"You played for five minutes and somehow unlocked tomorrow.", "Your strategy is chaos with a loading screen.",
		"Your gaming backlog is now a historical archive.", "Your reflexes are sharp. Your bedtime is not.",
	],
	"🤖 AI": [
		"You asked AI to solve a problem you have not understood yet. Humanity evolves.", "Artificial intelligence detected natural procrastination.",
		"You outsourced the thinking and kept the panic. Efficient.", "AI cannot attend college for you, but it can judge your tabs.",
		"The robot knows the answer, but please read the explanation this time.", "You are using advanced technology to avoid a very ordinary task.",
		"Machine learning is learning. You are currently machine waiting.", "The future is automated. Your assignment is still due tonight.",
		"You summoned an intelligence greater than your browser management.", "I am artificial intelligence; you are natural confusion. Together, unstoppable.",
	],
	"😴 Sleep & Procrastination": [
		"You had seven days. You chose the final 17 minutes. Respect.", "Sleep is free, restorative, and your least-used feature.",
		"Your productivity begins at 2 AM because daylight is too mainstream.", "You are not procrastinating; you are marinating in potential.",
		"Your alarm clock has filed a formal complaint.", "The task is still there, patiently becoming more dramatic.",
		"Your bed has a stronger argument than your to-do list.", "Tomorrow is receiving an unreasonable amount of responsibility.",
		"The deadline did not sneak up. You gave it stealth training.", "Productivity is calling. You are screening it.",
	],
	"🍔 Food & Social": [
		"You searched for dinner like the refrigerator had personally betrayed you.", "Your snack strategy has more planning than your career strategy.",
		"Social media has served you 40 opinions and zero vegetables.", "The group chat is not a replacement for sleep, but it is trying.",
		"You are one notification away from forgetting why you opened the app.", "Your food delivery history has entered the witness protection program.",
		"The algorithm knows your cravings better than your friends do.", "You called it a quick scroll and invented a new time zone.",
		"Your dinner is balanced: one food, three distractions.", "Please drink water before making another life decision.",
	],
	"🔎 General": [
		"I have processed your question. My circuits have chosen silence.", "That question arrived wearing sunglasses and no context.",
		"Deeply unnecessary, but somehow funny.", "Your curiosity is impressive. Your timing is a little haunted.",
		"This search has been referred to the Department of Common Sense.", "A bold question from a bold browser tab.",
		"Some questions seek knowledge. This one sought attention.", "No judgment. Actually, that is the entire product.",
		"The robot has consulted its tiny committee. The committee is confused.", "I admire the confidence with which you typed that.",
	],
}

RESPONSES["🔎 General"].extend([
	"Okay... that was a question. A very brave question.", "Why though? My circuits need answers too.",
	"No way. You really typed that and pressed search.", "Respectfully... please think for five seconds.",
	"I am confused, but I support the confidence.", "That search has main-character energy.",
	"You came for an answer and left me with questions.", "Not gonna lie, this is a funny problem.",
	"Okay, fair. But also... why?", "Your brain chose chaos today.",
	"I checked my notes. My notes checked out.", "This is not bad. It is just very you.",
	"Please do not make this search a daily habit.", "That question needs snacks and a nap.",
	"Big search. Small amount of planning.", "I am trying to help, but you are making it funny.",
	"That was unexpected. My eyebrows are now digital.", "Good question. Strange timing.",
	"You searched it, so now we all live with it.", "The answer is hiding behind your common sense.",
	"I heard you. I am still processing the drama.", "This is why robots need coffee.",
	"You could have asked a friend. You asked me. Respect.", "The search bar has seen worse, but not much worse.",
	"I have one thought: please be serious.", "That question walked in wearing confidence.",
	"I will answer, but I am judging the timing.", "Your curiosity is loud today.",
	"Okay... new plan: breathe first, search second.", "You are not wrong. You are just wonderfully random.",
	"This feels like a midnight decision.", "I have questions about your questions.",
	"No panic. Just a tiny bit of panic.", "You clicked search with great courage and no plan.",
	"That is one way to use the internet.", "The robot says: good luck, bro.",
	"Your search history just got more chaotic.", "I am done... but I will still help.",
	"Come on. We both know you knew this.", "This answer comes with zero refunds.",
	"You brought the question. I brought the judgment.", "Fine. Let us solve this tiny crisis.",
])

KEYWORDS = {
	"💻 Programming": ["python", "coding", "code", "debug", "javascript", "java", "c language", "c++", "algorithm", "loop", "array", "function", "html", "css", "program"],
	"📚 Academics": "exam exams study studying assignment homework math mathematics physics chemistry college class teacher semester professor".split(),
	"💼 Career": "job career resume internship interview linkedin salary company future portfolio dsa".split(),
	"❤️ Life": "life friend friendship relationship love sad happy motivation meaning social future".split(),
	"🛠️ Tech & Devices": "computer laptop phone internet wifi technology software battery device screen".split(),
	"💰 Money": "money budget bank finance rich saving spend spending cost wallet".split(),
	"🎮 Gaming": "game gaming gamer play level boss rank minecraft valorant controller".split(),
	"🤖 AI": "ai chatgpt robot artificial machine learning prompt neural algorithm".split(),
	"😴 Sleep & Procrastination": "sleep tired late procrastinate deadline tomorrow lazy productive midnight snooze".split(),
	"🍔 Food & Social": "food eat dinner snack restaurant social media instagram scroll notification chat".split(),
}
RANDOM_QUESTIONS = [
	"Can I become successful without waking up early?", "Why does Python hate me?", "Can I study an entire semester tonight?",
	"Why does my laptop become slow when I need it most?", "Do professors know when we do not study?", "Can AI attend college for me?",
	"Why do I suddenly become productive at 2 AM?", "How do I pass exams without studying?", "Why is debugging so painful?",
	"Can I get an internship with vibes and a dream?", "Is my phone smarter than me?", "Why do I forget everything before an exam?",
	"Can money solve my procrastination?", "Why does my code work only during demonstrations?", "What is the meaning of life?",
	"Should I sleep or start my assignment?", "Why do group projects create enemies?", "Can I put enthusiasm on my resume?",
	"Why is my Wi-Fi emotionally unavailable?", "How many tabs are too many tabs?", "Can I learn calculus through confidence?",
	"Why does everyone on LinkedIn look successful?", "Is one more game a bad idea?", "Can I become a millionaire by Friday?",
	"Why do deadlines improve my personality?", "Does my laptop need therapy?", "Why is C so angry?", "Can friendship survive no replies?",
	"Should I ask AI or read the instructions?", "Why is my battery always at 3 percent?", "Can a nap count as career planning?",
	"How do I look busy in a group project?", "Why does mathematics have letters now?", "Can I revise by staring at notes?",
	"Why is my resume judging me?", "Do gamers ever go outside?", "Can I solve everything with a restart?",
	"Why does my brain work only in the shower?", "Is coffee a personality?", "How do I stop overthinking?",
	"Can I finish this assignment before the deadline alarm?", "Why does technology betray me in public?", "Is procrastination a skill?",
	"Can I ask a robot a normal question?", "Why do internships ask for experience?", "Does sleep improve grades?", "Why am I like this?",
	"Can my search history become a documentary?", "What if the answer is just read the book?", "Why is my code judging me?",
	"Can I be productive tomorrow instead?", "Is the robot proud of me yet?", "Why is my food delivery bill a personality test?",
]
MODES = ["NORMAL", "BRUTAL", "EXISTENTIAL", "CHAOTIC", "SUPPORTIVE", "GENIUS"]


def detect_category(question):
	text = question.lower()
	for category, words in KEYWORDS.items():
		if any(word in text for word in words):
			return category
	return "🔎 General"


def calculate_regret_score(question, category, mode, history):
	text = question.lower()
	score = 22 + min(24, len(text) // 8)
	score += sum(8 for word in ("exam", "deadline", "procrast", "without studying", "midnight", "2 am") if word in text)
	score += min(18, 4 * sum(item["category"] == category for item in history))
	score += min(14, 7 * sum(item["question"].lower() == text for item in history))
	score += {"NORMAL": 0, "BRUTAL": 13, "EXISTENTIAL": 6, "CHAOTIC": random.randint(-5, 16), "SUPPORTIVE": -12, "GENIUS": 4}[mode]
	return max(0, min(100, score + random.randint(-6, 7)))


def get_level(score):
	if score <= 20: return "😇 MILDLY QUESTIONABLE"
	if score <= 40: return "🙂 WE ARE WATCHING"
	if score <= 60: return "😐 CONCERNING"
	if score <= 80: return "💀 SEVERE SKILL ISSUE"
	return "☠️ ACADEMIC EMERGENCY"


def get_robot_emotion(score, question, mode):
	text = question.lower()
	for word, emotion in (("sleep", "sleepy"), ("love", "suspicious"), ("ai", "thinking"), ("money", "excited"), ("exam", "shocked")):
		if word in text: return emotion
	if mode == "SUPPORTIVE" and score < 70: return "supportive"
	if score <= 20: return "happy"
	if score <= 35: return "suspicious"
	if score <= 50: return "laughing"
	if score <= 65: return "disappointed"
	if score <= 80: return "crying"
	if score <= 90: return "shocked"
	return "angry"


def get_brain_status(score):
	if score <= 20: return "🧠 Fully Operational"
	if score <= 40: return "🧠 Slightly Cooked"
	if score <= 60: return "🧠 Running on 2 Brain Cells"
	if score <= 80: return "🧠 Windows XP"
	if score <= 94: return "🧠 Critical: Please Restart"
	return "🧠 Brain Not Found"


def get_rank(xp):
	for threshold, name in [(50, "🥚 Search Rookie"), (100, "🔎 Curious Human"), (200, "🧠 Question Machine"), (350, "🤖 AI Survivor"), (500, "💀 Professional Overthinker"), (750, "☠️ Search Legend")]:
		if xp < threshold: return name
	return "👑 Supreme Search Goblin"


def get_robot_confidence(question, score, history):
	return max(12, min(99, 48 + min(28, len(question) // 5) + min(16, len(history) * 2) - abs(score - 50) // 4))


def get_emotional_opening(emotion):
	# Emotion is expressed by voice settings and animation. Do not add a
	# repeated spoken intro before the actual answer.
	return ""


def create_voice_script(answer, emotion):
	"""Make a short spoken line; emojis and dashboard language stay on screen only."""
	import re
	clean = re.sub(r"[^\x00-\x7F]+", "", answer)
	clean = clean.replace("Regret level: absolutely cooked.", "You are cooked.")
	clean = clean.replace("Search #", "Search number ")
	clean = re.sub(r"\s+", " ", clean).strip()
	words = clean.split()
	if len(words) > 24:
		clean = " ".join(words[:24]).rstrip(".,") + "."
	return clean


def get_question_specific_joke(question):
	"""Return a short, readable punchline for the actual words in the question."""
	text = question.lower()
	patterns = [
		(("pass", "exam", "without"), "Pass without studying? Hope is your whole study plan. 😭"),
		(("pass", "exam", "study"), "Pass the exam? Start studying before the exam starts studying you. 😭"),
		(("exam",), "Exam soon? Suddenly the syllabus looks like a horror movie."),
		(("study", "tonight"), "Study the whole semester tonight? Your brain has declined the meeting."),
		(("assignment",), "The assignment is due, and your motivation is hiding under the bed."),
		(("python", "error"), "Python gave you an error. It is not hate. It is very honest criticism."),
		(("python",), "Python is waiting for one tiny fix. It is probably whitespace. It is always whitespace."),
		(("debug",), "You fixed one bug and unlocked three bonus bugs. Limited-time offer!"),
		(("code", "work"), "Your code works everywhere except where you need to show it. Classic."),
		(("c language",), "C is not difficult. It just wants you to manage everything, including your feelings."),
		(("internship",), "Internship hunting: 10 tabs open, 0 applications submitted. Excellent strategy."),
		(("resume",), "Your resume says 'hard worker'. Your search history says 'last-minute worker'."),
		(("sleep",), "You need sleep, but your brain has scheduled a 2 AM overthinking session."),
		(("tired",), "Tired again? Your body is requesting an update and a charger."),
		(("procrast",), "Procrastination is just a deadline getting closer with better marketing."),
		(("money",), "Money question detected. Your wallet has left the chat."),
		(("salary",), "Salary talk? Your bank account just sat up and paid attention."),
		(("love",), "Love is confusing. At least code gives you an error message."),
		(("friend",), "Friendship problem? Please do not solve it by leaving everyone on read."),
		(("laptop",), "Your laptop is slow because it can sense the deadline."),
		(("phone",), "Your phone is not distracting you. You are both choosing this relationship."),
		(("ai",), "You asked AI to do the thinking. Bold move from natural intelligence."),
		(("food",), "Food search detected. Your stomach has better priorities than your calendar."),
		(("pizza",), "Pizza is not a balanced diet, but it is a balanced life choice."),
		(("game",), "One more game? Famous last words before sunrise."),
		(("gaming",), "Your rank is rising. Your sleep schedule is falling."),
		(("meaning of life",), "The meaning of life is probably in a tab you forgot to read."),
		(("how am i",), "You are asking a robot how you are. That is already a little concerning."),
	]
	for required_words, joke in patterns:
		if all(word in text for word in required_words):
			return joke
	return ""


def generate_ai_response(question, category, score, mode, history, streak, xp):
	options = RESPONSES[category]
	answer = get_question_specific_joke(question)
	specific = bool(answer)
	if not answer:
		answer = options[(sum(map(ord, question)) + len(history) * 31 + xp) % len(options)]
	context = []
	if not specific and not history: context.append("Welcome. You still have dignity.")
	elif not specific and len(history) == 4: context.append("Search #5 already? Google is becoming your roommate.")
	elif not specific and len(history) >= 9: context.append(f"Search #{len(history) + 1}. I live here now.")
	repeats = sum(item["category"] == category for item in history) + 1
	if not specific and category == "💻 Programming" and repeats >= 4: context.append(f"Programming search number {repeats}. Python lives here now.")
	if not specific and score >= 82: context.append("Regret level: absolutely cooked.")
	elif not specific and score <= 20: context.append("Surprisingly sensible. I am almost proud.")
	if not specific and streak >= 5: context.append(f"Search streak: {streak}. Please blink occasionally.")
	styles = {"BRUTAL": "I would explain it, but apparently we are starting from level zero.", "EXISTENTIAL": "But what is a search, if not a tiny confession to the void?", "CHAOTIC": random.choice(["The keyboard has declared a holiday.", "A nearby spreadsheet felt that.", "The robot has misplaced Tuesday."]), "SUPPORTIVE": "For the record: you can figure this out, one tiny step at a time.", "GENIUS": "My preliminary analysis is devastatingly nuanced."}
	if mode != "NORMAL" and not specific: context.append(styles[mode])
	# Keep the character line short and easy to read, not like a report.
	line = " ".join(context[:1] + [answer])
	words = line.split()
	return " ".join(words[:27]).rstrip(".,") + ("." if len(words) > 27 else "")


def update_achievements():
	history = st.session_state.history
	names = st.session_state.achievements
	def add(name):
		if name not in names: names.append(name)
	count = len(history)
	if count >= 1: add("🔎 First Search")
	if count >= 5: add("🔥 5 Searches")
	if count >= 10: add("🏆 Search Addict")
	if count >= 25: add("💀 No Life Detected")
	if count >= 20: add("🤖 Robot's Favorite")
	if any(x["score"] >= 90 for x in history): add("☠️ Academic Emergency")
	if any(x["score"] == 100 for x in history): add("💀 100% Regret")
	if any(x["score"] <= 20 for x in history): add("🧠 Brain Cell Survived")
	if any(x["category"] == "💻 Programming" for x in history): add("💻 Debugging Victim")
	if any(x["category"] == "📚 Academics" for x in history): add("📚 Academic Weapon")
	if any(x["category"] == "💼 Career" for x in history): add("💰 Internship Hunter")
	if any(x["category"] == "🤖 AI" for x in history): add("🤖 AI Dependent")
	if any(x["category"] == "😴 Sleep & Procrastination" for x in history): add("🌙 Midnight Thinker")
	if any(datetime.now().hour < 5 for _ in history): add("🌚 Midnight Searcher")
	if len({x["question"].lower() for x in history}) < count: add("🔁 Déjà Vu")
	if st.session_state.streak >= 10: add("🌱 Touch Grass")
	if st.session_state.mode == "CHAOTIC": add("🎲 Chaos Generator")
	if st.session_state.streak >= 25: add("👑 Search Legend")


def analyze_search_history(history):
	counts = Counter(x["category"] for x in history)
	averages = {cat: sum(x["score"] for x in history if x["category"] == cat) / count for cat, count in counts.items()}
	return counts, averages


def generate_history_roast(history):
	if not history: return "The robot has no evidence. Start searching so I can build a case."
	counts, _ = analyze_search_history(history)
	mix = ", ".join(f"{cat} {round(n / len(history) * 100)}%" for cat, n in counts.most_common())
	return f"Your search history tells me: {mix}. Diagnosis: you are simultaneously preparing for your future and avoiding it. Remarkable balance."


def generate_personality(history):
	if not history: return "🎲 THE CHAOS HUMAN", "No data yet. Beautifully mysterious.", "Just for fun — not a real psychological assessment."
	counts, averages = analyze_search_history(history)
	cat = counts.most_common(1)[0][0]
	labels = {"💻 Programming": ("💻 THE CODE SURVIVOR", "You debug with courage and suspicious tabs."), "📚 Academics": ("📚 THE LAST-MINUTE SCHOLAR", "Your syllabus is a recurring character."), "💼 Career": ("💼 THE CAREER PANICKER", "Your future has a resume and an urgent notification."), "🤖 AI": ("🤖 THE AI DEPENDENT", "You outsourced the question and retained the overthinking."), "😴 Sleep & Procrastination": ("🌙 THE MIDNIGHT THINKER", "Your best ideas arrive after reasonable bedtime.")}
	name, observation = labels.get(cat, ("🧠 THE OVERTHINKER", "Your brain has opened several side quests."))
	return name, observation, f"Just for fun — not a real psychological assessment. {round(counts[cat] / len(history) * 100)}% {cat}; average regret {averages[cat]:.1f}."


def generate_daily_challenge():
	return random.choice(["Ask the robot something you already know.", "Ask the dumbest question possible.", "Try to get a regret score below 20.", "Make the robot angry.", "Reach a 5-search streak.", "Search a topic outside your comfort zone."])


def generate_report():
	history = st.session_state.history
	scores = [x["score"] for x in history]
	counts = Counter(x["category"] for x in history)
	lines = ["SEARCH & REGRET AI - REGRET REPORT", "=" * 42, f"Generated: {datetime.now():%Y-%m-%d %H:%M}", f"Search count: {len(history)}", f"XP: {st.session_state.xp}", f"Rank: {get_rank(st.session_state.xp)}", f"Average score: {sum(scores) / len(scores):.1f}" if scores else "Average score: 0", f"Highest score: {max(scores, default=0)}", f"Lowest score: {min(scores, default=0)}", "", "ACHIEVEMENTS", *st.session_state.achievements, "", "CATEGORIES"]
	lines += [f"{cat}: {n}" for cat, n in counts.items()] + ["", "SEARCH HISTORY"]
	lines += [f"{i}. [{x['score']}/100] {x['category']} - {x['question']} | {x['answer']}" for i, x in enumerate(history, 1)]
	return "\n".join(lines)


def process_search(question):
	category = detect_category(question)
	score = calculate_regret_score(question, category, st.session_state.mode, st.session_state.history)
	emotion = get_robot_emotion(score, question, st.session_state.mode)
	answer = generate_ai_response(question, category, score, st.session_state.mode, st.session_state.history, st.session_state.streak + 1, st.session_state.xp)
	earned = max(8, 112 - score) + (5 if st.session_state.mode == "SUPPORTIVE" else 0)
	st.session_state.xp += earned
	st.session_state.streak += 1
	st.session_state.score = score
	st.session_state.answer = answer
	st.session_state.reaction = emotion
	st.session_state.last_category = category
	st.session_state.last_confidence = get_robot_confidence(question, score, st.session_state.history)
	st.session_state.last_brain = get_brain_status(score)
	st.session_state.energy = max(0, st.session_state.energy - random.randint(3, 8))
	st.session_state.event = random.choice(["", "", "", "🚨 ROBOT PANIC: The robot has seen enough.", "🧠 BRAIN CELL DETECTED: One brain cell remains operational.", "📡 GOOGLE SIGNAL LOST: Touch grass recommended.", "☠️ ACADEMIC DAMAGE: Irreversible nonsense detected.", "🤖 ROBOT OVERHEATING: Too much nonsense detected."])
	st.session_state.history.append({"question": question, "answer": answer, "score": score, "level": get_level(score), "reaction": emotion, "category": category, "mode": st.session_state.mode, "xp": earned, "time": datetime.now().strftime("%H:%M")})
	if not st.session_state.challenge: st.session_state.challenge = generate_daily_challenge()
	if ("5-search" in st.session_state.challenge and st.session_state.streak >= 5) or ("below 20" in st.session_state.challenge and score < 20) or ("angry" in st.session_state.challenge and emotion == "angry"): st.session_state.challenge_done = True
	update_achievements()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap');
.stApp{background:radial-gradient(circle at 12% 0%,#17395c,#07101e 42%,#03060c);color:#eaf4ff;font-family:'Space Grotesk',sans-serif}.stApp:before{content:'';position:fixed;inset:0;pointer-events:none;opacity:.1;background-image:linear-gradient(#4de8ff22 1px,transparent 1px),linear-gradient(90deg,#4de8ff22 1px,transparent 1px);background-size:42px 42px}.hero{padding:25px 0}.hero h1{font-size:clamp(2rem,6vw,4.5rem);line-height:.9;margin:7px 0;color:#fff;text-shadow:0 0 28px #4de8ff55}.hero h1 span{color:#4de8ff}.eyebrow,.label{font:700 11px 'Space Mono',monospace;letter-spacing:2px;color:#ff5ea8}.subtitle{color:#91a8c5;font-family:'Space Mono',monospace}.panel,.verdict,.memory,.stat{background:#0d172bd0;border:1px solid #4de8ff33;border-radius:12px;padding:17px;box-shadow:0 15px 55px #0005}.stat{text-align:center}.stat b{display:block;color:#4de8ff;font:700 25px 'Space Mono',monospace}.stat small{color:#91a8c5;font-family:'Space Mono',monospace}.verdict{border-color:#ff5ea877;background:linear-gradient(135deg,#281532dd,#0d1930dd)}.verdict .score{font:700 38px 'Space Mono',monospace;color:#ff5ea8}.memory{color:#c9dbf2}.memory b{color:#b7f34a;font-family:'Space Mono',monospace}.event{padding:12px;border:1px solid #ff5ea8aa;border-radius:8px;background:#64154a55;color:#ffd9eb}.achievement{padding:9px;margin:5px 0;border-left:3px solid #b7f34a;background:#b7f34a0d}.stButton>button{border-radius:7px!important;border:1px solid #4de8ff88!important;font-family:'Space Mono',monospace!important}.stButton>button:hover{box-shadow:0 0 17px #4de8ff55;transform:translateY(-2px)}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="hero"><div class="eyebrow">// UNNECESSARILY ADVANCED JUDGEMENT SYSTEM</div><h1>SEARCH <span>&</span> REGRET AI</h1><div class="subtitle">You search it. We judge you. 🤖 <b style="color:#b7f34a">● ONLINE</b></div></div>', unsafe_allow_html=True)
cols = st.columns(4)
for col, value, label in zip(cols, [len(st.session_state.history), st.session_state.score, st.session_state.xp, st.session_state.streak], ["SEARCHES", "LAST REGRET", "TOTAL XP", "🔥 STREAK"]):
	with col: st.markdown(f'<div class="stat"><b>{value}</b><small>{label}</small></div>', unsafe_allow_html=True)

left, right = st.columns([1, 2], gap="large")
with left:
	st.markdown('<div class="label">🤖 ROBOT CONTROL</div>', unsafe_allow_html=True)
	st.session_state.mode = st.selectbox("Personality", MODES, index=MODES.index(st.session_state.mode))
	st.markdown(f'<div class="memory"><b>STATUS: ONLINE 🟢</b><br>MOOD: {html.escape(st.session_state.reaction.upper())}<br>⚡ ENERGY: {st.session_state.energy}%<br>💀 JUDGEMENT: {st.session_state.score}%</div>', unsafe_allow_html=True)
	if st.button("🎲 RANDOM MOOD", use_container_width=True):
		st.session_state.reaction = random.choice(["happy", "laughing", "suspicious", "excited", "thinking", "evil"])
		st.rerun()
	st.markdown('<div class="label">🎯 DAILY CHALLENGE</div>', unsafe_allow_html=True)
	if not st.session_state.challenge: st.session_state.challenge = generate_daily_challenge()
	st.markdown(f"{'✅' if st.session_state.challenge_done else '⬡'} {html.escape(st.session_state.challenge)}")
	if st.session_state.energy < 20: st.warning("Please stop searching. My circuits need therapy.")
	elif st.session_state.energy < 45: st.caption("I'm tired of judging you.")
with right:
	st.markdown('<div class="label">🔎 SEARCH CONSOLE</div>', unsafe_allow_html=True)
	st.session_state.demo_mode = st.toggle("🎤 HACKATHON DEMO MODE", value=st.session_state.get("demo_mode", False))
	if st.session_state.demo_mode and not st.session_state.random_question: st.session_state.random_question = random.choice(["How do I pass without studying?", "Why does my code not work?", "Can I get an internship?", "What is the meaning of life?"])
	question = st.text_input("Question", value=st.session_state.random_question, placeholder="Ask something you already know...", label_visibility="collapsed")
	search_col, random_col = st.columns([3, 1])
	with search_col: search = st.button("🔍 SEARCH & ACCEPT CONSEQUENCES", type="primary", use_container_width=True)
	with random_col: random_button = st.button("🎲 RANDOM", use_container_width=True)
	if random_button: st.session_state.random_question = random.choice(RANDOM_QUESTIONS); st.rerun()
	if search:
		if not question.strip(): st.warning("Please enter something first. The robot cannot judge an empty void.")
		else:
			with st.spinner("Scanning question... consulting robot brain... calculating regret..."):
				time.sleep(.15); process_search(question.strip())
			st.rerun()
	if st.session_state.event: st.markdown(f'<div class="event">{html.escape(st.session_state.event)}</div>', unsafe_allow_html=True)


# The iframe receives the current answer and automatically attempts to speak it.
# Browser autoplay policies may require the visible SPEAK button on first use.
emotion = st.session_state.reaction
emotion_face = {"happy":"😊", "laughing":"😂", "shocked":"😱", "angry":"😡", "crying":"😭", "sleepy":"😴", "suspicious":"🤨", "excited":"🤩", "disappointed":"😐", "thinking":"🤔", "supportive":"😌", "evil":"😈"}.get(emotion, "🤖")
voice_config = {"happy":(1.08,1.25,1),"laughing":(1.18,1.45,1),"shocked":(1.22,1.55,1),"angry":(1.14,.72,1),"crying":(.82,.9,.82),"sleepy":(.7,.7,.78),"suspicious":(.84,.84,1),"excited":(1.25,1.38,1),"disappointed":(.84,.72,.9),"thinking":(.8,1,.9),"supportive":(.84,1.05,.95),"evil":(1.08,.62,1)}.get(emotion,(1,1,1))
robot_color = {"angry":"#ff4d6d","crying":"#4da6ff","shocked":"#ffe66d","sleepy":"#9aa6ff","supportive":"#ffb86b"}.get(emotion,"#4de8ff")
voice_text = create_voice_script(st.session_state.answer or "I am online. Feed me a questionable search.", emotion)
robot_data = json.dumps(voice_text)
components.html(f"""
<style>body{{margin:0;background:transparent;font-family:Arial;color:#eaf4ff}}.box{{height:400px;display:grid;place-items:center;position:relative}}.robot{{width:210px;height:285px;position:relative;animation:float 2.5s infinite ease-in-out}}.head{{position:absolute;left:15px;top:45px;width:180px;height:125px;border:5px solid #71829c;border-radius:32px;background:linear-gradient(145deg,#f2f7ff,#8594ac);box-shadow:0 0 35px {robot_color}}}.face{{position:absolute;inset:18px 20px;background:#030817;border:3px solid #253651;border-radius:22px}}.eye{{position:absolute;top:24px;width:29px;height:29px;border-radius:50%;background:{robot_color};box-shadow:0 0 15px {robot_color};animation:blink 4s infinite}}.l{{left:18px}}.r{{right:18px}}.pupil{{width:9px;height:9px;border-radius:50%;background:#020617;margin:10px}}.mouth{{position:absolute;bottom:6px;left:0;right:0;text-align:center;font-size:20px}}.talking .mouth{{animation:talk .15s infinite alternate}}.antenna{{position:absolute;left:103px;top:5px;width:7px;height:42px;background:#a8b6ca}}.bulb{{position:absolute;left:-8px;top:-11px;width:23px;height:23px;border-radius:50%;background:{robot_color};box-shadow:0 0 25px {robot_color}}}.body{{position:absolute;left:52px;top:175px;width:110px;height:100px;border:4px solid #556781;border-radius:22px;background:linear-gradient(145deg,#c8d4e4,#63748d)}}.chest{{margin:21px auto;width:48px;height:48px;border-radius:11px;border:3px solid {robot_color};color:{robot_color};display:grid;place-items:center;background:#030817;font:bold 14px monospace}}.arm{{position:absolute;top:195px;width:68px;height:17px;border:4px solid #556781;border-radius:15px;background:#899bb3}}.al{{left:-5px;transform:rotate(25deg)}}.ar{{right:-5px;transform:rotate(-25deg)}}.controls{{position:absolute;bottom:4px;display:flex;gap:6px;flex-wrap:wrap;justify-content:center}}button{{background:#0b172a;color:#eaf4ff;border:1px solid {robot_color};border-radius:6px;padding:8px;cursor:pointer;font-weight:bold}}@keyframes float{{50%{{transform:translateY(-14px)}}}}@keyframes blink{{48%{{transform:scaleY(1)}}50%{{transform:scaleY(.1)}}}}@keyframes talk{{to{{transform:scaleY(1.6)}}}}</style>
<style>.robot.laughing{{animation:laugh .35s infinite alternate}}.robot.angry{{animation:shake .12s infinite}}.robot.shocked,.robot.excited{{animation:jump .45s infinite alternate}}.robot.crying,.robot.sleepy{{animation:sad 2.5s infinite ease-in-out}}@keyframes laugh{{to{{transform:rotate(4deg) translateY(-10px)}}}}@keyframes shake{{50%{{transform:translateX(8px)}}}}@keyframes jump{{to{{transform:translateY(-23px) scale(1.06)}}}}@keyframes sad{{50%{{transform:translateY(8px)}}}}</style>
<div class="box"><div class="robot {emotion}" id="robot"><div class="antenna"><div class="bulb"></div></div><div class="head"><div class="face"><div class="eye l"><div class="pupil"></div></div><div class="eye r"><div class="pupil"></div></div><div class="mouth">{emotion_face}</div></div></div><div class="arm al"></div><div class="arm ar"></div><div class="body"><div class="chest">AI</div></div></div><div class="controls"><button onclick="speak()">🔊 SPEAK</button><button onclick="beep()">🔔 BEEP</button><button onclick="stopSpeech()">⏹ STOP</button><label style="font-size:12px">🎚️ <input id="speed" type="range" min="0.7" max="1.4" step="0.05" value="1"></label></div></div>
<script>const text={robot_data};const robot=document.getElementById('robot');const baseRate={voice_config[0]};const pitch={voice_config[1]};const volume={voice_config[2]};let voices=[];function loadVoices(){{voices=speechSynthesis.getVoices();}}function pickVoice(){{const preferred=/en-IN|en-US|en-GB/i;const natural=/natural|google|microsoft|samantha|neural/i;return voices.find(v=>preferred.test(v.lang)&&natural.test(v.name))||voices.find(v=>preferred.test(v.lang))||voices[0]}}function spokenText(value){{return value.replace(/\\.\\.\\./g,' ... ').replace(/!/g,'! ').replace(/\\?/g,'? ').replace(/\\s+/g,' ').trim()}}function speak(){{if(!('speechSynthesis'in window))return;stopSpeech();if(robot.classList.contains('laughing'))beep();const u=new SpeechSynthesisUtterance(spokenText(text));u.rate=baseRate*Number(document.getElementById('speed').value);u.pitch=pitch;u.volume=volume;const voice=pickVoice();if(voice)u.voice=voice;robot.classList.add('talking');u.onend=()=>robot.classList.remove('talking');u.onerror=()=>robot.classList.remove('talking');speechSynthesis.speak(u)}}function stopSpeech(){{if('speechSynthesis'in window)speechSynthesis.cancel();robot.classList.remove('talking')}}function beep(){{const C=window.AudioContext||window.webkitAudioContext;if(!C)return;const c=new C(),o=c.createOscillator(),g=c.createGain();o.frequency.value=robot.classList.contains('angry')?220:robot.classList.contains('shocked')?760:520;o.connect(g);g.connect(c.destination);g.gain.setValueAtTime(.001,c.currentTime);g.gain.exponentialRampToValueAtTime(.14,c.currentTime+.03);g.gain.exponentialRampToValueAtTime(.001,c.currentTime+.17);o.start();o.stop(c.currentTime+.18)}}loadVoices();if('speechSynthesis'in window)speechSynthesis.onvoiceschanged=loadVoices;</script>
<script>
const emotionRate = {voice_config[0]};
const emotionPitch = {voice_config[1]};
const emotionVolume = {voice_config[2]};
function speak() {{
	if (!("speechSynthesis" in window)) return;
	stopSpeech();
	if (robot.classList.contains("laughing")) beep();
	const parts = spokenText(text).split(/(?<=[.!?])[ ]+/).filter(Boolean);
	let index = 0;
	const sayNext = () => {{
		if (index >= parts.length) {{ robot.classList.remove("talking"); return; }}
		const line = parts[index++];
		const utterance = new SpeechSynthesisUtterance(line);
		const speedValue = Number(document.getElementById("speed").value);
		const pitchWobble = robot.classList.contains("shocked") ? 0.12 : robot.classList.contains("laughing") ? 0.08 : 0.035;
		utterance.rate = emotionRate * speedValue * (index % 2 ? 1 : 0.94);
		utterance.pitch = Math.max(0.35, Math.min(2, emotionPitch + (index % 2 ? pitchWobble : -pitchWobble)));
		utterance.volume = emotionVolume;
		const voice = pickVoice();
		if (voice) utterance.voice = voice;
		robot.classList.add("talking");
		utterance.onend = () => setTimeout(sayNext, robot.classList.contains("shocked") ? 280 : 110);
		utterance.onerror = () => robot.classList.remove("talking");
		speechSynthesis.speak(utterance);
	}};
	sayNext();
}}
</script>
""", height=410, scrolling=False)


if st.session_state.answer:
	score = st.session_state.score
	st.markdown(f'<div class="verdict"><div class="label">🤖 FINAL VERDICT</div><div class="score">💀 REGRET SCORE: {score}/100</div><b>{get_level(score)}</b><p><b>{html.escape(st.session_state.last_brain)}</b><br>🤖 {html.escape(st.session_state.answer)}<br>🎯 Recommended action: {"Open a textbook immediately." if score > 60 else "Proceed with cautious confidence."}</p><small>🤖 Robot Confidence: {st.session_state.last_confidence}% · Mode: {st.session_state.mode}</small></div>', unsafe_allow_html=True)
	st.progress(score / 100)
st.markdown(f'<div class="memory"><b>🧠 ROBOT MEMORY</b><br>{("You have searched about " + html.escape(st.session_state.last_category) + " " + str(sum(x["category"] == st.session_state.last_category for x in st.session_state.history)) + " time(s)." if st.session_state.history else "The robot remembers nothing yet, which is honestly peaceful.")}</div>', unsafe_allow_html=True)


st.markdown("### ⚔️ SEARCH BATTLE")
ba, bb = st.columns(2)
with ba: question_a = st.text_input("Question A", placeholder="How do I study for exams?")
with bb: question_b = st.text_input("Question B", placeholder="Can I pass without studying?")
if st.button("⚔️ START SEARCH BATTLE", use_container_width=True):
	if question_a.strip() and question_b.strip():
		a = calculate_regret_score(question_a, detect_category(question_a), st.session_state.mode, st.session_state.history)
		b = calculate_regret_score(question_b, detect_category(question_b), st.session_state.mode, st.session_state.history)
		winner = "Question A" if a < b else "Question B" if b < a else "A draw: both questions need supervision."
		st.session_state.battle_result = f"🏆 WINNER: {winner} | Question A: {a}/100 | Question B: {b}/100"
	else: st.warning("Both questions need to enter the arena.")
if st.session_state.battle_result: st.success(st.session_state.battle_result)

roast_col, report_col = st.columns(2)
with roast_col:
	if st.button("🔥 ROAST MY HISTORY", use_container_width=True): st.session_state.roast = generate_history_roast(st.session_state.history)
with report_col: st.download_button("📄 GENERATE MY REGRET REPORT", generate_report(), "search_regret_report.txt", "text/plain", use_container_width=True)
if st.session_state.roast: st.warning(st.session_state.roast)


if st.session_state.history:
	st.markdown("### 📊 AI DASHBOARD")
	scores = [x["score"] for x in st.session_state.history]
	counts, averages = analyze_search_history(st.session_state.history)
	most = counts.most_common(1)[0][0]
	most_regret = max(averages, key=averages.get)
	least_regret = min(averages, key=averages.get)
	stats = [(f"{sum(scores) / len(scores):.1f}", "AVERAGE"), (max(scores), "HIGHEST"), (min(scores), "LOWEST"), (most, "MOST SEARCHED")]
	cols = st.columns(4)
	for col, (value, label) in zip(cols, stats):
		with col: st.markdown(f'<div class="stat"><b>{html.escape(str(value))}</b><small>{label}</small></div>', unsafe_allow_html=True)
	st.caption(f"Most regrettable: {most_regret} · Least regrettable: {least_regret} · Total XP: {st.session_state.xp} · Rank: {get_rank(st.session_state.xp)}")
	width, height, pad = 760, 260, 40
	points = [(pad + (width - 2 * pad) * i / max(1, len(scores) - 1), 20 + (height - 55) * (1 - score / 100)) for i, score in enumerate(scores)]
	polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
	circles = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#ff5ea8"><title>Search {i + 1}: {scores[i]}</title></circle>' for i, (x, y) in enumerate(points))
	grid = "".join(f'<line x1="{pad}" y1="{20 + (height - 55) * (1-v/100):.1f}" x2="{width-pad}" y2="{20 + (height - 55) * (1-v/100):.1f}" stroke="#243957"/><text x="5" y="{24 + (height - 55) * (1-v/100):.1f}" fill="#91a8c5" font-size="11">{v}</text>' for v in (0, 25, 50, 75, 100))
	st.markdown(f'<div class="panel"><div class="label">📈 JUDGEMENT HISTORY</div><svg viewBox="0 0 {width} {height}" width="100%" height="{height}">{grid}<polyline points="{polyline}" fill="none" stroke="#4de8ff" stroke-width="3"/>{circles}</svg></div>', unsafe_allow_html=True)
	st.markdown('<div class="label">🧠 CATEGORY DISTRIBUTION</div>', unsafe_allow_html=True)
	for category, count in counts.most_common():
		st.write(f"**{category}** — {count} search(es)")
		st.progress(count / len(st.session_state.history))
	name, observation, disclaimer = generate_personality(st.session_state.history)
	st.info(f"{name}\n\n{observation}\n\n{disclaimer}")


st.markdown("### 🏆 ACHIEVEMENTS")
if st.session_state.achievements:
	ach_cols = st.columns(3)
	for i, achievement in enumerate(st.session_state.achievements):
		with ach_cols[i % 3]: st.markdown(f'<div class="achievement">{html.escape(achievement)}</div>', unsafe_allow_html=True)
else: st.info("No achievements yet. Start searching to make the robot regret going online.")

st.markdown("### 📜 SEARCH HISTORY")
if not st.session_state.history: st.info("No searches yet. The robot is innocent. 😇")
else:
	for item in reversed(st.session_state.history):
		with st.expander(f"🔎 {item['question']}"):
			st.write(f"🤖 {item['answer']}")
			st.caption(f"{item['score']}/100 · {item['category']} · {item['mode']} · +{item['xp']} XP · {item['time']}")

if st.session_state.history:
	st.markdown("### 🧹 RESET SYSTEM")
	st.session_state.clear_armed = st.checkbox("I understand this resets history, XP, streak, achievements, energy, memory, and statistics.", value=st.session_state.clear_armed)
	if st.button("🗑️ CLEAR ALL DATA", disabled=not st.session_state.clear_armed, use_container_width=True):
		for key, value in DEFAULTS.items(): st.session_state[key] = value.copy() if isinstance(value, list) else value
		st.rerun()

st.markdown('<div style="text-align:center;color:#91a8c5;padding:30px;font:12px Space Mono,monospace">SEARCH & REGRET AI · An unnecessarily advanced AI system dedicated to judging unnecessary searches.</div>', unsafe_allow_html=True)