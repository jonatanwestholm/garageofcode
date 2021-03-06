import numpy as np


import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.collections as col
from matplotlib.colors import Normalize
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import cartopy.io.shapereader as shpreader

import pandas as pd

questions = {
            "EXT1": ("I am the life of the party.", 1),
            "EXT2": ("I don't talk a lot.", -1),
            "EXT3": ("I feel comfortable around people.", 1),
            "EXT4": ("I keep in the background.", -1),
            "EXT5": ("I start conversations.", 1),
            "EXT6": ("I have little to say.", -1),
            "EXT7": ("I talk to a lot of different people at parties.", 1),
            "EXT8": ("I don't like to draw attention to myself.", -1),
            "EXT9": ("I don't mind being the center of attention.", 1),
            "EXT10": ("I am quiet around strangers.", -1),
            "EST1": ("I get stressed out easily.", 1),
            "EST2": ("I am relaxed most of the time.", -1),
            "EST3": ("I worry about things.", 1),
            "EST4": ("I seldom feel blue.", -1),
            "EST5": ("I am easily disturbed.", 1),
            "EST6": ("I get upset easily.", 1),
            "EST7": ("I change my mood a lot.", 1),
            "EST8": ("I have frequent mood swings.", 1),
            "EST9": ("I get irritated easily.", 1),
            "EST10": ("I often feel blue.", 1),
            "AGR1": ("I feel little concern for others.", -1),
            "AGR2": ("I am interested in people.", 1),
            "AGR3": ("I insult people.", -1),
            "AGR4": ("I sympathize with others' feelings.", 1),
            "AGR5": ("I am not interested in other people's problems.", -1),
            "AGR6": ("I have a soft heart.", 1),
            "AGR7": ("I am not really interested in others.", -1),
            "AGR8": ("I take time out for others.", 1),
            "AGR9": ("I feel others' emotions.", 1),
            "AGR10": ("I make people feel at ease.", 1),
            "CSN1": ("I am always prepared.", 1),
            "CSN2": ("I leave my belongings around.", -1),
            "CSN3": ("I pay attention to details.", 1),
            "CSN4": ("I make a mess of things.", -1),
            "CSN5": ("I get chores done right away.", 1),
            "CSN6": ("I often forget to put things back in their proper place.", -1),
            "CSN7": ("I like order.", 1),
            "CSN8": ("I shirk my duties.", -1),
            "CSN9": ("I follow a schedule.", 1),
            "CSN10": ("I am exacting in my work.", 1),
            "OPN1": ("I have a rich vocabulary.", 1),
            "OPN2": ("I have difficulty understanding abstract ideas.", -1),
            "OPN3": ("I have a vivid imagination.", 1),
            "OPN4": ("I am not interested in abstract ideas.", -1),
            "OPN5": ("I have excellent ideas.", 1),
            "OPN6": ("I do not have a good imagination.", -1),
            "OPN7": ("I am quick to understand things.", 1),
            "OPN8": ("I use difficult words.", 1),
            "OPN9": ("I spend time reflecting on things.", 1),
            "OPN10": ("I am full of ideas.", 1),
}

