# חלקי הדף: תבניות HTML

כל התבניות משתמשות במחלקות של `assets/base.css`. הטקסט בסוגריים מרובעים מגיע מהקופי המאושר. אם חסר טקסט לחלק, מדלגים על החלק, לא ממציאים.

סדר מקובל (מדלגים על מה שאין לו קופי): פס עליון, ראש הדף, הבעיה, מי אני, איך זה עובד, מה מקבלים, הוכחות, למי זה מתאים, ההצעה והמחיר, שאלות, כפתור אחרון, תחתית. **המחיר אף פעם לא בראש הדף.**

מחליפים משטחים לאורך הדף: `s-dark`, `s-base`, `s-tint`, `s-soft`, ולפעמים `s-brand`. לא שני חלקים רצופים באותו משטח.

## פס עליון (לא חובה)
```html
<div class="strip">[משפט קצר אחד, למשל תאריך או למי זה]</div>
```

## ראש הדף
```html
<section class="s-dark">
  <div class="wrap">
    <h1>[הכותרת, בלי נקודה בסוף]</h1>
    <p class="lead">[תת הכותרת]</p>
    <a class="btn" href="[יעד הכפתור]">[נוסח הכפתור]</a>
    <img src="images/hero.jpg" alt="[תיאור התמונה]" width="1200" height="750">
  </div>
</section>
```

## הבעיה
```html
<section class="s-base">
  <div class="wrap">
    <h2 class="pain">[כותרת הבעיה]</h2>
    <p>[פסקה]</p>
    <ul class="list pain-list"><li>[נקודה]</li><li>[נקודה]</li></ul>
  </div>
</section>
```
`pain-list` מחליף את סימן ה-✓ בסימן ✗ בצבע של הכאב.

## מי אני
```html
<section class="s-soft">
  <div class="wrap">
    <img class="portrait" src="images/me.jpg" alt="[שם]" width="400" height="400">
    <h2>[כותרת]</h2>
    <p>[הסיפור, פסקה אחרי פסקה]</p>
  </div>
</section>
```

## איך זה עובד (3 צעדים)
```html
<section class="s-tint">
  <div class="wrap">
    <h2>[כותרת]</h2>
    <ol class="steps">
      <li><h3>[צעד]</h3><p>[הסבר קצר]</p></li>
      <li><h3>[צעד]</h3><p>[הסבר קצר]</p></li>
      <li><h3>[צעד]</h3><p>[הסבר קצר]</p></li>
    </ol>
  </div>
</section>
```

## מה מקבלים
```html
<section class="s-base">
  <div class="wrap stack">
    <h2>[כותרת]</h2>
    <div class="card"><h3>[פריט]</h3><p>[מה זה נותן]</p></div>
    <div class="card"><h3>[פריט]</h3><p>[מה זה נותן]</p></div>
  </div>
</section>
```

## הוכחות (רק אמיתיות)
```html
<section class="s-soft">
  <div class="wrap-wide">
    <h2>[כותרת]</h2>
    <div class="compare">
      <figure class="card"><p class="lead">"[התוצאה, במילים של הלקוח]"</p><p>[הציטוט]</p><figcaption class="small">[שם, ומה הוא עושה]</figcaption></figure>
    </div>
  </div>
</section>
```
אין הוכחות? מדלגים על החלק. לא כותבים "לקוחות מרוצים" כללי.

## השוואה (המקום היחיד לשתי עמודות)
```html
<section class="s-tint">
  <div class="wrap-wide">
    <h2>[כותרת]</h2>
    <div class="compare">
      <div class="card"><h3>[לפני / הדרך הרגילה]</h3><ul class="list"><li>[...]</li></ul></div>
      <div class="card"><h3>[אחרי / הדרך שלנו]</h3><ul class="list"><li>[...]</li></ul></div>
    </div>
  </div>
</section>
```

## ההצעה והמחיר
```html
<section class="s-tint">
  <div class="wrap">
    <h2>[מה כלול]</h2>
    <ul class="list"><li>[פריט]</li><li>[פריט]</li></ul>
    <p class="lead">[המחיר, כולל מע"מ אם העסק גובה מע"מ]</p>
    <a class="btn" href="[יעד]">[נוסח הכפתור]</a>
  </div>
</section>
```
מחיר "לפני" מחוק רק אם הוא באמת היה המחיר.

## שאלות נפוצות
```html
<section class="s-soft">
  <div class="wrap">
    <h2>שאלות נפוצות</h2>
    <details><summary>[שאלה]</summary><p>[תשובה]</p></details>
  </div>
</section>
```

## כפתור אחרון
```html
<section class="s-dark">
  <div class="wrap">
    <h2>[כותרת סוגרת]</h2>
    <p>[משפט או שניים]</p>
    <a class="btn" href="[יעד]">[אותו נוסח כפתור]</a>
  </div>
</section>
```

## תחתית
```html
<footer>
  <p>[שם העסק] · [טלפון או מייל]</p>
  <p><a href="privacy.html">מדיניות פרטיות</a></p>
</footer>
```

## הדגשה בתוך משפט
- מילה חשובה: `<b>` בתוך המשפט
- מספר או טענה מרכזית, במשורה: `<span class="mark">[...]</span>`
- לא שולפים מילים לתגיות, כפתורונים או שורת אייקונים. זה נראה כמו עיצוב אוטומטי
