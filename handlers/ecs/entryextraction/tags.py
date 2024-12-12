from collections import namedtuple
from enum import Enum

version = "1.0"

FirstLevelCategories = namedtuple(
    "FirstLevelCategories", ["id", "key", "version", "has_parent", "parent_id", "alias"]
)


class FirstLevel(Enum):
    SubsectorsTag = FirstLevelCategories(
        id="1",
        key="subsectors",
        version=version,
        has_parent=False,
        parent_id=None,
        alias="Subsectors",
    )
    FirstLevelTag = FirstLevelCategories(
        id="2",
        key="first_level_tags",
        version=version,
        has_parent=False,
        parent_id=None,
        alias="First Level Tags",
    )
    Subpillars1DTag = FirstLevelCategories(
        id="3",
        key="subpillars_1d",
        version=version,
        has_parent=False,
        parent_id=None,
        alias="Subpillars 1D",
    )
    Subpillars2DTag = FirstLevelCategories(
        id="4",
        key="subpillars_2d",
        version=version,
        has_parent=False,
        parent_id=None,
        alias="Subpillars 2D",
    )
    SecondaryTags = FirstLevelCategories(
        id="5",
        key="secondary_tags",
        version=version,
        has_parent=False,
        parent_id=None,
        alias="Secondary Tags",
    )

    @classmethod
    def first_level_lst(cls):
        return [
            t.value._asdict()
            for t in [
                FirstLevel.SubsectorsTag,
                FirstLevel.FirstLevelTag,
                FirstLevel.Subpillars1DTag,
                FirstLevel.Subpillars2DTag,
                FirstLevel.SecondaryTags,
            ]
        ]


SecondLevelCategories = namedtuple(
    "SecondLevelCategories",
    ["id", "key", "version", "has_parent", "parent_id", "alias"],
)
version = "1.0"


class SecondLevel(Enum):
    EducationTag = SecondLevelCategories(
        id="101",
        key="Education",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Education",
    )
    HealthTag = SecondLevelCategories(
        id="102",
        key="Health",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Health",
    )
    LivelihoodsTag = SecondLevelCategories(
        id="103",
        key="Livelihoods",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Livelihoods",
    )
    LogisticsTag = SecondLevelCategories(
        id="104",
        key="Logistics",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Logistics",
    )
    ShelterTag = SecondLevelCategories(
        id="105",
        key="Shelter",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Shelter",
    )
    NutritionTag = SecondLevelCategories(
        id="106",
        key="Nutrition",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Nutrition",
    )
    ProtectionTag = SecondLevelCategories(
        id="107",
        key="Protection",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Protection",
    )
    WashTag = SecondLevelCategories(
        id="108",
        key="Wash",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SubsectorsTag.value, "id"),
        alias="Wash",
    )
    SectorsTag = SecondLevelCategories(
        id="201",
        key="sectors",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.FirstLevelTag.value, "id"),
        alias="Sectors",
    )
    Pillars1DTag = SecondLevelCategories(
        id="202",
        key="pillars_1d",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.FirstLevelTag.value, "id"),
        alias="Pillars 1D",
    )
    Pillars2DTag = SecondLevelCategories(
        id="203",
        key="pillars_2d",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.FirstLevelTag.value, "id"),
        alias="Pillars 2D",
    )
    AffectedTag = SecondLevelCategories(
        id="204",
        key="Affected",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.FirstLevelTag.value, "id"),
        alias="Affected",
    )
    CasualtiesTag = SecondLevelCategories(
        id="301",
        key="Casualties",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars1DTag.value, "id"),
        alias="Casualties",
    )
    ContextTag = SecondLevelCategories(
        id="302",
        key="Context",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars1DTag.value, "id"),
        alias="Context",
    )
    Covid19Tag = SecondLevelCategories(
        id="303",
        key="Covid-19",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars1DTag.value, "id"),
        alias="COVID-19",
    )
    DisplacementTag = SecondLevelCategories(
        id="304",
        key="Displacement",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars1DTag.value, "id"),
        alias="Displacement",
    )
    HumanitarianAccessTag = SecondLevelCategories(
        id="305",
        key="Humanitarian access",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars1DTag.value, "id"),
        alias="Humanitarian Access",
    )
    InfoAndCommTag = SecondLevelCategories(
        id="306",
        key="Information and communication",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars1DTag.value, "id"),
        alias="Information and Communication",
    )
    ShockEventTag = SecondLevelCategories(
        id="307",
        key="Shock/event",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars1DTag.value, "id"),
        alias="Shock/Event",
    )
    AtRiskTag = SecondLevelCategories(
        id="401",
        key="At risk",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars2DTag.value, "id"),
        alias="At Risk",
    )
    CapacitiesAndResponseTag = SecondLevelCategories(
        id="402",
        key="Capacities & response",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars2DTag.value, "id"),
        alias="Capacities And Response",
    )
    HumanitarianConditionsTag = SecondLevelCategories(
        id="403",
        key="Humanitarian conditions",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars2DTag.value, "id"),
        alias="Humanitarian Conditions",
    )
    ImpactTag = SecondLevelCategories(
        id="404",
        key="Impact",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars2DTag.value, "id"),
        alias="Impact",
    )
    PriorityInterventionsTag = SecondLevelCategories(
        id="405",
        key="Priority interventions",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars2DTag.value, "id"),
        alias="Priority Interventions",
    )
    PriorityNeedsTag = SecondLevelCategories(
        id="406",
        key="Priority needs",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.Subpillars2DTag.value, "id"),
        alias="Priority Needs",
    )
    DisplacedTag = SecondLevelCategories(
        id="501",
        key="Displaced",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SecondaryTags.value, "id"),
        alias="Displaced",
    )
    NonDisplacedTag = SecondLevelCategories(
        id="502",
        key="Non displaced",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SecondaryTags.value, "id"),
        alias="Non Displaced",
    )
    AgeTag = SecondLevelCategories(
        id="503",
        key="Age",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SecondaryTags.value, "id"),
        alias="Age",
    )
    GenderTag = SecondLevelCategories(
        id="504",
        key="Gender",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SecondaryTags.value, "id"),
        alias="Gender",
    )
    ReliabilityTag = SecondLevelCategories(
        id="505",
        key="reliability",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SecondaryTags.value, "id"),
        alias="Reliability",
    )
    SeverityTag = SecondLevelCategories(
        id="506",
        key="severity",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SecondaryTags.value, "id"),
        alias="Severity",
    )
    SpecificNeedsGroupsTag = SecondLevelCategories(
        id="507",
        key="specific_needs_groups",
        version=version,
        has_parent=True,
        parent_id=getattr(FirstLevel.SecondaryTags.value, "id"),
        alias="Specific Needs Groups",
    )

    @classmethod
    def second_level_lst(cls):
        return [
            t.value._asdict()
            for t in [
                SecondLevel.EducationTag,
                SecondLevel.HealthTag,
                SecondLevel.LivelihoodsTag,
                SecondLevel.LogisticsTag,
                SecondLevel.ShelterTag,
                SecondLevel.NutritionTag,
                SecondLevel.ProtectionTag,
                SecondLevel.WashTag,
                SecondLevel.SectorsTag,
                SecondLevel.Pillars1DTag,
                SecondLevel.Pillars2DTag,
                SecondLevel.AffectedTag,
                SecondLevel.CasualtiesTag,
                SecondLevel.ContextTag,
                SecondLevel.Covid19Tag,
                SecondLevel.DisplacementTag,
                SecondLevel.HumanitarianAccessTag,
                SecondLevel.InfoAndCommTag,
                SecondLevel.ShockEventTag,
                SecondLevel.AtRiskTag,
                SecondLevel.CapacitiesAndResponseTag,
                SecondLevel.HumanitarianConditionsTag,
                SecondLevel.ImpactTag,
                SecondLevel.PriorityInterventionsTag,
                SecondLevel.PriorityNeedsTag,
                SecondLevel.DisplacedTag,
                SecondLevel.NonDisplacedTag,
                SecondLevel.AgeTag,
                SecondLevel.GenderTag,
                SecondLevel.ReliabilityTag,
                SecondLevel.SeverityTag,
                SecondLevel.SpecificNeedsGroupsTag,
            ]
        ]


