import json
from locations.models import Division, District, Thana, PostOffice


def load_bd_master():
    # -------- Divisions --------
    with open('locations/data/bd-divisions.json', encoding='utf-8') as f:
        divisions = json.load(f)["divisions"]

    division_map = {}
    for d in divisions:
        obj, _ = Division.objects.get_or_create(
            id=d["id"],
            name=d["name"]
        )
        division_map[d["id"]] = obj

    # -------- Districts --------
    with open('locations/data/bd-districts.json', encoding='utf-8') as f:
        districts = json.load(f)["districts"]

    district_map = {}
    for d in districts:
        obj, _ = District.objects.get_or_create(
            id=d["id"],
            name=d["name"],
            division=division_map[d["division_id"]]
        )
        district_map[d["id"]] = obj

    # -------- Upazilas / Thana --------
    with open('locations/data/bd-upazilas.json', encoding='utf-8') as f:
        upazilas = json.load(f)["upazilas"]

    thana_map = {}
    for u in upazilas:
        obj, _ = Thana.objects.get_or_create(
            id=u["id"],
            name=u["name"],
            district=district_map[u["district_id"]]
        )
        thana_map[u["id"]] = obj

    # -------- Post Offices --------
# -------- Post Offices --------
with open('locations/data/bd-postcodes.json', encoding='utf-8') as f:
    data = json.load(f)["postcodes"]

for p in data:
    upazila_name = p["upazila"]

    # name দিয়ে thana খুঁজবো
    thana = Thana.objects.filter(name__iexact=upazila_name).first()

    if thana:
        PostOffice.objects.get_or_create(
            name=p["postOffice"],
            post_code=p["postCode"],
            thana=thana
        )
