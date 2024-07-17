# abyss
What is abyss? abyss is a tiny tool I built as a distraction-free journal, of sorts. The main difference between abyss and other platforms is the increased ability to stay in control of your data.

For example-
- You can choose to turn off your "thoughts" page or protect it with a password.
- All "thoughts" are encrypted with your account password by default.

abyss also emphasizes your thoughtspace, not your social space. There are no likes, comments, or followers. Just you and your thoughts. By design, you aren't meant to go to your own page or others' pages. The only link to your page is in the settings tab, and there's no feed for you to visit others.

## Self Hosting
If you're interested in self-hosting abyss, you can do so by following these steps:
1. Clone this repository
2. Run `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in the necessary fields
    a. It is recommended to use appwrite for your database for optimal performance- however, sqlite is a great option for a quick local install or in situations with low load. In both cases, abyss will handle database/table creation for you when you first start the app.
4. Run `python main.py`
5. abyss should now be running on `0.0.0.0:9023`

> [!NOTE]
> If you ran this program before July 17th around 3pm EST (or before [this](https://github.com/CoolCoderSJ/abyss/commit/49384e8a3036260d84dc72ce92ae5fc62fcaefef) commit), run `python migration.py` to convert to the new encryption method. This uses a randomly generated encryption key to encrypt posts instead of the user's password. This way, whenever passwords are updated, only the encryption key needs to be re-encrypted, not every post.