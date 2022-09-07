# Voice Balancer Bot

Discord bot to find out the optimal volume settings for people in a voice channel!

It uses the international loudness measurement standard [ITU-R BS.1770-4](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-4-201510-I!!PDF-E.pdf) for optimal measurement.

Use `/measure` to have the bot join your voice channel, measure everyone's loudness, and recommend at what % you should set everyone's volume at.

### ➔ [Invite link](https://discord.com/api/oauth2/authorize?client_id=949624987629813780&permissions=1049600&scope=bot%20applications.commands)



---

## Example

![image](https://user-images.githubusercontent.com/76059582/184538958-a4a4b86c-2acc-48c8-b936-67a0199d76f4.png)

For example, if you are "Fev", you should set others' volumes at 84% and 90% percents, while the other two people should set you at 75% percent.

This will make your Discord audio _balanced_ on your end; if it makes everyone too loud or too silent, you would need to adjust Discord's audio as a whole.

(The dB values are just for additional information, and show the needed adjustments in dB relative to a target of -28 LUFS.)

---

### Permissions
The bot requires "Connect" permission.  
In addition, "View Channels (Read Messages)" permission is needed for **only** the Voice Channels; you can disable this permission for every other channel.

---

## Hosting the bot

You can run the bot with docker:

`docker build -t voice_eq_bot https://github.com/OdielDomanie/voice_eq_bot.git`  
`docker run -d -e DISCORD_TOKEN=123abc voice_eq_bot`

You can also host the bot in Heroku, using this buildpack: https://github.com/xrisk/heroku-opus
