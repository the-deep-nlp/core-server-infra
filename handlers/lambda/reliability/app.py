from collections import Counter
from enum import Enum


class Reliability(Enum):
    """List of Reliability Scores"""

    UNRELIABLE = 0
    USUALLY_RELIABLE = 1
    FAIRLY_RELIABLE = 2
    COMPLETELY_RELIABLE = 3

    @classmethod
    def id_to_scoretype(cls, score_type: Enum) -> str:
        """Mapping function"""
        id_to_score_mapping = {
            Reliability.UNRELIABLE: "unreliable",
            Reliability.USUALLY_RELIABLE: "Usually reliable",
            Reliability.FAIRLY_RELIABLE: "Fairly Reliable",
            Reliability.COMPLETELY_RELIABLE: "Completely reliable",
        }
        return id_to_score_mapping.get(score_type, "unreliable")


organisation_reliabilities = {
    "Authoring Organizations": {
        "ReliefWeb": Reliability.USUALLY_RELIABLE,
        "humanitarianresponse": Reliability.USUALLY_RELIABLE,
        "Redhum": Reliability.USUALLY_RELIABLE,
        "Humanitarian Response": Reliability.USUALLY_RELIABLE,
        "Reliefweb": Reliability.USUALLY_RELIABLE,
        "Interpeace": Reliability.USUALLY_RELIABLE,
        "United Nations": Reliability.USUALLY_RELIABLE,
        "AllAfrica": Reliability.USUALLY_RELIABLE,
        "Operational Data Portal": Reliability.USUALLY_RELIABLE,
        "RedHum": Reliability.USUALLY_RELIABLE,
        "unmissions": Reliability.USUALLY_RELIABLE,
        "Institut National de la Statistique et de la Démographie Burkina Faso": Reliability.USUALLY_RELIABLE,
        "zoom-eco": Reliability.USUALLY_RELIABLE,
        "InfoSegura": Reliability.USUALLY_RELIABLE,
        "Radio Okapi": Reliability.USUALLY_RELIABLE,
        "Logistics Cluster": Reliability.USUALLY_RELIABLE,
        "rdccovidbusinesssurvey": Reliability.USUALLY_RELIABLE,
        "Research Gate": Reliability.FAIRLY_RELIABLE,
        "Nigeria Center for Disease Control": Reliability.USUALLY_RELIABLE,
        "CCCM Cluster": Reliability.USUALLY_RELIABLE,
        "Science Direct": Reliability.USUALLY_RELIABLE,
        "preventepidemics": Reliability.USUALLY_RELIABLE,
        "Groupe Urgence - Réhabilitation - Développement": Reliability.USUALLY_RELIABLE,
        "The Lancet": Reliability.USUALLY_RELIABLE,
        "Acta Académica": Reliability.USUALLY_RELIABLE,
        "Oxford Academic Journals": Reliability.USUALLY_RELIABLE,
        "elespectador": Reliability.USUALLY_RELIABLE,
        "theconversation": Reliability.USUALLY_RELIABLE,
        "adiac-congo": Reliability.USUALLY_RELIABLE,
        "dailypost": Reliability.USUALLY_RELIABLE,
        "Analitica": Reliability.USUALLY_RELIABLE,
        "uni-muenchen": Reliability.FAIRLY_RELIABLE,
        "actualite": Reliability.USUALLY_RELIABLE,
        "caracol": Reliability.USUALLY_RELIABLE,
        "acleddata": Reliability.FAIRLY_RELIABLE,
        "Twitter": Reliability.USUALLY_RELIABLE,
        "Global Voices": Reliability.USUALLY_RELIABLE,
        "BRAC University": Reliability.USUALLY_RELIABLE,
        "mediacongo": Reliability.USUALLY_RELIABLE,
        "Common Market for Eastern and Southern Africa": Reliability.USUALLY_RELIABLE,
        "reliefweb": Reliability.USUALLY_RELIABLE,
        "British Medical Journal": Reliability.USUALLY_RELIABLE,
        "Telemundo": Reliability.USUALLY_RELIABLE,
        "Eurodad": Reliability.USUALLY_RELIABLE,
        "nkafu": Reliability.FAIRLY_RELIABLE,
        "Canal 1": Reliability.USUALLY_RELIABLE,
        "courrierinternational": Reliability.USUALLY_RELIABLE,
        "MedRxiv": Reliability.USUALLY_RELIABLE,
        "GIGA Focus": Reliability.FAIRLY_RELIABLE,
        "Business Insider": Reliability.USUALLY_RELIABLE,
        "msn": Reliability.USUALLY_RELIABLE,
        "orfonline": Reliability.USUALLY_RELIABLE,
        "Real Instituto Elcano Royal Institute": Reliability.COMPLETELY_RELIABLE,
        "humdata": Reliability.USUALLY_RELIABLE,
        "Panorama.com.ve": Reliability.USUALLY_RELIABLE,
        "canal1": Reliability.USUALLY_RELIABLE,
        "APO Group - Africa Newsroom": Reliability.USUALLY_RELIABLE,
        "Migration Data Portal": Reliability.USUALLY_RELIABLE,
    },
    "Publishing Organizations": {
        "dhakatribune": Reliability.USUALLY_RELIABLE,
        "International Organization for Migration": Reliability.USUALLY_RELIABLE,
        "impact-repository": Reliability.USUALLY_RELIABLE,
        "United Nations Office for the Coordination of Humanitarian Affairs": Reliability.USUALLY_RELIABLE,
        "UNHCR": Reliability.USUALLY_RELIABLE,
        "United News of Bangladesh": Reliability.USUALLY_RELIABLE,
        "World Health Organization": Reliability.USUALLY_RELIABLE,
        "United Nations High Commissioner for Refugees": Reliability.USUALLY_RELIABLE,
        "fscluster": Reliability.USUALLY_RELIABLE,
        "WASH  Cluster": Reliability.USUALLY_RELIABLE,
        "fews": Reliability.USUALLY_RELIABLE,
        "OCHA": Reliability.USUALLY_RELIABLE,
        "Assessment Capacities Project": Reliability.USUALLY_RELIABLE,
        "REACH Initiative": Reliability.USUALLY_RELIABLE,
        "Proyecto Migración Venezuela": Reliability.USUALLY_RELIABLE,
        "Food and Agriculture Organization of the United Nations": Reliability.USUALLY_RELIABLE,
        "World Food Programme": Reliability.USUALLY_RELIABLE,
        "worldbank": Reliability.USUALLY_RELIABLE,
        "Syrian Arab News Agency": Reliability.USUALLY_RELIABLE,
        "Food Security Cluster": Reliability.USUALLY_RELIABLE,
        "UN High Commissioner for Refugees": Reliability.USUALLY_RELIABLE,
        "R4V": Reliability.USUALLY_RELIABLE,
        "premiumtimesng": Reliability.USUALLY_RELIABLE,
        "United Nations Development Programme": Reliability.USUALLY_RELIABLE,
        "Humanitarian Needs Assessment Programme (HNAP) from  United Nations": Reliability.USUALLY_RELIABLE,
        "United Nations - Cameroon": Reliability.USUALLY_RELIABLE,
        "Northeast Syria NGO Forum": Reliability.USUALLY_RELIABLE,
        "Protection Cluster": Reliability.USUALLY_RELIABLE,
        "squarespace": Reliability.USUALLY_RELIABLE,
        "Instituto Nacional de Salud": Reliability.USUALLY_RELIABLE,
        "Displacement Tracking Matrix": Reliability.USUALLY_RELIABLE,
        "Human Rights Watch": Reliability.USUALLY_RELIABLE,
        "enabbaladi": Reliability.USUALLY_RELIABLE,
        "Aljazeera": Reliability.USUALLY_RELIABLE,
        "World Vision": Reliability.USUALLY_RELIABLE,
        "UN Children's Fund": Reliability.USUALLY_RELIABLE,
        "The Syria Report": Reliability.USUALLY_RELIABLE,
        "UNICEF": Reliability.USUALLY_RELIABLE,
        "Interpeace": Reliability.USUALLY_RELIABLE,
        "International Federation of Red Cross And Red Crescent Societies": Reliability.USUALLY_RELIABLE,
        "Le Monde": Reliability.USUALLY_RELIABLE,
        "El Espectador": Reliability.USUALLY_RELIABLE,
        "United Nations": Reliability.USUALLY_RELIABLE,
        "Jesuit Migrant Service": Reliability.USUALLY_RELIABLE,
        "Syrian Observatory for Human Rights": Reliability.USUALLY_RELIABLE,
        "Profamilia": Reliability.USUALLY_RELIABLE,
        "United Nations Population Fund": Reliability.USUALLY_RELIABLE,
        "Shelter Cluster": Reliability.USUALLY_RELIABLE,
        "Radio France Internationale": Reliability.USUALLY_RELIABLE,
        "World Bank": Reliability.USUALLY_RELIABLE,
        "Le Faso": Reliability.USUALLY_RELIABLE,
        "Organización Panamericana de la Salud": Reliability.USUALLY_RELIABLE,
        "AllAfrica": Reliability.USUALLY_RELIABLE,
        "ipcinfo": Reliability.USUALLY_RELIABLE,
        "Pan American Health Organization": Reliability.USUALLY_RELIABLE,
        "Semana": Reliability.USUALLY_RELIABLE,
        "African Development Bank": Reliability.USUALLY_RELIABLE,
        "careevaluations": Reliability.USUALLY_RELIABLE,
        "UNHCR Portal": Reliability.USUALLY_RELIABLE,
        "BBC Media Action": Reliability.USUALLY_RELIABLE,
        "Premium times": Reliability.USUALLY_RELIABLE,
        "Government of Burkina Faso": Reliability.USUALLY_RELIABLE,
        "syrianobserver": Reliability.USUALLY_RELIABLE,
        "Agency for Technical Cooperation and Development": Reliability.USUALLY_RELIABLE,
        "Actualite.cd": Reliability.USUALLY_RELIABLE,
        "United Nations Organization": Reliability.USUALLY_RELIABLE,
        "International Monetary Fund": Reliability.USUALLY_RELIABLE,
        "Famine Early Warning System Network": Reliability.USUALLY_RELIABLE,
        "Operational Data Portal": Reliability.USUALLY_RELIABLE,
        "Inter Sector Coordination Group": Reliability.USUALLY_RELIABLE,
        "INTERSOS": Reliability.USUALLY_RELIABLE,
        "Economic comm": Reliability.USUALLY_RELIABLE,
        "Burkina24": Reliability.USUALLY_RELIABLE,
        "Government of Nigeria": Reliability.USUALLY_RELIABLE,
        "The Guardian": Reliability.USUALLY_RELIABLE,
        "lefaso": Reliability.USUALLY_RELIABLE,
        "British Broadcasting Corporation": Reliability.USUALLY_RELIABLE,
        "Mercy Corps": Reliability.USUALLY_RELIABLE,
        "Women's Refugee Commission": Reliability.USUALLY_RELIABLE,
        "Institut National de la Statistique République Démocratique du Congo": Reliability.USUALLY_RELIABLE,
        "REACH": Reliability.USUALLY_RELIABLE,
        "thenewhumanitarian": Reliability.USUALLY_RELIABLE,
        "Integrated Food Security Phase Classification": Reliability.USUALLY_RELIABLE,
        "Syria TV": Reliability.USUALLY_RELIABLE,
        "Response For Venezuleans": Reliability.USUALLY_RELIABLE,
        "Respuesta A Venezolanos. Plataforma de Coordinación para Refugiados y Migrantes de Venezuela": Reliability.USUALLY_RELIABLE,  # noqa
        "Sidwaya": Reliability.USUALLY_RELIABLE,
        "vanguardngr": Reliability.USUALLY_RELIABLE,
        "International Rescue Committee": Reliability.USUALLY_RELIABLE,
        "CARE": Reliability.USUALLY_RELIABLE,
        "United Nations Entity for Gender Equality and the Empowerment of Women": Reliability.USUALLY_RELIABLE,
        "zoom-eco": Reliability.USUALLY_RELIABLE,
        "crisisgroup": Reliability.FAIRLY_RELIABLE,
        "Ministère de la Santé - Burkina Faso": Reliability.USUALLY_RELIABLE,
        "Amnesty International": Reliability.USUALLY_RELIABLE,
        "Thomson Reuters Foundation": Reliability.USUALLY_RELIABLE,
        "Cluster Protection Burkina Faso": Reliability.USUALLY_RELIABLE,
        "Partnership for Evidence-Based Response to COVID-19": Reliability.USUALLY_RELIABLE,
        "Syria in Context": Reliability.USUALLY_RELIABLE,
        "libyaobserver": Reliability.USUALLY_RELIABLE,
        "El Nacional": Reliability.USUALLY_RELIABLE,
        "Food and Agriculture Organization": Reliability.USUALLY_RELIABLE,
        "Andolu Agency": Reliability.USUALLY_RELIABLE,
        "CARE International - United Kingdom": Reliability.USUALLY_RELIABLE,
        "Syria Direct": Reliability.USUALLY_RELIABLE,
        "globalprotectioncluster": Reliability.USUALLY_RELIABLE,
        "eltiempo": Reliability.USUALLY_RELIABLE,
        "BBVA": Reliability.USUALLY_RELIABLE,
        "unwomen": Reliability.USUALLY_RELIABLE,
        "Economic Commission for Latin America and the Caribbean": Reliability.USUALLY_RELIABLE,
        "Comisión Argentina para Refugiados y Migrantes": Reliability.USUALLY_RELIABLE,
        "International Crisis Group": Reliability.USUALLY_RELIABLE,
        "Deutsche Welle": Reliability.USUALLY_RELIABLE,
        "The New Humanitarian": Reliability.USUALLY_RELIABLE,
        "Government of Colombia": Reliability.USUALLY_RELIABLE,
        "Health Cluster": Reliability.USUALLY_RELIABLE,
        "Médecins Sans Frontières": Reliability.USUALLY_RELIABLE,
        "Danish Refugee Council": Reliability.USUALLY_RELIABLE,
        "savethechildren": Reliability.USUALLY_RELIABLE,
        "The Syria report": Reliability.USUALLY_RELIABLE,
        "Overseas Development Institute": Reliability.USUALLY_RELIABLE,
        "Departamento Administrativo Nacional de Estadística": Reliability.USUALLY_RELIABLE,
        "Save the Children": Reliability.USUALLY_RELIABLE,
        "Politico": Reliability.USUALLY_RELIABLE,
        "internal-displacement": Reliability.USUALLY_RELIABLE,
        "migracioncolombia": Reliability.USUALLY_RELIABLE,
        "Logistics Cluster": Reliability.USUALLY_RELIABLE,
        "El Comercio": Reliability.USUALLY_RELIABLE,
        "middleeastmonitor": Reliability.USUALLY_RELIABLE,
        "alwatan": Reliability.USUALLY_RELIABLE,
        "Council on Foreign Relations": Reliability.USUALLY_RELIABLE,
        "theguardian": Reliability.USUALLY_RELIABLE,
        "The Asia Foundation": Reliability.USUALLY_RELIABLE,
        "Jesuit Refugee Service": Reliability.USUALLY_RELIABLE,
        "El Colombiano": Reliability.USUALLY_RELIABLE,
        "Primature de la Republique Democratique du Congo": Reliability.USUALLY_RELIABLE,
        "Caribe Afirmativo": Reliability.USUALLY_RELIABLE,
        "Corporación Sisma Mujer": Reliability.USUALLY_RELIABLE,
        "fasoamazone": Reliability.USUALLY_RELIABLE,
        "Inter-American Development Bank": Reliability.USUALLY_RELIABLE,
        "International Labour Organization": Reliability.USUALLY_RELIABLE,
        "El Universal": Reliability.USUALLY_RELIABLE,
        "Asociación de Venezolanos en la República Argentina": Reliability.USUALLY_RELIABLE,
        "laborpresse": Reliability.USUALLY_RELIABLE,
        "Portafolio": Reliability.USUALLY_RELIABLE,
        "United Nations Children's Fund": Reliability.USUALLY_RELIABLE,
        "washcluster": Reliability.USUALLY_RELIABLE,
        "opendatadrc": Reliability.USUALLY_RELIABLE,
        "Government of Bangladesh": Reliability.USUALLY_RELIABLE,
        "UN Country Team in Bangladesh": Reliability.USUALLY_RELIABLE,
        "Action Contre la Faim": Reliability.USUALLY_RELIABLE,
        "UN Office of the High Commissioner for Human Rights": Reliability.USUALLY_RELIABLE,
        "UN Educational, Scientific and Cultural Organization": Reliability.USUALLY_RELIABLE,
        "BRAC": Reliability.USUALLY_RELIABLE,
        "France24": Reliability.USUALLY_RELIABLE,
        "Today Online": Reliability.USUALLY_RELIABLE,
        "libyanexpress": Reliability.USUALLY_RELIABLE,
        "ennonline": Reliability.USUALLY_RELIABLE,
        "Government Information Service": Reliability.USUALLY_RELIABLE,
        "sheltercluster": Reliability.USUALLY_RELIABLE,
        "Norwegian Refugee Council": Reliability.USUALLY_RELIABLE,
        "Afrik": Reliability.USUALLY_RELIABLE,
        "syriadirect": Reliability.USUALLY_RELIABLE,
        "lemonde": Reliability.USUALLY_RELIABLE,
        "TV5MONDE": Reliability.USUALLY_RELIABLE,
        "Instituto Nacional de Estadística": Reliability.USUALLY_RELIABLE,
        "libyaherald": Reliability.USUALLY_RELIABLE,
        "El Tiempo": Reliability.USUALLY_RELIABLE,
        "Servicio Jesuita a Migrantes": Reliability.USUALLY_RELIABLE,
        "UN Development Programme": Reliability.USUALLY_RELIABLE,
        "ProBogotá": Reliability.USUALLY_RELIABLE,
        "middleeasteye": Reliability.USUALLY_RELIABLE,
        "Sputnik Mundo": Reliability.USUALLY_RELIABLE,
        "El País": Reliability.USUALLY_RELIABLE,
        "Cash Working Group": Reliability.USUALLY_RELIABLE,
        "save the children international": Reliability.USUALLY_RELIABLE,
        "London School of Economics and Political Science": Reliability.USUALLY_RELIABLE,
        "thenationonlineng": Reliability.USUALLY_RELIABLE,
        "Joining Forces": Reliability.USUALLY_RELIABLE,
        "NES Sites and Settlements Working Group": Reliability.USUALLY_RELIABLE,
        "Autonomous Authority of North and East Syria": Reliability.USUALLY_RELIABLE,
        "syriahr": Reliability.USUALLY_RELIABLE,
        "Refugees International": Reliability.USUALLY_RELIABLE,
        "Vanguardia": Reliability.USUALLY_RELIABLE,
        "ACNUR": Reliability.COMPLETELY_RELIABLE,
        "Punch Nigeria": Reliability.USUALLY_RELIABLE,
        "Caritas": Reliability.USUALLY_RELIABLE,
        "Enab Baladi": Reliability.USUALLY_RELIABLE,
        "Ground Truth Solutions": Reliability.USUALLY_RELIABLE,
        "Mixed Migration Centre": Reliability.USUALLY_RELIABLE,
        "Amazon AWS": Reliability.USUALLY_RELIABLE,
        "7sur7": Reliability.USUALLY_RELIABLE,
        "Cuso International": Reliability.USUALLY_RELIABLE,
        "The Washington Post": Reliability.USUALLY_RELIABLE,
        "ORGANIZACION INTERNACIONAL PARA LAS MIGRACIONES": Reliability.USUALLY_RELIABLE,
        "refugeesinternational": Reliability.USUALLY_RELIABLE,
        "alwatanonline": Reliability.USUALLY_RELIABLE,
        "Fundación Panamericana para el Desarrollo -Colombia": Reliability.USUALLY_RELIABLE,
        "laopinion": Reliability.USUALLY_RELIABLE,
        "UN Organization Stabilization Mission in the Democratic Republic of the Congo": Reliability.USUALLY_RELIABLE,
        "Local Coordination Team": Reliability.USUALLY_RELIABLE,
        "Nigeria Center for Disease Control": Reliability.USUALLY_RELIABLE,
        "Emol": Reliability.USUALLY_RELIABLE,
        "CCCM Cluster": Reliability.USUALLY_RELIABLE,
        "RCN": Reliability.USUALLY_RELIABLE,
        "Migración Colombia": Reliability.USUALLY_RELIABLE,
        "Agencia EFE": Reliability.USUALLY_RELIABLE,
        "afghanistan-analysts": Reliability.USUALLY_RELIABLE,
        "Organization of American States": Reliability.USUALLY_RELIABLE,
        "Crónica": Reliability.USUALLY_RELIABLE,
        "UN Country Team in Ecuador": Reliability.USUALLY_RELIABLE,
        "Ouestaf": Reliability.USUALLY_RELIABLE,
        "Media Congo": Reliability.USUALLY_RELIABLE,
        "Africanews": Reliability.USUALLY_RELIABLE,
        "African Union": Reliability.USUALLY_RELIABLE,
        "Programa Venezolano de Educación - Acción en Derechos Humanos": Reliability.USUALLY_RELIABLE,
        "Internal Displacement Monitoring Centre": Reliability.USUALLY_RELIABLE,
        "CARE International": Reliability.USUALLY_RELIABLE,
        "afia-amanigrandslacs": Reliability.USUALLY_RELIABLE,
        "European Civil Protection and Humanitarian Aid Operations": Reliability.USUALLY_RELIABLE,
        "The Libya Observer": Reliability.USUALLY_RELIABLE,
        "Imperial College London": Reliability.USUALLY_RELIABLE,
        "congoactu": Reliability.USUALLY_RELIABLE,
        "Cable News Network": Reliability.USUALLY_RELIABLE,
        "Radio Nacional De Colombia": Reliability.USUALLY_RELIABLE,
        "apnews": Reliability.USUALLY_RELIABLE,
        "UNOCHA EHP": Reliability.USUALLY_RELIABLE,
        "Swedish International Development Cooperation Agency": Reliability.USUALLY_RELIABLE,
        "British Red Cross": Reliability.COMPLETELY_RELIABLE,
        "SPUTNIK MUNDO": Reliability.USUALLY_RELIABLE,
        "Government of Afghanistan": Reliability.USUALLY_RELIABLE,
        "allodocteurs": Reliability.USUALLY_RELIABLE,
        "Instituto de estudios para el desarrollo y la paz": Reliability.USUALLY_RELIABLE,
        "actalliance": Reliability.FAIRLY_RELIABLE,
        "US Agency for International Development": Reliability.USUALLY_RELIABLE,
        "Associazione Volontari per il Servizio Internazionale": Reliability.USUALLY_RELIABLE,
        "Libyan Express": Reliability.USUALLY_RELIABLE,
        "UN News Service": Reliability.USUALLY_RELIABLE,
        "Red Cross Society of Bosnia and Herzegovina": Reliability.USUALLY_RELIABLE,
        "Christian Science Monitor": Reliability.USUALLY_RELIABLE,
        "reuters-af": Reliability.USUALLY_RELIABLE,
        "International Committee of the Red Cross": Reliability.USUALLY_RELIABLE,
        "agenceecofin": Reliability.USUALLY_RELIABLE,
        "Afghanistan Education in Emergencies Working Group": Reliability.FAIRLY_RELIABLE,
        "Programa de Estudios Sociales en Salud": Reliability.FAIRLY_RELIABLE,
        "Somos Iberoamérica": Reliability.USUALLY_RELIABLE,
        "faso-actu": Reliability.USUALLY_RELIABLE,
        "DEPARTAMENTO DE INVESTIGACION Y ESTUDIOS MIGRATORIOS INSTITUTO NACIONAL DE MIGRACION": Reliability.USUALLY_RELIABLE,
        "uniandes": Reliability.USUALLY_RELIABLE,
        "Banco de la República": Reliability.USUALLY_RELIABLE,
        "International Finance Corporation": Reliability.USUALLY_RELIABLE,
        "sky": Reliability.USUALLY_RELIABLE,
        "Infobae": Reliability.USUALLY_RELIABLE,
        "European Union External Action": Reliability.USUALLY_RELIABLE,
        "Vanguard News": Reliability.USUALLY_RELIABLE,
        "congovirtuel": Reliability.USUALLY_RELIABLE,
        "Education Cluster": Reliability.USUALLY_RELIABLE,
        "ouaga24": Reliability.USUALLY_RELIABLE,
        "dailysabah": Reliability.USUALLY_RELIABLE,
        "Active Learning Network for Accountability and Performance in Humanitarian Action": Reliability.USUALLY_RELIABLE,
        "The Syrian Observer": Reliability.USUALLY_RELIABLE,
        "Al-Araby": Reliability.USUALLY_RELIABLE,
        "Gouvernement de la République Démocratique du Congo": Reliability.USUALLY_RELIABLE,
        "Caritas Venezuela": Reliability.USUALLY_RELIABLE,
        "thisdaylive": Reliability.USUALLY_RELIABLE,
        "UN Economic and Social Commission for Western Asia": Reliability.USUALLY_RELIABLE,
        "Hoy Diario de Magdalena": Reliability.USUALLY_RELIABLE,
        "Tishreen news": Reliability.USUALLY_RELIABLE,
        "Soy Chile": Reliability.USUALLY_RELIABLE,
        "European Commission": Reliability.USUALLY_RELIABLE,
        "Adventist Development and Relief Agency International": Reliability.USUALLY_RELIABLE,
        "Jeune Afrique": Reliability.USUALLY_RELIABLE,
        "issuu.com": Reliability.USUALLY_RELIABLE,
        "financialafrik": Reliability.USUALLY_RELIABLE,
        "El Impulso.Com": Reliability.USUALLY_RELIABLE,
        "Sham FM": Reliability.USUALLY_RELIABLE,
        "Action Against Hunger": Reliability.USUALLY_RELIABLE,
        "El Universo": Reliability.USUALLY_RELIABLE,
        "Panorama": Reliability.USUALLY_RELIABLE,
        "Oxford Academic Journals": Reliability.USUALLY_RELIABLE,
        "Forbes": Reliability.USUALLY_RELIABLE,
        "La Republica": Reliability.USUALLY_RELIABLE,
        "Observatorio Feminicidios Colombia": Reliability.USUALLY_RELIABLE,
        "Nextier SPD": Reliability.USUALLY_RELIABLE,
        "Defensoría del Pueblo Colombia": Reliability.USUALLY_RELIABLE,
        "africacdc": Reliability.USUALLY_RELIABLE,
        "Dhaka Tribune": Reliability.USUALLY_RELIABLE,
        "Citizen's Platform for SDGs, Bangladesh": Reliability.USUALLY_RELIABLE,
        "Ministère de l'Economie, des Finances et du Développement": Reliability.USUALLY_RELIABLE,
        "Africa Centres for Disease Control and Prevention": Reliability.USUALLY_RELIABLE,
        "Food Security and Nutrition Analysis Unit": Reliability.USUALLY_RELIABLE,
        "Plan International": Reliability.USUALLY_RELIABLE,
        "dailypost": Reliability.USUALLY_RELIABLE,
        "LePoint": Reliability.USUALLY_RELIABLE,
        "Intertional Federation of Red Cross": Reliability.USUALLY_RELIABLE,
        "United States Agency for International Development": Reliability.USUALLY_RELIABLE,
        "Gestion": Reliability.USUALLY_RELIABLE,
        "Diario del Sur": Reliability.USUALLY_RELIABLE,
        "United Nations Office on Drugs and Crime": Reliability.USUALLY_RELIABLE,
        "Ministère de la Santé (République Démocratique du Congo)": Reliability.USUALLY_RELIABLE,
        "W Radio": Reliability.USUALLY_RELIABLE,
        "COOPI - Cooperazione Internazionale": Reliability.USUALLY_RELIABLE,
        "Perfil": Reliability.USUALLY_RELIABLE,
        "Cruz Roja Ecuatoriana": Reliability.USUALLY_RELIABLE,
        "channelstv": Reliability.USUALLY_RELIABLE,
        "FUNDACIÓN DE AYUDA SOCIAL DE LAS IGLESIAS CRISTIANAS": Reliability.USUALLY_RELIABLE,
        "Xinhuanet": Reliability.USUALLY_RELIABLE,
        "Salon Syria": Reliability.USUALLY_RELIABLE,
        "Grupo Interagencial sobre Flujos Migratorios Mixtos": Reliability.USUALLY_RELIABLE,
        "Analitica": Reliability.USUALLY_RELIABLE,
        "nih": Reliability.USUALLY_RELIABLE,
        "Washington Office on Latin America": Reliability.USUALLY_RELIABLE,
        "The Committee for the Coordination of Statistical Activities": Reliability.USUALLY_RELIABLE,
        "uni-muenchen": Reliability.FAIRLY_RELIABLE,
        "La República": Reliability.USUALLY_RELIABLE,
        "internationalmedicalcorps": Reliability.USUALLY_RELIABLE,
        "República de las Ideas": Reliability.USUALLY_RELIABLE,
        "panampost": Reliability.USUALLY_RELIABLE,
        "La Razón": Reliability.USUALLY_RELIABLE,
        "Diario De Lara La Prensa": Reliability.USUALLY_RELIABLE,
        "Efecto Cocuyo": Reliability.USUALLY_RELIABLE,
        "infosplus": Reliability.USUALLY_RELIABLE,
        "Unidad Nacional para la Gestión del Riesgo de Desastres": Reliability.USUALLY_RELIABLE,
        "La Nación": Reliability.USUALLY_RELIABLE,
        "Ministerio de Salud y Protección Social": Reliability.USUALLY_RELIABLE,
        "congoindependant": Reliability.USUALLY_RELIABLE,
        "Gender in Humanitarian Action Working Group": Reliability.USUALLY_RELIABLE,
        "El Telégrafo": Reliability.USUALLY_RELIABLE,
        "Diario del Norte": Reliability.USUALLY_RELIABLE,
        "thedefensepost": Reliability.USUALLY_RELIABLE,
        "United Nation International Children's Emergency Fund": Reliability.USUALLY_RELIABLE,
        "Cordaid": Reliability.FAIRLY_RELIABLE,
        "Organisation for Economic Co-operation and Development": Reliability.USUALLY_RELIABLE,
        "El Heraldo": Reliability.USUALLY_RELIABLE,
        "downtoearth": Reliability.USUALLY_RELIABLE,
        "El Nuevo Siglo": Reliability.USUALLY_RELIABLE,
        "WASH Cluster": Reliability.USUALLY_RELIABLE,
        "Association pour la Promotion et l’Intégration de la Jeunesse du Centre Nord": Reliability.USUALLY_RELIABLE,
        "Insightcrime": Reliability.USUALLY_RELIABLE,
        "Diario As Colombia": Reliability.USUALLY_RELIABLE,
        "NBC News": Reliability.USUALLY_RELIABLE,
        "Noticiero Digital": Reliability.USUALLY_RELIABLE,
        "diarioeltiempo": Reliability.USUALLY_RELIABLE,
        "issafrica": Reliability.USUALLY_RELIABLE,
        "El Diario De Los Andes": Reliability.USUALLY_RELIABLE,
        "La fm": Reliability.USUALLY_RELIABLE,
        "Ministry of Public Health (Democratic Republic of Congo)": Reliability.USUALLY_RELIABLE,
        "mediacongo": Reliability.USUALLY_RELIABLE,
        "National Bureau of Statistic": Reliability.USUALLY_RELIABLE,
        "El Destape Web": Reliability.USUALLY_RELIABLE,
        "Nutrition Cluster": Reliability.USUALLY_RELIABLE,
        "Oxfam": Reliability.USUALLY_RELIABLE,
        "Ojo Público": Reliability.USUALLY_RELIABLE,
        "The Economist": Reliability.USUALLY_RELIABLE,
        "National Meteorological Agency Burkina Faso": Reliability.USUALLY_RELIABLE,
        "Al-Khabar": Reliability.USUALLY_RELIABLE,
        "Interactuar": Reliability.USUALLY_RELIABLE,
        "UN Relief and Works Agency for Palestine Refugees in the Near East": Reliability.USUALLY_RELIABLE,
        "lalibre": Reliability.USUALLY_RELIABLE,
        "larepublica": Reliability.USUALLY_RELIABLE,
        "El Cronista": Reliability.USUALLY_RELIABLE,
        "mailchi": Reliability.USUALLY_RELIABLE,
        "El siglo": Reliability.USUALLY_RELIABLE,
        "Common Market for Eastern and Southern Africa": Reliability.USUALLY_RELIABLE,
        "congodurable": Reliability.USUALLY_RELIABLE,
        "Clarín": Reliability.USUALLY_RELIABLE,
        "rojavainformationcenter": Reliability.USUALLY_RELIABLE,
        "Manusher Jonno Foundation": Reliability.USUALLY_RELIABLE,
        "Consultative Group to Assist the Poor (CGAP)": Reliability.USUALLY_RELIABLE,
        "UN News": Reliability.USUALLY_RELIABLE,
        "Departamento de Extranjería y Migración Chile": Reliability.USUALLY_RELIABLE,
        "voanews": Reliability.USUALLY_RELIABLE,
        "Ministerio de Educación": Reliability.USUALLY_RELIABLE,
        "North Press Agency": Reliability.USUALLY_RELIABLE,
        "Al Watan online": Reliability.USUALLY_RELIABLE,
        "Protection Cluster Syria": Reliability.USUALLY_RELIABLE,
        "The National News": Reliability.USUALLY_RELIABLE,
        "Humvenezuela": Reliability.USUALLY_RELIABLE,
        "digitalcongo": Reliability.USUALLY_RELIABLE,
        "Primicia": Reliability.USUALLY_RELIABLE,
        "care-international": Reliability.USUALLY_RELIABLE,
        "Peace News": Reliability.USUALLY_RELIABLE,
        "wvi": Reliability.USUALLY_RELIABLE,
        "Ultimas Noticias": Reliability.USUALLY_RELIABLE,
        "The Adecco Group": Reliability.USUALLY_RELIABLE,
        "Performance Monitoring for Action": Reliability.USUALLY_RELIABLE,
        "Version Final": Reliability.USUALLY_RELIABLE,
        "Asociación Mujeres Unidas, Migrantes y Refugiadas en Argentina": Reliability.USUALLY_RELIABLE,
        "El Tribuno": Reliability.USUALLY_RELIABLE,
        "infobascongo": Reliability.USUALLY_RELIABLE,
        "nairametrics": Reliability.USUALLY_RELIABLE,
        "habarirdc": Reliability.UNRELIABLE,
        "prensalibre": Reliability.USUALLY_RELIABLE,
        "fasozine": Reliability.USUALLY_RELIABLE,
        "saharareporters": Reliability.USUALLY_RELIABLE,
        "stereo100": Reliability.USUALLY_RELIABLE,
        "International Organization for Migration and Displacement Tracking Matrix": Reliability.USUALLY_RELIABLE,
        "cgtn": Reliability.USUALLY_RELIABLE,
        "ktpress": Reliability.USUALLY_RELIABLE,
        "venezuela al dia": Reliability.USUALLY_RELIABLE,
        "Agence Française de Développement": Reliability.USUALLY_RELIABLE,
        "usembassy": Reliability.USUALLY_RELIABLE,
        "wradio": Reliability.USUALLY_RELIABLE,
        "redcross": Reliability.USUALLY_RELIABLE,
        "Americas Quarterly": Reliability.USUALLY_RELIABLE,
        "fragomen": Reliability.USUALLY_RELIABLE,
        "GRUPO BANCO MUNDIAL": Reliability.COMPLETELY_RELIABLE,
        "Cruz Roja Argentina": Reliability.COMPLETELY_RELIABLE,
        "GIGA Focus": Reliability.FAIRLY_RELIABLE,
        "Aporrea": Reliability.USUALLY_RELIABLE,
        "Un Minuto Radio": Reliability.USUALLY_RELIABLE,
        "acento": Reliability.USUALLY_RELIABLE,
        "EV TVmiami": Reliability.USUALLY_RELIABLE,
        "Ministère de la santé (Burkina Faso)": Reliability.USUALLY_RELIABLE,
        "Efecto cocuyo": Reliability.COMPLETELY_RELIABLE,
        "lasillavacia": Reliability.USUALLY_RELIABLE,
        "Modern Diplomacy": Reliability.USUALLY_RELIABLE,
        "NIRAPAD": Reliability.USUALLY_RELIABLE,
        "headtopics": Reliability.USUALLY_RELIABLE,
        "Center for Global Development": Reliability.USUALLY_RELIABLE,
        "elvenezolanocolombia": Reliability.USUALLY_RELIABLE,
        "albaathmedia": Reliability.USUALLY_RELIABLE,
        "El Frente": Reliability.USUALLY_RELIABLE,
        "The Tribune": Reliability.USUALLY_RELIABLE,
        "elanrdc": Reliability.USUALLY_RELIABLE,
        "Syria Health Network": Reliability.USUALLY_RELIABLE,
        "Al Jazeera": Reliability.USUALLY_RELIABLE,
        "Revista Entornos": Reliability.USUALLY_RELIABLE,
        "Assistance Coordination Unit": Reliability.USUALLY_RELIABLE,
        "Associated Press": Reliability.USUALLY_RELIABLE,
        "Syria Times": Reliability.USUALLY_RELIABLE,
        "BBC Afrique": Reliability.USUALLY_RELIABLE,
        "60_decibels": Reliability.USUALLY_RELIABLE,
        "TRT World": Reliability.USUALLY_RELIABLE,
        "Rojava Information Center": Reliability.USUALLY_RELIABLE,
        "Dirección del Trabajo, Chile": Reliability.USUALLY_RELIABLE,
        "Caritas Germany": Reliability.USUALLY_RELIABLE,
        "Aleteia": Reliability.USUALLY_RELIABLE,
        "slobodnaevropa": Reliability.USUALLY_RELIABLE,
        "vivafrik": Reliability.USUALLY_RELIABLE,
        "Sistema Económico Latinoamericano y del Caribe": Reliability.USUALLY_RELIABLE,
        "The Independent": Reliability.USUALLY_RELIABLE,
        "El periodiquito": Reliability.USUALLY_RELIABLE,
        "Pulzo": Reliability.USUALLY_RELIABLE,
        "efectococuyo": Reliability.USUALLY_RELIABLE,
        "Manos VeneGuayas": Reliability.USUALLY_RELIABLE,
        "congosynthese": Reliability.USUALLY_RELIABLE,
        "allafrica": Reliability.USUALLY_RELIABLE,
        "La Tercera": Reliability.USUALLY_RELIABLE,
        "Garda World": Reliability.USUALLY_RELIABLE,
        "Arab News": Reliability.USUALLY_RELIABLE,
        "CBC": Reliability.USUALLY_RELIABLE,
        "Bethany Christian Services": Reliability.USUALLY_RELIABLE,
        "La Opinión": Reliability.USUALLY_RELIABLE,
        "caracoltv": Reliability.USUALLY_RELIABLE,
        "lafm.": Reliability.USUALLY_RELIABLE,
        "areion24": Reliability.USUALLY_RELIABLE,
        "environews-rdc": Reliability.USUALLY_RELIABLE,
        "Amani Institute": Reliability.FAIRLY_RELIABLE,
        "Alcaldía de Bogotá": Reliability.USUALLY_RELIABLE,
        "MDZ Diario de Mendoza": Reliability.USUALLY_RELIABLE,
        "Middle East Institute": Reliability.USUALLY_RELIABLE,
        "Ministerio de Vivienda": Reliability.USUALLY_RELIABLE,
        "Permanent Interstate Committee for Drought Control in the Sahel": Reliability.USUALLY_RELIABLE,
        "El Periódico": Reliability.USUALLY_RELIABLE,
        "El Ceo": Reliability.USUALLY_RELIABLE,
        "interkinois": Reliability.USUALLY_RELIABLE,
        "iagua": Reliability.USUALLY_RELIABLE,
        "Doctors Without borders": Reliability.USUALLY_RELIABLE,
        "Razón Pública": Reliability.USUALLY_RELIABLE,
        "Diario Libre": Reliability.USUALLY_RELIABLE,
        "Radio Télévision Belge Francophone": Reliability.USUALLY_RELIABLE,
        "Daraj": Reliability.USUALLY_RELIABLE,
        "Cripto Noticias": Reliability.USUALLY_RELIABLE,
        "Child protection Cox's Bazar sub sector": Reliability.USUALLY_RELIABLE,
        "globalcitizen": Reliability.USUALLY_RELIABLE,
        "elheraldo": Reliability.USUALLY_RELIABLE,
        "acpcongo": Reliability.USUALLY_RELIABLE,
        "voaafrique": Reliability.USUALLY_RELIABLE,
        "eje21": Reliability.USUALLY_RELIABLE,
        "forumdesas": Reliability.USUALLY_RELIABLE,
        "radiookapi": Reliability.USUALLY_RELIABLE,
        "mprnews": Reliability.USUALLY_RELIABLE,
        "borgenmagazine": Reliability.USUALLY_RELIABLE,
        "presidencia": Reliability.USUALLY_RELIABLE,
        "tchadinfos": Reliability.FAIRLY_RELIABLE,
        "newstatesman": Reliability.USUALLY_RELIABLE,
        "US Department of State - Humanitarian Information Unit": Reliability.USUALLY_RELIABLE,
        "faapa": Reliability.USUALLY_RELIABLE,
        "bdnews24": Reliability.USUALLY_RELIABLE,
        "eluniverso": Reliability.USUALLY_RELIABLE,
        "Emergency Telecommunications Cluster": Reliability.USUALLY_RELIABLE,
        "Informe21.Com": Reliability.USUALLY_RELIABLE,
        "Reporte Confidencial": Reliability.USUALLY_RELIABLE,
        "CCCM: Shelter and NFI": Reliability.USUALLY_RELIABLE,
        "Primer Informe": Reliability.USUALLY_RELIABLE,
        "Runrun": Reliability.USUALLY_RELIABLE,
        "Grupo Bancolombia": Reliability.USUALLY_RELIABLE,
        "International Medical Corps": Reliability.USUALLY_RELIABLE,
        "MedGlobal": Reliability.USUALLY_RELIABLE,
        "Seervicio jesuita a refugiados": Reliability.USUALLY_RELIABLE,
        "Sudanese Red Crescent Society": Reliability.USUALLY_RELIABLE,
        "Noticias curazao": Reliability.USUALLY_RELIABLE,
        "Meganoticias": Reliability.USUALLY_RELIABLE,
        "Atlantic Council": Reliability.USUALLY_RELIABLE,
        "Caracol Diario": Reliability.USUALLY_RELIABLE,
        "Newsday": Reliability.USUALLY_RELIABLE,
        "Hoy Digital": Reliability.USUALLY_RELIABLE,
        "New Lines Institute": Reliability.USUALLY_RELIABLE,
        "Syrian Network for Human Rights": Reliability.USUALLY_RELIABLE,
        "Center for Operational Analysis and Research": Reliability.USUALLY_RELIABLE,
        "El Informador": Reliability.FAIRLY_RELIABLE,
        "thecable": Reliability.USUALLY_RELIABLE,
        "n1info": Reliability.USUALLY_RELIABLE,
        "Ministerio de Salud y Desarrollo Social": Reliability.USUALLY_RELIABLE,
        "Publimetro": Reliability.USUALLY_RELIABLE,
        "Australian Agency for International Development": Reliability.USUALLY_RELIABLE,
        "Physicians for Human Rights": Reliability.USUALLY_RELIABLE,
        "securitycouncilreport": Reliability.FAIRLY_RELIABLE,
        "Global News": Reliability.USUALLY_RELIABLE,
        "Federal Ministry of Health (Nigeria)": Reliability.USUALLY_RELIABLE,
        "Observatorio Venezolano de Migración": Reliability.USUALLY_RELIABLE,
        "iMMAP": Reliability.USUALLY_RELIABLE,
        "Middle East Eye": Reliability.USUALLY_RELIABLE,
        "theeastafrican": Reliability.USUALLY_RELIABLE,
        "Notimerica": Reliability.USUALLY_RELIABLE,
        "VOA News": Reliability.USUALLY_RELIABLE,
        "Diario La Nacion": Reliability.FAIRLY_RELIABLE,
        "santetropicale": Reliability.USUALLY_RELIABLE,
        "actu24": Reliability.USUALLY_RELIABLE,
        "Nextier SPD (Security, Peace, and Development)": Reliability.USUALLY_RELIABLE,
        "CR hoy.Com": Reliability.USUALLY_RELIABLE,
        "bhrt": Reliability.USUALLY_RELIABLE,
        "Insecurity Insight": Reliability.USUALLY_RELIABLE,
        "El Mostrador": Reliability.USUALLY_RELIABLE,
        "Reuters": Reliability.USUALLY_RELIABLE,
        "El Observador": Reliability.USUALLY_RELIABLE,
        "zonacero": Reliability.USUALLY_RELIABLE,
        "Solidarités International": Reliability.USUALLY_RELIABLE,
        "salaamgateway": Reliability.USUALLY_RELIABLE,
        "Syrian Centre for Policy Research": Reliability.USUALLY_RELIABLE,
        "237actu": Reliability.FAIRLY_RELIABLE,
        "La Cuarta": Reliability.USUALLY_RELIABLE,
        "ecupunto": Reliability.USUALLY_RELIABLE,
        "UNHCR Innovation": Reliability.USUALLY_RELIABLE,
        "la-croix": Reliability.USUALLY_RELIABLE,
        "Tu Barco": Reliability.USUALLY_RELIABLE,
    },
}

