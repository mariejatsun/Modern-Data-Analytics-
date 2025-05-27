import pycountry
import base64
import countryinfo


def convert_iso2_to_iso3(iso2_code):
    try:
        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
    except:
        return None

def iso3_to_name(iso3):
    try:
        return pycountry.countries.get(alpha_3=iso3).name
    except:
        return iso3 

# Afbeelding


def get_image_base64(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpg;base64,{encoded}"


def get_lat_lon_from_iso2(iso2):
    try:
        info = countryinfo.CountryInfo(iso2)
        latlng = info.latlng()
        if latlng and len(latlng) == 2:
            return latlng[0], latlng[1]
    except Exception:
        pass
    return None, None