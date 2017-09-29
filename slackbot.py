from slackclient import SlackClient
from tqdm import tqdm

TOKEN = "xoxp-37196295941-243837863827-248698471057-8ba9198cc8f6879d82f8634cb4b7f38b"
sc = SlackClient(TOKEN)

text = """
Dear Pixels Camp participator. More than half of the Hackathon has passed. Awesome projects are emerging, as one would expect from the best community in the WWW (whole wide world).

But how can you pick the best? You certainly don't want to waste your precious Exposure on a project that, cool as it may be, won't make it to the main stage and make you proud.

Let us help you! At PixelsFund, we're experienced in investment strategy, and we'll invest your Exposure wisely so as to ensure it will help the ones who are the most worthy of it.

So join us, and together we'll reap the profit of intelligent investing, backed by predictive models and RedBull-powered-sleepless-hours.
---------------------
It's NOT a scam, check how it works at https://pixelsfund.github.io
Our address: `0x51bdb634ab627f79cc0166cc0bab0cd29f6d8294`
Our promotional video: https://youtu.be/ZO_wYW8Me5Y
"""


def send_message(member):
    try:
        sc.api_call(
            "chat.postMessage",
            channel="@%s" % member,
            text=text,
            username='pixelsfund.github.io'
        )
    except Exception as e:
        print(e)


member_names = list(map(lambda x: x['name'], (sc.api_call("users.list", exclude_archived=1))['members']))

for x in tqdm(member_names):
    send_message(x)