authoring_organisations = list(
    organisation_reliabilities["Authoring Organizations"].keys()
)
publishing_organisations = list(
    organisation_reliabilities["Publishing Organizations"].keys()
)


def return_org_reliability(publishing_org, authoring_org=None):
    """Returns the reliability score of the organizations"""
    lst = []
    if authoring_org is None or not authoring_org:
        if publishing_org not in publishing_organisations:
            lst.append("")
        else:
            lst.append(
                organisation_reliabilities["Publishing Organizations"][publishing_org]
            )
    else:
        for author_org in authoring_org:
            if author_org in authoring_organisations:
                lst.append(
                    organisation_reliabilities["Authoring Organizations"][author_org]
                )
    cnt_items = Counter(lst)
    return (
        Reliability.id_to_scoretype(cnt_items.most_common(1)[0][0])
        if cnt_items
        else Reliability.id_to_scoretype(Reliability.UNRELIABLE)
    )


def lambda_handler(event, context):
    """Main entry point for lambda handler"""
    if "publishing_organization" not in event:
        return {
            "statusCode": 200,
            "prediction": Reliability.id_to_scoretype(Reliability.UNRELIABLE),
        }
    publishing_org = event["publishing_organization"]
    authoring_org = (
        event["authoring_organization"] if "authoring_organization" in event else None
    )

    return {
        "statusCode": 200,
        "prediction": return_org_reliability(publishing_org, authoring_org),
    }
