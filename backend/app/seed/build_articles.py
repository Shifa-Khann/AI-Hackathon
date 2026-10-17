"""Generates seed/articles.json — SAMPLE articles from fictional outlets (offline demo pool).

Run:  python -m app.seed.build_articles
All headlines, outlets and URLs are invented for demo purposes. Live ingest (LIVE_INGEST=1) brings real news.
"""
from __future__ import annotations

import json
from pathlib import Path

SOURCES = {
    "tech": ["Circuit Wire", "Open Source Weekly", "The Byte Ledger"],
    "biz": ["Indus Business Review", "Ledger & Loom", "Harbor Markets"],
    "pk": ["Karachi Ledger", "Margalla Post", "Lahore Dispatch"],
    "world": ["The Meridian", "Crescent Courier", "Atlas Report"],
    "sport": ["Pitchside", "The Long Room", "Boundary Line"],
    "sci": ["Harbor Science", "The Lab Notebook", "Orbit Daily"],
    "life": ["The Quiet Press", "Margin Notes", "Weekend Folio"],
}

# topic -> (source pool, [(title, summary, hours_ago), ...])
DATA: dict[str, tuple[str, list[tuple[str, str, int]]]] = {
    "ai": ("tech", [
        ("Small language models are quietly taking over everyday phone tasks",
         "Device makers are shipping compact models that run fully on-device, cutting latency and cloud costs. Early benchmarks suggest they handle most summarising and drafting jobs well.", 5),
        ("Regulators draft first rules for AI systems used in hiring",
         "A new proposal would require employers to disclose when automated tools screen candidates. Industry groups say the audit requirements are vague and costly.", 9),
        ("Why AI coding assistants still struggle with large legacy codebases",
         "Engineers report that assistants excel at new files but lose track of decades of implicit conventions. Teams are responding with better repository indexing and written style guides.", 14),
        ("Chipmakers race to cut the power draw of data-center accelerators",
         "Electricity is becoming the main constraint on training clusters. New designs trade peak speed for efficiency per watt.", 20),
        ("Researchers show a new way to make chatbots admit when they do not know",
         "A calibration technique lets models flag low-confidence answers without hurting accuracy. The authors say it could reduce confident but wrong responses in medical and legal tools.", 30),
    ]),
    "software": ("tech", [
        ("A decade on, Rust adoption reaches mainstream infrastructure teams",
         "More companies are rewriting performance-critical services in Rust, citing memory safety. Hiring remains the main obstacle.", 7),
        ("The case for boring technology in small engineering teams",
         "A veteran engineer argues that choosing well-understood tools frees time for product work. Novelty, she says, should be rationed like a budget.", 18),
        ("Open source maintainers weigh new funding models after burnout survey",
         "A survey finds most maintainers work unpaid and consider quitting. Sponsorship programmes help a few projects but leave the long tail exposed.", 26),
    ]),
    "cybersecurity": ("tech", [
        ("Phishing kits now imitate bank apps with near-perfect pixel accuracy",
         "Analysts say new kits copy login flows so well that visual checks no longer help. Hardware security keys remain effective against them.", 6),
        ("A routine software update closed a flaw affecting millions of routers",
         "Vendors urge owners to install the patch, as attackers had begun scanning for exposed devices. Many home routers update only when users act.", 22),
        ("Ransomware gangs shift to stealing data instead of encrypting it",
         "Incident responders see more extortion without lockouts, which makes backups less useful. Defenders are focusing on limiting what attackers can copy.", 40),
    ]),
    "startups": ("biz", [
        ("Seed investors grow pickier as founders return to profitability targets",
         "Early-stage funds report more questions about unit economics and fewer about growth at any cost. Smaller rounds are becoming common.", 4),
        ("Karachi founders build a logistics startup around neighbourhood shops",
         "The company routes small deliveries through existing kiryana stores to cut last-mile costs. It plans to expand to three more cities this year.", 12),
        ("What a failed startup taught its founder about hiring too early",
         "In a candid post-mortem, the founder says payroll outran learning. The advice: stay small until customers pull you forward.", 28),
        ("Accelerator demo days look different in a quieter funding climate",
         "Investors now ask about customers and cash runway first, and the pitch second. Founders say the shift rewards clear thinking.", 44),
    ]),
    "markets": ("biz", [
        ("Benchmark index edges higher as investors await earnings season",
         "Trading was thin with energy and banking shares leading gains. Analysts expect guidance, not results, to move prices.", 3),
        ("Bond yields ease as inflation data comes in softer than forecast",
         "Lower yields lifted rate-sensitive stocks. Strategists caution that one report does not make a trend.", 8),
        ("Retail investors pile into index funds for the long haul",
         "Fund flow data shows steady monthly buying regardless of headlines. Advisers say consistency matters more than timing.", 21),
        ("Why dividend stocks are back in fashion with cautious savers",
         "Steady payouts look attractive as growth stocks swing. Analysts warn about chasing high yields without checking cash flow.", 36),
    ]),
    "economy_pk": ("pk", [
        ("Rupee holds steady as remittance inflows stay strong",
         "Overseas transfers continued to support the external account this month. Economists say the cushion depends on exchange-rate stability.", 5),
        ("Budget talks focus on widening the tax net without hurting salaried earners",
         "Officials are weighing property and retail measures to raise revenue. Business groups ask for predictable rules.", 11),
        ("Exporters ask for cheaper power to stay competitive",
         "Textile and leather exporters say energy costs erode thin margins. The government is reviewing a targeted tariff.", 25),
        ("Inflation cools for the third month, central bank watching closely",
         "Food prices eased while utility costs remained elevated. Analysts debate how soon policy rates can fall.", 33),
    ]),
    "business": ("biz", [
        ("Retailers rethink inventory after a year of unpredictable demand",
         "Chains are ordering smaller batches more often to avoid markdowns. Suppliers say the shift pushes costs upstream.", 10),
        ("Family-run manufacturers adopt software to survive tighter margins",
         "Simple inventory and billing tools are helping owners spot waste. Adoption is slow but steady.", 27),
        ("Supply-chain managers diversify ports after repeated shipping delays",
         "Companies now route cargo through several hubs to reduce single points of failure. The cost is higher but delays have dropped.", 38),
    ]),
    "energy": ("biz", [
        ("Rooftop solar boom reshapes electricity demand on the national grid",
         "Households installing panels are cutting daytime consumption, leaving utilities with unusual evening peaks. Planners are studying storage.", 6),
        ("Oil prices drift as producers signal steady output",
         "Traders weighed inventory data against cautious demand forecasts. Refiners expect a calm quarter.", 16),
        ("Battery storage projects move from pilots to procurement",
         "Utilities are tendering grid-scale batteries to smooth renewable output. Costs have fallen sharply over five years.", 34),
    ]),
    "climate": ("sci", [
        ("Heatwave season arrives earlier, testing city cooling plans",
         "Municipal planners are adding shade, water points and cool roofs. Health officials urge outdoor workers to adjust schedules.", 13),
        ("Farmers adopt drought-tolerant seed as rainfall patterns shift",
         "Agronomists say new varieties can hold yields with less water. Access to credit remains the main barrier.", 29),
        ("Coastal cities weigh mangrove restoration as a low-cost flood defence",
         "Restored mangroves reduce storm surge and support fisheries. Projects need years of community stewardship to succeed.", 42),
    ]),
    "politics_pk": ("pk", [
        ("Assembly session opens with debate on provincial funding formula",
         "Lawmakers traded proposals on dividing federal revenue. Observers expect negotiations to continue for weeks.", 2),
        ("Court asks for clearer timelines in a long-running public land case",
         "The bench urged agencies to file complete records at the next hearing. Residents say delays have stalled local projects.", 12),
        ("Local government reform returns to the policy agenda",
         "Analysts argue that empowered councils could improve service delivery. Parties disagree on how much authority to devolve.", 24),
        ("Parliamentary committees quietly shape most of the year's legislation",
         "A review finds that committee amendments change many bills before they reach the floor. Transparency groups want public minutes.", 41),
    ]),
    "geopolitics": ("world", [
        ("Regional talks resume as mediators propose a phased ceasefire",
         "Negotiators described the discussions as constructive but fragile. Humanitarian groups are pressing for aid corridors.", 4),
        ("Trade corridors become the new diplomacy between neighbouring states",
         "Governments are using customs and transit deals to build ties. Analysts say economic links can calm political friction.", 17),
        ("A summit's quiet outcome: agreement to keep talking",
         "Leaders left without a joint declaration but scheduled follow-up meetings. Diplomats called that a small success.", 31),
    ]),
    "cricket": ("sport", [
        ("Opener's unbeaten century puts the home side in control of the Test",
         "A patient innings anchored a total that tested the visiting attack all day. The pitch is expected to turn on day four.", 1),
        ("Selectors name a young fast bowler in the squad for the T20 series",
         "The 20-year-old impressed in domestic cricket with pace and a late swing. Captains praised the selection's balance.", 7),
        ("How spin is reshaping the new-ball overs in modern T20",
         "Teams increasingly open with a spinner to stall the powerplay. Data shows it cuts boundary rates against left-handers.", 15),
        ("Women's league announces a longer season with more home matches",
         "Organisers say the schedule will give players steadier workloads. Broadcasters have agreed to cover every game.", 23),
        ("Grassroots coaches argue for more turf pitches in small cities",
         "Players trained on concrete often struggle on bouncier surfaces. A pilot programme will lay five new grounds.", 39),
        ("Retiring captain reflects on two decades of dressing-room change",
         "He recalled how fitness, analytics and mental-health support transformed team culture. His advice to youngsters: stay curious.", 52),
    ]),
    "football": ("sport", [
        ("Title race tightens after a late winner in the weekend's big match",
         "A stoppage-time goal separated two sides who had traded the lead twice. Managers praised the intensity.", 9),
        ("Clubs experiment with smaller academy squads to speed development",
         "Coaches say fewer players receive more minutes and personal attention. Critics worry about missing late bloomers.", 25),
        ("The data behind the modern high press",
         "Analysts show how pressing triggers have become more selective. Teams now press in short bursts rather than for 90 minutes.", 37),
    ]),
    "f1": ("sport", [
        ("Qualifying shake-up: rookie takes pole in a wet session",
         "Changing conditions rewarded bold tyre calls. The champion starts fourth after a late error.", 8),
        ("Teams debate next season's rules as budget caps tighten",
         "Engineers say aerodynamic changes could reshape the pecking order. Smaller teams want a fairer share of testing.", 19),
        ("Inside the pit wall: how strategists decide when to stop",
         "A strategist explains the models used to weigh track position against tyre wear. Human judgement still breaks ties.", 46),
    ]),
    "health": ("sci", [
        ("Large study links regular walking to lower risk of heart disease",
         "Researchers followed participants for ten years and found benefits even at modest step counts. Doctors say consistency counts most.", 12),
        ("Hospitals trial AI note-taking to give clinicians time back",
         "Early pilots show doctors spending less time on paperwork. Privacy teams are reviewing how recordings are stored.", 21),
        ("What sleep researchers wish everyone knew about late-night screens",
         "Experts say light matters but so does mental stimulation. Simple evening routines beat gadgets and supplements.", 35),
    ]),
    "science": ("sci", [
        ("Physicists measure a tiny effect that could test a long-standing theory",
         "The experiment used ultra-cold atoms to detect a faint shift. Results will need independent replication.", 14),
        ("Deep-sea expedition catalogues dozens of unfamiliar species",
         "The team's cameras recorded unusual jellyfish and bottom-dwelling fish. Samples will be sequenced over the coming months.", 27),
        ("Why replication projects are changing how labs publish",
         "Journals are rewarding careful confirmation as well as novelty. Researchers say the culture is shifting slowly.", 45),
    ]),
    "space": ("sci", [
        ("Lunar lander mission sets a landing date after final tests",
         "Engineers completed fuel and navigation checks this week. The craft will carry instruments to study dust near the south pole.", 10),
        ("Amateur astronomers help confirm a faint new comet",
         "Backyard telescopes captured the object's motion over several nights. Professionals will refine its orbit.", 32),
        ("Small satellites make Earth observation affordable for new countries",
         "Compact imaging satellites are letting agencies track crops and floods. Launch rideshares have lowered the entry cost.", 48),
    ]),
    "education": ("pk", [
        ("Universities redesign first-year courses around projects, not lectures",
         "Faculty say project work improves retention and teamwork. Assessment remains the hardest part to reform.", 15),
        ("Scholarship programme expands to cover rural students",
         "The fund will pay tuition and living costs for several hundred students. Applications open next month.", 30),
        ("Why exam stress is pushing schools to rethink homework",
         "Counsellors report rising anxiety before board exams. Some schools are trimming homework and adding study skills sessions.", 43),
    ]),
    "design": ("life", [
        ("Designers revisit typography as screens get larger and calmer",
         "Generous line spacing and serif body text are returning to reading apps. Designers say reading comfort drives retention.", 11),
        ("Accessibility testing moves earlier in the product cycle",
         "Teams that prototype with screen readers catch problems before engineering begins. Costs fall as a result.", 24),
        ("Interfaces that end: the case against infinite scroll",
         "Researchers argue that finite lists respect attention and improve satisfaction. Some products now add natural stopping points.", 36),
    ]),
    "books": ("life", [
        ("Debut novel on a Lahore family wins praise for quiet precision",
         "Reviewers admire its small domestic scenes and understated humour. The author wrote it over six years of early mornings.", 20),
        ("Essay collections are having a moment among younger readers",
         "Booksellers report brisk sales of personal essays. Readers say short pieces fit busy schedules.", 33),
        ("The slow pleasure of rereading a favourite book",
         "A critic argues that rereading shows how much of a book lives in the reader. She suggests choosing one title each year.", 50),
    ]),
    "film_music": ("life", [
        ("Festival jury praises a low-budget drama shot in a single week",
         "Critics noted the film's patient camera and non-professional cast. It will screen in cinemas next month.", 16),
        ("Independent musicians turn to subscription fan clubs",
         "Artists say small recurring support is more stable than streaming royalties. Platforms are courting them.", 28),
        ("Why long-running series are shrinking their seasons",
         "Shorter runs mean tighter stories and fewer filler episodes. Viewers say they finish more shows.", 47),
    ]),
    "culture": ("life", [
        ("Old-city walking tours help residents rediscover their neighbourhoods",
         "Volunteer guides share stories of bazaars, havelis and craft traditions. Tours sell out within hours.", 18),
        ("Craft fairs return, with makers selling directly online",
         "Handmade jewellery, textiles and ceramics drew steady crowds. Many makers now take orders through social media.", 31),
        ("The quiet revival of community libraries",
         "Volunteers are turning spare rooms into lending libraries. Donations of children's books are in highest demand.", 49),
    ]),
    "travel": ("life", [
        ("Northern valleys prepare for a record tourist season",
         "Guesthouses are upgrading facilities and road crews are clearing passes. Officials urge visitors to check weather alerts.", 13),
        ("Airlines add direct routes to secondary cities",
         "Regional airports expect more traffic as carriers test point-to-point flights. Fares may fall on busy routes.", 26),
        ("Slow travel: spending a week in one place",
         "Travellers report lower costs and deeper experiences when they stay put. Tour operators are building longer itineraries.", 40),
    ]),
    "crypto": ("tech", [
        ("Regulators sketch a licensing framework for digital asset platforms",
         "The draft sets capital and custody rules for exchanges. Industry groups welcome clarity but dispute the fees.", 19),
        ("Mobile wallets push digital payments into small-town markets",
         "Shopkeepers say QR payments reduce cash handling. Fraud awareness campaigns accompany the rollout.", 29),
        ("Stablecoins find a niche in cross-border freelancer payments",
         "Freelancers use them to avoid slow bank transfers. Tax treatment remains unclear in many countries.", 43),
    ]),
}


