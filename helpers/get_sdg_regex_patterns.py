import re

flatten = lambda t: [item for sublist in t for item in sublist]

# From Christian and Nadim
ADDITIONAL_KEYWORDS = {
    "sdg1": "extreme Armut | sozialer Schutz | arm | verwundbar | Gleichberechtigung | wirtschaftliche Ressourcen | Grundversorgung | Eigentum | Erbschaft | Mikrofinanz | Mikrokredite | Finanzdienstleistungen | Armutsbekämpfung | Entwicklungszusammenarbeit | extreme poverty | social protection | poor | vulnerable | equal rights | economic resources | basic services | property | inheritance | microfinance | microcredit | financial services | poverty eradication | development cooperation",
    "sdg2": "sichere Ernährung | nahrhafte Ernährung | ausreichende Ernährung | Unterernährung | Ernährung | Landwirtschaftsbetriebe | Bauern | Fischer | einheimische Bevölkerung | Landwirtschaft | Wetter | Dürre | Überschwemmungen | widerstandsfähige Landwirtschaft | Boden | Viehzucht | Lebensmittelpreise | Nahrung | Pflanzen | Samen | end hunger | safe food | nutritious food | sufficient food | malnutrition | nutrition | farms | farmers | fishers | indigenuous people | agriculture | weather | drought | flooding | resilient agriculture | soil | livestock | food price | food | plants | seeds",
    "sdg3": "Müttersterblichkeit | Neugeborenensterblichkeit | Epidemie | AIDS | Tuberkulose | Malaria | Hepatitis | Krankheiten | Krankheitsvorbeugung | Krankheitsbehandlung | Krankheitsbehandlung | Psychische Gesundheit | Drogenmissbrauch | Alkoholmissbrauch | Drogenabhängigkeit | Alkoholabhängigkeit | Verkehrsunfälle | Autounfälle | Todesfälle | Verletzungen | sexuelle Gesundheit | reproduktive Gesundheit | Familienplanung | allgemeine Gesundheitsversorgung | Gesundheitswesen | Gesundheitsversorgung | Medikamente | Impfstoffe | gefährliche Chemikalien | Luftverschmutzung | Bodenverschmutzung | Wasserverschmutzung | Luftverschmutzung | Wasserverschmutzung | Bodenverschmutzung | übertragbare Krankheiten | nicht übertragbare Krankheiten | öffentliches Gesundheitswesen | Gesundheitsfinanzierung | Gesundheitspersonal | Beschäftigte im Gesundheitswesen | Gesundheitspersonal | Krankenversicherung | Gesundheitsrisiken | Vergiftung | maternal mortality | neonatal mortality | eppidemics | AIDS | tuberculosis | Malaria | hepatitis | diseases | disease prevention | disease treatment | illness prevention | illness treatment | mental health | substance abuse | drug abuse | alcohol abuse | substance addiction | drug addiction | alcohol addiction | traffic accidents | car accidents | deaths | injuries | sexual health | reproductive health | family planning | universal health coverage | universal healthcare | healthcare | health care | medicines | vaccines | hazardous chemicals | air pollution | soil pollution | water pollution | air contamination | water contamination | soil contamination | communicable diseases | non-communicable diseases | public health | health financing | health workforce | health workers | healthcare workers | health insurance | health risks | poisoning",
    "sdg4": "inklusive Bildung | gerechte Bildung | qualitativ hochwertige Bildung | lebenslanges Lernen | effektives Lernen | Schulen | Bildungseinrichtungen | Lernumgebungen | Berufsbildung | Lehrer | Ausbildungsentwicklung | inclusive education | equitable education | quality education | lifelong learning | effective learning | schools | learning facilities | education facilities | learning environments | vocational training | teacher | training development",
    "sdg5": "Geschlechtergleichstellung | Empowerment von Frauen | häusliche Gewalt | sexuelle Ausbeutung | Menschenhandel | Genitalverstümmelung | Zwangsheirat | Chancengleichheit | reproduktive Gesundheit | sexuelle Gesundheit | Gleichberechtigung der Frau | gender equality | female empowerment | domestic violence | sexual exploitation | human trafficking | genital mutilation | forced marriage | equal opportunities | reproductive health | sexual health | women equal rights",
    "sdg6": "Trinkwasser | Siedlungshygiene | Hygiene | Wassergleichheit | Abwasser | Abwasserrecycling | Wasserressourcenmanagement | wasserbezogene Ökosysteme | drinking water | sanitation | hygiene | water equality | wastewater | wastewater recycling | water resource management | water-related ecosystems",
    "sdg7": "erschwingliche Energieversorgung | zuverlässige Energieversorgung | Energiedienstleistungen | erneuerbare Energie | saubere Energie | Energieeffizienz | nachhaltige Energie | saubere Energietechnologie | saubere Technologie | affordable energy | reliable energy | energy services | renewable energy | clean energy | energy efficency | sustainable energy | clean energy technology | clean tech",
    "sdg8": "Wirtschaftswachstum | Bruttoinlandsprodukt | wirtschaftliche Produktivität | technologischer Fortschritt | Innovation | menschenwürdiger Arbeitsplätze | Unternehmertum | Kreativität | Zugang zu Finanzmitteln | produktive Beschäftigung | menschenwürdige Arbeit | Arbeitsrechte | sichere Arbeitsumgebung | Finanzinstitute | Wirtschaftsförderung | economic growth | gross domestic product | economic productivity | technological upgrading | innovation | decent job creation | entrepreneurship | creativity | access to finance | productive employment | decent work | labour rights | save working environment | financial institutions | trade support",
    "sdg9": "nachhaltige Industrialisierung | nachhaltige industrielle Prozesse | Forschung und Entwicklung | F&E | nachhaltige Infrastruktur | industrielle Diversifizierung | Internetzugang | resilient infrastructure | sustainable industrialization | retrofit | sustainable industrial processes | research and development | R&D | sustainable infrastructure | industrial diversification | internet access",
    "sdg10": "income | reduce inquealities | social protection | migration | mobility of people | discrimination | discriminatory laws | social inclusion | political inclusion | racial inclusion | racism | racial discrimination | sexual discrimination | LGBTQ | queer | lesbian | harassment | sexual harrassment | disabilitiy | disabilities | religious discrimination | ethnic discrinimination | xenophobia | islamophobia | anti semitism | extremism | Einkommen | Verringerung von Ungleichheiten | Sozialschutz | Migration | Mobilität von Menschen | Diskriminierung | diskriminierende Gesetze | soziale Integration | politische Integration | Anti-Rassismus | Rassismus | Rassendiskriminierung | sexuelle Diskriminierung | LGBTQ | schwul | lesbisch | Belästigung | sexuelle Belästigung | Behinderung* | religiöse Diskriminierung | ethnische Diskriminierung | Fremdenfeindlichkeit | Islamophobie | Antisemitismus | Extremismus",
    "sdg11": "sicherer Wohnraum | erschwinglicher Wohnraum | Slums | menschliche Siedlung | öffentlicher Verkehr | Verkehrssicherheit | inklusive Urbanisierung | Naturerbe | kulturelles Erbe | partizipative Urbanisierung | Abfallwirtschaft | Luftqualität | Luftverschmutzung | Umweltauswirkungen | Urbanisierung | nachhaltige Gebäude | widerstandsfähige Gebäude | nachhaltige Materialien | Ressourceneffizienz | Katastrophenresistenz | Sendai-Rahmenwerk | safe housing | affordable housing | slums | human settlement | public transport | road safety | affordable transportation | inclusive urbanisation | natural heritage | cultural heritage | participatory urbanization | waste management | air quality | air polution | environmental impact | urbanization | sustainable buildings | resilient buildings | sustainable materials | resource efficiency | disaster resilience | sendai framework",
    "sdg12": "nachhaltiger Konsum | nachhaltiges Management | Lebensmittelabfälle | Lebensmittelverluste | Verluste nach der Ernte | Lebenszyklusmanagement | Abfallerzeugung | Recycling | Wiederverwendung | Kreislaufwirtschaft | nachhaltige Praxis | integrierte Nachhaltigkeit | Natur | wissenschaftliche Kapazität | technologische Kapazität | nachhaltiger Tourismus | schädliche Subventionen | nachhaltige Beschaffung | sustainable consumption | sustainable management | food waste | food losses | post-harvest losses | life cycle mangement | waste generation | recycling | reuse | circular-economy | sustainable practice | integrated sustainability | nature | scientific capacity | technological capacity | sustainable tourism | harmful subsidies | sustainable procurement",
    "sdg13": "Klimarisiko | Klimafinanzierung | Klimawandel | Klimaschutz | Anpassung an den Klimawandel | Klimaanpassung | Klimaaktion | Sequestrierung | Kohlenstoffbindung | Kohlenstoffabscheidung | Kohlenstoff-Fussabdruck | Kohlenstoffemissionen | GHG | Treibhausgase | climate risk | climate finance | climate change | climate change mitigation | climate change adaptation | climate adapatpation | climate action | sequestration | carbon capture | carbon footprint | carbon emissions | GHG | Greenhouse Gases",
    "sdg14": "Meeresverschmutzung | Meeresschutt | Meeresplastik | Nährstoffbelastung | gesunde Ozeane | produktive Ozeane | Überfischung | nachhaltige Fischerei | Fischbestände | Ozeanversauerung | Meeresressourcen | Aquakultur | unregulierte Fischerei | Überfischung | marine Biodiversität | marine Biodiversität | Seerecht | Meeresgesundheit | Meerestechnik | Küstengebiete | Kleinfischerei | marine pollution | marine debris | ocean plastic | nutrient pollution | healtyh oceans | productive oceans | overfishing | sustainable fisihing | fish stocks | ocean acidification | marine resources | aquaculture | unregulated fishing | overfishing | marine biodiversity | ocean biodiversity | law of the sea | ocean health | marine technology | costal areas | small-scale fisheries",
    "sdg15": "Entwaldung | Ökosysteme | Biodiversität | Aufforstung | Wiederaufforstung | Bodendegradation | Naturschutz | natürliche Lebensräume | Aussterben | bedrohte Arten | Wiederherstellung | Wälder | Feuchtgebiete | Wilderei | Menschenhandel | Flora | Fauna | Wildtiere | invasive Arten | deforestation | terrestrial ecosystems | ecosystem services | biodiversity | afforestation | reforestation | land degradation | conservation | natural habitats | extinction | threatened species | restoration | forests | wetlands | poaching | trafficking | flora | fauna | wildlife | invasive species",
    "sdg16": "Gewalt | inklusive Gesellschaften | Gerechtigkeit | inklusive Institutionen | Ausbeutung | Handel | Folter | Rechtsstaatlichkeit | illegale Finanzströme | Waffenströme | organisiertes Verbrechen | gestohlene Vermögenswerte | Korruption | Bestechung | effektive Institutionen | rechenschaftspflichtige Institutionen | transparente Institutionen | reaktionsfähige Entscheidung Entscheidungsfindung | integrative Entscheidungsfindung | partizipative Entscheidungsfindung | repräsentative Entscheidungsfindung | Global-Governance | Rechtspersönlichkeit | Zugang zu Informationen | Redefreiheit | Religionsfreiheit | Terrorismus | Kriminalität | nichtdiskriminierende Gesetze | nichtdiskriminierende Politik | violence | inclusive societies | justice | inclusive institutions | exploitation | trafficking | torture | rule of law | illicit financial flows | arms flows | organized crime | stolen assets | corruption | bribery | effective insitutions | accountable institutions | transparent institutions | responsive decison-making | inclusive decision-making | participatory decision-making | representative decison-making | global-governance | legal identity | access to information | freedom of speech | freedom of religion | terrorism | crime | non-discriminatory laws | non-discriminatory policies",
    "sdg17": "Partnerschaft | Globale Partnerschaft | Ressourcenmobilisierung | Internationale Unterstützung | Entwicklungshilfe | Internationale Zusammenarbeit | Internationale Entwicklung | Kapazitätsaufbau | Technologietransfer | Investitionen | Finanzierung | Schulden | Handel | Politikkoordination | Daten | Multi-Stakeholder | PPP | Innovation | Partnership | Global Partnership | Resource Mobilization | International Support | Development Assistance | International Cooperation | International Development | Capacity Building | technology transfer | investment | financing | debt | trading | policy coordination | policy coherence | data | multi-stakeholder | PPP | development assistance | resource mobilization | innovation",
}

