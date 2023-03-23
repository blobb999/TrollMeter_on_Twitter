#  ------------------------- Terms Usement -------------------------------
# 
# SENTINEL_WORDS are terms used often by most lekely paid agent provocateurs for offending a topic or user in question
#
# AGGRESSIVENESS_WORDS are terms distracting from a fair discussion, poisoning the climate and leading to nowhere which is the goal 
#
# PRO_TOPICS are topics where paid influencer are pushing, spreading or liking positive as serious threads
#
# CONTRA_TOPICS are topics where causal people are critical or sceptict
#
# PRO_ACCOUNTS are paid influencer spreading PRO_TOPICS, using AGGRESSIVENESS_WORDS and SENTINEL_WORDS
#
# CONTRA_ACCOUNTS are causal people discusing or spreading CONTRA_TOPICS but get distracted or attacked from PRO_ACCOUNTS

SENTINEL_WORDS = {'schwurbler': 1, 'verschwörungstheoretiker': 1, 'vtler': 1, 'dunning-kruger': 1, 'flacherdler': 1, 'covidiot': 1, 'aluhut': 1, 'schwachsinn': 1, 'leerdenker': 1, 'querdenker': 1, 'paulanergarten': 1, 'nachweise': 1, 'beweise': 1, 'impfgegner': 1}

AGGRESSIVENESS_WORDS = {'oberpfeife': 1, 'dummheit': 1, 'flasche': 1, 'vollpfosten': 1, 'idioten': 1, 'spinner': 1, 'rechtsextreme': 1, 'antisemit': 1, 'leugner': 1, 'rechter': 1}

PRO_TOPICS = {'co2': 1, 'klimawandel': 1, 'transgender': 1, 'flache erde': 1, 'flatearth': 1, 'alien': 1, 'impfskeptiker': 1, 'reichsbürger': 1, 'klimaleugner': 1,}

CONTRA_TOPICS = {'mondlandung': 1, 'chemtrails': 1, 'impfung': 1, 'bilderberger': 1, 'covid': 1, 'alternative': 1}

PRO_ACCOUNTS = {'@goldeneraluhut': 1, '@volksverpetzer': 1}

CONTRA_ACCOUNTS = {'@danieleganser': 1, '@kenfm': 1}
