"""All env vars, constants, and the 100-prompt bank (populated in Phase 2)."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
ARCHIVIST_CHAT_ID: int = int(os.environ["ARCHIVIST_CHAT_ID"])
MOM_CHAT_ID: int = int(os.environ["MOM_CHAT_ID"]) if os.environ.get("MOM_CHAT_ID") else 0
DAD_CHAT_ID: int = int(os.environ["DAD_CHAT_ID"]) if os.environ.get("DAD_CHAT_ID") else 0

# --- Anthropic ---
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

# --- Supabase ---
SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

# --- Google Drive ---
GOOGLE_DRIVE_FOLDER_ID: str = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
GOOGLE_SERVICE_ACCOUNT_JSON: str = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

# --- Schedule config ---
MOM_PROMPT_TIME: str = os.environ.get("MOM_PROMPT_TIME", "10:00")
DAD_PROMPT_TIME: str = os.environ.get("DAD_PROMPT_TIME", "10:00")
PROMPT_CADENCE_DAYS: int = int(os.environ.get("PROMPT_CADENCE_DAYS", "2"))
MOM_TIMEZONE: str = os.environ.get("MOM_TIMEZONE", "America/New_York")
DAD_TIMEZONE: str = os.environ.get("DAD_TIMEZONE", "America/New_York")

# --- Obsidian ---
OBSIDIAN_VAULT_NAME: str = os.environ.get("OBSIDIAN_VAULT_NAME", "Family Archive")

# --- Feature flags ---
DRY_RUN: bool = os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")

# --- Allowed senders ---
ALLOWED_CHAT_IDS: dict[str, int] = {
    "Mom": MOM_CHAT_ID,
    "Dad": DAD_CHAT_ID,
}

# --- Prompt bank (populated in Phase 2) ---
PROMPT_BANK: list[str] = [
    # Childhood
    "What's a memory from your childhood that still makes you smile?",
    "What did you love doing most after school when you were a kid?",
    "Tell me about your best friend growing up — what were they like?",
    "What was your favorite meal as a child, and who made it for you?",
    "What game or toy did you love more than anything when you were little?",
    "What was your bedroom like when you were growing up?",
    "What's something you got in trouble for as a kid that makes you laugh now?",
    "Tell me about the neighborhood you grew up in — what was it like?",
    "What was the first concert, movie, or big event you remember going to?",
    "What TV show or book were you completely obsessed with as a child?",
    "What did summers look like when you were growing up?",
    "Who was your favorite teacher, and what made them special?",
    "What did you want to be when you grew up, and did that ever change?",
    "Tell me about a time you did something adventurous or daring as a kid.",
    "What's the earliest memory you have — even just a small moment or feeling?",
    "What were birthdays like in your house when you were little?",
    "Did you have any pets growing up? Tell me about them.",
    "What's a smell or sound from your childhood that instantly takes you back?",
    "What was the most magical holiday memory you have from when you were young?",
    "Tell me about a time a friend made you feel really lucky to know them.",

    # Family history
    "What do you know about where our family originally came from?",
    "Tell me about your grandparents — what were they like as people?",
    "What's a tradition your family had when you were growing up that you loved?",
    "Did your family ever move? What was that like?",
    "Tell me about a family reunion or gathering you remember clearly.",
    "What's a story your parents told about their own childhood that stuck with you?",
    "What did your parents do for work, and did that shape who you became?",
    "Is there a family member who passed away that you'd love me to know about?",
    "What do you know about your grandparents' lives before they had kids?",
    "Did any part of your family come from another country? What do you know about that journey?",
    "What family traditions did you carry into your own life as an adult?",
    "Who in your family had the most interesting life story?",
    "What's a story about your parents that surprised you when you found it out?",
    "Tell me about a time a family member helped you through something hard.",
    "What was your family's relationship with food and cooking like?",

    # Advice & wisdom
    "What's the most important lesson your parents ever taught you?",
    "What advice would you give your younger self if you could go back?",
    "What's something you used to believe that you've completely changed your mind about?",
    "What does a good life look like to you — what really matters?",
    "Is there something you regret not doing sooner in your life?",
    "What did your parents get right in how they raised you?",
    "What's the hardest decision you ever made, and how did you make it?",
    "What do you wish someone had told you before you became a parent?",
    "What's a belief you hold deeply that not everyone agrees with?",
    "What does it mean to be a good person, in your eyes?",
    "What would you do differently if you had your twenties over again?",
    "What's the most important thing you've learned about relationships?",
    "What do you think makes a marriage or long partnership actually work?",
    "What did going through something hard teach you that nothing else could?",
    "If you could leave me just one piece of wisdom, what would it be?",

    # About the archivist (memories of me growing up)
    "What's a memory of me as a little kid that still makes you smile?",
    "What were you feeling the day I was born?",
    "What did you notice about me early on that you thought was special?",
    "Tell me about a moment when you felt really proud of me.",
    "What did you dream my life would look like when I was little?",
    "What was my personality like as a toddler?",
    "What's something I used to say or do as a kid that you still think about?",
    "Tell me about a time I scared you or gave you a real scare growing up.",
    "What did you most love doing together with me when I was young?",
    "What's a hope or wish you still carry for me today?",
    "What were the teenage years like from your side?",
    "Was there a time you felt like I really needed you, and you were there?",
    "What did you want to teach me about life more than anything?",
    "What surprised you most about who I turned out to be?",
    "Tell me about a moment when you saw me become my own person.",

    # Funny & embarrassing
    "What's the most embarrassing thing that ever happened to you that you can laugh about now?",
    "Tell me a story about a time something went hilariously wrong.",
    "What's the funniest thing a family member ever said or did?",
    "Did you ever do something as a teenager that your parents never found out about?",
    "What's a ridiculous fashion or style choice you made that you can't believe now?",
    "Tell me about the most chaotic family vacation you ever took.",
    "What's a time you laughed so hard you cried?",
    "What's the most awkward moment you ever survived?",
    "Tell me about a prank, joke, or mix-up that got completely out of hand.",
    "What's the silliest argument you remember having with someone you love?",

    # Work & career
    "What was your very first job, and what do you remember about it?",
    "Tell me about the work you're most proud of in your career.",
    "Who was the best boss you ever had, and what made them great?",
    "What was the hardest job or work experience you went through?",
    "What did your work teach you about people?",
    "Was there a moment in your career when everything clicked?",
    "What's a coworker or colleague you still think about?",
    "Tell me about a time at work when you had to do something really hard.",
    "What did you wish you'd known when you were starting out in your career?",
    "How did you decide what path to take in your work life?",
    "What's the proudest professional moment of your life?",
    "Tell me about a job or project that surprised you — something you didn't expect to love.",

    # Romance & marriage
    "How did you and Mom/Dad meet — tell me the whole story.",
    "What was your first date like?",
    "When did you know this was the person you wanted to spend your life with?",
    "What were the early years of your marriage like?",
    "What's something about your partner that you fell in love with slowly, over time?",
    "Tell me about a moment in your relationship that stands out as really special.",
    "What has made your relationship last?",
    "What did getting married feel like — the day itself?",
    "Tell me about a hard time in your relationship and how you got through it.",
    "What's something your partner does that still makes you smile after all these years?",
    "What did being in love teach you?",
    "What do you admire most about your partner?",

    # Deeper reflections
    "What period of your life do you look back on most fondly?",
    "What does home mean to you?",
    "Is there something you always wanted to do but never got around to?",
    "What's a place that holds a special meaning for you?",
    "Tell me about a book, song, or movie that changed how you see the world.",
    "What's something about yourself that took a long time to accept?",
    "What do you think about when you can't sleep?",
    "Is there something you want to make sure I know about you?",
    "What are you most grateful for when you look at your life?",
    "What do you want to be remembered for?",
]
