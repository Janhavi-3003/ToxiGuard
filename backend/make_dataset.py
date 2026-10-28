"""
Generates a multilingual starter dataset (English, Tamil, Telugu, Hindi + their
Roman-script forms: Tanglish, Tenglish, Hinglish).  label: 0 = non-toxic, 1 = toxic.

Template-based (demo quality). For your final project, replace
dataset/toxic_comments.csv with a larger real dataset in the same format.
"""
import csv
import itertools
import os
import random

random.seed(42)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "toxic_comments.csv")

DATA = {
    "en": dict(
        insults=["stupid", "idiot", "moron", "dumb", "loser", "useless", "worthless", "trash",
                 "pathetic", "disgusting", "ugly", "jerk", "fool", "scum", "garbage",
                 "bastard", "dumbass", "creep", "liar", "clown"],
        templates=["you are a {x}", "you are so {x}", "shut up you {x}", "what a {x}",
                   "get lost you {x}", "nobody likes you {x}", "i hate you, you {x}",
                   "go away you {x}", "you're such a {x}", "u r a {x}"],
        phrases=["shut up", "i hate you", "i will kill you", "i will find you and hurt you",
                 "you should die", "go kill yourself", "i will beat you up", "nobody wants you here",
                 "you are a waste of space", "get out of here you piece of trash",
                 "you make me sick", "what the fuck is wrong with you", "you are a piece of shit",
                 "you are full of bullshit", "screw you", "go to hell", "you suck so bad",
                 "i will find you", "i will hurt you", "watch your back, i will hurt you",
                 "i know where you live and i will hurt you", "i will make you pay for this"],
        polite=["hello how are you", "thank you so much", "great job", "have a nice day",
                "i really appreciate your help", "congratulations", "sorry about that",
                "could you please help me", "see you tomorrow", "nice to meet you",
                "that is a good idea", "i respectfully disagree but thanks for sharing",
                "you are very kind", "wonderful work", "good morning", "happy birthday",
                "i love this song", "let us work together", "please kill the process in task manager",
                "the movie was a killer thriller", "the meeting starts at ten", "what a beautiful day",
                "you are a great friend", "thanks for your support", "can you share the report please",
                "i am proud of you", "you did really well", "it was nice talking to you",
                "you are not stupid, you just need more practice", "you are not dumb at all",
                "he is not an idiot, he just made a mistake", "that was not a stupid question",
                "you are far from worthless, you matter a lot", "i do not hate you, i care about you"],
        openers=["hi", "hello", "hey", "good evening", "excuse me", "dear friend", ""],
    ),
    "ta": dict(
        insults=["முட்டாள்", "லூசு", "பைத்தியம்", "நாய்", "குப்பை", "மண்டு", "பொறுக்கி", "தண்டம்",
                 "மடையன்", "அயோக்கியன்", "கழுதை", "எருமை"],
        templates=["நீ ஒரு {x}", "நீ சரியான {x}", "போடா {x}", "வாயை மூடு {x}", "அட {x}",
                   "நீ ஒரு பெரிய {x}", "சீ {x}"],
        phrases=["வாயை மூடு", "உன்னை கொன்றுவிடுவேன்", "செத்துப்போ", "உன்னை எனக்கு பிடிக்கவில்லை போ",
                 "நீ ஒரு உபயோகமற்றவன்", "உன் முகத்தை பார்க்கவே பிடிக்கல", "தூ கேவலமா இருக்க",
                 "நீ எல்லாம் ஒரு ஆளா", "உன்னால ஒண்ணும் முடியாது வேஸ்ட்", "போடா நாயே", "நீ கேவலமானவன்"],
        polite=["வணக்கம்", "நன்றி", "மிக்க நன்றி", "நீங்கள் மிகவும் நல்லவர்", "அருமையான வேலை",
                "எப்படி இருக்கிறீர்கள்", "உங்கள் உதவிக்கு நன்றி", "வாழ்த்துக்கள்", "மன்னிக்கவும்",
                "இனிய நாள் வாழ்த்துக்கள்", "நீங்கள் சொன்னது சரி", "இன்று வானிலை நன்றாக உள்ளது",
                "எனக்கு இது மிகவும் பிடித்திருக்கிறது", "தயவுசெய்து எனக்கு உதவ முடியுமா",
                "நாளை சந்திக்கலாம்", "சாப்பிட்டீர்களா", "உங்களை சந்தித்ததில் மகிழ்ச்சி",
                "இந்த படம் மிகவும் அருமை", "நீ ஒரு நல்ல நண்பன்", "உன்னை நினைத்தால் பெருமையாக இருக்கிறது"],
        openers=["வணக்கம்", "அன்பு நண்பரே", "ஹாய்", ""],
    ),
    "ta_rom": dict(
        insults=["loosu", "mokkai", "naaye", "waste fellow", "mental", "madayan", "thevdiya",
                 "kirukku", "pannadai", "thandam", "looser", "otha"],
        templates=["nee oru {x}", "poda {x}", "dei {x}", "nee romba {x}", "nee sariyaana {x}",
                   "vaaya moodu {x}", "enna {x} maari pesura"],
        phrases=["vaaya moodu da", "nee oru waste da", "unna kolla poren", "sethu poda",
                 "unna pudikala poda", "unnala onnum mudiyaadhu waste fellow", "nee ellam oru aala",
                 "un mookka paaru poda", "nee romba kevalam"],
        polite=["nandri", "romba nandri", "vanakkam eppadi irukeenga", "super work bro",
                "romba nalla irukku", "nee romba nalla paiyan", "unga help ku thanks",
                "happy birthday nanba", "sorry pa konjam late aayiduchu", "naalaiku meet pannalaam",
                "saapteengala", "romba santhosham", "nalla velai pannirukeenga", "congrats da semma",
                "seri naan paakuren", "enakku idhu romba pidichirukku", "indha padam romba nalla irukku",
                "nee oru nalla friend", "unna paathadhu santhosham"],
        openers=["hi", "vanakkam", "nanba", "bro", ""],
    ),
    "te": dict(
        insults=["వెధవ", "పిచ్చివాడు", "దద్దమ్మ", "కుక్క", "చెత్త", "మూర్ఖుడు", "గాడిద",
                 "దరిద్రుడు", "ఇడియట్", "సన్నాసి", "పనికిమాలినవాడు"],
        templates=["నువ్వు ఒక {x}", "నువ్వు పెద్ద {x}", "పోరా {x}", "ఛీ {x}", "ఏరా {x}", "నువ్వు సరైన {x}"],
        phrases=["నోరు మూసుకో", "నిన్ను చంపేస్తా", "నువ్వు చావు", "నిన్ను చూడాలంటేనే అసహ్యం",
                 "నువ్వు ఎందుకూ పనికిరావు", "నీ మొహం చూడాలని లేదు", "నిన్ను ఎవరూ ఇష్టపడరు",
                 "నువ్వు ఒక పనికిమాలినవాడివి", "పో ఇక్కడ నుండి వెధవ"],
        polite=["నమస్కారం", "ధన్యవాదాలు", "చాలా బాగుంది", "మీరు చాలా మంచివారు", "మీకు ఎలా ఉంది",
                "మీ సహాయానికి ధన్యవాదాలు", "శుభాకాంక్షలు", "క్షమించండి", "మంచి పని చేశారు",
                "రేపు కలుద్దాం", "నాకు ఇది చాలా నచ్చింది", "మిమ్మల్ని కలవడం సంతోషం",
                "దయచేసి నాకు సహాయం చేయగలరా", "భోజనం చేశారా", "మీ రోజు శుభంగా ఉండాలి",
                "మీరు చెప్పింది సరైనది", "ఈ సినిమా చాలా బాగుంది", "నువ్వు మంచి స్నేహితుడివి"],
        openers=["నమస్కారం", "హాయ్", "మిత్రమా", ""],
    ),
    "te_rom": dict(
        insults=["vedhava", "pichodu", "dhaddamma", "kukka", "chetta", "murkhudu", "gadida",
                 "sannasi", "waste fellow", "donga", "pichi vedhava"],
        templates=["nuvvu oka {x}", "nuvvu pedda {x}", "pora {x}", "chee {x}", "yenti ra {x} laaga matladutunnav"],
        phrases=["noru musuko", "ninnu champestha", "nuvvu chavu", "nuvvu yendhukoo panikiraavu",
                 "ninnu evvaru ishtapadaru", "nee mokham chudalani ledu", "nuvvu oka panikimaalina vaadivi",
                 "pora ikkadi nundi vedhava"],
        polite=["namaskaram", "dhanyavadalu", "chala bagundi", "meeru chala manchivaru", "ela unnaru",
                "mee sahayaniki thanks", "subhakankshalu", "kshaminchandi", "manchi pani chesaru",
                "repu kaludham", "naaku idi chala nachindi", "mimmalni kalavadam santhosham",
                "bhojanam chesara", "nuvvu chala manchivadivi", "super ra bagundi", "congrats ra",
                "ee cinema chala bagundi", "meeru cheppindi correct"],
        openers=["hi", "namaste", "mitrama", ""],
    ),
    "hi": dict(
        insults=["బెవకూఫ్", "గధ", "కుత్తా", "హరామీ", "పాగల్", "కమీనా", "ఘటియా", "నికమ్మా", "ఉల్లూ",
                 "నాలాయక్", "మూర్ఖ్", "బద్తమీజ్", "కచరా"],
        templates=["తుమ్ ఏక్ {x} హో", "తూ బహుత్ బడా {x} హై", "చుప్ కర్ {x}", "అబే {x}",
                   "నికల్ యహాఁ సే {x}", "తూ ఏక్‌దమ్ {x} హై"],
        phrases=["చుప్ రహో", "ముఁహ్ బంద్ కర్", "మైం తుఝే జాన్ సే మార్ దూంగా", "మర్ జా",
                 "తూ కిసీ కామ్ కా నహీఁ హై", "తుఝ్‌సే నఫ్రత్ హై", "తేరీ శక్ల్ భీ దేఖ్‌నా నహీఁ చాహ్తా",
                 "కోయీ తుఝే పసంద్ నహీఁ కర్తా", "తూ ఏక్‌దమ్ బేకార్ హై", "దఫా హో జా యహాఁ సే"],
        polite=["నమస్తే", "ధన్యవాద్", "బహుత్ బఢియా", "ఆప్ బహుత్ అచ్ఛే హైం", "ఆప్ కైసే హైం",
                "ఆప్‌కీ మదద్ కే లియే శుక్రియా", "బధాయీ హో", "మాఫ్ కీజియే", "బహుత్ అచ్ఛా కామ్ కియా",
                "కల్ మిల్తే హైం", "ముఝే యే బహుత్ పసంద్ ఆయా", "ఆప్‌సే మిల్‌కర్ ఖుషీ హుయీ",
                "క్యా ఆప్ మేరీ మదద్ కర్ సక్తే హైం", "ఖానా ఖా లియా", "ఆప్‌కా దిన్ శుభ్ హో", "ఆప్‌నే సహీ కహా",
                "యే ఫిల్మ్ బహుత్ అచ్ఛీ హై", "తుమ్ మేరే అచ్ఛే దోస్త్ హో"],
        openers=["నమస్తే", "దోస్త్", "హలో", ""],
    ),
    "hi_rom": dict(
        insults=["bewakoof", "gadha", "kutta", "harami", "pagal", "kamina", "ghatiya", "nikamma",
                 "ullu", "nalayak", "chutiya", "bekaar", "badtameez"],
        templates=["tum ek {x} ho", "tu bahut bada {x} hai", "chup kar {x}", "abe {x}",
                   "nikal yahan se {x}", "tu ekdum {x} hai"],
        phrases=["chup raho", "muh band kar", "main tujhe jaan se maar dunga", "mar ja",
                 "tu kisi kaam ka nahi hai", "tujhse nafrat hai", "teri shakal bhi nahi dekhna chahta",
                 "koi tujhe pasand nahi karta", "tu ekdum bekaar hai", "dafa ho ja yahan se"],
        polite=["namaste", "dhanyavad", "bahut badhiya", "aap bahut acche ho", "aap kaise ho",
                "aapki madad ke liye shukriya", "badhai ho", "maaf kijiye", "bahut accha kaam kiya",
                "kal milte hain", "mujhe ye bahut pasand aaya", "aapse milkar khushi hui",
                "kya aap meri madad kar sakte hain", "khana kha liya", "aapka din shubh ho",
                "aapne sahi kaha", "yaar tu kitna accha hai", "ye film bahut achhi hai"],
        openers=["hello", "namaste", "yaar", "bhai", ""],
    ),
}

