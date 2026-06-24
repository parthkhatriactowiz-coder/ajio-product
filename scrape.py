import json
from datetime import datetime


def read_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(output_path, data):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_gallery_images(images):
    gallery_images = []
    for img in images:
        if img.get("imageType", "") == "GALLERY" and img.get("format", "") == "product":
            gallery_images.append(img.get("url", ""))
    return gallery_images


def convert_timestamp(ms):
    if ms:
        return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
    return ""


def get_offers(offers):
    offer_list = []
    for offer in offers:
        offer_details = {
            "bank_id": offer.get("bankId", ""),
            "bank_name": offer.get("bankName", ""),
            "description": offer.get("description", ""),
            "start_date": convert_timestamp(offer.get("startDate", 0)),
            "end_date": convert_timestamp(offer.get("endDate", 0)),
            "offer_code": offer.get("offerCode", ""),
            "offer_amount": offer.get("offerAmount", 0),
        }
        offer_list.append(offer_details)
    return offer_list


def get_specifications(product_details_section, mandatory_info):
    specifications = {}

    for details in product_details_section:
        feature_values = []
        for fv in details.get("featureValues", []):
            feature_values.append(fv.get("value", ""))
        specifications[details.get("name", "")] = feature_values

    for info in mandatory_info:
        specifications[info.get("key", "")] = info.get("title", "")

    return specifications


def get_mrp_text(variant):
    for info in variant.get("mandatoryInfo", []):
        if info.get("key", "") == "MRP":
            title = info.get("title", "")
            subtitle = info.get("subTitle", "")
            return f"{title}({subtitle})"
    return ""


def get_discount_percent(price, original_price):
    if original_price > 0:
        return round(((original_price - price) / original_price) * 100, 2)
    return 0


def get_size_variants(variants):
    size_list = []
    for variant in variants:
        price = variant.get("priceData", {}).get("value", 0)
        original_price = variant.get("wasPriceData", {}).get("value", 0)

        size_info = {
            "size": variant.get("scDisplaySize", ""),
            "product_code": variant.get("code", ""),
            "price": price,
            "original_price": original_price,
            "discount_percent": get_discount_percent(price, original_price),
            "mrp": get_mrp_text(variant),
        }
        size_list.append(size_info)
    return size_list


def process_products(data, base_url):
    products = []
    product_details = data.get("product", {}).get("productDetails", {})
    variants = product_details.get("variantOptions", [])
    images = product_details.get("images", [])
    rate_response = product_details.get("ratingsResponse", {})
    rating = rate_response.get("aggregateRating", {}).get("averageRating", 0)
    total_reviews = rate_response.get("aggregateRating", {}).get("numUserRatings", 0)
    product_details_section = product_details.get("sectionOne", {}).get(
        "featureData", []
    )
    mandatory_info = product_details.get("mandatoryInfo", [])
    prepaid_offers = product_details.get("prepaidOffers", [])

    gallery_images = get_gallery_images(images)
    specifications = get_specifications(product_details_section, mandatory_info)
    offers = get_offers(prepaid_offers)
    size_variants = get_size_variants(variants)

    product_info = {
        "brand_name": product_details.get("brandName", ""),
        "product_name": product_details.get("name", ""),
        "product_id": rate_response.get("optionCode", ""),
        "url": base_url + product_details.get("url", ""),
        "rating": rating,
        "total_reviews": total_reviews,
        "color": product_details.get("verticalColor", ""),
        "other_images": gallery_images,
        "specifications": specifications,
        "sizes": size_variants,
        "offers": offers,
    }
    products.append(product_info)
    
    return products


input_path = "C:/Users/parth.khatri/Desktop/github/ajio-product/ajio.json"
output_path = "C:/Users/parth.khatri/Desktop/github/ajio-product/ajio_output.json"

data = read_json_file(input_path)
product_data = process_products(data, "https://www.ajio.com")
write_json_file(output_path, product_data)

