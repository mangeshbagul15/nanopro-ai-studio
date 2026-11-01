"""
Mangesh Nano Pro AI Studio - Natural Human Neural TTS Engine
Produces high-fidelity, natural human voices for educational videos in Marathi, Hindi, and English.
Architecture:
- Primary: ElevenLabs Multilingual Voice AI (if API key available)
- Fast Resilient Secondary: Microsoft Neural Edge-TTS (100% Free, Zero-Quota, Unlimited, Natural Human Accent)
  - Marathi: mr-IN-AarohiNeural (Female Teacher), mr-IN-ManoharNeural (Male Teacher)
  - Hindi: hi-IN-SwaraNeural (Female), hi-IN-MadhurNeural (Male)
  - English (India): en-IN-NeerjaNeural (Female), en-IN-PrabhatNeural (Male)
- Tertiary: Fallback Browser Web Speech API
"""

import os
import re
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Union
from app.core.logger import log_event
from app.core.elevenlabs_voice import elevenlabs_voice

# Pre-defined step-by-step educational teacher scripts for FAANG & MNC SQL Interviews
PRESET_SCRIPTS = {
    "sql_q1_second_highest_salary": {
        "mr": """एसक्यूएल इंटरव्ह्यूमधील सर्वात महत्त्वाचा प्रश्न: एम्प्लॉईज टेबलमधून दुसऱ्या क्रमांकाचा सर्वाधिक पगार कसा शोधायचा? चला लॉजिक समजून घेऊन स्टेप-बाय-स्टेप क्वेरी लिहूया!
पहिले प्रश्न नीट समजून घ्या. आपल्याला दुसरा डिस्टिंक्ट पगार हवा आहे, दुसरा कर्मचारी नाही. इथे ऐंशी हजार पगार दोनदा आला आहे. तो आपल्याला एकदाच मोजायचा आहे.
आता हे कसे सोडवायचे? प्रथम सर्वात मोठा पगार शोधा. मग तो पगार वगळा. आणि उरलेल्या पगारांमधून सर्वात मोठा पगार निवडा. तोच आपला दुसरा सर्वाधिक पगार!
चला आधी आतील क्वेरी लिहूया: सिलेक्ट मॅक्स सॅलरी फ्रॉम एम्प्लॉईज. ही क्वेरी आपल्याला ऐंशी हजार, म्हणजेच सर्वात मोठा पगार देते.
आता व्हेअर सॅलरी लहान सबक्वेरी ही अट लावून ऐंशी हजार वगळूया. यामुळे ऐंशी हजार असणाऱ्या दोन्ही नोंदी वगळल्या जाऊन सत्तर, साठ आणि पन्नास हजार उरतात.
आता बाहेरील मॅक्स फंक्शन उरलेल्या पगारांमधून सर्वात मोठा पगार शोधते. उरलेल्यांमध्ये सर्वात मोठी रक्कम आहे सत्तर हजार! सबक्वेरीमुळे हे उत्तर १०० टक्के अचूक येते!
इंटरव्ह्यू टिप! जर सर्वाधिक पगार अनेक लोकांचा समान असेल तरीही ही सबक्वेरी अचूक काम करते. पुढील एसक्यूएल प्रश्नांसाठी फॉलो करा कोड विथ मंगेश!""",
        "hi": """एसक्यूएल इंटरव्यू का एक बेहद पॉपुलर सवाल: एम्प्लॉईज टेबल से सेकंड हाईएस्ट सैलरी कैसे निकालें? आइए लॉजिक समझकर स्टेप बाय स्टेप क्वेरी बनाते हैं!
पहले सवाल को समझिए. हमें सेकंड हाईएस्ट डिस्टिंक्ट सैलरी चाहिए. ध्यान दीजिए कि अस्सी हजार दो बार आया है. हमें इसे केवल एक बार ही गिनना है.
अब इसे कैसे सॉल्व करें? पहले मैक्सिमम सैलरी निकालिए. फिर उसे बाहर कीजिए. और बाकी बची वैल्यूज में से मैक्सिमम निकालिए. वही है हमारी सेकंड हाईएस्ट सैलरी!
आइए पहले इनर क्वेरी लिखते हैं: सिलेक्ट मैक्स सैलरी फ्रॉम एम्प्लॉईज. यह हमें अस्सी हजार यानी सबसे बड़ी सैलरी देती है.
अब व्हेअर सैलरी लेस दैन सबक्वेरी लगाकर अस्सी हजार को फिल्टर करते हैं. इससे दोनों अस्सी हजार वाले रिकॉर्ड्स हट जाते हैं और सत्तर, साठ और पचास हजार बचते हैं.
अब आउटर मैक्स फंक्शन बचे हुए रिकॉर्ड्स को चेक करता है. सबसे बड़ी बची हुई वैल्यू है सत्तर हजार! यही हमारा सही जवाब है!
इंटरव्यू टिप! अगर हाईएस्ट सैलरी डुप्लीकेट भी हो, तब भी यह सबक्वेरी मेथड हमेशा सही उत्तर देता है. ऐसे ही एसक्यूएल सवालों के लिए फॉलो कीजिए कोड विथ मंगेश!""",
        "en": """Here's a popular SQL interview question. How do you find the second-highest salary from an Employees table? Let's understand the logic and build the query step by step.
First, understand the requirement. We need the second-highest distinct salary, not the second employee. Notice that eighty thousand appears twice. We must count it only once.
Now, how should we solve it? First, find the maximum salary. Then exclude that salary. Finally, find the maximum from the remaining values. That's our second-highest salary.
Let's write the inner query first. SELECT MAX salary FROM Employees. This returns eighty thousand, the highest salary in our table.
Next, we exclude the highest salary using WHERE salary is less than the result of our inner query. This removes both eighty-thousand values, leaving seventy, sixty, and fifty thousand.
Now the outer MAX function checks the remaining salaries. The highest remaining value is seventy thousand. That's our answer! The key is using a subquery to exclude the original maximum.
Interview tip! Always clarify whether they want the second-highest distinct salary. If the highest salary appears multiple times, this query still returns the correct second-highest value. Follow Code with Mangesh for more SQL interview questions!"""
    },
    "faang_dense_rank_ties": {
        "mr": """नमस्कार मित्रांनो! गुगल आणि ॲमेझॉनच्या एसक्यूएल इंटरव्ह्यूमध्ये ९५ टक्के मुलं या प्रश्नात फेल होतात!
प्रश्न असा आहे: कंपनीतील कर्मचाऱ्यांमधून दुसऱ्या क्रमांकाचा सर्वाधिक पगार मिळवणारे कर्मचारी कसे शोधायचे?
टेबलमध्ये पहा: आरव आणि रोहित या दोघांचाही पगार समान एक लाख पंच्याऐंशी हजार रुपये आहे!
जर आपण लिमिट १ ऑफसेट १ किंवा सामान्य रँक फंक्शन वापरले, तर ते दुसरा नंबर गाळून थेट तिसरा नंबर देते, ज्यामुळे निकाल १०० टक्के चुकतो!
इथे कस कोड लिहायचा ते नीट समजून घ्या: आपण वापरणार आहोत डेन्स रँक ओव्हर ऑर्डर बाय सॅलरी डीसेंडिंग!
डेन्स रँक समान पगार असतानाही पुढचा रँक नंबर अजिबात गाळत नाही!
निकाल बघा: आरव आणि रोहित दोघांना पहिला नंबर, आणि प्रिया कुलकर्णीला मिळाला अचूक दुसरा क्रमांक!
नेहमी लक्षात ठेवा: जेव्हा समान व्हॅल्यूज असतात, तेव्हा इंटरव्ह्यूमध्ये नेहमी डेन्स रँक चाच वापर करावा!""",
        "hi": """नमस्ते दोस्तों! गूगल और अमेज़ॉन के एसक्यूएल इंटरव्यू में ९५% कैंडिडेट्स इस सवाल में फेल हो जाते हैं!
सवाल है: कंपनी में सेकंड हाईएस्ट सैलरी पाने वाले एम्प्लॉई को कैसे निकालें?
टेबल देखिए: आरव और रोहित दोनों की सैलरी बराबर १ लाख ८५ हजार रुपये है!
अगर नॉर्मल RANK या LIMIT 1 OFFSET 1 लगाया, तो वह सेकंड रैंक स्किप करके सीधे थर्ड रैंक दे देगा, और जवाब गलत हो जाएगा!
यहाँ कोड कैसे लिखना है ध्यान से देखिए: हम इस्तेमाल करेंगे DENSE_RANK() OVER (ORDER BY salary DESC)।
DENSE_RANK कभी भी रैंक नंबर स्किप नहीं करता!
फाइनल रिजल्ट देखिए: आरव और रोहित को रैंक १, और प्रिया कुलकर्णी को मिली सटीक सेकंड रैंक!
हमेशा याद रखें: टाई होने पर सही रैंक निकालने के लिए हमेशा DENSE_RANK का ही उपयोग करें!""",
        "en": """Hello everyone! Over 95% of candidates fail this classic Google and Amazon SQL interview problem: Finding the second highest salary when ties exist!
Look at the table: Both Aarav and Rohit earn an identical top salary of 185,000!
If you use LIMIT 1 OFFSET 1 or standard RANK, it skips Rank 2 and jumps straight to Rank 3, causing a critical failure!
Here is how to write the code: We use DENSE_RANK() OVER (ORDER BY salary DESC).
DENSE_RANK never skips ranking numbers after ties!
Look at the output: Aarav and Rohit get Rank 1, and Priya Kulkarni correctly receives the exact Second Highest Salary!
Remember: whenever ties are possible, DENSE_RANK is mandatory!"""
    },
    "goldman_running_balance": {
        "mr": """गोल्डमन सॅक्स आणि एचडीएफसी बँकेच्या टेक्निकल राऊंडमधील नंबर १ प्रश्न: खात्याचा क्युम्युलेटिव्ह चालू बॅलन्स कसा काढायचा?
टेबलमध्ये पहा: खाते क्रमांक ८८२१ मध्ये आधी ५००० जमा झाले, नंतर १२०० काढले, आणि पुन्हा ८५०० जमा झाले.
जुनी को-रिलेटेड सब-क्वेरी वापरल्यास लाखो नोंदींवर बँक सर्व्हर हँग होतो!
इथे कोड कसा लिहायचा: सम अमाऊंट ओव्हर पार्टिशन बाय अकाउंट नंबर, ऑर्डर बाय ट्रॅन्झॅक्शन डेट!
पार्टिशन बाय मुळे प्रत्येक खात्याचा हिशोब स्वतंत्र राहतो आणि सम ओव्हर मुळे सुरुवातीपासून आजपर्यंतची चालू शिल्लक अचूक मोजली जाते!
निकाल बघा: ५००० मधून १२०० गेले ३८०० राहिले, त्यात ८५०० जोडले १२३०० झाले!
लक्षात ठेवा: रनिंग टोटल्ससाठी नेहमी विंडो ॲग्रीगेट्स वापरा, यामुळे क्वेरी लिनिअर वेळेत धावते!""",
        "hi": """गोल्डमैन सैक्स और एचडीएफसी बैंक इंटरव्यू का सबसे पसंदीदा सवाल: क्युमुलेटिव रनिंग बैलेंस कैसे निकालें?
ट्रांजैक्शन टेबल देखिए: अकाउंट ८८२१ में पहले ५००० जमा हुए, फिर १२०० डेबिट, और फिर ८५०० क्रेडिट हुए।
पुराने सब-क्वेरी तरीके से डेटाबेस धीमा हो जाता है।
कोड कैसे लिखना है: SUM(amount) OVER (PARTITION BY account_no ORDER BY txn_date)।
PARTITION BY हर बैंक खाते का हिसाब अलग रखता है, और SUM OVER चालू बैलेंस जोड़ता जाता है!
रिजल्ट देखिए: ५००० से घटकर ३८०० और फिर बढ़कर १२,३०० बैलेंस एकदम सटीक निकला!
याद रखें: रनिंग टोटल के लिए हमेशा Window Functions का ही उपयोग करें!""",
        "en": """Goldman Sachs and HDFC Bank top interview drill: Cumulative Running Account Balance!
Look at the ledger: Account 8821 has 5000 credit, 1200 debit, then 8500 credit.
Using correlated subqueries causes catastrophic O(N squared) performance!
Here is how to write the code: SUM(amount) OVER (PARTITION BY account_no ORDER BY txn_date).
PARTITION BY keeps each customer ledger strictly isolated while SUM OVER accumulates sequentially!
The running balance updates seamlessly: 5000 to 3800 to 12300!
Always remember: Window Functions compute running balances in linear O(N) time!"""
    },
    "uber_consecutive_active_days": {
        "mr": """उबर आणि स्विगीच्या डेटा सायन्स इंटरव्ह्यूमधील लीजेंडरी प्रश्न: सलग ३ दिवस सक्रिय असणारे ड्रायव्हर्स कसे शोधायचे?
याला एसक्यूएल मध्ये गॅप्स अँड आयलँड्स प्रॉब्लेम म्हणतात!
इथे युक्ती काय आहे? जेव्हा तारखा सलग असतात, तेव्हा ट्रिप डेट वजा रो नंबर केल्यास एकच स्थिर तारीख मिळते!
त्यानंतर ग्रुप बाय आयलँड ग्रुप आणि हॅव्हिंग काऊंट ३ पेक्षा जास्त दिल्यास सलग ट्रिप्स पूर्ण केलेले ड्रायव्हर्स अचूक सापडतात!
अल्गोरिदम डिझाइनच्या दृष्टीने हा एसक्यूएल मधील अत्यंत महत्त्वाचा प्रश्न आहे!""",
        "hi": """उबर और स्विगी डेटा एनालिस्ट इंटरव्यू का क्लासिक सवाल: लगातार ३ दिन एक्टिव रहने वाले राइडर्स कैसे खोजें?
इसे SQL में Gaps and Islands समस्या कहते हैं।
यहाँ लॉजिक समझिए: जब तारीखें लगातार होती हैं, तो trip_date में से ROW_NUMBER घटाने पर एक स्थिर ग्रुप की मिलती है!
फिर GROUP BY और HAVING COUNT >= 3 लगाने पर लगातार काम करने वाले ड्राइवर्स तुरंत सामने आ जाते हैं!""",
        "en": """Uber and Swiggy Data Analyst interview drill: Solving the famous Gaps and Islands problem to find drivers active for 3 consecutive days!
The trick: subtracting ROW_NUMBER() from consecutive dates yields an identical anchor date!
Grouping by this island key with HAVING COUNT >= 3 isolates consecutive streaks effortlessly!"""
    },
    "netflix_top_n_per_category": {
        "mr": """नेटफ्लिक्स आणि स्पॉटिफायच्या मुलाखतीत सर्वात जास्त विचारला जाणारा प्रश्न: प्रत्येक कॅटेगरीतील टॉप २ शो कसे शोधायचे?
टेबलमध्ये ॲक्शन, ड्रामा, आणि कॉमेडी अशा विविध कॅटेगरीज आहेत.
इथे संपूर्ण टेबलवर रँक न लावता आपण वापरणार आहोत: डेन्स रँक ओव्हर पार्टिशन बाय जॉनर, ऑर्डर बाय वॉच अवर्स डीसेंडिंग!
पार्टिशन बाय मुळे प्रत्येक जॉनरचे स्वतंत्र रँकिंग तयार होते आणि व्हेअर रँक लहान किंवा बरोबर २ दिल्यावर टॉप २ चित्रपट अलगद बाहेर येतात!""",
        "hi": """नेटफ्लिक्स और स्पॉटिफाय का हाई-यील्ड इंटरव्यू सवाल: हर कैटेगरी में से टॉप २ सबसे ज्यादा देखे गए टाइटल्स कैसे निकालें?
यहाँ हम DENSE_RANK() OVER (PARTITION BY genre ORDER BY watch_hours DESC) का इस्तेमाल करेंगे।
PARTITION BY हर जॉनर को अलग पार्टीशन में बांटता है, और WHERE rank <= 2 हर कैटेगरी के टॉप २ टाइटल्स फिल्टर कर देता है!""",
        "en": """Netflix and Spotify technical interview drill: Finding the Top 2 most streamed titles within every genre!
We use DENSE_RANK() OVER (PARTITION BY genre ORDER BY watch_hours DESC).
PARTITION BY segments the ranking per genre without collapsing individual movie rows!"""
    },
    "meta_reciprocal_friends": {
        "mr": """मेटा म्हणजेच फेसबुक आणि लिंक्डइनच्या एसक्यूएल टेस्टमध्ये म्युचुअल फॉलोवर्सच्या जोड्या कशा शोधायच्या?
जर युजर ए युजर बी ला फॉलो करतो आणि बी देखील ए ला फॉलो करतो, तर ही म्युचुअल फ्रेंडशिप झाली!
इथे आपण सेल्फ जॉइन वापरणार आहोत. पण एक गोष्ट लक्षात ठेवा: निकालात ए बी आणि बी ए अशा दोनदा नोंदी नकोत!
म्हणून व्हेअर क्लॉजमध्ये युजर ए लहान युजर बी अशी अट लावल्यास एकच अचूक युनिक जोडी मिळते!""",
        "hi": """मेटा और लिंक्डइन इंटरव्यू: दो लोग जो एक-दूसरे को फॉलो करते हैं उनकी म्यूचुअल जोड़ी कैसे निकालें?
यहाँ हम सेल्फ-जॉइन इस्तेमाल करेंगे। डुप्लिकेट रिवर्स जोड़ी रोकने के लिए WHERE user_a < user_b की शर्त लगाई जाती है!""",
        "en": """Meta and LinkedIn graph interview problem: Finding reciprocal follow connections using a Self-Join!
Joining user_follows on itself with condition f1.user_id < f1.following_id eliminates redundant mirrored pairs!"""
    },
    "amazon_churn_zero_orders": {
        "mr": """ॲमेझॉनच्या एसक्यूएल राऊंड १ मधील ट्रॅप प्रश्न: ज्या ग्राहकांनी खाते उघडले पण आजपर्यंत एकही खरेदी केली नाही ते कसे शोधायचे?
९० टक्के मुलं नॉट इन सब-क्वेरी लिहून फसतात! कारण ऑर्डर्स टेबलमध्ये एकही नल व्हॅल्यू असेल तर नॉट इन पूर्ण निकाल रिकामा दाखवते!
योग्य उत्तर: कस्टमर्स टेबलला ऑर्डर्स टेबलसोबत लेफ्ट जॉइन करा आणि व्हेअर ऑर्डर आयडी इज नल लावा! हा इंटरव्ह्यूअरचा आवडता नियम आहे!""",
        "hi": """अमेज़ॉन एसक्यूएल इंटरव्यू: वे कस्टमर्स जिन्होंने रजिस्टर किया पर कभी ऑर्डर नहीं दिया!
यहाँ NOT IN मत लिखिए क्योंकि NULL वैल्यू होने पर NOT IN खाली रिजल्ट देता है।
हमेशा LEFT JOIN लगाकर WHERE orders.order_id IS NULL का इस्तेमाल करें!""",
        "en": """Amazon and Flipkart classic trap question: Finding registered customers who never placed an order!
Why does NOT IN fail? If the orders table contains even a single NULL, NOT IN evaluates to UNKNOWN and returns zero rows!
The industry standard solution is LEFT JOIN with WHERE order_id IS NULL!"""
    },
    "stripe_consecutive_fraud": {
        "mr": """स्ट्राइप आणि पेपालच्या फ्रॉड डिटेक्शनमधील प्रश्न: एकाच कार्डवरून ५ मिनिटांत सलग दोन मोठे विड्रॉव्हल्स कसे पकडायचे?
इथे महागडा सेल्फ-जॉइन न वापरता आपण लॅग फंक्शन वापरणार आहोत: लॅग अमाऊंट ओव्हर पार्टिशन बाय कार्ड नंबर!
लॅग फंक्शन मागील व्यवहाराची रक्कम थेट पुढच्या ओळीत आणून ठेवते, ज्यामुळे फ्रॉड एका सेकंदात पकडला जातो!""",
        "hi": """स्ट्राइप और पेपाल फ्रॉड डिटेक्शन: एक ही कार्ड से लगातार दो बड़े विड्रॉल कैसे पकड़ें?
यहाँ हम LAG(amount, 1) OVER (PARTITION BY card_no ORDER BY tx_time) का इस्तेमाल करेंगे। पिछली रकम तुरंत सामने आ जाती है!""",
        "en": """Stripe and PayPal fraud detection: Detecting consecutive rapid high-value transactions!
Using LAG(amount, 1) OVER (PARTITION BY card_no ORDER BY tx_time), we pull the previous withdrawal onto the current row to flag anomalies instantly!"""
    },
    "zomato_mom_growth": {
        "mr": """स्विगी आणि झोमॅटोच्या बिझनेस इंटेलिजन्स रिपोर्टिंगमध्ये दर महिन्याची टक्केवारीतील वाढ म्हणजेच मंथ ओव्हर मंथ ग्रोथ कशी काढायची?
सूत्राप्रमाणे: चालू महिन्याचा रेव्हेन्यू वजा मागील महिन्याचा रेव्हेन्यू, भागिले मागील महिन्याचा रेव्हेन्यू, गुणिले १००!
इथे मागील महिन्याचा रेव्हेन्यू काढण्यासाठी लॅग टोटल रेव्हेन्यू ओव्हर ऑर्डर बाय मंथ वापरले जाते!""",
        "hi": """ज़ोमैटो और स्विगी बिज़नेस एनालिटिक्स: Month-over-Month रेवेन्यू ग्रोथ % कैसे निकालें?
चालू महीने का रेवेन्यू माइनस पिछला रेवेन्यू, डिवाइडेड बाय पिछला रेवेन्यू, गुणा १००। पिछले महीने का रेवेन्यू LAG() से आसानी से निकल आता है!""",
        "en": """Swiggy and Zomato analytics: Calculating Month-over-Month (MoM) revenue growth percentage!
We use LAG(total_revenue, 1) OVER (ORDER BY report_month) to access the preceding month's revenue and compute percentage growth!"""
    }
}


