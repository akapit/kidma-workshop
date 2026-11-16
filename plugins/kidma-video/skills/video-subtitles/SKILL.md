---
name: video-subtitles
description: "Use when the user wants burned-in subtitles on a video (a talking head, a reel, an ad, an avatar video), in Hebrew or English: transcribes with word timings, groups the words into short lines, burns them in a clean look (white bold Assistant, black outline, soft shadow, no box) and writes a matching .srt file. Triggers: \"כתוביות\", \"תוסיף כתוביות\", \"תמלול לסרטון\", \"קובץ srt\", \"subtitles\", \"captions\"."
---

# כתוביות לסרטון

**מה זה:** לוקח סרטון, מתמלל אותו עם זמן לכל מילה, ומוסיף כתוביות שרופות בסגנון נקי: לבן, מודגש, קו מתאר שחור וצל רך, בלי מלבן מאחור. בנוסף יוצא קובץ `.srt` להעלאה לפלטפורמות.
**צריך פעם אחת:** `ffmpeg` (במק: `brew install ffmpeg`), דפדפן Google Chrome, וחשבון ElevenLabs לתמלול. הסקיל בודק ומסביר מה חסר.

## 1. מסתכל על הסרטון
```bash
V="/path/to/video.mp4"; W=subtitles-work; mkdir -p "$W"
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact "$V"
ffmpeg -y -v error -i "$V" -vf "fps=1/2,scale=240:-1,tile=6x2" -frames:v 1 "$W/sheet.jpg"
ffmpeg -y -v error -i "$V" -vn -c:a libmp3lame -b:a 192k "$W/audio.mp3"
```
מסתכל על `sheet.jpg`: יש כבר כתוביות בסרטון? המקום של הכתוביות (בערך 70% מלמעלה בסרטון לאורך) יושב על פנים? אם כן, מזיז בשלב 4 עם `--top`.

## 2. מתמלל, עם זמן לכל מילה
התמלול עולה כסף בחשבון של המשתמש. אומר לו לפני, פעם אחת. אחת משתי דרכים:

- **החיבור של ElevenLabs ב-Claude** (אם מחובר): מפעיל את כלי התמלול בלי לחבר קובץ, כדי שייפתח חלון בחירה, ופותח למשתמש את התיקייה עם `audio.mp3` כדי שיבחר אותו. שומר את רשימת המילים מהתוצאה ב-`$W/words.json`.
- **מפתח API של ElevenLabs**: המשתמש שומר את המפתח בעצמו כמשתנה סביבה `ELEVENLABS_API_KEY` (אף פעם לא בקובץ בתיקייה, ולא בצ'אט). ואז:
  ```bash
  curl -s https://api.elevenlabs.io/v1/speech-to-text -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -F model_id=scribe_v1 -F timestamps_granularity=word -F file=@"$W/audio.mp3" > "$W/words.json"
  ```
  (אם יש דגם Scribe חדש יותר, אפשר להחליף את `model_id`.)

תמלול מקומי (Whisper) רק כמוצא אחרון, ואומרים את זה: הוא טועה הרבה בעברית.

## 3. מחלק לשורות, וקורא אותן
```bash
S=<התיקייה של הסקיל הזה>/scripts
python3 -I $S/words_to_cues.py "$W/words.json" --duration <אורך הסרטון בשניות> --out "$W/cues.json"
```
עד 5 מילים בשורה, שורה חדשה בסוף משפט או בהפסקה, ומשפט ארוך נחצה באמצע הטבעי שלו.
**קורא את כל השורות לפני שורף:** מתקן טעויות תמלול ברורות, ומוסיף נקודה בסוף משפט שאיבד אותה. אם חלוקה נקראת רע, מתקן ב-`cues.json`. לא מוסיף מילים שלא נאמרו.

## 4. שורף את הכתוביות
```bash
python3 -I $S/burn_captions.py "$V" "$W/cues.json" --work "$W/render"
```
- יוצא `<שם>_subtitled.mp4` ו-`<שם>.srt` ליד המקור. הקול לא נוגע
- הגודל מתאים את עצמו לסרטון: 75 פיקסלים על כל 1080 של הצלע הקצרה. סרטון לאורך: בערך 70% מלמעלה. לרוחב: קרוב לתחתית
- `--top` / `--bottom` להזיז, `--size` לשנות גודל, `--color` לצבע אחר
- Chrome לא נמצא? מגדירים `CHROME_PATH` לנתיב שלו

## 5. בודק ומגיש
- פותח את `$W/render/check.png` (תמונה אחת לכל שורה): כל השורות שם, הפיסוק העברי בצד הנכון, לא על הפנים, שום דבר לא חתוך
- מראה למשתמש את השורות, ואומר אילו כדאי לו לבדוק באוזן
- בסוף מוחק את תיקיית העבודה `subtitles-work`, אחרי שהמשתמש ראה את התוצאה

## אף פעם לא
- להמציא מילים שלא נאמרו, או "לשפר" את מה שהדובר אמר
- לשמור מפתח API בקובץ, בתיקייה או ב-GitHub
- לשרוף כתוביות על סרטון שכבר יש בו כתוביות, בלי לשאול

<!-- סקיל מערכת "צוות AI לעסק", מאת אלכסנדר קאפיט. לשנות חופשי. -->