country_codes = {
                    "Afghanistan": "AF",
                    "Albania": "AL",
                    "Algeria": "DZ",
                    "American Samoa": "AS",
                    "Andorra": "AD",
                    "Angola": "AO",
                    "Anguilla": "AI",
                    "Antarctica": "AQ",
                    "Antigua and Barbuda": "AG",
                    "Argentina": "AR",
                    "Armenia": "AM",
                    "Aruba": "AW",
                    "Australia": "AU",
                    "Austria": "AT",
                    "Azerbaijan": "AZ",
                    "Bahamas (the)": "BS",
                    "Bahrain": "BH",
                    "Bangladesh": "BD",
                    "Barbados": "BB",
                    "Belarus": "BY",
                    "Belgium": "BE",
                    "Belize": "BZ",
                    "Benin": "BJ",
                    "Bermuda": "BM",
                    "Bhutan": "BT",
                    "Bolivia (Plurinational State of)": "BO",
                    "Bonaire, Sint Eustatius and Saba": "BQ",
                    "Bosnia and Herzegovina": "BA",
                    "Botswana": "BW",
                    "Bouvet Island": "BV",
                    "Brazil": "BR",
                    "British Indian Ocean Territory (the)": "IO",
                    "Brunei Darussalam": "BN",
                    "Bulgaria": "BG",
                    "Burkina Faso": "BF",
                    "Burundi": "BI",
                    "Cabo Verde": "CV",
                    "Cambodia": "KH",
                    "Cameroon": "CM",
                    "Canada": "CA",
                    "Cayman Islands (the)": "KY",
                    "Central African Republic (the)": "CF",
                    "Chad": "TD",
                    "Chile": "CL",
                    "China": "CN",
                    "Christmas Island": "CX",
                    "Cocos (Keeling) Islands (the)": "CC",
                    "Colombia": "CO",
                    "Comoros (the)": "KM",
                    "Congo (the Democratic Republic of the)": "CD",
                    "Congo (the)": "CG",
                    "Cook Islands (the)": "CK",
                    "Costa Rica": "CR",
                    "Croatia": "HR",
                    "Cuba": "CU",
                    "Curaçao": "CW",
                    "Cyprus": "CY",
                    "Czechia": "CZ",
                    "Côte d'Ivoire": "CI",
                    "Denmark": "DK",
                    "Djibouti": "DJ",
                    "Dominica": "DM",
                    "Dominican Republic (the)": "DO",
                    "Ecuador": "EC",
                    "Egypt": "EG",
                    "El Salvador": "SV",
                    "Equatorial Guinea": "GQ",
                    "Eritrea": "ER",
                    "Estonia": "EE",
                    "Eswatini": "SZ",
                    "Ethiopia": "ET",
                    "Falkland Islands (the) [Malvinas]": "FK",
                    "Faroe Islands (the)": "FO",
                    "Fiji": "FJ",
                    "Finland": "FI",
                    "France": "FR",
                    "French Guiana": "GF",
                    "French Polynesia": "PF",
                    "French Southern Territories (the)": "TF",
                    "Gabon": "GA",
                    "Gambia (the)": "GM",
                    "Georgia": "GE",
                    "Germany": "DE",
                    "Ghana": "GH",
                    "Gibraltar": "GI",
                    "Greece": "GR",
                    "Greenland": "GL",
                    "Grenada": "GD",
                    "Guadeloupe": "GP",
                    "Guam": "GU",
                    "Guatemala": "GT",
                    "Guernsey": "GG",
                    "Guinea": "GN",
                    "Guinea-Bissau": "GW",
                    "Guyana": "GY",
                    "Haiti": "HT",
                    "Heard Island and McDonald Islands": "HM",
                    "Holy See (the)": "VA",
                    "Honduras": "HN",
                    "Hong Kong": "HK",
                    "Hungary": "HU",
                    "Iceland": "IS",
                    "India": "IN",
                    "Indonesia": "ID",
                    "Iran": "IR",
                    "Iraq": "IQ",
                    "Ireland": "IE",
                    "Isle of Man": "IM",
                    "Israel": "IL",
                    "Italy": "IT",
                    "Jamaica": "JM",
                    "Japan": "JP",
                    "Jersey": "JE",
                    "Jordan": "JO",
                    "Kazakhstan": "KZ",
                    "Kenya": "KE",
                    "Kiribati": "KI",
                    "Korea (the Democratic People's Republic of)": "KP",
                    "South Korea": "KR",
                    "Kuwait": "KW",
                    "Kyrgyzstan": "KG",
                    "Lao People's Democratic Republic (the)": "LA",
                    "Latvia": "LV",
                    "Lebanon": "LB",
                    "Lesotho": "LS",
                    "Liberia": "LR",
                    "Libya": "LY",
                    "Liechtenstein": "LI",
                    "Lithuania": "LT",
                    "Luxembourg": "LU",
                    "Macao": "MO",
                    "Madagascar": "MG",
                    "Malawi": "MW",
                    "Malaysia": "MY",
                    "Maldives": "MV",
                    "Mali": "ML",
                    "Malta": "MT",
                    "Marshall Islands (the)": "MH",
                    "Martinique": "MQ",
                    "Mauritania": "MR",
                    "Mauritius": "MU",
                    "Mayotte": "YT",
                    "Mexico": "MX",
                    "Micronesia (Federated States of)": "FM",
                    "Moldova (the Republic of)": "MD",
                    "Monaco": "MC",
                    "Mongolia": "MN",
                    "Montenegro": "ME",
                    "Montserrat": "MS",
                    "Morocco": "MA",
                    "Mozambique": "MZ",
                    "Myanmar": "MM",
                    "Namibia": "NA",
                    "Nauru": "NR",
                    "Nepal": "NP",
                    "Netherlands": "NL",
                    "New Caledonia": "NC",
                    "New Zealand": "NZ",
                    "Nicaragua": "NI",
                    "Niger": "NE",
                    "Nigeria": "NG",
                    "Niue": "NU",
                    "Norfolk Island": "NF",
                    "Northern Mariana Islands (the)": "MP",
                    "Norway": "NO",
                    "Oman": "OM",
                    "Pakistan": "PK",
                    "Palau": "PW",
                    "Palestine, State of": "PS",
                    "Panama": "PA",
                    "Papua New Guinea": "PG",
                    "Paraguay": "PY",
                    "Peru": "PE",
                    "Philippines": "PH",
                    "Pitcairn": "PN",
                    "Poland": "PL",
                    "Portugal": "PT",
                    "Puerto Rico": "PR",
                    "Qatar": "QA",
                    "Republic of North Macedonia": "MK",
                    "Romania": "RO",
                    "Russia": "RU",
                    "Rwanda": "RW",
                    "Réunion": "RE",
                    "Saint Barthélemy": "BL",
                    "Saint Helena, Ascension and Tristan da Cunha": "SH",
                    "Saint Kitts and Nevis": "KN",
                    "Saint Lucia": "LC",
                    "Saint Martin (French part)": "MF",
                    "Saint Pierre and Miquelon": "PM",
                    "Saint Vincent and the Grenadines": "VC",
                    "Samoa": "WS",
                    "San Marino": "SM",
                    "Sao Tome and Principe": "ST",
                    "Saudi Arabia": "SA",
                    "Senegal": "SN",
                    "Serbia": "RS",
                    "Seychelles": "SC",
                    "Sierra Leone": "SL",
                    "Singapore": "SG",
                    "Sint Maarten (Dutch part)": "SX",
                    "Slovakia": "SK",
                    "Slovenia": "SI",
                    "Solomon Islands": "SB",
                    "Somalia": "SO",
                    "South Africa": "ZA",
                    "South Georgia and the South Sandwich Islands": "GS",
                    "South Sudan": "SS",
                    "Spain": "ES",
                    "Sri Lanka": "LK",
                    "Sudan (the)": "SD",
                    "Suriname": "SR",
                    "Svalbard and Jan Mayen": "SJ",
                    "Sweden": "SE",
                    "Switzerland": "CH",
                    "Syrian Arab Republic": "SY",
                    "Taiwan": "TW",
                    "Tajikistan": "TJ",
                    "Tanzania, United Republic of": "TZ",
                    "Thailand": "TH",
                    "Timor-Leste": "TL",
                    "Togo": "TG",
                    "Tokelau": "TK",
                    "Tonga": "TO",
                    "Trinidad and Tobago": "TT",
                    "Tunisia": "TN",
                    "Turkey": "TR",
                    "Turkmenistan": "TM",
                    "Turks and Caicos Islands": "TC",
                    "Tuvalu": "TV",
                    "Uganda": "UG",
                    "Ukraine": "UA",
                    "UAE": "AE",
                    "UK": "GB",
                    "United States Minor Outlying Islands (the)": "UM",
                    "USA": "US",
                    "Uruguay": "UY",
                    "Uzbekistan": "UZ",
                    "Vanuatu": "VU",
                    "Venezuela": "VE",
                    "Viet Nam": "VN",
                    "Virgin Islands (British)": "VG",
                    "Virgin Islands, (U.S.)": "VI",
                    "Wallis and Futuna": "WF",
                    "Western Sahara": "EH",
                    "Yemen": "YE",
                    "Zambia": "ZM",
                    "Zimbabwe": "ZW",
                    "Åland Islands": "AX",
}

