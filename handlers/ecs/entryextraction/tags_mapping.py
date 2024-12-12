from collections import namedtuple
from enum import Enum

from constants import (AFFECTED_GRP_VERSION, AGE_VERSION,
                       DEMOGRAPHIC_GROUP_VERSION, GENDER_VERSION,
                       RELIABILITY_VERSION, SECTOR_VERSION, SEVERITY_VERSION,
                       SPECIFIC_NEEDS_GROUP_VERSION, SUBPILLAR_VERSION,
                       SUBPILLARS_1D_VERSION, SUBPILLARS_2D_VERSION)

MainCategories = namedtuple(
    "MainCategories", ["id", "key", "version", "is_category", "alias"]
)
MainTags = namedtuple(
    "MainTags", ["id", "key", "version", "is_category", "category_id"]
)


class Categories(Enum):
    SECTORS = MainCategories(
        id="1", key="sectors", version=SECTOR_VERSION, is_category=True, alias="Sectors"
    )
    SUBPILLARS_1D = MainCategories(
        id="2",
        key="subpillars_1d",
        version=SUBPILLAR_VERSION,
        is_category=True,
        alias="Subpillars 1D",
    )
    SUBPILLARS_2D = MainCategories(
        id="3",
        key="subpillars_2d",
        version=SUBPILLAR_VERSION,
        is_category=True,
        alias="Subpillars 2D",
    )
    SPECIFIC_NEEDS_GROUP = MainCategories(
        id="4",
        key="specific_needs_groups",
        version=AFFECTED_GRP_VERSION,
        is_category=True,
        alias="Specific Needs Group",
    )
    GENDER = MainCategories(
        id="5", key="gender", version=GENDER_VERSION, is_category=True, alias="Gender"
    )
    AGE = MainCategories(
        id="6", key="age", version=AGE_VERSION, is_category=True, alias="Age"
    )
    SEVERITY = MainCategories(
        id="7",
        key="severity",
        version=SEVERITY_VERSION,
        is_category=True,
        alias="Severity",
    )
    AFFECTED_GROUPS = MainCategories(
        id="8",
        key="affected_groups",
        version=SECTOR_VERSION,
        is_category=True,
        alias="Affected Groups",
    )
    DEMOGRAPHIC_GROUP = MainCategories(
        id="9",
        key="demographic_group",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=True,
        alias="Demographic Groups",
    )
    RELIABILITY = MainCategories(
        id="10",
        key="reliability",
        version=RELIABILITY_VERSION,
        is_category=True,
        alias="Reliability",
    )

    @classmethod
    def all_models(cls):
        return [
            t.value._asdict()
            for t in [
                Categories.SECTORS,
                Categories.SUBPILLARS_1D,
                Categories.SUBPILLARS_2D,
                Categories.AGE,
                Categories.GENDER,
                Categories.DEMOGRAPHIC_GROUP,
                Categories.AFFECTED_GROUPS,
                Categories.SPECIFIC_NEEDS_GROUP,
                Categories.SEVERITY,
                Categories.RELIABILITY,
            ]
        ]