class NeuralTTSEngine:
    """
    Enterprise Multilingual Neural TTS Engine with Edge-TTS and ElevenLabs.
    Features: Premium Indian Male Tech Educator persona (28-32y, natural conversational delivery,
    fluent Hindi-English code switching, crystal-clear database and code terminology).
    """

    def __init__(self):
        self.output_dir = Path(__file__).resolve().parents[2] / "data" / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.voice_map = {
            "hi": "hi-IN-SwaraNeural",         # 🇮🇳 Indian Hindi Tech Educator (Swara Neural) - Human Warmth, Clarity & Care
            "hi_female": "hi-IN-SwaraNeural",  # 🇮🇳 Swara Neural (Default Female Teacher)
            "hi_male": "hi-IN-MadhurNeural",   # 🇮🇳 Madhur Neural (Male Teacher)
            "en": "en-IN-NeerjaNeural",        # 🇬🇧 Indian English Tech Educator (Neerja Neural) - Clear & Expressive
            "en_female": "en-IN-NeerjaNeural", # 🇬🇧 Neerja Neural (Default Female Teacher)
            "en_male": "en-IN-PrabhatNeural",  # 🇬🇧 Prabhat Neural (Male Teacher)
            "mr": "mr-IN-AarohiNeural",        # 🇮🇳 Indian Marathi Tech Educator (Aarohi Neural) - Human Warmth & Understanding
            "mr_female": "mr-IN-AarohiNeural", # 🇮🇳 Aarohi Neural (Default Female Teacher)
            "mr_male": "mr-IN-ManoharNeural"   # 🇮🇳 Manohar Neural (Male Teacher)
        }

    def _prepare_conversational_text(self, text: str, for_eleven_v4: bool = False) -> str:
        """
        Enhances text with pure natural conversational pauses and crystal-clear technical pronunciation:
        - STRICTLY ZERO XML / ZERO SSML TAGS (Edge-TTS speaks plain text; XML tags get read aloud!)
        - Persona: Natural Indian Tech Educator & Mentor (Swara / Aarohi)
        - Natural breathing pauses created using pure punctuation (commas, question marks, periods, newlines)
        """
        if not text:
            return ""
        t = text.strip()

        # 1. Strictly strip ANY XML/HTML/SSML tags so Edge-TTS never speaks "speak", "break", "http", etc.
        t = re.sub(r'<[^>]+>', ' ', t)
        t = re.sub(r'&(?:amp|lt|gt|quot|apos);', ' ', t)

        # 2. Natural conversational commas around key explanatory discourse markers:
        t = re.sub(r'\b(yaani|yani)\b', ', yaani,', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(matlab)\b', ', matlab,', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(dekhiye)\b', ', dekhiye,', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(chaliye)\b', 'chaliye,', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(म्हणजेच|म्हणजे)\b', ', म्हणजेच,', t)
        t = re.sub(r'\b(बघा|लक्ष द्या)\b', ', बघा,', t)
        t = re.sub(r'\b(चला|सर्वप्रथम)\b', 'चला,', t)

        # 3. Clean human teacher punctuation pauses (Edge-TTS pauses naturally on punctuation):
        t = re.sub(r'\?\s*', '? ', t)
        t = re.sub(r':\s*', ', ', t)
        t = re.sub(r'!\s*', '! ', t)
        t = re.sub(r'\.\s+', '. ', t)
        t = re.sub(r',\s*,+', ', ', t)
        t = re.sub(r'\s{2,}', ' ', t)

        if not for_eleven_v4:
            t = re.sub(r'\[(curious|confident|enthusiastic|whispering|thoughtful)\]\s*', '', t, flags=re.IGNORECASE)

        return t.strip()

    async def _synthesize_edge_tts(self, text: str, voice: str, output_path: Path):
        """Synthesizes speech via Microsoft Edge Neural TTS with 100% clean plain text (ZERO SSML/XML tags)."""
        import asyncio
        import edge_tts

        formatted = self._prepare_conversational_text(text, for_eleven_v4=False)
        last_error = None
        for attempt in range(3):
            try:
                # Pure human conversational speech at calm educator rate (-2%)
                communicate = edge_tts.Communicate(formatted, voice=voice, rate="-2%", pitch="+0Hz")
                await asyncio.wait_for(communicate.save(str(output_path)), timeout=60)
                if output_path.exists() and output_path.stat().st_size > 1000:
                    return
                last_error = RuntimeError("Edge Neural TTS returned an empty audio file.")
            except Exception as exc:
                last_error = exc
                log_event(f"Edge Neural TTS attempt {attempt + 1}/3 failed: {exc}", level="WARNING", component="NeuralTTS")

            if attempt < 2:
                await asyncio.sleep(1.2 * (attempt + 1))
        raise RuntimeError(f"Edge Neural TTS failed after 3 attempts: {last_error}")

    async def synthesize_async(self, text: str, language: str = "hi", voice_gender: str = "female", custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Asynchronously synthesizes text into natural human speech.
        Implements the 25-35y Indian Male Tech Educator Persona across Eleven v4 & Microsoft Neural TTS.
        """
        lang = language.lower() if language else "hi"
        if lang not in ["mr", "hi", "en"]:
            lang = "hi"

        # Resolve voice: Default to Indian Female Educator (Swara / Aarohi / Neerja)
        if voice_gender == "male":
            voice_key = f"{lang}_male"
        else:
            voice_key = f"{lang}_female" if f"{lang}_female" in self.voice_map else lang
        edge_voice = self.voice_map.get(voice_key, self.voice_map.get(lang, "hi-IN-SwaraNeural"))

        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
        if not custom_filename or "scenario" in custom_filename or "master_prompt" in custom_filename:
            fname = f"voice_{lang}_{text_hash}.mp3"
        else:
            fname = custom_filename
        out_path = self.output_dir / fname

        # If already cached for this exact text hash, return immediately
        if out_path.exists() and out_path.stat().st_size > 1000:
            return {
                "status": "success",
                "audio_url": f"/audio/{fname}",
                "file_path": str(out_path),
                "provider": "Cache",
                "voice_persona": "Premium Indian Male Tech Educator (25-35y • Eleven v4)",
                "language": lang
            }

        # 1. ElevenLabs Attempt (Liam / Aarav - 25-35y Indian Male Educator with Eleven v4)
        if elevenlabs_voice.is_available():
            try:
                log_event(f"Attempting ElevenLabs Indian Male synthesis (Eleven v4) for {lang} ({len(text)} chars)...", component="NeuralTTS")
                v4_text = self._prepare_conversational_text(text, for_eleven_v4=True)
                res = elevenlabs_voice.generate_speech(
                    text=v4_text,
                    output_filename=fname,
                    voice_id="TX3LPaxmHKxFdv7VOQHJ", # Liam / Aarav - 25-35y Indian Male Tech Educator
                    model_id="eleven_v4",             # Flagship Eleven v4 Architecture
                    stability=0.55,
                    similarity_boost=0.85
                )
                if res.get("status") == "success":
                    return {
                        "status": "success",
                        "audio_url": f"/audio/{fname}",
                        "file_path": res.get("file_path"),
                        "provider": "ElevenLabs Voice AI (Liam / Eleven v4)",
                        "voice_persona": "Premium Indian Male Tech Educator (25-35y • Eleven v4)",
                        "language": lang
                    }
            except Exception as e:
                log_event(f"ElevenLabs v4 notice ({e}). Cascading to Microsoft Neural TTS [{edge_voice}]...", level="INFO", component="NeuralTTS")

        # 2. Microsoft Edge Neural TTS Cascade (hi-IN-MadhurNeural / en-IN-PrabhatNeural / mr-IN-ManoharNeural)
        try:
            log_event(f"Synthesizing via Natural Indian Educator Neural TTS [{edge_voice}]...", component="NeuralTTS")
            await self._synthesize_edge_tts(text, edge_voice, out_path)
            if out_path.exists() and out_path.stat().st_size > 1000:
                log_event(f"Natural Indian Educator Neural TTS synthesized successfully: {out_path.name} ({out_path.stat().st_size} bytes)", component="NeuralTTS")
                return {
                    "status": "success",
                    "audio_url": f"/audio/{fname}",
                    "file_path": str(out_path),
                    "provider": f"Microsoft Neural TTS ({edge_voice})",
                    "voice_persona": "Natural Indian Tech Educator (Swara/Aarohi Neural • Human Understanding)",
                    "language": lang
                }
        except Exception as e:
            log_event(f"Microsoft Neural TTS error: {e}", level="ERROR", component="NeuralTTS")

        return {
            "status": "fallback",
            "message": "Cloud voice synthesis unavailable. Falling back to browser speech.",
            "voice_persona": "Natural Indian Tech Educator (Human Understanding)",
            "language": lang
        }

    def synthesize(self, text: str, language: str = "mr", voice_gender: str = "female") -> Dict[str, Any]:
        """Synchronous wrapper for synthesize_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, self.synthesize_async(text, language, voice_gender)).result()
            else:
                return loop.run_until_complete(self.synthesize_async(text, language, voice_gender))
        except Exception:
            return asyncio.run(self.synthesize_async(text, language, voice_gender))

    async def get_preset_audio_async(self, preset_id: str, language: str = "mr") -> Dict[str, Any]:
        """Returns or synthesizes step-by-step teacher audio for a preset asynchronously."""
        lang = language.lower() if language in ["mr", "hi", "en"] else "mr"
        preset = PRESET_SCRIPTS.get(preset_id, PRESET_SCRIPTS["faang_dense_rank_ties"])
        script = preset.get(lang, preset["mr"])

        fname = f"preset_{preset_id}_{lang}.mp3"
        out_path = self.output_dir / fname

        if out_path.exists() and out_path.stat().st_size > 1000:
            return {
                "status": "success",
                "audio_url": f"/audio/{fname}",
                "file_path": str(out_path),
                "script": script,
                "provider": "Pre-Rendered Neural Audio"
            }

        # Synthesize via Neural TTS
        return await self.synthesize_async(text=script, language=lang, voice_gender="female", custom_filename=fname)

    def get_preset_audio(self, preset_id: str, language: str = "mr") -> Dict[str, Any]:
        """Synchronous wrapper for get_preset_audio_async."""
        return asyncio.run(self.get_preset_audio_async(preset_id, language))

    def generate_speech(self, text: str, output_path: Union[str, Path], voice: Optional[str] = None) -> bool:
        """
        Synthesizes high-fidelity speech using Microsoft Edge Neural TTS for a specific voice actor.
        Supports:
        - Marathi: mr-IN-AarohiNeural (Female Teacher), mr-IN-ManoharNeural (Male Teacher)
        - Hindi: hi-IN-MadhurNeural (Male Teacher), hi-IN-SwaraNeural (Female)
        - English: en-US-JennyNeural (Female), en-US-GuyNeural (Male), en-IN-NeerjaNeural, en-IN-PrabhatNeural
        Returns True if successful, False otherwise.
        """
        if not text or not text.strip():
            return False

        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        v = (voice or "").strip()
        if not v or "Neural" not in v:
            v = "mr-IN-AarohiNeural"

        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    pool.submit(asyncio.run, self._synthesize_edge_tts(text, v, out_path)).result(timeout=65)
            else:
                asyncio.run(self._synthesize_edge_tts(text, v, out_path))

            return out_path.exists() and out_path.stat().st_size > 100
        except Exception as e:
            log_event(f"Microsoft Neural TTS generate_speech error for {v}: {e}", level="ERROR", component="NeuralTTS")
            return False

    async def generate_speech_async(self, text: str, output_path: Union[str, Path], voice: Optional[str] = None) -> bool:
        """Asynchronous synthesis helper for Edge-TTS."""
        if not text or not text.strip():
            return False
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        v = (voice or "").strip()
        if not v or "Neural" not in v:
            v = "mr-IN-AarohiNeural"
        try:
            await self._synthesize_edge_tts(text, v, out_path)
            return out_path.exists() and out_path.stat().st_size > 100
        except Exception as e:
            log_event(f"Microsoft Neural TTS generate_speech_async error for {v}: {e}", level="ERROR", component="NeuralTTS")
            return False


# Global Singleton instance
neural_tts = NeuralTTSEngine()


def generate_speech(text: str, output_path: Union[str, Path], voice: Optional[str] = None) -> bool:
    """Module-level wrapper for neural_tts.generate_speech."""
    return neural_tts.generate_speech(text, output_path, voice=voice)


async def generate_speech_async(text: str, output_path: Union[str, Path], voice: Optional[str] = None) -> bool:
    """Module-level wrapper for neural_tts.generate_speech_async."""
    return await neural_tts.generate_speech_async(text, output_path, voice=voice)