# From TU Berlin research paper
KEYWORDS = {
    "sdgs": "SDG([1-9]|1[0-7]) | SDGs?( [1-9]|1[0-7])? | Sustainable Development Goals? | Nachhaltigkeitsziele? | Ziele für Nachhaltige Entwicklung",
    "sdg1": "Armut | ärm* | Sozialsystem | Sozialschutzsystem | Grundsicherung | Mikrofinanz* | Basisschutz | arm* | poverty | poor | social protection system | microfinanc* | basic income | basic provision | basic social security",
    "sdg2": "Hunger | Nahrung* | nachhaltige Landwirtschaft | Landwirtschaft | Agrar* | Saat* | *Ernährung | essen* | Bauer* | Kleinbauer | Übergewicht* | Fehlernähr* | Adipositas | Adipös | Fettleibigkeit | Obesitas | food | algricult* | hunger | farm* | *nutrition | sustainable farm* | pastoralist | fisher | seed | cultivat* | domesticate | livestock | obesity | overweight | obese | eat*",
    "sdg3": "Gesund* | Wohlergehen | Müttersterb* | Kindersterb* | Epidem* | Krankheit* | Frühsterblich* | Impf* | Lebendgeburt* | Neugeb* | Arznei* | Medikament* | Medizin* | Todes* | Aids* | Tuberkulose* | Malaria* | Behandl* | Sucht* | Drogen* | Verletz* | Lebenserwartung* | Sterblichkeit | Unfalltot* | sex* | Hygiene | sauber* | Ärzt* | Arzt | Doktor | Patient | Praxis  | Betreuung | behind* | Therapie | Wohlbefinden | Lebensqualität | Pflege |  health | diseas* | medicin* | mortal* | birth* | death* | vaccine* | well-being | newborn | neonatal mortality | epidemics | aids | tuberculosis | malaria | narcotic* | drug* | injur* | accident | reproductive | illness* | hygien* | life expectancy | Doctor | Therapy | pharma* | Care | Handicap | disab*",
    "sdg4": "*Bildung | *bilden | Qualifi* | *schul* | Analphabet* | Schüler* | lernen | Unterricht* | student | Lehr* | educat* | vocation* | training | school | literacy | illiterate | pupil | teach* | learn",
    "sdg5": "Geschlechterg* | Chanceng* | Selbstbestimm* | Diskrimi* | Menschenhandel | Verhütung* | Gleichstellung* | Mädchen | Diversit* | Kinderheirat | Zwangsheirat | Zwangsehe | Genitalverstü* | Beschneidung | Gender Pay Gap | Gender Wage Gap | equality | gender | empowerment | self-determine* | discriminat* | trafficking | forced marriage | genital mutilation | circumcision |  child marriage | Gender Pay Gap | Gender Wage Gap | emancipat* | Emanz* | Frau(?!nhofer)* | Woman | Women | Girls",
    "sdg6": "Sauberes Wasser | Sanitär* | Wasserknapp* | Wassernutz* | Trinkwasser | Notdurftverricht* | Wasserqualität | Abwasser | Wasserressourcen | Grundwasser | Frischwasser | WC | clean water | water usage | water scarcity | water quality | water reuse | water recycling | water resources | sanitation | wastewater | open defecation | freshwater | water-related | wetland | aquifer | water efficiency | water harvesting | desalinat* | toilette | toilet",
    "sdg7": "Energie* | Erneuerbare Energie | Energiewende | Brennstoff* | Strom* | Windturbine | Photovoltaik* | Solar* | Biogas* | PV*Anlage | Batterie* | clean energy | green energy | modern energy | renewable energy | sustainable energy | photovoltaic | wind turbine | solar | biogas | energy efficiency | clean fossil-fuel | energy infrastructure | energy technology | energy storage | power supply | energy grid | power grid",
    "sdg8": "Kinderarbeit | Vollbeschäftigung | Wirtschaftswachstum | Bruttoinlandsprodukt* | Arbeitspl* | menschenwürdig* | nachhaltiges Wachstum | Zwangsarbeit | Sklaverei | Menschenhandel | Kindersoldat* | Arbeitsrecht* | Wanderarbeit* | prekär* Beschäftig* | nachhaltiger Tourismus | Arbeitslos* | Arbeitsbeschaffung* | *employ* | labor | labour | economic growth | gross domestic product | economic productivity | job creation | sustainable growth | job | decent work | slavery | child soldiers | sustainable tourism | working environment | worker",
    "sdg9": "Infrastruktur* | Industrialisierung | Technologieentwicklung | Technologieförderung | Forschung* | Internetzugang | verkehr | industrie 4.0 | Fahr* | Mobilität | Logistik* | Industrie 4 | künstliche Intelligenz | maschinelles lernen | infrastructure | industrialisation | industrialization | research | technology transfer | technology support | technology development | access to internet | internet access | development spending | R&D | smart | traffic | transport | digital* | IoT | internet of things | industry 4.0 | automat* | augmented reality | virtual reality | driv* | vehicle* | Mobility | logistic* | industry 4 | machine learning | artificial intelligence",
    "sdg10": "Ungleichheit* | Einkommenswachstum | Selbstbestimm* | Inklusion | Geschlechterg* | Chanceng* | Diskrimi* | Lohnungleichheit* | Arm und Reich | Lohnunterschied* | Entwicklungsl* | Migration* | Flüchtling | Flucht | Teilhabe | Partizipation | barrierefrei* | Behinder* | Diversit* | flücht* | Rollstuhl | inequalit* | unequal* | income growth | inclusion | discriminit* | equality | poor and rich | developing countr* | migration | inclusive | refugee | Disabilit* | Wheelchair",
    "sdg11": "Nachhaltige Städte | Nachhaltige Stadt | Nachhaltige Gemeind* | Gemeinde* | Wohnraum | Slum* | *Verkehr* | öffentlicher Nahverkehr | ÖPNV | Verstädterung | Siedlung* | Weltkulturerbe | Weltnaturerbe | Gentrifizier* | komunal* | Naturkatastrophen | nachhaltiges Bauen | nachhaltiges Baumaterial* | nachhaltige Baumaterial* | stadt | städte |  kommun* | städti* | Elektro* | Mobilität | Logistik* | sustainable cit* | sustainable communit* | public transport | traffic | settlement | slum | sustainable transport | affordable transport | safe transport |  accessible transport | housing | urbanization | urbanization | public space | green space | safe space | disaster | sustainable building | building sustainable | construction |  cultural heritage | natural heritage | city | cities | communit* | electr* | Mobility | logistic*",
    "sdg12": "Konsum* | nachhaltige Produktion | Produktionsmuster | Ressourceneinsatz | Ressourcennutz* | Ressourcenproduk* | Abfall* | Abfälle | Nahrungsmittelverschwendung | Nahrungsmittelverluste | Nachernteverluste | Kreislaufwirtschaft | Wiederverwendung | Wiederverwertung | Elektroschrott | nachhaltiger Einkauf | nachhaltiger Tourismus | nachhaltig* | umweltfreund* | Recycling | Recyc* | E*waste | sustainable production | sustainable consumption | consumption | resource efficiency | food waste | food loss* |  post-harvest loss* | circular economy | circular business | recycling | waste | reuse | sustainable procurement | sustainable tourism | e*waste | fair trade | sustain* | eco-friendly | environmentally friendly | share | sharing | organic | bio* | ecological",
    "sdg13": "Klimawandel* | Klimaschutz* | CO2 | Treibhausgas* | klimabedingt | klimafolge* | Klimaanpassung* | Klimaauswirk* | Emission* | climate change | climate action | climate mitigation | climate adaptation | CO2 | greenhouse gas | climate related | Emission",
    "sdg14": "Ozean* | Meeresressource* | Fischerei* | Überfisch* | Küstenökosystem* | Fischbestand | Fischbestände | Aquakultur* | Meerestechnolog* | Kleinfischer | marine | ocean* | fishing | fisheries | coastal | overfishing | aquaculture | fish",
    "sdg15": "Bodendegradation | Landökosysteme | Desertifikation | Wald* | Artenvielfalt | Wälder | Wüstenbild* | *aufforst* | Wilderei | Entwald* | Biodiversität | ökologische Vielfalt | biologische Vielfalt | bedrohte Arten | Aussterben | Neobiota | invasive Arten | invasive* gebietsfremde* Art* | Ökosystemdiversität  | Flächenversiegel* | Erosion | biodiversity | forest* | desertificat* | poach* | reforest* | terrestrial ecosystem* | renaturation* | natural habitat* | extinction | threatened species | wildlife | invasive species | alien species | eradicat* |  non-indigenous species | impervious surface",
    "sdg16": "Friede* | Gewalt* | Justiz* | Krimin* | Rechtsstart* | Waffen* | Korruption | Bestechung | Kleptokrat* | Völkerrecht* | Menschenrecht* | Mord* | Verbrech* | leistungsfähige Institutionen | rechenschaftspflichtige Institutionen | inklusive Institutionen | Sicher* | justice | peace | violence | war | effective institution* | accountable institution* | inclusive institution* | crime | criminal | judici* | torture | rule of law | weapon | illicit | corrupt* | brib* | transparent institutions | human rights | international law | kleptocracy | participat* | Secur*",
    "sdg17": "Entwicklungshilfe* | Entwicklungszusammenarbeit* | Nord-Süd-Zusammenarbeit | Süd-Süd-Zusammenarbeit | Dreieckskooperation* | Leapfrog* | Technologietransf* | Kapazitätsaufbau* | Capacity Building | fairer Welthandel | gerechter Welthandel | Handelsbarriere* | Protektionismus | development aid | development assistance | development cooperation | foreign aid | capacity building | north-south | ODA | official development assistance | least developed countr* | south-south | triangular cooperation | technology transfer | technology facilitation | leapfrog* | fair trade | trade barriers",
}

# Return an object of regex patterns
def get_sdg_regex_patterns():
    # Prepare search regexes
    regex_patterns = {"main": None, "items": []}
    search_terms = {}
    for goal, needle in KEYWORDS.items():
        # Add additional keywords
        needle = needle + " | " + ADDITIONAL_KEYWORDS.get(goal, "")

        # Generate list of search terms
        terms = [term.strip() for term in needle.split(" | ")]

        # Remove empty strings
        terms = list(filter(None, terms))

        # Convert * character into wildcard match
        search_terms[goal] = [term.replace("*", r"\w*?") for term in terms]

    # Create one primary pattern by combining all regexes
    regex_patterns["main"] = re.compile(
        r"\b(%s)\b" % "|".join(flatten(search_terms.values())),
        flags=re.IGNORECASE,
    )

    # Create one regex pattern for each term/keyword
    for goal, terms in search_terms.items():
        for term in terms:
            regex_patterns["items"].append(
                {
                    "sdg": goal,
                    "keyword": term,
                    "pattern": re.compile(r"\b%s\b" % term, flags=re.IGNORECASE),
                }
            )

    return regex_patterns