ThirdLevelCategories = namedtuple(
    "ThirdLevelCategories", ["id", "key", "version", "has_parent", "parent_id", "alias"]
)
version = "1.0"


class ThirdLevel(Enum):
    # Education - 101
    FacilitiesAndAmenitiesTag = ThirdLevelCategories(
        id="1101",
        key="Facilities and amenities",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.EducationTag.value, "id"),
        alias="Facilities and Amenities",
    )
    LearningEnvironmentTag = ThirdLevelCategories(
        id="1102",
        key="Learning environment",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.EducationTag.value, "id"),
        alias="Learning Environment",
    )
    TeachersAndEduPersonnelTag = ThirdLevelCategories(
        id="1103",
        key="Teachers and education personnel",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.EducationTag.value, "id"),
        alias="Teachers and Education Personnel",
    )
    TeachingAndLearningTag = ThirdLevelCategories(
        id="1104",
        key="Teaching and learning",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.EducationTag.value, "id"),
        alias="Teaching and Learning",
    )
    # Health - 102
    HealthCareSystemTag = ThirdLevelCategories(
        id="1201",
        key="Health care system",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HealthTag.value, "id"),
        alias="Health Care System",
    )
    HealthStatusTag = ThirdLevelCategories(
        id="1202",
        key="Health status",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HealthTag.value, "id"),
        alias="Health Status",
    )
    # Livelihoods - 103
    AssetsTag = ThirdLevelCategories(
        id="1301",
        key="Assets",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.LivelihoodsTag.value, "id"),
        alias="Assets",
    )
    ExpendituresTag = ThirdLevelCategories(
        id="1302",
        key="Expenditures",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.LivelihoodsTag.value, "id"),
        alias="Expenditures",
    )
    IncomeTag = ThirdLevelCategories(
        id="1303",
        key="Income",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.LivelihoodsTag.value, "id"),
        alias="Income",
    )
    SkillsAndQualificationsTag = ThirdLevelCategories(
        id="1304",
        key="Skills and qualifications",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.LivelihoodsTag.value, "id"),
        alias="Skills and Qualifications",
    )
    # Logistics - 104
    SupplyChainTag = ThirdLevelCategories(
        id="1401",
        key="Supply chain",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.LogisticsTag.value, "id"),
        alias="Supply Chain",
    )

    CommunicationTag = ThirdLevelCategories(
        id="1402",
        key="Communication",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.LogisticsTag.value, "id"),
        alias="Communication",
    )

    # Shelter - 105
    DomesticLivingSpaceTag = ThirdLevelCategories(
        id="1501",
        key="Domestic living space",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ShelterTag.value, "id"),
        alias="Domestic Living Space",
    )
    DwellingEnvelopeTag = ThirdLevelCategories(
        id="1502",
        key="Dwelling enveloppe",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ShelterTag.value, "id"),
        alias="Dwelling Enveloppe",
    )
    # Nutrition - 106
    NutritionGoodsAndServicesTag = ThirdLevelCategories(
        id="1601",
        key="Nutrition goods and services",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.NutritionTag.value, "id"),
        alias="Nutrition Goods And Services",
    )
    NutritionalStatusTag = ThirdLevelCategories(
        id="1602",
        key="Nutritional status",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.NutritionTag.value, "id"),
        alias="Nutritional Status",
    )
    # Protection - 107
    ChildProtectionTag = ThirdLevelCategories(
        id="1701",
        key="Child protection",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Child Protection",
    )
    CivilAndPoliticalRightsTag = ThirdLevelCategories(
        id="1702",
        key="Civil and political rights",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Civil and Political Rights",
    )
    DocumentationTag = ThirdLevelCategories(
        id="1703",
        key="Documentation",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Documentation",
    )
    FreedomOfMovementTag = ThirdLevelCategories(
        id="1704",
        key="Freedom of movement",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Freedom of Movement",
    )
    HousingLandAndPropertyTag = ThirdLevelCategories(
        id="1705",
        key="Housing land and property",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Housing land and property",
    )
    HumanRightsTag = ThirdLevelCategories(
        id="1706",
        key="Human rights",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Human rights",
    )
    JusticeAndRuleOfLawTag = ThirdLevelCategories(
        id="1707",
        key="Justice and rule of law",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Justice And Rule Of Law",
    )
    LibertyTag = ThirdLevelCategories(
        id="1708",
        key="Liberty",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Liberty",
    )
    MinesTag = ThirdLevelCategories(
        id="1709",
        key="Mines",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Mines",
    )
    PhysicalSafetyAndSecurityTag = ThirdLevelCategories(
        id="1710",
        key="Physical safety and security",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Physical Safety and Security",
    )
    SexualAndGenderBasedViolenceTag = ThirdLevelCategories(
        id="1711",
        key="Sexual and gender based violence",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ProtectionTag.value, "id"),
        alias="Sexual and gender based violence",
    )
    # 108
    HygieneTag = ThirdLevelCategories(
        id="1801",
        key="Hygiene",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.WashTag.value, "id"),
        alias="Hygiene",
    )
    SanitationTag = ThirdLevelCategories(
        id="1802",
        key="Sanitation",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.WashTag.value, "id"),
        alias="Sanitation",
    )
    WaterSupplyTag = ThirdLevelCategories(
        id="1803",
        key="Water supply",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.WashTag.value, "id"),
        alias="Water Supply",
    )
    WasteManagementTag = ThirdLevelCategories(
        id="1804",
        key="Waste management",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.WashTag.value, "id"),
        alias="Waste Management",
    )
    VectorControlTag = ThirdLevelCategories(
        id="1805",
        key="Vector control",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.WashTag.value, "id"),
        alias="Vector Control",
    )
    # 201
    LivelihoodsTag = ThirdLevelCategories(
        id="2101",
        key="Livelihoods",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Livelihoods",
    )
    NutritionTag = ThirdLevelCategories(
        id="2102",
        key="Nutrition",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Nutrition",
    )
    AgricultureTag = ThirdLevelCategories(
        id="2103",
        key="Agriculture",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Agriculture",
    )
    CrossTag = ThirdLevelCategories(
        id="2104",
        key="Cross",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Cross",
    )
    FoodSecurityTag = ThirdLevelCategories(
        id="2105",
        key="Food security",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Food Security",
    )
    ShelterTag = ThirdLevelCategories(
        id="2106",
        key="Shelter",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Shelter",
    )
    EducationTag = ThirdLevelCategories(
        id="2107",
        key="Education",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Education",
    )
    WashTag = ThirdLevelCategories(
        id="2108",
        key="Wash",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Wash",
    )
    LogisticsTag = ThirdLevelCategories(
        id="2109",
        key="Logistics",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Logistics",
    )
    HealthTag = ThirdLevelCategories(
        id="2110",
        key="Health",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Health",
    )
    ProtectionTag = ThirdLevelCategories(
        id="2111",
        key="Protection",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SectorsTag.value, "id"),
        alias="Protection",
    )
    # 202
    DisplacementTag = ThirdLevelCategories(
        id="2201",
        key="Displacement",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars1DTag.value, "id"),
        alias="Displacement",
    )
    ShockEventTag = ThirdLevelCategories(
        id="2202",
        key="Shock/event",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars1DTag.value, "id"),
        alias="Shock/Event",
    )
    Covid19Tag = ThirdLevelCategories(
        id="2203",
        key="Covid-19",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars1DTag.value, "id"),
        alias="Covid-19",
    )
    InformationAndCommTag = ThirdLevelCategories(
        id="2204",
        key="Information and communication",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars1DTag.value, "id"),
        alias="Information and Communication",
    )
    ContextTag = ThirdLevelCategories(
        id="2205",
        key="Context",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars1DTag.value, "id"),
        alias="Context",
    )
    CasualtiesTag = ThirdLevelCategories(
        id="2206",
        key="Casualties",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars1DTag.value, "id"),
        alias="Casualties",
    )
    HumanitarianAccessTag = ThirdLevelCategories(
        id="2207",
        key="Humanitarian access",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars1DTag.value, "id"),
        alias="Humanitarian Access",
    )
    # 203
    ImpactTag = ThirdLevelCategories(
        id="2301",
        key="Impact",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars2DTag.value, "id"),
        alias="Impact",
    )
    AtRiskTag = ThirdLevelCategories(
        id="2302",
        key="At risk",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars2DTag.value, "id"),
        alias="At Risk",
    )
    CapacitiesAndResponseTag = ThirdLevelCategories(
        id="2303",
        key="Capacities & response",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars2DTag.value, "id"),
        alias="Capacities & Response",
    )
    PriorityInterventionsTag = ThirdLevelCategories(
        id="2304",
        key="Priority interventions",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars2DTag.value, "id"),
        alias="Priority Interventions",
    )
    HumanitarianConditionsTag = ThirdLevelCategories(
        id="2305",
        key="Humanitarian conditions",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars2DTag.value, "id"),
        alias="Humanitarian conditions",
    )
    PriorityNeedsTag = ThirdLevelCategories(
        id="2306",
        key="Priority needs",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Pillars2DTag.value, "id"),
        alias="Priority needs",
    )
    # 204
    NonDisplacedTag = ThirdLevelCategories(
        id="2401",
        key="Non displaced",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AffectedTag.value, "id"),
        alias="Non displaced",
    )
    DisplacedTag = ThirdLevelCategories(
        id="2402",
        key="Displaced",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AffectedTag.value, "id"),
        alias="Displaced",
    )
    # 301
    InjuredTag = ThirdLevelCategories(
        id="3101",
        key="Injured",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CasualtiesTag.value, "id"),
        alias="Injured",
    )
    DeadTag = ThirdLevelCategories(
        id="3102",
        key="Dead",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CasualtiesTag.value, "id"),
        alias="Dead",
    )
    MissingTag = ThirdLevelCategories(
        id="3103",
        key="Missing",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CasualtiesTag.value, "id"),
        alias="Missing",
    )
    # 302
    TechnologicalTag = ThirdLevelCategories(
        id="3201",
        key="Technological",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Technological",
    )
    LegalAndPolicyTag = ThirdLevelCategories(
        id="3202",
        key="Legal & policy",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Legal and Policy",
    )
    EconomyTag = ThirdLevelCategories(
        id="3203",
        key="Economy",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Economy",
    )
    SecurityAndStabilityTag = ThirdLevelCategories(
        id="3204",
        key="Security & stability",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Security & stability",
    )
    SocioCulturalTag = ThirdLevelCategories(
        id="3205",
        key="Socio cultural",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Socio cultural",
    )
    DemographyTag = ThirdLevelCategories(
        id="3206",
        key="Demography",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Demography",
    )
    PoliticsTag = ThirdLevelCategories(
        id="3207",
        key="Politics",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Politics",
    )
    EnvironmentTag = ThirdLevelCategories(
        id="3208",
        key="Environment",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ContextTag.value, "id"),
        alias="Environment",
    )
    # 303
    ContactTracingTag = ThirdLevelCategories(
        id="3301",
        key="Contact tracing",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Contact tracing",
    )
    HospitalizationAndCareTag = ThirdLevelCategories(
        id="3302",
        key="Hospitalization & care",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Hospitalization And Care",
    )
    DeathsTag = ThirdLevelCategories(
        id="3303",
        key="Deaths",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Deaths",
    )
    CasesTag = ThirdLevelCategories(
        id="3304",
        key="Cases",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Cases",
    )
    PreventionCampaignTag = ThirdLevelCategories(
        id="3305",
        key="Prevention campaign",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Prevention campaign",
    )
    VaccinationTag = ThirdLevelCategories(
        id="3306",
        key="Vaccination",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Vaccination",
    )
    ResearchAndOutlookTag = ThirdLevelCategories(
        id="3307",
        key="Research and outlook",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Research and outlook",
    )
    TestingTag = ThirdLevelCategories(
        id="3308",
        key="Testing",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Testing",
    )
    RestrictionMeasuresTag = ThirdLevelCategories(
        id="3309",
        key="Restriction measures",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.Covid19Tag.value, "id"),
        alias="Restriction measures",
    )
    # 304
    PushFactors = ThirdLevelCategories(
        id="3401",
        key="Push factors",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacementTag.value, "id"),
        alias="Push Factors",
    )
    LocalIntegrationTag = ThirdLevelCategories(
        id="3402",
        key="Local integration",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacementTag.value, "id"),
        alias="Local integration",
    )
    TypeNumbersMovementsTag = ThirdLevelCategories(
        id="3403",
        key="Type/numbers/movements",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacementTag.value, "id"),
        alias="Type/numbers/movements",
    )
    PullFactorsTag = ThirdLevelCategories(
        id="3404",
        key="Pull factors",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacementTag.value, "id"),
        alias="Pull Factors",
    )
    IntentionsTag = ThirdLevelCategories(
        id="3405",
        key="Intentions",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacementTag.value, "id"),
        alias="Intentions",
    )
    # 305
    PeopleHumanitarianAccessConstraintsTag = ThirdLevelCategories(
        id="3501",
        key="People facing humanitarian access constraints/humanitarian access gaps",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianAccessTag.value, "id"),
        alias="People facing humanitarian access constraints/humanitarian access gaps",
    )
    PhysicalConstraintsTag = ThirdLevelCategories(
        id="3502",
        key="Physical constraints",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianAccessTag.value, "id"),
        alias="Physical constraints",
    )
    SecurityConstraintsTag = ThirdLevelCategories(
        id="3503",
        key="Security constraints",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianAccessTag.value, "id"),
        alias="Security Constraints",
    )
    PopulationToReliefTag = ThirdLevelCategories(
        id="3504",
        key="Population to relief",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianAccessTag.value, "id"),
        alias="Population to relief",
    )
    ReliefToPopulationTag = ThirdLevelCategories(
        id="3505",
        key="Relief to population",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianAccessTag.value, "id"),
        alias="Relief to population",
    )
    # 306
    InfoChallengesAndBarriersTag = ThirdLevelCategories(
        id="3601",
        key="Information challenges and barriers",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.InfoAndCommTag.value, "id"),
        alias="Information challenges and barriers",
    )
    CommMeansAndPreferencesTag = ThirdLevelCategories(
        id="3602",
        key="Communication means and preferences",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.InfoAndCommTag.value, "id"),
        alias="Communication means and preferences",
    )
    KnowledgeAndInfoGapsHumTag = ThirdLevelCategories(
        id="3603",
        key="Knowledge and info gaps (hum)",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.InfoAndCommTag.value, "id"),
        alias="Knowledge and info gaps (hum)",
    )
    KnowledgeAndInfoGapsPopTag = ThirdLevelCategories(
        id="3604",
        key="Knowledge and info gaps (pop)",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.InfoAndCommTag.value, "id"),
        alias="Knowledge and info gaps (pop)",
    )
    # 307
    MitigatingFactorsTag = ThirdLevelCategories(
        id="3701",
        key="Mitigating factors",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ShockEventTag.value, "id"),
        alias="Mitigating factors",
    )
    TypeAndCharacteristicsTag = ThirdLevelCategories(
        id="3702",
        key="Type and characteristics",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ShockEventTag.value, "id"),
        alias="Type and characteristics",
    )
    HazardAndThreatsTag = ThirdLevelCategories(
        id="3703",
        key="Hazard & threats",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ShockEventTag.value, "id"),
        alias="Hazard & threats",
    )
    UnderlyingAggravatingFactorsTag = ThirdLevelCategories(
        id="3704",
        key="Underlying/aggravating factors",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ShockEventTag.value, "id"),
        alias="Underlying/aggravating factors",
    )
    # 401
    RiskAndVulnerabilitiesTag = ThirdLevelCategories(
        id="4101",
        key="Risk and vulnerabilities",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AtRiskTag.value, "id"),
        alias="Risk and vulnerabilities",
    )
    NumberOfPeopleAtRiskTag = ThirdLevelCategories(
        id="4102",
        key="Number of people at risk",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AtRiskTag.value, "id"),
        alias="Number of people at risk",
    )
    # 402
    LocalResponseTag = ThirdLevelCategories(
        id="4201",
        key="Local response",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CapacitiesAndResponseTag.value, "id"),
        alias="Local response",
    )
    NationalResponseTag = ThirdLevelCategories(
        id="4202",
        key="National response",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CapacitiesAndResponseTag.value, "id"),
        alias="National Response",
    )
    HumanitarianCoordinationTag = ThirdLevelCategories(
        id="4203",
        key="Humanitarian coordination",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CapacitiesAndResponseTag.value, "id"),
        alias="Humanitarian coordination",
    )
    InternationalResponseTag = ThirdLevelCategories(
        id="4204",
        key="International response",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CapacitiesAndResponseTag.value, "id"),
        alias="International response",
    )
    RedCrossTag = ThirdLevelCategories(
        id="4205",
        key="Red cross/red crescent",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CapacitiesAndResponseTag.value, "id"),
        alias="Red cross/red crescent",
    )
    PeopleReachedResponseGapsTag = ThirdLevelCategories(
        id="4206",
        key="People reached/response gaps",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.CapacitiesAndResponseTag.value, "id"),
        alias="People reached/response gaps",
    )
    # 403
    PhysicalAndMentalWellBeingTag = ThirdLevelCategories(
        id="4301",
        key="Physical and mental well being",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianConditionsTag.value, "id"),
        alias="Physical and mental well being",
    )
    LivingStandardsTag = ThirdLevelCategories(
        id="4302",
        key="Living standards",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianConditionsTag.value, "id"),
        alias="Living standards",
    )
    CopingMechanismsTag = ThirdLevelCategories(
        id="4303",
        key="Coping mechanisms",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianConditionsTag.value, "id"),
        alias="Coping Mechanisms",
    )
    NumberOfPeopleInNeedTag = ThirdLevelCategories(
        id="4304",
        key="Number of people in need",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.HumanitarianConditionsTag.value, "id"),
        alias="Number of people in need",
    )
    # 404
    ImpactOnSystemsServicesNetworksTag = ThirdLevelCategories(
        id="4401",
        key="Impact on systems, services and networks",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ImpactTag.value, "id"),
        alias="Impact on systems, services and networks",
    )
    DriverAggravatingFactorsTag = ThirdLevelCategories(
        id="4402",
        key="Driver/aggravating factors",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ImpactTag.value, "id"),
        alias="Driver/aggravating factors",
    )
    NumberOfPeopleAffectedTag = ThirdLevelCategories(
        id="4403",
        key="Number of people affected",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ImpactTag.value, "id"),
        alias="Number of people affected",
    )
    ImpactOnPeopleTag = ThirdLevelCategories(
        id="4404",
        key="Impact on people",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ImpactTag.value, "id"),
        alias="Impact on people",
    )
    # 405
    ExpressedByHumanitarianStaffTag = ThirdLevelCategories(
        id="4501",
        key="Expressed by humanitarian staff",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.PriorityInterventionsTag.value, "id"),
        alias="Expressed by humanitarian staff",
    )
    ExpressedByPopulationTag = ThirdLevelCategories(
        id="4502",
        key="Expressed by population",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.PriorityInterventionsTag.value, "id"),
        alias="Expressed by population",
    )
    # 406

    # 501
    PendularTag = ThirdLevelCategories(
        id="5101",
        key="Pendular",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Pendular",
    )
    AsylumSeekersTag = ThirdLevelCategories(
        id="5102",
        key="Asylum seekers",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Asylum seekers",
    )
    RefugeesTag = ThirdLevelCategories(
        id="5103",
        key="Refugees",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Refugees",
    )
    RegularTag = ThirdLevelCategories(
        id="5104",
        key="Regular",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Regular",
    )
    ReturneesTag = ThirdLevelCategories(
        id="5105",
        key="Returnees",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Returnees",
    )
    InTransitTag = ThirdLevelCategories(
        id="5106",
        key="In transit",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="In transit",
    )
    OthersOfConcernTag = ThirdLevelCategories(
        id="5107",
        key="Others of concern",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Others of concern",
    )
    IrregularTag = ThirdLevelCategories(
        id="5108",
        key="Irregular",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Irregular",
    )
    IDPTag = ThirdLevelCategories(
        id="5109",
        key="Idp",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Idp",
    )
    StatelessTag = ThirdLevelCategories(
        id="5110",
        key="Stateless",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Stateless",
    )
    MigrantsTag = ThirdLevelCategories(
        id="5111",
        key="Migrants",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.DisplacedTag.value, "id"),
        alias="Migrants",
    )
    # 502
    HostTag = ThirdLevelCategories(
        id="5201",
        key="Host",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.NonDisplacedTag.value, "id"),
        alias="Host",
    )
    NonHostTag = ThirdLevelCategories(
        id="5202",
        key="Non host",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.NonDisplacedTag.value, "id"),
        alias="Non host",
    )
    # 503
    Age18YearsOldTag = ThirdLevelCategories(
        id="5301",
        key="<18 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="<18 years old",
    )
    Age2559YearsOldTag = ThirdLevelCategories(
        id="5302",
        key="25-59 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="25-59 years old",
    )
    Age1217YearsOldTag = ThirdLevelCategories(
        id="5303",
        key="12-17 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="12-17 years old",
    )
    Age60YearsOldTag = ThirdLevelCategories(
        id="5304",
        key=">60 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias=">60 years old",
    )
    Age5YearsOldTag = ThirdLevelCategories(
        id="5305",
        key="<5 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="<5 years old",
    )
    Age1824YearsOldTag = ThirdLevelCategories(
        id="5306",
        key="18-24 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="18-24 years old",
    )
    Age511YearsOldTag = ThirdLevelCategories(
        id="5307",
        key="5-11 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="5-11 years old",
    )
    Age18YearsTag = ThirdLevelCategories(
        id="5308",
        key="<18 years",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="<18 years",
    )
    Age517YearsOldTag = ThirdLevelCategories(
        id="5309",
        key="5-17 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="5-17 years old",
    )
    Age1859YearsOldTag = ThirdLevelCategories(
        id="5310",
        key="18-59 years old",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.AgeTag.value, "id"),
        alias="18-59 years old",
    )
    # 504
    FemaleTag = ThirdLevelCategories(
        id="5401",
        key="Female",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.GenderTag.value, "id"),
        alias="Female",
    )
    MaleTag = ThirdLevelCategories(
        id="5402",
        key="Male",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.GenderTag.value, "id"),
        alias="Male",
    )
    AllTag = ThirdLevelCategories(
        id="5403",
        key="All",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.GenderTag.value, "id"),
        alias="All",
    )
    # 505
    UnreliableTag = ThirdLevelCategories(
        id="5501",
        key="Unreliable",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ReliabilityTag.value, "id"),
        alias="Unreliable",
    )
    CompletelyReliableTag = ThirdLevelCategories(
        id="5502",
        key="Completely reliable",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ReliabilityTag.value, "id"),
        alias="Completely reliable",
    )
    CannotBeJudgedTag = ThirdLevelCategories(
        id="5503",
        key="Cannot be judged",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ReliabilityTag.value, "id"),
        alias="Cannot be judged",
    )
    UsuallyReliableTag = ThirdLevelCategories(
        id="5504",
        key="Usually reliable",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ReliabilityTag.value, "id"),
        alias="Usually reliable",
    )
    FairlyReliableTag = ThirdLevelCategories(
        id="5505",
        key="Fairly reliable",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.ReliabilityTag.value, "id"),
        alias="Fairly reliable",
    )
    # 506
    IssueOfConcernTag = ThirdLevelCategories(
        id="5601",
        key="Issue of concern",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SeverityTag.value, "id"),
        alias="Issue of concern",
    )
    SevereIssueTag = ThirdLevelCategories(
        id="5602",
        key="Severe issue",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SeverityTag.value, "id"),
        alias="Severe issue",
    )
    MinorIssueTag = ThirdLevelCategories(
        id="5603",
        key="Minor issue",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SeverityTag.value, "id"),
        alias="Minor issue",
    )
    CriticalIssueTag = ThirdLevelCategories(
        id="5604",
        key="Critical issue",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SeverityTag.value, "id"),
        alias="Critical issue",
    )
    NoIssueTag = ThirdLevelCategories(
        id="5605",
        key="No issue",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SeverityTag.value, "id"),
        alias="No issue",
    )
    # 507
    PregnantOrLactatingWomenTag = ThirdLevelCategories(
        id="5701",
        key="Pregnant or lactating women",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Pregnant or lactating women",
    )
    SingleWomenInclWidowsTag = ThirdLevelCategories(
        id="5702",
        key="Single women (including widows)",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Single women (including widows)",
    )
    ChildHeadOfHouseholdTag = ThirdLevelCategories(
        id="5703",
        key="Child head of household",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Child head of household",
    )
    UnaccompaniedAndSeparatedChildrenTag = ThirdLevelCategories(
        id="5704",
        key="Unaccompanied or/and separated children",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Unaccompanied or/and separated children",
    )
    MinoritiesTag = ThirdLevelCategories(
        id="5705",
        key="Minorities",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Minorities",
    )
    LGBTQIATag = ThirdLevelCategories(
        id="5706",
        key="Lgbtqia+",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Lgbtqia+",
    )
    PersonsWithDisabilityTag = ThirdLevelCategories(
        id="5707",
        key="Persons with disability",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Persons with disability",
    )
    FemaleHeadOfHouseholdTag = ThirdLevelCategories(
        id="5708",
        key="Female head of household",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Female head of household",
    )
    ChronicallyIllTag = ThirdLevelCategories(
        id="5709",
        key="Chronically ill",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Chronically ill",
    )
    UnaccompaniedOrSeparatedChildrenTag = ThirdLevelCategories(
        id="5710",
        key="Unaccompanied or separated children",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Unaccompanied or separated children",
    )
    ElderlyHeadOfHouseholdTag = ThirdLevelCategories(
        id="5711",
        key="Elderly head of household",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Elderly head of household",
    )
    IndigenousPeopleTag = ThirdLevelCategories(
        id="5712",
        key="Indigenous people",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Indigenous people",
    )
    GBVSurvivorsTag = ThirdLevelCategories(
        id="5713",
        key="Gbv survivors",
        version=version,
        has_parent=True,
        parent_id=getattr(SecondLevel.SpecificNeedsGroupsTag.value, "id"),
        alias="Gbv survivors",
    )

    @classmethod
    def third_level_lst(cls):
        return [
            t.value._asdict()
            for t in [
                ThirdLevel.FacilitiesAndAmenitiesTag,  # 101
                ThirdLevel.LearningEnvironmentTag,
                ThirdLevel.TeachersAndEduPersonnelTag,
                ThirdLevel.TeachingAndLearningTag,
                ThirdLevel.HealthCareSystemTag,  # 102
                ThirdLevel.HealthStatusTag,
                ThirdLevel.AssetsTag,  # 103
                ThirdLevel.ExpendituresTag,
                ThirdLevel.IncomeTag,
                ThirdLevel.SkillsAndQualificationsTag,
                ThirdLevel.SupplyChainTag,  # 104
                ThirdLevel.CommunicationTag,
                ThirdLevel.DomesticLivingSpaceTag,  # 105
                ThirdLevel.DwellingEnvelopeTag,
                ThirdLevel.NutritionGoodsAndServicesTag,  # 106
                ThirdLevel.NutritionalStatusTag,
                ThirdLevel.ChildProtectionTag,  # 107
                ThirdLevel.CivilAndPoliticalRightsTag,
                ThirdLevel.DocumentationTag,
                ThirdLevel.FreedomOfMovementTag,
                ThirdLevel.HousingLandAndPropertyTag,
                ThirdLevel.HumanRightsTag,
                ThirdLevel.JusticeAndRuleOfLawTag,
                ThirdLevel.LibertyTag,
                ThirdLevel.MinesTag,
                ThirdLevel.PhysicalSafetyAndSecurityTag,
                ThirdLevel.SexualAndGenderBasedViolenceTag,
                ThirdLevel.HygieneTag,  # 108
                ThirdLevel.SanitationTag,
                ThirdLevel.WaterSupplyTag,
                ThirdLevel.WasteManagementTag,
                ThirdLevel.VectorControlTag,
                ThirdLevel.LivelihoodsTag,  # 201
                ThirdLevel.NutritionTag,
                ThirdLevel.AgricultureTag,
                ThirdLevel.CrossTag,
                ThirdLevel.FoodSecurityTag,
                ThirdLevel.ShelterTag,
                ThirdLevel.EducationTag,
                ThirdLevel.WashTag,
                ThirdLevel.LogisticsTag,
                ThirdLevel.HealthTag,
                ThirdLevel.ProtectionTag,
                ThirdLevel.DisplacementTag,  # 202
                ThirdLevel.ShockEventTag,
                ThirdLevel.Covid19Tag,
                ThirdLevel.InformationAndCommTag,
                ThirdLevel.ContextTag,
                ThirdLevel.CasualtiesTag,
                ThirdLevel.HumanitarianAccessTag,
                ThirdLevel.ImpactTag,  # 203
                ThirdLevel.AtRiskTag,
                ThirdLevel.CapacitiesAndResponseTag,
                ThirdLevel.PriorityInterventionsTag,
                ThirdLevel.HumanitarianConditionsTag,
                ThirdLevel.PriorityNeedsTag,
                ThirdLevel.NonDisplacedTag,  # 204
                ThirdLevel.DisplacedTag,
                ThirdLevel.InjuredTag,  # 301
                ThirdLevel.DeadTag,
                ThirdLevel.MissingTag,
                ThirdLevel.TechnologicalTag,  # 302
                ThirdLevel.LegalAndPolicyTag,
                ThirdLevel.EconomyTag,
                ThirdLevel.SecurityAndStabilityTag,
                ThirdLevel.SocioCulturalTag,
                ThirdLevel.DemographyTag,
                ThirdLevel.PoliticsTag,
                ThirdLevel.EnvironmentTag,
                ThirdLevel.ContactTracingTag,  # 303
                ThirdLevel.HospitalizationAndCareTag,
                ThirdLevel.DeathsTag,
                ThirdLevel.CasesTag,
                ThirdLevel.PreventionCampaignTag,
                ThirdLevel.VaccinationTag,
                ThirdLevel.ResearchAndOutlookTag,
                ThirdLevel.TestingTag,
                ThirdLevel.RestrictionMeasuresTag,
                ThirdLevel.PushFactors,  # 304
                ThirdLevel.LocalIntegrationTag,
                ThirdLevel.TypeNumbersMovementsTag,
                ThirdLevel.PullFactorsTag,
                ThirdLevel.IntentionsTag,
                ThirdLevel.PeopleHumanitarianAccessConstraintsTag,  # 305
                ThirdLevel.PhysicalConstraintsTag,
                ThirdLevel.SecurityConstraintsTag,
                ThirdLevel.PopulationToReliefTag,
                ThirdLevel.ReliefToPopulationTag,
                ThirdLevel.InfoChallengesAndBarriersTag,  # 306
                ThirdLevel.CommMeansAndPreferencesTag,
                ThirdLevel.KnowledgeAndInfoGapsHumTag,
                ThirdLevel.KnowledgeAndInfoGapsPopTag,
                ThirdLevel.MitigatingFactorsTag,  # 307
                ThirdLevel.TypeAndCharacteristicsTag,
                ThirdLevel.HazardAndThreatsTag,
                ThirdLevel.UnderlyingAggravatingFactorsTag,
                ThirdLevel.RiskAndVulnerabilitiesTag,  # 401
                ThirdLevel.NumberOfPeopleAtRiskTag,
                ThirdLevel.LocalResponseTag,  # 402
                ThirdLevel.NationalResponseTag,
                ThirdLevel.HumanitarianCoordinationTag,
                ThirdLevel.InternationalResponseTag,
                ThirdLevel.RedCrossTag,
                ThirdLevel.PeopleReachedResponseGapsTag,
                ThirdLevel.PhysicalAndMentalWellBeingTag,  # 403
                ThirdLevel.LivingStandardsTag,
                ThirdLevel.CopingMechanismsTag,
                ThirdLevel.NumberOfPeopleInNeedTag,
                ThirdLevel.ImpactOnSystemsServicesNetworksTag,  # 404
                ThirdLevel.DriverAggravatingFactorsTag,
                ThirdLevel.NumberOfPeopleAffectedTag,
                ThirdLevel.ImpactOnPeopleTag,
                ThirdLevel.ExpressedByHumanitarianStaffTag,  # 405
                ThirdLevel.ExpressedByPopulationTag,
                ThirdLevel.PendularTag,  # 501
                ThirdLevel.AsylumSeekersTag,
                ThirdLevel.RefugeesTag,
                ThirdLevel.RegularTag,
                ThirdLevel.ReturneesTag,
                ThirdLevel.InTransitTag,
                ThirdLevel.OthersOfConcernTag,
                ThirdLevel.IrregularTag,
                ThirdLevel.IDPTag,
                ThirdLevel.StatelessTag,
                ThirdLevel.MigrantsTag,
                ThirdLevel.HostTag,  # 502
                ThirdLevel.NonHostTag,
                ThirdLevel.Age18YearsOldTag,  # 503
                ThirdLevel.Age2559YearsOldTag,
                ThirdLevel.Age1217YearsOldTag,
                ThirdLevel.Age60YearsOldTag,
                ThirdLevel.Age5YearsOldTag,
                ThirdLevel.Age1824YearsOldTag,
                ThirdLevel.Age511YearsOldTag,
                ThirdLevel.Age18YearsTag,
                ThirdLevel.Age517YearsOldTag,
                ThirdLevel.Age1859YearsOldTag,
                ThirdLevel.FemaleTag,  # 504
                ThirdLevel.MaleTag,
                ThirdLevel.AllTag,
                ThirdLevel.UnreliableTag,  # 505
                ThirdLevel.CompletelyReliableTag,
                ThirdLevel.CannotBeJudgedTag,
                ThirdLevel.UsuallyReliableTag,
                ThirdLevel.FairlyReliableTag,
                ThirdLevel.IssueOfConcernTag,  # 506
                ThirdLevel.SevereIssueTag,
                ThirdLevel.MinorIssueTag,
                ThirdLevel.CriticalIssueTag,
                ThirdLevel.NoIssueTag,
                ThirdLevel.PregnantOrLactatingWomenTag,  # 507
                ThirdLevel.SingleWomenInclWidowsTag,
                ThirdLevel.ChildHeadOfHouseholdTag,
                ThirdLevel.UnaccompaniedAndSeparatedChildrenTag,
                ThirdLevel.MinoritiesTag,
                ThirdLevel.LGBTQIATag,
                ThirdLevel.PersonsWithDisabilityTag,
                ThirdLevel.FemaleHeadOfHouseholdTag,
                ThirdLevel.ChronicallyIllTag,
                ThirdLevel.UnaccompaniedOrSeparatedChildrenTag,
                ThirdLevel.ElderlyHeadOfHouseholdTag,
                ThirdLevel.IndigenousPeopleTag,
                ThirdLevel.GBVSurvivorsTag,
            ]
        ]


total_tags = [
    FirstLevel.first_level_lst(),
    SecondLevel.second_level_lst(),
    ThirdLevel.third_level_lst(),
]
