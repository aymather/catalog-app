from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Character, CharacterDiscussion, Tier

engine = create_engine('sqlite:///ssbmdatabase.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#################################################
# USERS
#################################################

# user1 = User(name = 'Alec Mather', username = 'aymather', email = 'aymather@gmail.com', main_character = 'Falco')
# session.add(user1)
# session.commit()

#################################################
# TIERS
#################################################

SStier = Tier(name = 'SS', description = 'Reserved only for the best...')
session.add(SStier)

Stier = Tier(name = 'S', description = 'Very...very...good characters. Will still win most tournaments.')
session.add(Stier)

Atier = Tier(name = 'A', description = 'Good characters, although will have a harder time winning major tournaments.')
session.add(Atier)

Btier = Tier(name = 'B', description = 'Viable, but not ideal for winning major tournaments.')
session.add(Btier)

Ctier = Tier(name = 'C', description = 'Possible to win local tournaments, but have never won a major tournament.')
session.add(Ctier)

Dtier = Tier(name = 'D', description = 'Fun characters to play with your friends, not ideal for tournament settings.')
session.add(Dtier)

Etier = Tier(name = 'E', description = "Characters your friends play when they say that they're 'Really good at smash bros'")
session.add(Etier)

Ftier = Tier(name = 'F', description = "Home of the sacred 'Six jumps and down+b combo'")
session.add(Ftier)

session.commit()

#################################################
# CHARACTERS
#################################################

SStier = session.query(Tier).filter_by(name = 'SS').one()
fox = Character(name = 'Fox', image = 'fox.png', character_tier = SStier.name, description = 'The one to rule them all...')
session.add(fox)

Stier = session.query(Tier).filter_by(name = 'S').one()
falco = Character(name = 'Falco', image = 'falco.png', character_tier = Stier.name, description = 'Super-cali-swagalistic-sexy-hella-dopeness')
shiek = Character(name = 'Shiek', image = 'shiek.png', character_tier = Stier.name, description = 'E-Z win gg k thnx bi')
marth = Character(name = 'Marth', image = 'marth.png', character_tier = Stier.name, description = 'Sword guy. Also known to his friends as Mark. In reality, probably the best character in the game.')
session.add(falco)
session.add(shiek)
session.add(marth)

Atier = session.query(Tier).filter_by(name = 'A').one()
CFalcon = Character(name = 'Captain Falcon', image = 'cfalcon.png', character_tier = Atier.name, description = "The people's champ. A forever practicioner of the fact that stomp out of shield is a good option.")
jiggly = Character(name = 'Jigglypuff', image = 'jigglypuff.png', character_tier = Atier.name, description = "AKA Kanye Rest. AKA Clutchbox. AKA the most annoying character in the game.")
ic = Character(name = 'Ice Climbers', image = 'iceclimbers.png', character_tier = Atier.name, description = 'Wobble baby wobble baby wobble baby wobble.')
peach = Character(name = 'Peach', image = 'peach.png', character_tier = Atier.name, description = "RIP Armada...")
session.add(CFalcon)
session.add(jiggly)
session.add(ic)
session.add(peach)

Btier = session.query(Tier).filter_by(name = 'B').one()
pikachu = Character(name = 'Pikachu', image = 'pikachu.png', character_tier = Btier.name, description = "@Axe | the poor man's Fox.")
samus = Character(name = 'Samus', image = 'samus.png', character_tier = Btier.name, description = 'The character your friend plays.')
session.add(pikachu)
session.add(samus)

Ctier = session.query(Tier).filter_by(name = 'C').one()
doc = Character(name = 'Doctor Mario', image = 'drmario.png', character_tier = Ctier.name, description = "Mario's twin brother who is actually invited to family parties.")
yoshi = Character(name = 'Yoshi', image = 'yoshi.png', character_tier = Ctier.name, description = 'C tier character, SS tier taunt.')
luigi = Character(name = 'Luigi', image = 'luigi.png', character_tier = Ctier.name, description = "It's pronounced Lou - Iggy")
session.add(doc)
session.add(yoshi)
session.add(luigi)

Dtier = session.query(Tier).filter_by(name = 'D').one()
mario = Character(name = 'Mario', image = 'mario.png', character_tier = Dtier.name, description = "The Mario brother who decided to live his dreams.")
link = Character(name = 'Link', image = 'link.png', character_tier = Dtier.name, description = 'The character you played before you decided to take melee seriously.')
younglink = Character(name = 'Young Link', image = 'younglink.png', character_tier = Dtier.name, description = 'Owner of the domain: littlebrotherswhopwntheirolderbrothers.net')
dk = Character(name = 'Donkey Kong', image = 'dk.png', character_tier = Dtier.name, description = "The character you play when you're drunk.")
ganon = Character(name = 'Ganondorf', image = 'ganondorf.png', character_tier = Dtier.name, description = "[friend selects Ganondorf] 'Lawl you play Ganon-dork???'")
session.add(mario)
session.add(link)
session.add(younglink)
session.add(dk)
session.add(ganon)

Etier = session.query(Tier).filter_by(name = 'E').one()
roy = Character(name = 'Roy', image = 'roy.png', character_tier = Etier.name, description = "He's got a fire sword...")
mrgaw = Character(name = 'Mr. Game and Watch', image = 'gameandwatch.png', character_tier = Etier.name, description = """Director: WE NEED SOMETHING, ANYTHING, JOHN, WE NEED ONE MORE CHARACTER | John: I've got a black robot with a chair in a git repository I made when I was 9? | Director: YES FINE LITERALLY ANYTHING""")
mewtwo = Character(name = 'Mewtwo', image = 'mewtwo.png', character_tier = Etier.name, description = "The character you think is good until you try him once and never play him again.")
zelda = Character(name = 'Zelda', image = 'zelda.png', character_tier = Etier.name, description = "I honestly forgot about this character because I always just think about her as being shiek.")
ness = Character(name = 'Ness', image = 'ness.png', character_tier = Etier.name, description = "I've been playing this game for 10 years and I still can't do the up+B recovery thing...")
session.add(roy)
session.add(mrgaw)
session.add(mewtwo)
session.add(zelda)
session.add(ness)

Ftier = session.query(Tier).filter_by(name = 'F').one()
pichu = Character(name = 'Pichu', image = 'pichu.png', character_tier = Ftier.name, description = "Less good Pikachu.")
bowser = Character(name = 'Bowser', image = 'bowser.png', character_tier = Ftier.name, description = "The character you practice your combo game on.")
kirby = Character(name = 'Kirby', image = 'kirby.png', character_tier = Ftier.name, description = "Your friend who says he's 'really good at smash.'")
session.add(pichu)
session.add(bowser)
session.add(kirby)

session.commit()