class Tags(Enum):
    # Sectors Enum
    AGRICULTURE = MainTags(
        id="101",
        key="Agriculture",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    CROSS = MainTags(
        id="102",
        key="Cross",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    EDUCATION = MainTags(
        id="103",
        key="Education",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    FOOD_SECURITY = MainTags(
        id="104",
        key="Food Security",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    HEALTH = MainTags(
        id="105",
        key="Health",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    LIVELIHOODS = MainTags(
        id="106",
        key="Livelihoods",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    LOGISTICS = MainTags(
        id="107",
        key="Logistics",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    NUTRITION = MainTags(
        id="108",
        key="Nutrition",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    PROTECTION = MainTags(
        id="109",
        key="Protection",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    SHELTER = MainTags(
        id="110",
        key="Shelter",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )
    WASH = MainTags(
        id="111",
        key="WASH",
        version=SECTOR_VERSION,
        is_category=False,
        category_id=getattr(Categories.SECTORS.value, "id"),
    )

    # 1D SubPillars
    CONTEXT_ENVIRONMENT = MainTags(
        id="201",
        key="Context->Environment",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CONTEXT_SOCIO_CULTURAL = MainTags(
        id="202",
        key="Context->Socio Cultural",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CONTEXT_ECONOMY = MainTags(
        id="203",
        key="Context->Economy",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CONTEXT_DEMOGRAPHY = MainTags(
        id="204",
        key="Context->Demography",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CONTEXT_LEGAL_AND_POLICY = MainTags(
        id="205",
        key="Context->Legal & Policy",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CONTEXT_SECURITY_AND_STABILITY = MainTags(
        id="206",
        key="Context->Security & Stability",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CONTEXT_POLITICS = MainTags(
        id="207",
        key="Context->Politics",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    SHOCK_EVENT_TYPE_AND_CHARACTERISTICS = MainTags(
        id="208",
        key="Shock/Event->Type And Characteristics",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    SHOCK_EVENT_UNDERLYING_AGGRAVATING_FACTORS = MainTags(
        id="209",
        key="Shock/Event->Underlying/Aggravating Factors",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    SHOCK_EVENT_HAZARD_THREATS = MainTags(
        id="210",
        key="Shock/Event->Hazard & Threats",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    # Key duplicated in sub piller
    # DISPLACEMENT_TYPE_NUMBERS_MOVEMENTS = 211, _('Displacement->Type/Numbers/Movements')
    DISPLACEMENT_TYPE_NUMBERS_MOVEMENTS = MainTags(
        id="212",
        key="Displacement->Type/Numbers/Movements",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    DISPLACEMENT_PUSH_FACTORS = MainTags(
        id="213",
        key="Displacement->Push Factors",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    DISPLACEMENT_PULL_FACTORS = MainTags(
        id="214",
        key="Displacement->Pull Factors",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    DISPLACEMENT_INTENTIONS = MainTags(
        id="215",
        key="Displacement->Intentions",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    DISPLACEMENT_LOCAL_INTEGRATION = MainTags(
        id="216",
        key="Displacement->Local Integration",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CASUALTIES_INJURED = MainTags(
        id="217",
        key="Casualties->Injured",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CASUALTIES_MISSING = MainTags(
        id="218",
        key="Casualties->Missing",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CASUALTIES_DEAD = MainTags(
        id="219",
        key="Casualties->Dead",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    HUMANITARIAN_ACCESS_RELIEF_TO_POPULATION = MainTags(
        id="220",
        key="Humanitarian Access->Relief To Population",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    HUMANITARIAN_ACCESS_POPULATION_TO_RELIEF = MainTags(
        id="221",
        key="Humanitarian Access->Population To Relief",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    HUMANITARIAN_ACCESS_PHYSICAL_CONSTRAINTS = MainTags(
        id="222",
        key="Humanitarian Access->Physical Constraints",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    HUMANITARIAN_ACCESS_GAPS = MainTags(
        id="223",
        key="Humanitarian Access->Number Of People Facing Humanitarian Access Constraints/Humanitarian Access Gaps",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    INFORMATION_AND_COMMUNICATION_MEANS_AND_PREFERENCES = MainTags(
        id="224",
        key="Information And Communication->Communication Means And Preferences",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    INFORMATION_AND_COMMUNICATION_INFO_CHALLENGES_AND_BARRIERS = MainTags(
        id="225",
        key="Information And Communication->Information Challenges And Barriers",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    INFORMATION_AND_COMMUNICATION_KNOWLEDGE_AND_INFO_GAPS_POP = MainTags(
        id="226",
        key="Information And Communication->Knowledge And Info Gaps (Pop)",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    INFORMATION_AND_COMMUNICATION_KNOWLEDGE_AND_INFO_GAPS_HUM = MainTags(
        id="227",
        key="Information And Communication->Knowledge And Info Gaps (Hum)",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    COVID_19_CASES = MainTags(
        id="228",
        key="Covid-19->Cases",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    COVID_19_CONTACT_CASES = MainTags(
        id="229",
        key="Covid-19->Contact Tracing",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    COVID_19_DEATHS = MainTags(
        id="230",
        key="Covid-19->Deaths",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    COVID_19_HOSPITALIZATION_AND_CARE = MainTags(
        id="231",
        key="Covid-19->Hospitalization & Care",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    COVID_19_RESTRICTION_MEASURES = MainTags(
        id="232",
        key="Covid-19->Restriction Measures",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    COVID_19_TESTING = MainTags(
        id="233",
        key="Covid-19->Testing",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    COVID_19_VACCINATION = MainTags(
        id="234",
        key="Covid-19->Vaccination",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )
    CONTEXT_TECHNOLOGICAL = MainTags(
        id="235",
        key="Context->Technological",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )  #
    COVID_19_PREVENTION_CAMPAIGN = MainTags(
        id="236",
        key="Covid-19->Prevention campaign",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )  #
    COVID_19_RESEARCH_OUTLOOK = MainTags(
        id="237",
        key="Covid-19->Research and outlook",
        version=SUBPILLARS_1D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_1D.value, "id"),
    )  #

    # 2D SubPillars
    AT_RISK_NUMBER_OF_PEOPLE = MainTags(
        id="301",
        key="At Risk->Number Of People At Risk",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    AT_RISK_VULNERABILITIES = MainTags(
        id="302",
        key="At Risk->Risk And Vulnerabilities",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    CAPACITIES_RESPONSE_INTERNATIONAL = MainTags(
        id="303",
        key="Capacities & Response->International Response",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    CAPACITIES_RESPONSE_LOCAL = MainTags(
        id="304",
        key="Capacities & Response->Local Response",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    CAPACITIES_RESPONSE_NATIONAL = MainTags(
        id="305",
        key="Capacities & Response->National Response",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    CAPACITIES_RESPONSE_NUM_PEOPLE_REACHED = MainTags(
        id="306",
        key="Capacities & Response->Number Of People Reached/Response Gaps",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    HUMANITARIAN_CONDITIONS_COPING_MECHANISMS = MainTags(
        id="307",
        key="Humanitarian Conditions->Coping Mechanisms",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    HUMANITARIAN_CONDITIONS_LIVING_STANDARDS = MainTags(
        id="308",
        key="Humanitarian Conditions->Living Standards",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    HUMANITARIAN_CONDITIONS_NUM_PEOPLE_IN_NEED = MainTags(
        id="309",
        key="Humanitarian Conditions->Number Of People In Need",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    HUMANITARIAN_CONDITIONS_PHY_MENTAL_WELL_BEING = MainTags(
        id="310",
        key="Humanitarian Conditions->Physical And Mental Well Being",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    IMPACT_DRIVER_AGGRAVATING_FACTORS = MainTags(
        id="311",
        key="Impact->Driver/Aggravating Factors",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    IMPACT_ON_PEOPLE = MainTags(
        id="312",
        key="Impact->Impact On People",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    IMPACT_ON_SYSTEMS_SRV_NET = MainTags(
        id="313",
        key="Impact->Impact On Systems, Services And Networks",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    IMPACT_NUM_OF_PEOPLE_AFFECTED = MainTags(
        id="314",
        key="Impact->Number Of People Affected",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    PRIORITY_INTERVENTIONS_HUMANITARIAN_STAFF = MainTags(
        id="315",
        key="Priority Interventions->Expressed By Humanitarian Staff",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    PRIORITY_INTERVENTIONS_EXPRESSED_BY_POPULATION = MainTags(
        id="316",
        key="Priority Interventions->Expressed By Population",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    PRIORITY_NEEDS_EXPRESSED_BY_HUMANITARIAN_STAFF = MainTags(
        id="317",
        key="Priority Needs->Expressed By Humanitarian Staff",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    PRIORITY_NEEDS_EXPRESSED_BY_POPULATION = MainTags(
        id="318",
        key="Priority Needs->Expressed By Population",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )
    CAPACITIES_RESPONSE_HUMANITARIAN_COORDINATION = MainTags(
        id="319",
        key="Capacities & response->Humanitarian coordination",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )  #
    CAPACITIES_RESPONSE_PEOPLE_REACHED_RESPONSE_GAPS = MainTags(
        id="320",
        key="Capacities & response->People reached/response gaps",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )  #
    CAPACITIES_RESPONSE_RED_CROSS_RED_CRESCENT = MainTags(
        id="321",
        key="Capacities & response->Red cross/red crescent",
        version=SUBPILLARS_2D_VERSION,
        is_category=False,
        category_id=getattr(Categories.SUBPILLARS_2D.value, "id"),
    )  #

    # Specific Needs Group
    CHILD_HEAD_OF_HOUSEHOLD = MainTags(
        id="401",
        key="Child Head of Household",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    CHRONICALLY_ILL = MainTags(
        id="402",
        key="Chronically Ill",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    ELDERLY_HEAD_OF_HOUSEHOLD = MainTags(
        id="403",
        key="Elderly Head of Household",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    FEMALE_HEAD_OF_HOUSEHOLD = MainTags(
        id="404",
        key="Female Head of Household",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    GBV_SURVIVORS = MainTags(
        id="405",
        key="GBV survivors",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    INDIGENOUS_PEOPLE = MainTags(
        id="406",
        key="Indigenous people",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    LGBTQI = MainTags(
        id="407",
        key="LGBTQI+",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    MINORITIES = MainTags(
        id="408",
        key="Minorities",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    PERSONS_WITH_DISABILITY = MainTags(
        id="409",
        key="Persons with Disability",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    PREGNANT_OR_LACTATING_WOMEN = MainTags(
        id="410",
        key="Pregnant or Lactating Women",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    SINGLE_WOMEN_INCLUDING_WIDOWS = MainTags(
        id="411",
        key="Single Women (including Widows)",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    UNACCOMPANIED_OR_SEPARATED_CHILDREN = MainTags(
        id="412",
        key="Unaccompanied or Separated Children",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    LGBTQIA_PLUS = MainTags(
        id="413",
        key="Lgbtqia+",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )
    UNACCOMPANIED_OR_AND_SEPARATED_CHILDREN = MainTags(
        id="414",
        key="Unaccompanied or/and separated children",
        version=SPECIFIC_NEEDS_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.SPECIFIC_NEEDS_GROUP.value, "id"),
    )

    # Gender
    FEMALE = MainTags(
        id="501",
        key="Female",
        version=GENDER_VERSION,
        is_category=False,
        category_id=getattr(Categories.GENDER.value, "id"),
    )
    MALE = MainTags(
        id="502",
        key="Male",
        version=GENDER_VERSION,
        is_category=False,
        category_id=getattr(Categories.GENDER.value, "id"),
    )
    ALL = MainTags(
        id="503",
        key="All",
        version=GENDER_VERSION,
        is_category=False,
        category_id=getattr(Categories.GENDER.value, "id"),
    )

    # Age
    ADULT_18_TO_59_YEARS_OLD = MainTags(
        id="601",
        key="Adult (18 to 59 years old)",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )
    CHILDREN_YOUTH_5_TO_17 = MainTags(
        id="602",
        key="Children/Youth (5 to 17 years old)",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )
    INFANTS_TODDLERS_LESS_THAN_5_YEARS = MainTags(
        id="603",
        key="Infants/Toddlers (<5 years old)",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )
    OLDER_PERSON_60_PLUS = MainTags(
        id="604",
        key="Older Persons (60+ years old)",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )
    TWELVE_SEVENTEEN_YEARS = MainTags(
        id="605",
        key="12-17 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    EIGHTEEN_TWENTYFOUR_YEARS = MainTags(
        id="606",
        key="18-24 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    EIGHTEEN_FIFTYNINE_YEARS = MainTags(
        id="607",
        key="18-59 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    TWENTYFIVE_FIFTYNINE_YEARS = MainTags(
        id="608",
        key="25-59 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    FIVE_ELEVEN_YEARS = MainTags(
        id="609",
        key="5-11 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    FIVE_SEVENTEEN_YEARS = MainTags(
        id="610",
        key="5-17 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    LESS_THAN_EIGHTEEN_YEARS = MainTags(
        id="611",
        key="<18 years",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    LESS_THAN_EIGHTEEN_YEARS_OLD = MainTags(
        id="612",
        key="<18 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    LESS_THAN_FIVE_YEARS = MainTags(
        id="613",
        key="<5 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #
    GREATER_THAN_SIXTY_YEARS = MainTags(
        id="614",
        key=">60 years old",
        version=AGE_VERSION,
        is_category=False,
        category_id=getattr(Categories.AGE.value, "id"),
    )  #

    # Demographic Groups
    D_GRP_INFANTS_TODDLERS_LESS_THAN_5_YEARS = MainTags(
        id="901",
        key="Infants/Toddlers (<5 years old) ",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.DEMOGRAPHIC_GROUP.value, "id"),
    )  # check this with 603
    D_GRP_FEMALE_CHILDREN_YOUTH_5_TO_17 = MainTags(
        id="902",
        key="Female Children/Youth (5 to 17 years old)",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.DEMOGRAPHIC_GROUP.value, "id"),
    )
    D_GRP_MALE_CHILDREN_YOUTH_5_TO_17 = MainTags(
        id="903",
        key="Male Children/Youth (5 to 17 years old)",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.DEMOGRAPHIC_GROUP.value, "id"),
    )
    D_GRP_FEMALE_ADULT_18_TO_59_YEARS_OLD = MainTags(
        id="904",
        key="Female Adult (18 to 59 years old)",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.DEMOGRAPHIC_GROUP.value, "id"),
    )
    D_GRP_MALE_ADULT_18_TO_59_YEARS_OLD = MainTags(
        id="905",
        key="Male Adult (18 to 59 years old)",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.DEMOGRAPHIC_GROUP.value, "id"),
    )
    D_GRP_FEMALE_OLDER_PERSON_60_PLUS = MainTags(
        id="906",
        key="Female Older Persons (60+ years old)",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.DEMOGRAPHIC_GROUP.value, "id"),
    )
    D_GRP_MALE_OLDER_PERSON_60_PLUS = MainTags(
        id="907",
        key="Male Older Persons (60+ years old)",
        version=DEMOGRAPHIC_GROUP_VERSION,
        is_category=False,
        category_id=getattr(Categories.DEMOGRAPHIC_GROUP.value, "id"),
    )

    # Severity
    CRITICAL = MainTags(
        id="701",
        key="Critical",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )
    MAJOR = MainTags(
        id="702",
        key="Major",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )
    MINOR_PROBLEM = MainTags(
        id="703",
        key="Minor Problem",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )
    NO_PROBLEM = MainTags(
        id="704",
        key="No problem",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )
    OF_CONCERN = MainTags(
        id="705",
        key="Of Concern",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )
    CRITICAL_ISSUE = MainTags(
        id="706",
        key="Critical issue",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )  #
    ISSUE_OF_CONCERN = MainTags(
        id="707",
        key="Issue of concern",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )  #
    MINOR_ISSUE = MainTags(
        id="708",
        key="Minor issue",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )  #
    NO_ISSUE = MainTags(
        id="709",
        key="No issue",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )  #
    SEVERE_ISSUE = MainTags(
        id="710",
        key="Severe issue",
        version=SEVERITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.SEVERITY.value, "id"),
    )  #

    # Affected Groups
    ASYLUM_SEEKERS = MainTags(
        id="801",
        key="Asylum Seekers",
        version=AFFECTED_GRP_VERSION,
        is_category=False,
        category_id=getattr(Categories.AFFECTED_GROUPS.value, "id"),
    )
    HOST = MainTags(
        id="802",
        key="Host",
        version=AFFECTED_GRP_VERSION,
        is_category=False,
        category_id=getattr(Categories.AFFECTED_GROUPS.value, "id"),
    )
    IDP = MainTags(
        id="803",
        key="IDP",
        version=AFFECTED_GRP_VERSION,
        is_category=False,
        category_id=getattr(Categories.AFFECTED_GROUPS.value, "id"),
    )
    MIGRANTS = MainTags(
        id="804",
        key="Migrants",
        version=AFFECTED_GRP_VERSION,
        is_category=False,
        category_id=getattr(Categories.AFFECTED_GROUPS.value, "id"),
    )
    REFUGEES = MainTags(
        id="805",
        key="Refugees",
        version=AFFECTED_GRP_VERSION,
        is_category=False,
        category_id=getattr(Categories.AFFECTED_GROUPS.value, "id"),
    )
    RETURNEES = MainTags(
        id="806",
        key="Returnees",
        version=AFFECTED_GRP_VERSION,
        is_category=False,
        category_id=getattr(Categories.AFFECTED_GROUPS.value, "id"),
    )

    # Reliability
    COMPLETELY_RELIABLE = MainTags(
        id="1001",
        key="Completely reliable",
        version=RELIABILITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.RELIABILITY.value, "id"),
    )
    USUALLY_RELIABLE = MainTags(
        id="1002",
        key="Usually reliable",
        version=RELIABILITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.RELIABILITY.value, "id"),
    )
    FAIRLY_RELIABLE = MainTags(
        id="1003",
        key="Fairly Reliable",
        version=RELIABILITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.RELIABILITY.value, "id"),
    )
    UNRELIABLE = MainTags(
        id="1004",
        key="Unreliable",
        version=RELIABILITY_VERSION,
        is_category=False,
        category_id=getattr(Categories.RELIABILITY.value, "id"),
    )

    @classmethod
    def sector_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.AGRICULTURE,
                Tags.CROSS,
                Tags.EDUCATION,
                Tags.FOOD_SECURITY,
                Tags.HEALTH,
                Tags.LIVELIHOODS,
                Tags.LOGISTICS,
                Tags.NUTRITION,
                Tags.PROTECTION,
                Tags.SHELTER,
                Tags.WASH,
            ]
        ]

    @classmethod
    def subpillars_1d_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.CONTEXT_ENVIRONMENT,
                Tags.CONTEXT_SOCIO_CULTURAL,
                Tags.CONTEXT_ECONOMY,
                Tags.CONTEXT_DEMOGRAPHY,
                Tags.CONTEXT_LEGAL_AND_POLICY,
                Tags.CONTEXT_SECURITY_AND_STABILITY,
                Tags.CONTEXT_POLITICS,
                Tags.SHOCK_EVENT_TYPE_AND_CHARACTERISTICS,
                Tags.SHOCK_EVENT_UNDERLYING_AGGRAVATING_FACTORS,
                Tags.SHOCK_EVENT_HAZARD_THREATS,
                Tags.DISPLACEMENT_TYPE_NUMBERS_MOVEMENTS,
                Tags.DISPLACEMENT_PUSH_FACTORS,
                Tags.DISPLACEMENT_PULL_FACTORS,
                Tags.DISPLACEMENT_INTENTIONS,
                Tags.DISPLACEMENT_LOCAL_INTEGRATION,
                Tags.CASUALTIES_INJURED,
                Tags.CASUALTIES_MISSING,
                Tags.CASUALTIES_DEAD,
                Tags.HUMANITARIAN_ACCESS_RELIEF_TO_POPULATION,
                Tags.HUMANITARIAN_ACCESS_POPULATION_TO_RELIEF,
                Tags.HUMANITARIAN_ACCESS_PHYSICAL_CONSTRAINTS,
                Tags.HUMANITARIAN_ACCESS_GAPS,
                Tags.INFORMATION_AND_COMMUNICATION_MEANS_AND_PREFERENCES,
                Tags.INFORMATION_AND_COMMUNICATION_INFO_CHALLENGES_AND_BARRIERS,
                Tags.INFORMATION_AND_COMMUNICATION_KNOWLEDGE_AND_INFO_GAPS_POP,
                Tags.INFORMATION_AND_COMMUNICATION_KNOWLEDGE_AND_INFO_GAPS_HUM,
                Tags.COVID_19_CASES,
                Tags.COVID_19_CONTACT_CASES,
                Tags.COVID_19_DEATHS,
                Tags.COVID_19_HOSPITALIZATION_AND_CARE,
                Tags.COVID_19_RESTRICTION_MEASURES,
                Tags.COVID_19_TESTING,
                Tags.COVID_19_VACCINATION,
                Tags.CONTEXT_TECHNOLOGICAL,  #
                Tags.COVID_19_PREVENTION_CAMPAIGN,  #
                Tags.COVID_19_RESEARCH_OUTLOOK,  #
            ]
        ]

    @classmethod
    def subpillars_2d_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.AT_RISK_NUMBER_OF_PEOPLE,
                Tags.AT_RISK_VULNERABILITIES,
                Tags.CAPACITIES_RESPONSE_INTERNATIONAL,
                Tags.CAPACITIES_RESPONSE_LOCAL,
                Tags.CAPACITIES_RESPONSE_NATIONAL,
                Tags.CAPACITIES_RESPONSE_NUM_PEOPLE_REACHED,
                Tags.HUMANITARIAN_CONDITIONS_COPING_MECHANISMS,
                Tags.HUMANITARIAN_CONDITIONS_LIVING_STANDARDS,
                Tags.HUMANITARIAN_CONDITIONS_NUM_PEOPLE_IN_NEED,
                Tags.HUMANITARIAN_CONDITIONS_PHY_MENTAL_WELL_BEING,
                Tags.IMPACT_DRIVER_AGGRAVATING_FACTORS,
                Tags.IMPACT_ON_PEOPLE,
                Tags.IMPACT_ON_SYSTEMS_SRV_NET,
                Tags.IMPACT_NUM_OF_PEOPLE_AFFECTED,
                Tags.PRIORITY_INTERVENTIONS_HUMANITARIAN_STAFF,
                Tags.PRIORITY_INTERVENTIONS_EXPRESSED_BY_POPULATION,
                Tags.PRIORITY_NEEDS_EXPRESSED_BY_HUMANITARIAN_STAFF,
                Tags.PRIORITY_NEEDS_EXPRESSED_BY_POPULATION,
                Tags.CAPACITIES_RESPONSE_HUMANITARIAN_COORDINATION,  #
                Tags.CAPACITIES_RESPONSE_PEOPLE_REACHED_RESPONSE_GAPS,  #
                Tags.CAPACITIES_RESPONSE_RED_CROSS_RED_CRESCENT,  #
            ]
        ]

    @classmethod
    def specific_needs_group_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.CHILD_HEAD_OF_HOUSEHOLD,
                Tags.CHRONICALLY_ILL,
                Tags.ELDERLY_HEAD_OF_HOUSEHOLD,
                Tags.FEMALE_HEAD_OF_HOUSEHOLD,
                Tags.GBV_SURVIVORS,
                Tags.INDIGENOUS_PEOPLE,
                Tags.LGBTQI,
                Tags.MINORITIES,
                Tags.PERSONS_WITH_DISABILITY,
                Tags.PREGNANT_OR_LACTATING_WOMEN,
                Tags.SINGLE_WOMEN_INCLUDING_WIDOWS,
                Tags.UNACCOMPANIED_OR_SEPARATED_CHILDREN,
                Tags.LGBTQIA_PLUS,  #
                Tags.UNACCOMPANIED_OR_AND_SEPARATED_CHILDREN,  #
            ]
        ]

    @classmethod
    def gender_list(cls):
        return [t.value._asdict() for t in [Tags.FEMALE, Tags.MALE, Tags.ALL]]  #

    @classmethod
    def age_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.ADULT_18_TO_59_YEARS_OLD,
                Tags.CHILDREN_YOUTH_5_TO_17,
                Tags.INFANTS_TODDLERS_LESS_THAN_5_YEARS,
                Tags.OLDER_PERSON_60_PLUS,
                Tags.TWELVE_SEVENTEEN_YEARS,  #
                Tags.EIGHTEEN_TWENTYFOUR_YEARS,  #
                Tags.EIGHTEEN_FIFTYNINE_YEARS,  #
                Tags.TWENTYFIVE_FIFTYNINE_YEARS,  #
                Tags.FIVE_ELEVEN_YEARS,  #
                Tags.FIVE_SEVENTEEN_YEARS,  #
                Tags.LESS_THAN_EIGHTEEN_YEARS,  #
                Tags.LESS_THAN_EIGHTEEN_YEARS_OLD,  #
                Tags.LESS_THAN_FIVE_YEARS,  #
                Tags.GREATER_THAN_SIXTY_YEARS,  #
            ]
        ]

    @classmethod
    def demographic_group_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.D_GRP_INFANTS_TODDLERS_LESS_THAN_5_YEARS,
                Tags.D_GRP_FEMALE_CHILDREN_YOUTH_5_TO_17,
                Tags.D_GRP_MALE_CHILDREN_YOUTH_5_TO_17,
                Tags.D_GRP_FEMALE_ADULT_18_TO_59_YEARS_OLD,
                Tags.D_GRP_MALE_ADULT_18_TO_59_YEARS_OLD,
                Tags.D_GRP_FEMALE_OLDER_PERSON_60_PLUS,
                Tags.D_GRP_MALE_OLDER_PERSON_60_PLUS,
            ]
        ]

    @classmethod
    def severity_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.CRITICAL,
                Tags.MAJOR,
                Tags.MINOR_PROBLEM,
                Tags.NO_PROBLEM,
                Tags.OF_CONCERN,
                Tags.CRITICAL_ISSUE,  #
                Tags.ISSUE_OF_CONCERN,  #
                Tags.MINOR_ISSUE,  #
                Tags.NO_ISSUE,  #
                Tags.SEVERE_ISSUE,  #
            ]
        ]

    @classmethod
    def affected_group_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.ASYLUM_SEEKERS,
                Tags.HOST,
                Tags.IDP,
                Tags.MIGRANTS,
                Tags.REFUGEES,
                Tags.RETURNEES,
            ]
        ]

    @classmethod
    def reliablity_list(cls):
        return [
            t.value._asdict()
            for t in [
                Tags.COMPLETELY_RELIABLE,
                Tags.USUALLY_RELIABLE,
                Tags.FAIRLY_RELIABLE,
                Tags.UNRELIABLE,
            ]
        ]


def get_all_mappings():
    all_tags = (
        Categories.all_models() +
        Tags.sector_list() +
        Tags.subpillars_1d_list() +
        Tags.subpillars_2d_list() +
        Tags.specific_needs_group_list() +
        Tags.gender_list() +
        Tags.age_list() +
        Tags.demographic_group_list() +
        Tags.severity_list() +
        Tags.affected_group_list() +
        Tags.reliablity_list()
    )
    return {d["key"].lower(): (d["id"], d["version"]) for d in all_tags}


def get_categories():
    all_categories = Categories.all_models()
    return {d["key"].lower(): (d["id"], d["version"]) for d in all_categories}


def id_to_alias_categories():
    all_categories = Categories.all_models()
    return {d["id"]: d["alias"] for d in all_categories}


def get_vf_list():
    show_tags = (
        Tags.sector_list() +
        Tags.subpillars_1d_list() +
        Tags.subpillars_2d_list() +
        Tags.specific_needs_group_list() +
        Tags.demographic_group_list() +
        Tags.severity_list() +
        Tags.affected_group_list() +
        Tags.reliablity_list()
    )

    id_to_alias = id_to_alias_categories()

    def handle_mapping(tags, hide_tag=False):
        vf_tags_temp = {}
        for d in tags:
            temp = {}
            if "->" in d["key"]:
                int_id = d["id"]
                temp[int_id] = {}
                temp[int_id]["label"] = d["key"].split("->")[1]
                temp[int_id]["group"] = d["key"].split("->")[0]

                if d["is_category"]:
                    temp[int_id]["is_category"] = True
                    temp[int_id]["hide_in_analysis_framework_mapping"] = True
                else:
                    temp[int_id]["is_category"] = False
                    temp[int_id]["parent_id"] = d["category_id"]
                    temp[int_id]["hide_in_analysis_framework_mapping"] = hide_tag
            else:
                int_id = d["id"]
                temp[int_id] = {}
                temp[int_id]["label"] = d["key"]
                temp[int_id]["group"] = (
                    id_to_alias[d["category_id"]] if "category_id" in d else d["alias"]
                )

                if d["is_category"]:
                    temp[int_id]["is_category"] = True
                    temp[int_id]["hide_in_analysis_framework_mapping"] = True
                else:
                    temp[int_id]["is_category"] = False
                    temp[int_id]["parent_id"] = d["category_id"]
                    temp[int_id]["hide_in_analysis_framework_mapping"] = hide_tag

            vf_tags_temp.update(temp)
        return vf_tags_temp

    hide_tags = Categories.all_models() + Tags.gender_list() + Tags.age_list()
    final_vf_tags = handle_mapping(show_tags)
    final_vf_tags.update(handle_mapping(hide_tags, True))

    return final_vf_tags
