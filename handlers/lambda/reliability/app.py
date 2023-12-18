from collections import Counter

organisation_reliabilities = {
    "Authoring Organizations": {
        "ReliefWeb": "Usually reliable",
        "humanitarianresponse": "Usually reliable",
        "Redhum": "Usually reliable",
        "Humanitarian Response": "Usually reliable",
        "Reliefweb": "Usually reliable",
        "Interpeace": "Usually reliable",
        "United Nations": "Usually reliable",
        "AllAfrica": "Usually reliable",
        "Operational Data Portal": "Usually reliable",
        "RedHum": "Usually reliable",
        "unmissions": "Usually reliable",
        "Institut National de la Statistique et de la Démographie Burkina Faso": "Usually reliable",
        "zoom-eco": "Usually reliable",
        "InfoSegura": "Usually reliable",
        "Radio Okapi": "Usually reliable",
        "Logistics Cluster": "Usually reliable",
        "rdccovidbusinesssurvey": "Usually reliable",
        "Research Gate": "Fairly Reliable",
        "Nigeria Center for Disease Control": "Usually reliable",
        "CCCM Cluster": "Usually reliable",
        "Science Direct": "Usually reliable",
        "preventepidemics": "Usually reliable",
        "Groupe Urgence - Réhabilitation - Développement": "Usually reliable",
        "The Lancet": "Usually reliable",
        "Acta Académica": "Usually reliable",
        "Oxford Academic Journals": "Usually reliable",
        "elespectador": "Usually reliable",
        "theconversation": "Usually reliable",
        "adiac-congo": "Usually reliable",
        "dailypost": "Usually reliable",
        "Analitica": "Usually reliable",
        "uni-muenchen": "Fairly Reliable",
        "actualite": "Usually reliable",
        "caracol": "Usually reliable",
        "acleddata": "Fairly Reliable",
        "Twitter": "Usually reliable",
        "Global Voices": "Usually reliable",
        "BRAC University": "Usually reliable",
        "mediacongo": "Usually reliable",
        "Common Market for Eastern and Southern Africa": "Usually reliable",
        "reliefweb": "Usually reliable",
        "British Medical Journal": "Usually reliable",
        "Telemundo": "Usually reliable", "Eurodad": "Usually reliable",
        "nkafu": "Fairly Reliable",
        "Canal 1": "Usually reliable",
        "courrierinternational": "Usually reliable",
        "MedRxiv": "Usually reliable",
        "GIGA Focus": "Fairly Reliable",
        "Business Insider": "Usually reliable",
        "msn": "Usually reliable",
        "orfonline": "Usually reliable",
        "Real Instituto Elcano Royal Institute": "Completely reliable",
        "humdata": "Usually reliable",
        "Panorama.com.ve": "Usually reliable",
        "canal1": "Usually reliable",
        "APO Group - Africa Newsroom": "Usually reliable",
        "Migration Data Portal": "Usually reliable"
    },
    "Publishing Organizations": {
        "dhakatribune": "Usually reliable",
        "International Organization for Migration": "Usually reliable",
        "impact-repository": "Usually reliable",
        "United Nations Office for the Coordination of Humanitarian Affairs": "Usually reliable",
        "UNHCR": "Usually reliable",
        "United News of Bangladesh": "Usually reliable",
        "World Health Organization": "Usually reliable",
        "United Nations High Commissioner for Refugees": "Usually reliable",
        "fscluster": "Usually reliable",
        "WASH  Cluster": "Usually reliable",
        "fews": "Usually reliable",
        "OCHA": "Usually reliable",
        "Assessment Capacities Project": "Usually reliable",
        "REACH Initiative": "Usually reliable",
        "Proyecto Migración Venezuela": "Usually reliable",
        "Food and Agriculture Organization of the United Nations": "Usually reliable",
        "World Food Programme": "Usually reliable",
        "worldbank": "Usually reliable",
        "Syrian Arab News Agency": "Usually reliable",
        "Food Security Cluster": "Usually reliable",
        "UN High Commissioner for Refugees": "Usually reliable",
        "R4V": "Usually reliable",
        "premiumtimesng": "Usually reliable",
        "United Nations Development Programme": "Usually reliable",
        "Humanitarian Needs Assessment Programme (HNAP) from  United Nations": "Usually reliable",
        "United Nations - Cameroon": "Usually reliable",
        "Northeast Syria NGO Forum": "Usually reliable",
        "Protection Cluster": "Usually reliable",
        "squarespace": "Usually reliable",
        "Instituto Nacional de Salud": "Usually reliable",
        "Displacement Tracking Matrix": "Usually reliable",
        "Human Rights Watch": "Usually reliable",
        "enabbaladi":"Usually reliable",
        "Aljazeera": "Usually reliable",
        "World Vision": "Usually reliable",
        "UN Children's Fund": "Usually reliable",
        "The Syria Report": "Usually reliable",
        "UNICEF": "Usually reliable",
        "Interpeace": "Usually reliable",
        "International Federation of Red Cross And Red Crescent Societies": "Usually reliable",
        "Le Monde": "Usually reliable",
        "El Espectador": "Usually reliable",
        "United Nations": "Usually reliable",
        "Jesuit Migrant Service": "Usually reliable",
        "Syrian Observatory for Human Rights": "Usually reliable",
        "Profamilia": "Usually reliable",
        "United Nations Population Fund": "Usually reliable",
        "Shelter Cluster": "Usually reliable",
        "Radio France Internationale": "Usually reliable",
        "World Bank": "Usually reliable",
        "Le Faso": "Usually reliable",
        "Organización Panamericana de la Salud": "Usually reliable",
        "AllAfrica": "Usually reliable",
        "ipcinfo": "Usually reliable",
        "Pan American Health Organization": "Usually reliable",
        "Semana": "Usually reliable",
        "African Development Bank": "Usually reliable",
        "careevaluations": "Usually reliable",
        "UNHCR Portal": "Usually reliable",
        "BBC Media Action": "Usually reliable",
        "Premium times": "Usually reliable",
        "Government of Burkina Faso": "Usually reliable",
        "syrianobserver": "Usually reliable",
        "Agency for Technical Cooperation and Development": "Usually reliable",
        "Actualite.cd": "Usually reliable",
        "United Nations Organization": "Usually reliable",
        "International Monetary Fund": "Usually reliable",
        "Famine Early Warning System Network": "Usually reliable",
        "Operational Data Portal": "Usually reliable",
        "Inter Sector Coordination Group": "Usually reliable",
        "INTERSOS": "Usually reliable",
        "Economic comm": "Usually reliable",
        "Burkina24": "Usually reliable",
        "Government of Nigeria": "Usually reliable",
        "The Guardian": "Usually reliable",
        "lefaso": "Usually reliable",
        "British Broadcasting Corporation": "Usually reliable",
        "Mercy Corps": "Usually reliable",
        "Women's Refugee Commission": "Usually reliable",
        "Institut National de la Statistique République Démocratique du Congo": "Usually reliable",
        "REACH": "Usually reliable",
        "thenewhumanitarian": "Usually reliable",
        "Integrated Food Security Phase Classification": "Usually reliable",
        "Syria TV": "Usually reliable",
        "Response For Venezuleans": "Usually reliable",
        "Respuesta A Venezolanos. Plataforma de Coordinación para Refugiados y Migrantes de Venezuela": "Usually reliable",
        "Sidwaya": "Usually reliable",
        "vanguardngr": "Usually reliable",
        "International Rescue Committee": "Usually reliable",
        "CARE": "Usually reliable",
        "United Nations Entity for Gender Equality and the Empowerment of Women": "Usually reliable",
        "zoom-eco": "Usually reliable",
        "crisisgroup": "Fairly Reliable",
        "Ministère de la Santé - Burkina Faso": "Usually reliable",
        "Amnesty International": "Usually reliable",
        "Thomson Reuters Foundation": "Usually reliable",
        "Cluster Protection Burkina Faso": "Usually reliable",
        "Partnership for Evidence-Based Response to COVID-19": "Usually reliable",
        "Syria in Context": "Usually reliable",
        "libyaobserver": "Usually reliable",
        "El Nacional": "Usually reliable",
        "Food and Agriculture Organization": "Usually reliable",
        "Andolu Agency": "Usually reliable",
        "CARE International - United Kingdom": "Usually reliable",
        "Syria Direct": "Usually reliable",
        "globalprotectioncluster": "Usually reliable",
        "eltiempo": "Usually reliable",
        "BBVA": "Usually reliable",
        "unwomen": "Usually reliable",
        "Economic Commission for Latin America and the Caribbean": "Usually reliable",
        "Comisión Argentina para Refugiados y Migrantes": "Usually reliable",
        "International Crisis Group": "Usually reliable",
        "Deutsche Welle": "Usually reliable",
        "The New Humanitarian": "Usually reliable",
        "Government of Colombia": "Usually reliable",
        "Health Cluster": "Usually reliable",
        "Médecins Sans Frontières": "Usually reliable",
        "Danish Refugee Council": "Usually reliable",
        "savethechildren": "Usually reliable",
        "The Syria report": "Usually reliable",
        "Overseas Development Institute": "Usually reliable",
        "Departamento Administrativo Nacional de Estadística": "Usually reliable",
        "Save the Children": "Usually reliable",
        "Politico": "Usually reliable",
        "internal-displacement": "Usually reliable",
        "migracioncolombia": "Usually reliable",
        "Logistics Cluster": "Usually reliable",
        "El Comercio": "Usually reliable",
        "middleeastmonitor": "Usually reliable",
        "alwatan": "Usually reliable",
        "Council on Foreign Relations": "Usually reliable",
        "theguardian": "Usually reliable",
        "The Asia Foundation": "Usually reliable",
        "Jesuit Refugee Service": "Usually reliable",
        "El Colombiano": "Usually reliable",
        "Primature de la Republique Democratique du Congo": "Usually reliable",
        "Caribe Afirmativo": "Usually reliable",
        "Corporación Sisma Mujer": "Usually reliable",
        "fasoamazone": "Usually reliable",
        "Inter-American Development Bank": "Usually reliable",
        "International Labour Organization": "Usually reliable",
        "El Universal": "Usually reliable",
        "Asociación de Venezolanos en la República Argentina": "Usually reliable",
        "laborpresse": "Usually reliable",
        "Portafolio": "Usually reliable",
        "United Nations Children's Fund": "Usually reliable",
        "washcluster": "Usually reliable",
        "opendatadrc": "Usually reliable",
        "Government of Bangladesh": "Usually reliable",
        "UN Country Team in Bangladesh": "Usually reliable",
        "Action Contre la Faim": "Usually reliable",
        "UN Office of the High Commissioner for Human Rights": "Usually reliable",
        "UN Educational, Scientific and Cultural Organization": "Usually reliable",
        "BRAC": "Usually reliable",
        "France24": "Usually reliable",
        "Today Online": "Usually reliable",
        "libyanexpress": "Usually reliable",
        "ennonline": "Usually reliable",
        "Government Information Service": "Usually reliable",
        "sheltercluster": "Usually reliable",
        "Norwegian Refugee Council": "Usually reliable",
        "Afrik": "Usually reliable",
        "syriadirect": "Usually reliable",
        "lemonde": "Usually reliable",
        "TV5MONDE": "Usually reliable",
        "Instituto Nacional de Estadística": "Usually reliable",
        "libyaherald": "Usually reliable",
        "El Tiempo": "Usually reliable",
        "Servicio Jesuita a Migrantes": "Usually reliable",
        "UN Development Programme": "Usually reliable",
        "ProBogotá": "Usually reliable",
        "middleeasteye": "Usually reliable",
        "Sputnik Mundo": "Usually reliable",
        "El País": "Usually reliable",
        "Cash Working Group": "Usually reliable",
        "save the children international": "Usually reliable",
        "London School of Economics and Political Science": "Usually reliable",
        "thenationonlineng": "Usually reliable",
        "Joining Forces": "Usually reliable",
        "NES Sites and Settlements Working Group": "Usually reliable",
        "Autonomous Authority of North and East Syria": "Usually reliable",
        "syriahr": "Usually reliable",
        "Refugees International": "Usually reliable",
        "Vanguardia": "Usually reliable",
        "ACNUR": "Completely reliable",
        "Punch Nigeria": "Usually reliable",
        "Caritas": "Usually reliable",
        "Enab Baladi": "Usually reliable",
        "Ground Truth Solutions": "Usually reliable",
        "Mixed Migration Centre": "Usually reliable",
        "Amazon AWS": "Usually reliable",
        "7sur7": "Usually reliable",
        "Cuso International": "Usually reliable",
        "The Washington Post": "Usually reliable",
        "ORGANIZACION INTERNACIONAL PARA LAS MIGRACIONES": "Usually reliable",
        "refugeesinternational": "Usually reliable",
        "alwatanonline": "Usually reliable",
        "Fundación Panamericana para el Desarrollo -Colombia": "Usually reliable",
        "laopinion": "Usually reliable",
        "UN Organization Stabilization Mission in the Democratic Republic of the Congo": "Usually reliable",
        "Local Coordination Team": "Usually reliable",
        "Nigeria Center for Disease Control": "Usually reliable",
        "Emol": "Usually reliable",
        "CCCM Cluster": "Usually reliable",
        "RCN": "Usually reliable",
        "Migración Colombia": "Usually reliable",
        "Agencia EFE": "Usually reliable",
        "afghanistan-analysts": "Usually reliable",
        "Organization of American States": "Usually reliable",
        "Crónica": "Usually reliable",
        "UN Country Team in Ecuador": "Usually reliable",
        "Ouestaf": "Usually reliable",
        "Media Congo": "Usually reliable",
        "Africanews": "Usually reliable",
        "African Union": "Usually reliable",
        "Programa Venezolano de Educación - Acción en Derechos Humanos": "Usually reliable",
        "Internal Displacement Monitoring Centre": "Usually reliable",
        "CARE International": "Usually reliable",
        "afia-amanigrandslacs": "Usually reliable",
        "European Civil Protection and Humanitarian Aid Operations": "Usually reliable",
        "The Libya Observer": "Usually reliable",
        "Imperial College London": "Usually reliable",
        "congoactu": "Usually reliable",
        "Cable News Network": "Usually reliable",
        "Radio Nacional De Colombia": "Usually reliable",
        "apnews": "Usually reliable",
        "UNOCHA EHP": "Usually reliable",
        "Swedish International Development Cooperation Agency": "Usually reliable",
        "British Red Cross": "Completely reliable",
        "SPUTNIK MUNDO": "Usually reliable",
        "Government of Afghanistan": "Usually reliable",
        "allodocteurs": "Usually reliable",
        "Instituto de estudios para el desarrollo y la paz": "Usually reliable",
        "actalliance": "Fairly Reliable",
        "US Agency for International Development": "Usually reliable",
        "Associazione Volontari per il Servizio Internazionale": "Usually reliable",
        "Libyan Express": "Usually reliable",
        "UN News Service": "Usually reliable",
        "Red Cross Society of Bosnia and Herzegovina": "Usually reliable",
        "Christian Science Monitor": "Usually reliable",
        "reuters-af": "Usually reliable",
        "International Committee of the Red Cross": "Usually reliable",
        "agenceecofin": "Usually reliable",
        "Afghanistan Education in Emergencies Working Group": "Fairly Reliable",
        "Programa de Estudios Sociales en Salud": "Fairly Reliable",
        "Somos Iberoamérica": "Usually reliable",
        "faso-actu": "Usually reliable",
        "DEPARTAMENTO DE INVESTIGACION Y ESTUDIOS MIGRATORIOS INSTITUTO NACIONAL DE MIGRACION": "Usually reliable",
        "uniandes": "Usually reliable",
        "Banco de la República": "Usually reliable",
        "International Finance Corporation": "Usually reliable",
        "sky": "Usually reliable",
        "Infobae": "Usually reliable",
        "European Union External Action": "Usually reliable",
        "Vanguard News": "Usually reliable",
        "congovirtuel": "Usually reliable",
        "Education Cluster": "Usually reliable",
        "ouaga24": "Usually reliable",
        "dailysabah": "Usually reliable",
        "Active Learning Network for Accountability and Performance in Humanitarian Action": "Usually reliable",
        "The Syrian Observer": "Usually reliable",
        "Al-Araby": "Usually reliable",
        "Gouvernement de la République Démocratique du Congo": "Usually reliable",
        "Caritas Venezuela": "Usually reliable",
        "thisdaylive": "Usually reliable",
        "UN Economic and Social Commission for Western Asia": "Usually reliable",
        "Hoy Diario de Magdalena": "Usually reliable",
        "Tishreen news": "Usually reliable",
        "Soy Chile": "Usually reliable",
        "European Commission": "Usually reliable",
        "Adventist Development and Relief Agency International": "Usually reliable",
        "Jeune Afrique": "Usually reliable",
        "issuu.com": "Usually reliable",
        "financialafrik": "Usually reliable",
        "El Impulso.Com": "Usually reliable",
        "Sham FM": "Usually reliable",
        "Action Against Hunger": "Usually reliable",
        "El Universo": "Usually reliable",
        "Panorama": "Usually reliable",
        "Oxford Academic Journals": "Usually reliable",
        "Forbes": "Usually reliable",
        "La Republica": "Usually reliable",
        "Observatorio Feminicidios Colombia": "Usually reliable",
        "Nextier SPD": "Usually reliable",
        "Defensoría del Pueblo Colombia": "Usually reliable",
        "africacdc": "Usually reliable",
        "Dhaka Tribune": "Usually reliable",
        "Citizen's Platform for SDGs, Bangladesh": "Usually reliable",
        "Ministère de l'Economie, des Finances et du Développement": "Usually reliable",
        "Africa Centres for Disease Control and Prevention": "Usually reliable",
        "Food Security and Nutrition Analysis Unit": "Usually reliable",
        "Plan International": "Usually reliable",
        "dailypost": "Usually reliable",
        "LePoint": "Usually reliable",
        "Intertional Federation of Red Cross": "Usually reliable",
        "United States Agency for International Development": "Usually reliable",
        "Gestion": "Usually reliable",
        "Diario del Sur": "Usually reliable",
        "United Nations Office on Drugs and Crime": "Usually reliable",
        "Ministère de la Santé (République Démocratique du Congo)": "Usually reliable",
        "W Radio": "Usually reliable",
        "COOPI - Cooperazione Internazionale": "Usually reliable",
        "Perfil": "Usually reliable",
        "Cruz Roja Ecuatoriana": "Usually reliable",
        "channelstv": "Usually reliable",
        "FUNDACIÓN DE AYUDA SOCIAL DE LAS IGLESIAS CRISTIANAS": "Usually reliable",
        "Xinhuanet": "Usually reliable",
        "Salon Syria": "Usually reliable",
        "Grupo Interagencial sobre Flujos Migratorios Mixtos": "Usually reliable",
        "Analitica": "Usually reliable",
        "nih": "Usually reliable",
        "Washington Office on Latin America": "Usually reliable",
        "The Committee for the Coordination of Statistical Activities": "Usually reliable",
        "uni-muenchen": "Fairly Reliable",
        "La República": "Usually reliable",
        "internationalmedicalcorps": "Usually reliable",
        "República de las Ideas": "Usually reliable",
        "panampost": "Usually reliable",
        "La Razón": "Usually reliable",
        "Diario De Lara La Prensa": "Usually reliable",
        "Efecto Cocuyo": "Usually reliable",
        "infosplus": "Usually reliable",
        "Unidad Nacional para la Gestión del Riesgo de Desastres": "Usually reliable",
        "La Nación": "Usually reliable",
        "Ministerio de Salud y Protección Social": "Usually reliable",
        "congoindependant": "Usually reliable",
        "Gender in Humanitarian Action Working Group": "Usually reliable",
        "El Telégrafo": "Usually reliable",
        "Diario del Norte": "Usually reliable",
        "thedefensepost": "Usually reliable",
        "United Nation International Children's Emergency Fund": "Usually reliable",
        "Cordaid": "Fairly Reliable",
        "Organisation for Economic Co-operation and Development": "Usually reliable",
        "El Heraldo": "Usually reliable",
        "downtoearth": "Usually reliable",
        "El Nuevo Siglo": "Usually reliable",
        "WASH Cluster": "Usually reliable",
        "Association pour la Promotion et l’Intégration de la Jeunesse du Centre Nord": "Usually reliable",
        "Insightcrime": "Usually reliable",
        "Diario As Colombia": "Usually reliable",
        "NBC News": "Usually reliable",
        "Noticiero Digital": "Usually reliable",
        "diarioeltiempo": "Usually reliable",
        "issafrica": "Usually reliable",
        "El Diario De Los Andes": "Usually reliable",
        "La fm": "Usually reliable",
        "Ministry of Public Health (Democratic Republic of Congo)": "Usually reliable",
        "mediacongo": "Usually reliable",
        "National Bureau of Statistic": "Usually reliable",
        "El Destape Web": "Usually reliable",
        "Nutrition Cluster": "Usually reliable",
        "Oxfam": "Usually reliable",
        "Ojo Público": "Usually reliable",
        "The Economist": "Usually reliable",
        "National Meteorological Agency Burkina Faso": "Usually reliable",
        "Al-Khabar": "Usually reliable",
        "Interactuar": "Usually reliable",
        "UN Relief and Works Agency for Palestine Refugees in the Near East": "Usually reliable",
        "lalibre": "Usually reliable",
        "larepublica": "Usually reliable",
        "El Cronista": "Usually reliable",
        "mailchi": "Usually reliable",
        "El siglo": "Usually reliable",
        "Common Market for Eastern and Southern Africa": "Usually reliable",
        "congodurable": "Usually reliable",
        "Clarín": "Usually reliable",
        "rojavainformationcenter": "Usually reliable",
        "Manusher Jonno Foundation": "Usually reliable",
        "Consultative Group to Assist the Poor (CGAP)": "Usually reliable",
        "UN News": "Usually reliable",
        "Departamento de Extranjería y Migración Chile": "Usually reliable",
        "voanews": "Usually reliable",
        "Ministerio de Educación": "Usually reliable",
        "North Press Agency": "Usually reliable",
        "Al Watan online": "Usually reliable",
        "Protection Cluster Syria": "Usually reliable",
        "The National News": "Usually reliable",
        "Humvenezuela": "Usually reliable",
        "digitalcongo": "Usually reliable",
        "Primicia": "Usually reliable",
        "care-international": "Usually reliable",
        "Peace News": "Usually reliable",
        "wvi": "Usually reliable",
        "Ultimas Noticias": "Usually reliable",
        "The Adecco Group": "Usually reliable",
        "Performance Monitoring for Action": "Usually reliable",
        "Version Final": "Usually reliable",
        "Asociación Mujeres Unidas, Migrantes y Refugiadas en Argentina": "Usually reliable",
        "El Tribuno": "Usually reliable",
        "infobascongo": "Usually reliable",
        "nairametrics": "Usually reliable",
        "habarirdc": "Unreliable",
        "prensalibre": "Usually reliable",
        "fasozine": "Usually reliable",
        "saharareporters": "Usually reliable",
        "stereo100": "Usually reliable",
        "International Organization for Migration and Displacement Tracking Matrix": "Usually reliable",
        "cgtn": "Usually reliable",
        "ktpress": "Usually reliable",
        "venezuela al dia": "Usually reliable",
        "Agence Française de Développement": "Usually reliable",
        "usembassy": "Usually reliable",
        "wradio": "Usually reliable",
        "redcross": "Usually reliable",
        "Americas Quarterly": "Usually reliable",
        "fragomen": "Usually reliable",
        "GRUPO BANCO MUNDIAL": "Completely reliable",
        "Cruz Roja Argentina": "Completely reliable",
        "GIGA Focus": "Fairly Reliable",
        "Aporrea": "Usually reliable",
        "Un Minuto Radio": "Usually reliable",
        "acento": "Usually reliable",
        "EV TVmiami": "Usually reliable",
        "Ministère de la santé (Burkina Faso)": "Usually reliable",
        "Efecto cocuyo": "Completely reliable",
        "lasillavacia": "Usually reliable",
        "Modern Diplomacy": "Usually reliable",
        "NIRAPAD": "Usually reliable",
        "headtopics": "Usually reliable",
        "Center for Global Development": "Usually reliable",
        "elvenezolanocolombia": "Usually reliable",
        "albaathmedia": "Usually reliable",
        "El Frente": "Usually reliable",
        "The Tribune": "Usually reliable",
        "elanrdc": "Usually reliable",
        "Syria Health Network": "Usually reliable",
        "Al Jazeera": "Usually reliable",
        "Revista Entornos": "Usually reliable",
        "Assistance Coordination Unit": "Usually reliable",
        "Associated Press": "Usually reliable",
        "Syria Times": "Usually reliable",
        "BBC Afrique": "Usually reliable",
        "60_decibels": "Usually reliable",
        "TRT World": "Usually reliable",
        "Rojava Information Center": "Usually reliable",
        "Dirección del Trabajo, Chile": "Usually reliable",
        "Caritas Germany": "Usually reliable",
        "Aleteia": "Usually reliable",
        "slobodnaevropa":"Usually reliable",
        "vivafrik": "Usually reliable",
        "Sistema Económico Latinoamericano y del Caribe": "Usually reliable",
        "The Independent": "Usually reliable",
        "El periodiquito": "Usually reliable",
        "Pulzo": "Usually reliable",
        "efectococuyo": "Usually reliable",
        "Manos VeneGuayas": "Usually reliable",
        "congosynthese": "Usually reliable",
        "allafrica": "Usually reliable",
        "La Tercera": "Usually reliable",
        "Garda World": "Usually reliable",
        "Arab News": "Usually reliable",
        "CBC": "Usually reliable",
        "Bethany Christian Services": "Usually reliable",
        "La Opinión": "Usually reliable",
        "caracoltv": "Usually reliable",
        "lafm.": "Usually reliable",
        "areion24": "Usually reliable",
        "environews-rdc": "Usually reliable",
        "Amani Institute": "Fairly Reliable",
        "Alcaldía de Bogotá": "Usually reliable",
        "MDZ Diario de Mendoza": "Usually reliable",
        "Middle East Institute": "Usually reliable",
        "Ministerio de Vivienda": "Usually reliable",
        "Permanent Interstate Committee for Drought Control in the Sahel": "Usually reliable",
        "El Periódico": "Usually reliable",
        "El Ceo": "Usually reliable",
        "interkinois": "Usually reliable",
        "iagua": "Usually reliable",
        "Doctors Without borders": "Usually reliable",
        "Razón Pública": "Usually reliable",
        "Diario Libre": "Usually reliable",
        "Radio Télévision Belge Francophone": "Usually reliable",
        "Daraj": "Usually reliable",
        "Cripto Noticias": "Usually reliable",
        "Child protection Cox's Bazar sub sector": "Usually reliable",
        "globalcitizen": "Usually reliable",
        "elheraldo": "Usually reliable",
        "acpcongo": "Usually reliable",
        "voaafrique": "Usually reliable",
        "eje21": "Usually reliable",
        "forumdesas": "Usually reliable",
        "radiookapi": "Usually reliable",
        "mprnews": "Usually reliable",
        "borgenmagazine": "Usually reliable",
        "presidencia": "Usually reliable",
        "tchadinfos": "Fairly Reliable",
        "newstatesman": "Usually reliable",
        "US Department of State - Humanitarian Information Unit": "Usually reliable",
        "faapa": "Usually reliable",
        "bdnews24": "Usually reliable",
        "eluniverso": "Usually reliable",
        "Emergency Telecommunications Cluster": "Usually reliable",
        "Informe21.Com": "Usually reliable",
        "Reporte Confidencial": "Usually reliable",
        "CCCM: Shelter and NFI": "Usually reliable",
        "Primer Informe": "Usually reliable",
        "Runrun": "Usually reliable",
        "Grupo Bancolombia": "Usually reliable",
        "International Medical Corps": "Usually reliable",
        "MedGlobal": "Usually reliable",
        "Seervicio jesuita a refugiados": "Usually reliable",
        "Sudanese Red Crescent Society": "Usually reliable",
        "Noticias curazao": "Usually reliable",
        "Meganoticias": "Usually reliable",
        "Atlantic Council": "Usually reliable",
        "Caracol Diario": "Usually reliable",
        "Newsday": "Usually reliable",
        "Hoy Digital": "Usually reliable",
        "New Lines Institute": "Usually reliable",
        "Syrian Network for Human Rights": "Usually reliable",
        "Center for Operational Analysis and Research": "Usually reliable",
        "El Informador": "Fairly Reliable",
        "thecable": "Usually reliable",
        "n1info": "Usually reliable",
        "Ministerio de Salud y Desarrollo Social": "Usually reliable",
        "Publimetro": "Usually reliable",
        "Australian Agency for International Development": "Usually reliable",
        "Physicians for Human Rights": "Usually reliable",
        "securitycouncilreport": "Fairly Reliable",
        "Global News": "Usually reliable",
        "Federal Ministry of Health (Nigeria)": "Usually reliable",
        "Observatorio Venezolano de Migración": "Usually reliable",
        "iMMAP": "Usually reliable",
        "Middle East Eye": "Usually reliable",
        "theeastafrican": "Usually reliable",
        "Notimerica": "Usually reliable",
        "VOA News": "Usually reliable",
        "Diario La Nacion": "Fairly Reliable",
        "santetropicale": "Usually reliable",
        "actu24": "Usually reliable",
        "Nextier SPD (Security, Peace, and Development)": "Usually reliable",
        "CR hoy.Com": "Usually reliable",
        "bhrt": "Usually reliable",
        "Insecurity Insight": "Usually reliable",
        "El Mostrador": "Usually reliable",
        "Reuters": "Usually reliable",
        "El Observador": "Usually reliable",
        "zonacero": "Usually reliable",
        "Solidarités International": "Usually reliable",
        "salaamgateway": "Usually reliable",
        "Syrian Centre for Policy Research": "Usually reliable",
        "237actu": "Fairly Reliable",
        "La Cuarta": "Usually reliable",
        "ecupunto": "Usually reliable",
        "UNHCR Innovation": "Usually reliable",
        "la-croix": "Usually reliable",
        "Tu Barco": "Usually reliable"
    }
}

authoring_organisations = list(organisation_reliabilities['Authoring Organizations'].keys())
publishing_organisations = list(organisation_reliabilities['Publishing Organizations'].keys())


def return_org_reliability(publishing_org, authoring_org=None):
    """ Returns the reliability score of the organizations """
    lst = []
    if authoring_org is None or not authoring_org:
        if publishing_org not in publishing_organisations:
            lst.append('')
        else:
            lst.append(organisation_reliabilities['Publishing Organizations'][publishing_org])
    else:
        for author_org in authoring_org:
            if author_org in authoring_organisations:
                lst.append(organisation_reliabilities['Authoring Organizations'][author_org])
    cnt_items = Counter(lst)
    return cnt_items.most_common(1)[0][0] if cnt_items else ""


def lambda_handler(event, context):
    """ Main entry point for lambda handler """
    if "publishing_organization" not in event:
        return {
            "statusCode": 200,
            "prediction": ""
        }
    publishing_org = event["publishing_organization"]
    authoring_org = event["authoring_organization"] if "authoring_organization" in event else None

    return {
        "statusCode": 200,
        "prediction": return_org_reliability(
            publishing_org, authoring_org
        )
    }