country_codes = {val: key for key, val in country_codes.items()}


def get_psy(df):
    get_strings = lambda s: [s + str(i) for i in range(1, 11)]
    metrics = ["EXT", "EST", "AGR", "CSN", "OPN"]
    #psy = pd.DataFrame({s: df[get_strings(s)].sum(axis=1) for s in metrics})
    psy = {}
    for met in metrics:
        met_cols = get_strings(met)
        coeff = np.array([questions[col][1] for col in met_cols])
        df_met = df[met_cols]
        psy[met] = df_met.dot(coeff)

    psy = pd.DataFrame(psy)
    return psy


def psy_density():
    df = pd.read_csv("/home/jdw/garageofcode/data/kaggle/big5/big5.csv", delimiter="\t", nrows=1000000)
    df_se = df[df["country"] == "PE"]

    '''
    for i in range(5):
        qi = columns[i]
        q_stringi = questions[q]
        si = df[q]
        si = si[si > 0]
        plt.hist(s, bins=[1, 2, 3, 4, 5, 6])
        plt.title(q_string)
        plt.show()
    '''

    #corr = df[["OPN" + str(i) for i in range(1, 11)]].corr().to_numpy()
    
    metrics = ["EXT", "EST", "AGR", "CSN", "OPN"]   
    #print(psy.corr())

    psy = get_psy(df)
    psy_se = get_psy(df_se)

    for met in metrics:
        plt.hist([psy[met], psy_se[met]], bins=range(-30, 40), density=True)
        plt.title(met)
        plt.show()

    #plt.hist2d(psy["CSN"], psy["OPN"])
    #plt.scatter(psy["EXT"], psy["EST"])
    #plt.show()


