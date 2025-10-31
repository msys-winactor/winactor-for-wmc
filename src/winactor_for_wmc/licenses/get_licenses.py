from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")

    if not base_url or not token:
        return {}

    endpoint = "/licenses"
    client = WMCApiClient(base_url, token)
    response = client.get(endpoint)
    return response


def get_feature_info(result, index=0):

    features = result["features"]
    target = features[index]
    return {
        "name": target.get("name", ""),
        "licenseType": target["licenseType"],
        "deathTime": target["deathTime"],
        "startTime": target["startTime"],
        "numLicenses": target["numLicenses"],
        "trialDaysLeft": target["trialDaysLeft"],
        "keyLifeTime": target["keyLifeTime"],
        "locale": target.get("locale", ""),
    }