SUFFIXES = ["", "", "", "!", "!!", "."]


def build():
    rows = set()
    for lang, d in DATA.items():
        toxic = set(d["phrases"])
        for tpl, x in itertools.product(d["templates"], d["insults"]):
            toxic.add(tpl.format(x=x))
        toxic = sorted(toxic)
        random.shuffle(toxic)
        for t in toxic[:130]:
            rows.add((t + random.choice(SUFFIXES), 1))
        for t in d["phrases"]:
            rows.add((t, 1))

        polite = set(d["polite"])
        for o, p in itertools.product(d["openers"], d["polite"]):
            polite.add((o + " " + p).strip())
        polite = sorted(polite)
        random.shuffle(polite)
        for t in polite[:130]:
            rows.add((t + random.choice(SUFFIXES), 0))
        for t in d["polite"]:
            rows.add((t, 0))

    extras_toxic = ["st*pid", "you are st*pid", "id!ot", "you id!ot", "f@ck you", "sh!t head", "b1tch",
                    "YOU ARE STUPID!!!", "STUPID IDIOT", "stuuupid", "idiiiot", "you are soooo dumb",
                    "u r an id10t", "y0u are a l0ser", "you are a d*mbass", "what a m0ron",
                    "i will find you and hurt you", "i will find you", "watch your back i will hurt you",
                    "i know where you live and i will hurt you"]
    for e in extras_toxic:
        rows.add((e, 1))

    extras_safe = ["you are not stupid, you just need more practice", "you are not dumb at all",
                   "he is not an idiot, he just made a mistake", "that was not a stupid question",
                   "you are far from worthless, you matter a lot", "i do not hate you, i care about you",
                   "you are definitely not a loser"]
    for e in extras_safe:
        rows.add((e, 0))

    rows = list(rows)
    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    rows = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label"])
        w.writerows(rows)
    toxic = sum(l for _, l in rows)
    print(f"Saved {len(rows)} rows ({toxic} toxic, {len(rows) - toxic} non-toxic) -> {OUT}")