def build() -> list[dict]:
    out: list[dict] = []
    n = 0
    for topic, (pool, items) in DATA.items():
        sources = SOURCES[pool]
        for i, (title, summary, hours) in enumerate(items):
            n += 1
            slug = "".join(c if c.isalnum() else "-" for c in title.lower())[:60].strip("-")
            out.append({
                "title": title,
                "summary": summary,
                "source": sources[i % len(sources)],
                "url": f"https://example.com/sample/{topic}/{slug}",
                "topics": [topic],
                "hours_ago": hours,
                "word_count": 520 + (n * 137) % 900,
            })
    # a few cross-topic stories
    cross = {
        "Chipmakers race to cut the power draw of data-center accelerators": ["ai", "energy"],
        "Karachi founders build a logistics startup around neighbourhood shops": ["startups", "business"],
        "Hospitals trial AI note-taking to give clinicians time back": ["health", "ai"],
        "Mobile wallets push digital payments into small-town markets": ["crypto", "economy_pk"],
        "Phishing kits now imitate bank apps with near-perfect pixel accuracy": ["cybersecurity", "crypto"],
        "Interfaces that end: the case against infinite scroll": ["design", "software"],
    }
    for a in out:
        if a["title"] in cross:
            a["topics"] = cross[a["title"]]
    return out


if __name__ == "__main__":
    arts = build()
    path = Path(__file__).with_name("articles.json")
    path.write_text(json.dumps(arts, indent=1, ensure_ascii=False))
    print(f"wrote {len(arts)} sample articles to {path}")