def top5():
    df = pd.read_csv("/home/jdw/garageofcode/data/kaggle/big5/big5.csv", delimiter="\t", nrows=100000)
    cc2psy = []
    
    for cc, df_cc in df.groupby("country"):
        if len(df_cc) < 100:
            continue
    
        psy_cc = get_psy(df_cc).mean()
        psy_cc["country"] = country_codes.get(cc, cc)[:20]

        cc2psy.append(psy_cc)
        
    cc2psy = pd.DataFrame(cc2psy)
    
    '''
    met = "OPN"
    print(cc2psy.sort_values(by=met, ascending=False).iloc[:5])
    print("...")
    print(cc2psy.sort_values(by=met, ascending=False).iloc[-5:])
    '''

    # ok, make the map
    feat = "OPN"

    shapefile = "/home/jdw/garageofcode/data/ne_10m_admin_0_countries"
    num_colors = 9
    title = "worldmap_" + feat
    fn_img = '/home/jdw/garageofcode/results/kaggle/big5/{}.png'.format(title)



    mpl.style.use('map')
    fig = plt.figure(figsize=(22, 12))

    ax = fig.add_subplot(111, axisbg='w', frame_on=False)
    #fig.suptitle("worldmap", fontsize=30, y=.95)

    m = Basemap(lon_0=0, projection='robin')
    m.drawmapboundary(color='w')

    m.readshapefile(shapefile, 'units', color='#444444', linewidth=.2)
    for info, shape in zip(m.units_info, m.units):
        iso2 = info['ADM0_A2']
        if iso3 not in df["country"]:
            color = '#dddddd'
        else:
            color = (float(df[df["country"] == iso2][feat]) + 15) / 60

        patches = [Polygon(np.array(shape), True)]
        pc = PatchCollection(patches)
        pc.set_facecolor(color)
        ax.add_collection(pc)

    plt.savefig(imgfile, bbox_inches='tight', pad_inches=.2)




if __name__ == '__main__':
    top5()