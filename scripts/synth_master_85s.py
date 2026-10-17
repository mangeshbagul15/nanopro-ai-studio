import os
import asyncio
import edge_tts

scenes_en = [
    "Here's a popular SQL interview question. How do you find the second-highest salary from an Employees table? Let's understand the logic and build the query step by step.",
    "First, understand the requirement. We need the second-highest distinct salary, not the second employee. Notice that eighty thousand appears twice. We must count it only once.",
    "Now, how should we solve it? First, find the maximum salary. Then exclude that salary. Finally, find the maximum from the remaining values. That's our second-highest salary.",
    "Let's write the inner query first. SELECT MAX salary FROM Employees. This returns eighty thousand, the highest salary in our table.",
    "Next, we exclude the highest salary using WHERE salary is less than the result of our inner query. This removes both eighty-thousand values, leaving seventy, sixty, and fifty thousand.",
    "Now the outer MAX function checks the remaining salaries. The highest remaining value is seventy thousand. That's our answer! The key is using a subquery to exclude the original maximum.",
    "Interview tip! Always clarify whether they want the second-highest distinct salary. If the highest salary appears multiple times, this query still returns the correct second-highest value. Follow Code with Mangesh for more SQL interview questions!"
]

scenes_mr = [
    "एसक्यूएल इंटरव्ह्यूमधील सर्वात महत्त्वाचा प्रश्न: एम्प्लॉईज टेबलमधून दुसऱ्या क्रमांकाचा सर्वाधिक पगार कसा शोधायचा? चला लॉजिक समजून घेऊन स्टेप-बाय-स्टेप क्वेरी लिहूया!",
    "पहिले प्रश्न नीट समजून घ्या. आपल्याला दुसरा डिस्टिंक्ट पगार हवा आहे, दुसरा कर्मचारी नाही. इथे ऐंशी हजार पगार दोनदा आला आहे. तो आपल्याला एकदाच मोजायचा आहे.",
    "आता हे कसे सोडवायचे? प्रथम सर्वात मोठा पगार शोधा. मग तो पगार वगळा. आणि उरलेल्या पगारांमधून सर्वात मोठा पगार निवडा. तोच आपला दुसरा सर्वाधिक पगार!",
    "चला आधी आतील क्वेरी लिहूया: सिलेक्ट मॅक्स सॅलरी फ्रॉम एम्प्लॉईज. ही क्वेरी आपल्याला ऐंशी हजार, म्हणजेच सर्वात मोठा पगार देते.",
    "आता व्हेअर सॅलरी लहान सबक्वेरी ही अट लावून ऐंशी हजार वगळूया. यामुळे ऐंशी हजार असणाऱ्या दोन्ही नोंदी वगळल्या जाऊन सत्तर, साठ आणि पन्नास हजार उरतात.",
    "आता बाहेरील मॅक्स फंक्शन उरलेल्या पगारांमधून सर्वात मोठा पगार शोधते. उरलेल्यांमध्ये सर्वात मोठी रक्कम आहे सत्तर हजार! सबक्वेरीमुळे हे उत्तर १०० टक्के अचूक येते!",
    "इंटरव्ह्यू टिप! जर सर्वाधिक पगार अनेक लोकांचा समान असेल तरीही ही सबक्वेरी अचूक काम करते. पुढील एसक्यूएल प्रश्नांसाठी फॉलो करा कोड विथ मंगेश!"
]

scenes_hi = [
    "एसक्यूएल इंटरव्यू का एक बेहद पॉपुलर सवाल: एम्प्लॉईज टेबल से सेकंड हाईएस्ट सैलरी कैसे निकालें? आइए लॉजिक समझकर स्टेप बाय स्टेप क्वेरी बनाते हैं!",
    "पहले सवाल को समझिए. हमें सेकंड हाईएस्ट डिस्टिंक्ट सैलरी चाहिए. ध्यान दीजिए कि अस्सी हजार दो बार आया है. हमें इसे केवल एक बार ही गिनना है.",
    "अब इसे कैसे सॉल्व करें? पहले मैक्सिमम सैलरी निकालिए. फिर उसे बाहर कीजिए. और बाकी बची वैल्यूज में से मैक्सिमम निकालिए. वही है हमारी सेकंड हाईएस्ट सैलरी!",
    "आइए पहले इनर क्वेरी लिखते हैं: सिलेक्ट मैक्स सैलरी फ्रॉम एम्प्लॉईज. यह हमें अस्सी हजार यानी सबसे बड़ी सैलरी देती है.",
    "अब व्हेअर सैलरी लेस दैन सबक्वेरी लगाकर अस्सी हजार को फिल्टर करते हैं. इससे दोनों अस्सी हजार वाले रिकॉर्ड्स हट जाते हैं और सत्तर, साठ और पचास हजार बचते हैं.",
    "अब आउटर मैक्स फंक्शन बचे हुए रिकॉर्ड्स को चेक करता है. सबसे बड़ी बची हुई वैल्यू है सत्तर हजार! यही हमारा सही जवाब है!",
    "इंटरव्यू टिप! अगर हाईएस्ट सैलरी डुप्लीकेट भी हो, तब भी यह सबक्वेरी मेथड हमेशा सही उत्तर देता है. ऐसे ही एसक्यूएल सवालों के लिए फॉलो कीजिए कोड विथ मंगेश!"
]

async def synth_all():
    os.makedirs("data/audio", exist_ok=True)
    full_en = "\n\n".join(scenes_en)
    full_mr = "\n\n".join(scenes_mr)
    full_hi = "\n\n".join(scenes_hi)
    
    await edge_tts.Communicate(full_en, "en-IN-NeerjaNeural", rate="-4%").save("data/audio/preset_sql_q1_second_highest_salary_en.mp3")
    print("EN synthesized:", os.path.getsize("data/audio/preset_sql_q1_second_highest_salary_en.mp3"))
    
    await edge_tts.Communicate(full_mr, "mr-IN-AarohiNeural", rate="-4%").save("data/audio/preset_sql_q1_second_highest_salary_mr.mp3")
    print("MR synthesized:", os.path.getsize("data/audio/preset_sql_q1_second_highest_salary_mr.mp3"))
    
    await edge_tts.Communicate(full_hi, "hi-IN-SwaraNeural", rate="-4%").save("data/audio/preset_sql_q1_second_highest_salary_hi.mp3")
    print("HI synthesized:", os.path.getsize("data/audio/preset_sql_q1_second_highest_salary_hi.mp3"))

if __name__ == "__main__":
    asyncio.run(synth_all())
