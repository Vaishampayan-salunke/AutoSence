"""
AutoSense Vehicle Image Downloader & Catalog Updater
Maps all 57 cars to exact Wikipedia articles and downloads authentic images to frontend/dist/images/cars/
"""
import os
import json
import re
import urllib.request
import urllib.parse
import time

CARS_WIKI_MAP = {
    # Mahindra
    ("Mahindra", "Thar"): ["Mahindra_Thar"],
    ("Mahindra", "Scorpio-N"): ["Mahindra_Scorpio", "Mahindra_Scorpio_Classic"],
    ("Mahindra", "XUV700"): ["Mahindra_XUV700"],
    ("Mahindra", "Bolero"): ["Mahindra_Bolero"],
    ("Mahindra", "XUV 3XO"): ["Mahindra_XUV300"],
    # Tata Motors
    ("Tata Motors", "Harrier"): ["Tata_Harrier"],
    ("Tata Motors", "Safari"): ["Tata_Safari"],
    ("Tata Motors", "Nexon"): ["Tata_Nexon"],
    ("Tata Motors", "Punch"): ["Tata_Punch"],
    ("Tata Motors", "Altroz"): ["Tata_Altroz"],
    # Toyota
    ("Toyota", "Fortuner"): ["Toyota_Fortuner"],
    ("Toyota", "Innova Hycross"): ["Toyota_Innova"],
    ("Toyota", "Hyryder"): ["Toyota_Urban_Cruiser_Hyryder"],
    ("Toyota", "Camry"): ["Toyota_Camry"],
    # Hyundai
    ("Hyundai", "Creta"): ["Hyundai_Creta"],
    ("Hyundai", "Verna"): ["Hyundai_Accent", "Hyundai_Verna"],
    ("Hyundai", "Venue"): ["Hyundai_Venue"],
    ("Hyundai", "i20"): ["Hyundai_i20"],
    ("Hyundai", "Exter"): ["Hyundai_Exter"],
    # Kia
    ("Kia", "Seltos"): ["Kia_Seltos"],
    ("Kia", "Sonet"): ["Kia_Sonet"],
    ("Kia", "Carens"): ["Kia_Carens"],
    ("Kia", "EV6"): ["Kia_EV6"],
    # Maruti Suzuki
    ("Maruti Suzuki", "Swift"): ["Suzuki_Swift"],
    ("Maruti Suzuki", "Fronx"): ["Suzuki_Fronx"],
    ("Maruti Suzuki", "Grand Vitara"): ["Suzuki_Grand_Vitara"],
    ("Maruti Suzuki", "Brezza"): ["Suzuki_Brezza", "Maruti_Brezza"],
    ("Maruti Suzuki", "Baleno"): ["Suzuki_Baleno"],
    # Volkswagen
    ("Volkswagen", "Virtus"): ["Volkswagen_Virtus"],
    ("Volkswagen", "Taigun"): ["Volkswagen_Taigun"],
    ("Volkswagen", "Tiguan"): ["Volkswagen_Tiguan"],
    # Skoda
    ("Skoda", "Slavia"): ["Škoda_Slavia", "Skoda_Slavia"],
    ("Skoda", "Kushaq"): ["Škoda_Kushaq", "Skoda_Kushaq"],
    ("Skoda", "Kodiaq"): ["Škoda_Kodiaq", "Skoda_Kodiaq"],
    # MG
    ("MG", "Hector"): ["MG_Hector", "Baojun_530"],
    ("MG", "ZS EV"): ["MG_ZS_(2017)"],
    ("MG", "Astor"): ["MG_ZS_(2017)"],
    ("MG", "Gloster"): ["Maxus_D90"],
    # BYD
    ("BYD", "Atto 3"): ["BYD_Atto_3"],
    ("BYD", "Seal"): ["BYD_Seal"],
    ("BYD", "e6"): ["BYD_e6"],
    # Jeep
    ("Jeep", "Compass"): ["Jeep_Compass"],
    ("Jeep", "Meridian"): ["Jeep_Commander_(2021)"],
    # Nissan
    ("Nissan", "Magnite"): ["Nissan_Magnite"],
    ("Nissan", "Altima"): ["Nissan_Altima"],
    ("Nissan", "Sentra"): ["Nissan_Sentra"],
    ("Nissan", "Frontier"): ["Nissan_Frontier"],
    ("Nissan", "X-Trail"): ["Nissan_X-Trail"],
    # Renault
    ("Renault", "Kiger"): ["Renault_Kiger"],
    ("Renault", "Triber"): ["Renault_Triber"],
    ("Renault", "Kwid"): ["Renault_Kwid"],
    # Citroen
    ("Citroen", "C3"): ["Citroën_C3_(CC21)", "Citroen_C3"],
    ("Citroen", "C3 Aircross"): ["Citroën_C3_Aircross", "Citroen_C3_Aircross"],
    ("Citroen", "Basalt"): ["Citroën_Basalt", "Citroen_Basalt"],
    # Honda
    ("Honda", "City"): ["Honda_City"],
    ("Honda", "Elevate"): ["Honda_Elevate"],
    ("Honda", "Amaze"): ["Honda_Amaze"],
}

def slugify(brand, model):
    s = f"{brand}_{model}".lower()
    return re.sub(r'[^a-z0-9_]+', '_', s).strip('_')

def run():
    target_dir = os.path.join("frontend", "dist", "images", "cars")
    os.makedirs(target_dir, exist_ok=True)
    
    bundle_path = os.path.join("frontend", "dist", "autosense_bundle.json")
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    catalog = bundle.get("models_catalog", [])
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 AutoSense/1.0"
    }
    
    updated_count = 0
    downloaded_count = 0

    for m in catalog:
        brand = m["brand"]
        model = m["model"]
        slug = slugify(brand, model)
        dest_filename = f"{slug}.jpg"
        local_rel_path = f"images/cars/{dest_filename}"
        local_full_path = os.path.join(target_dir, dest_filename)
        
        wiki_titles = CARS_WIKI_MAP.get((brand, model), [f"{brand}_{model}".replace(" ", "_")])
        
        img_url = None
        for title in wiki_titles:
            try:
                quoted_title = urllib.parse.quote(title)
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quoted_title}"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    # Use thumb directly from Wikipedia response without modification!
                    thumb = data.get("thumbnail", {}).get("source")
                    orig = data.get("originalimage", {}).get("source")
                    if thumb:
                        img_url = thumb
                        break
                    elif orig:
                        img_url = orig
                        break
            except Exception as e:
                continue
            
        if img_url:
            # Download file locally
            try:
                img_req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                    content = img_resp.read()
                    if len(content) > 1000:
                        with open(local_full_path, "wb") as out_f:
                            out_f.write(content)
                        downloaded_count += 1
                        m["image_url"] = local_rel_path
                        m["remote_image_url"] = img_url
                        print(f"[+] Downloaded {brand} {model} ({len(content)} bytes) -> {local_rel_path}")
                    else:
                        m["image_url"] = img_url
            except Exception as e:
                print(f"[-] Download failed for {brand} {model} from {img_url}: {e}")
                m["image_url"] = img_url
            updated_count += 1
            time.sleep(0.08)
        else:
            print(f"[!] No Wikipedia image found for {brand} {model}")

    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted! Downloaded {downloaded_count} local images, updated {updated_count} models in catalog.")

if __name__ == "__main__":
    run()
