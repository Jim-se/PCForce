import json
import re
import time
from decimal import Decimal
from html import escape, unescape
from http.client import InvalidURL
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product


COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
BING_IMAGE_URL = "https://www.bing.com/images/search"
USER_AGENT = "PCForceSeedProducts/1.0 (local Django project)"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


PRODUCTS = [
    {
        "code": "CPU-AMD-7600",
        "name": "AMD Ryzen 5 7600 AM5 Processor",
        "brand": "AMD",
        "category": "Processors",
        "price": "219.90",
        "stock": 14,
        "description": "6-core AM5 desktop processor for efficient gaming and everyday builds.",
        "image_search": "AMD Ryzen processor box",
    },
    {
        "code": "CPU-AMD-7800X3D",
        "name": "AMD Ryzen 7 7800X3D Gaming Processor",
        "brand": "AMD",
        "category": "Processors",
        "price": "389.90",
        "stock": 9,
        "description": "8-core gaming CPU with 3D V-Cache for high frame-rate PCs.",
        "image_search": "AMD Ryzen 7 processor",
    },
    {
        "code": "CPU-INTEL-I5-14600K",
        "name": "Intel Core i5-14600K LGA1700 Processor",
        "brand": "Intel",
        "category": "Processors",
        "price": "329.90",
        "stock": 11,
        "description": "Unlocked Intel desktop CPU suited to gaming, streaming, and multitasking.",
        "image_search": "Intel Core processor box",
    },
    {
        "code": "CPU-INTEL-I7-14700K",
        "name": "Intel Core i7-14700K Performance Processor",
        "brand": "Intel",
        "category": "Processors",
        "price": "449.90",
        "stock": 7,
        "description": "High-performance Intel processor for enthusiast gaming and creative workloads.",
        "image_search": "Intel Core i7 processor",
    },
    {
        "code": "GPU-RTX-4060TI",
        "name": "NVIDIA GeForce RTX 4060 Ti 8GB Graphics Card",
        "brand": "NVIDIA",
        "category": "Graphics Cards",
        "price": "399.90",
        "stock": 10,
        "description": "Efficient 1080p and 1440p gaming graphics card with modern ray tracing support.",
        "image_search": "NVIDIA GeForce RTX graphics card",
    },
    {
        "code": "GPU-RTX-4070S",
        "name": "NVIDIA GeForce RTX 4070 Super 12GB Graphics Card",
        "brand": "NVIDIA",
        "category": "Graphics Cards",
        "price": "679.90",
        "stock": 6,
        "description": "Powerful 1440p GPU with 12GB GDDR6X memory for demanding games.",
        "image_search": "GeForce RTX graphics card",
    },
    {
        "code": "GPU-RX-7800XT",
        "name": "AMD Radeon RX 7800 XT 16GB Graphics Card",
        "brand": "AMD",
        "category": "Graphics Cards",
        "price": "579.90",
        "stock": 5,
        "description": "16GB graphics card aimed at smooth 1440p gaming and creator work.",
        "image_search": "AMD Radeon graphics card",
    },
    {
        "code": "GPU-RTX-3060-12G",
        "name": "ASUS Dual GeForce RTX 3060 12GB",
        "brand": "ASUS",
        "category": "Graphics Cards",
        "price": "309.90",
        "stock": 12,
        "description": "Dual-fan 12GB GPU for balanced gaming and workstation upgrades.",
        "image_search": "dual fan graphics card",
    },
    {
        "code": "MB-ASUS-B650",
        "name": "ASUS TUF Gaming B650-Plus WiFi Motherboard",
        "brand": "ASUS",
        "category": "Motherboards",
        "price": "219.90",
        "stock": 8,
        "description": "ATX AM5 motherboard with WiFi, PCIe 5.0 support, and durable power delivery.",
        "image_search": "ATX motherboard",
    },
    {
        "code": "MB-MSI-B760",
        "name": "MSI MAG B760 Tomahawk WiFi Motherboard",
        "brand": "MSI",
        "category": "Motherboards",
        "price": "199.90",
        "stock": 9,
        "description": "Intel B760 ATX motherboard with wireless networking and multiple M.2 slots.",
        "image_search": "MSI motherboard",
    },
    {
        "code": "MB-GB-B650-AORUS",
        "name": "Gigabyte B650 AORUS Elite AX Motherboard",
        "brand": "Gigabyte",
        "category": "Motherboards",
        "price": "229.90",
        "stock": 6,
        "description": "AM5 motherboard with strong VRM cooling and next-gen storage connectivity.",
        "image_search": "Gigabyte motherboard",
    },
    {
        "code": "MB-ASROCK-B550M",
        "name": "ASRock B550M Pro4 Micro-ATX Motherboard",
        "brand": "ASRock",
        "category": "Motherboards",
        "price": "109.90",
        "stock": 13,
        "description": "Compact AMD motherboard for reliable budget and mid-range builds.",
        "image_search": "micro ATX motherboard",
    },
    {
        "code": "RAM-KINGSTON-32-DDR5",
        "name": "Kingston Fury Beast 32GB DDR5 6000MHz Kit",
        "brand": "Kingston",
        "category": "Memory",
        "price": "124.90",
        "stock": 18,
        "description": "Fast 32GB DDR5 memory kit for modern gaming PCs.",
        "image_search": "DDR5 RAM memory module",
    },
    {
        "code": "RAM-CORSAIR-RGB-32",
        "name": "Corsair Vengeance RGB 32GB DDR5 Kit",
        "brand": "Corsair",
        "category": "Memory",
        "price": "139.90",
        "stock": 16,
        "description": "RGB DDR5 memory kit with high-speed profiles and a clean black heatspreader.",
        "image_search": "RGB computer memory RAM",
    },
    {
        "code": "RAM-GSKILL-16-DDR4",
        "name": "G.Skill Ripjaws V 16GB DDR4 3200MHz Kit",
        "brand": "G.Skill",
        "category": "Memory",
        "price": "46.90",
        "stock": 25,
        "description": "Affordable DDR4 memory upgrade for gaming and office desktops.",
        "image_search": "DDR4 RAM memory module",
    },
    {
        "code": "RAM-CRUCIAL-32-DDR5",
        "name": "Crucial Pro 32GB DDR5 Desktop Memory Kit",
        "brand": "Crucial",
        "category": "Memory",
        "price": "112.90",
        "stock": 20,
        "description": "Low-profile DDR5 kit for stable everyday performance.",
        "image_search": "desktop computer RAM",
    },
    {
        "code": "SSD-SAMSUNG-990EVO-1TB",
        "name": "Samsung 990 EVO 1TB NVMe SSD",
        "brand": "Samsung",
        "category": "Storage",
        "price": "94.90",
        "stock": 21,
        "description": "Fast 1TB NVMe drive for operating systems, games, and applications.",
        "image_search": "NVMe SSD drive",
    },
    {
        "code": "SSD-WD-SN850X-2TB",
        "name": "WD Black SN850X 2TB NVMe SSD",
        "brand": "Western Digital",
        "category": "Storage",
        "price": "169.90",
        "stock": 10,
        "description": "High-end 2TB NVMe SSD for large game libraries and creative projects.",
        "image_search": "M.2 NVMe SSD",
    },
    {
        "code": "SSD-CRUCIAL-P3P-1TB",
        "name": "Crucial P3 Plus 1TB PCIe 4.0 SSD",
        "brand": "Crucial",
        "category": "Storage",
        "price": "74.90",
        "stock": 17,
        "description": "PCIe 4.0 solid-state storage with strong value for everyday builds.",
        "image_search": "solid state drive SSD",
    },
    {
        "code": "HDD-SEAGATE-2TB",
        "name": "Seagate Barracuda 2TB Desktop Hard Drive",
        "brand": "Seagate",
        "category": "Storage",
        "price": "64.90",
        "stock": 15,
        "description": "2TB 3.5-inch hard drive for mass storage, backups, and media files.",
        "image_search": "computer hard disk drive",
    },
    {
        "code": "PSU-CORSAIR-RM750E",
        "name": "Corsair RM750e 750W 80 Plus Gold PSU",
        "brand": "Corsair",
        "category": "Power Supplies",
        "price": "119.90",
        "stock": 12,
        "description": "Fully modular 750W power supply for quiet, efficient gaming systems.",
        "image_search": "modular computer power supply",
    },
    {
        "code": "PSU-SEASONIC-GX850",
        "name": "Seasonic Focus GX-850 850W Gold PSU",
        "brand": "Seasonic",
        "category": "Power Supplies",
        "price": "149.90",
        "stock": 7,
        "description": "Reliable 850W modular power supply for high-performance PCs.",
        "image_search": "850W computer power supply",
    },
    {
        "code": "PSU-BQ-PP12M-750",
        "name": "be quiet! Pure Power 12 M 750W PSU",
        "brand": "be quiet!",
        "category": "Power Supplies",
        "price": "124.90",
        "stock": 9,
        "description": "ATX 3.0 power supply with quiet operation and modern GPU connector support.",
        "image_search": "PC power supply unit",
    },
    {
        "code": "PSU-CM-MWE650",
        "name": "Cooler Master MWE 650 Bronze V2 PSU",
        "brand": "Cooler Master",
        "category": "Power Supplies",
        "price": "74.90",
        "stock": 18,
        "description": "650W bronze-rated power supply for budget gaming and office PCs.",
        "image_search": "computer PSU",
    },
    {
        "code": "CASE-NZXT-H5-FLOW",
        "name": "NZXT H5 Flow Mid-Tower Case",
        "brand": "NZXT",
        "category": "Cases",
        "price": "109.90",
        "stock": 10,
        "description": "Airflow-focused mid-tower case with clean cable management options.",
        "image_search": "gaming PC case",
    },
    {
        "code": "CASE-CORSAIR-4000D",
        "name": "Corsair 4000D Airflow Tempered Glass Case",
        "brand": "Corsair",
        "category": "Cases",
        "price": "99.90",
        "stock": 13,
        "description": "Popular ATX case with a high-airflow front panel and tidy interior.",
        "image_search": "computer tower case",
    },
    {
        "code": "CASE-FRACTAL-POP-AIR",
        "name": "Fractal Design Pop Air RGB Case",
        "brand": "Fractal Design",
        "category": "Cases",
        "price": "94.90",
        "stock": 8,
        "description": "Stylish airflow case with RGB fans and flexible storage support.",
        "image_search": "RGB PC case",
    },
    {
        "code": "CASE-LIANLI-216",
        "name": "Lian Li LANCOOL 216 Airflow Case",
        "brand": "Lian Li",
        "category": "Cases",
        "price": "119.90",
        "stock": 6,
        "description": "Roomy performance case designed for strong airflow and large components.",
        "image_search": "airflow PC case",
    },
    {
        "code": "COOL-ARCTIC-LF3-240",
        "name": "Arctic Liquid Freezer III 240 AIO Cooler",
        "brand": "Arctic",
        "category": "Cooling",
        "price": "89.90",
        "stock": 11,
        "description": "240mm liquid CPU cooler for quiet thermal performance.",
        "image_search": "liquid CPU cooler radiator",
    },
    {
        "code": "COOL-CM-H212",
        "name": "Cooler Master Hyper 212 Black CPU Cooler",
        "brand": "Cooler Master",
        "category": "Cooling",
        "price": "44.90",
        "stock": 18,
        "description": "Tower air cooler for dependable budget CPU cooling.",
        "image_search": "CPU air cooler",
    },
    {
        "code": "COOL-NOCTUA-U12S",
        "name": "Noctua NH-U12S redux CPU Cooler",
        "brand": "Noctua",
        "category": "Cooling",
        "price": "59.90",
        "stock": 9,
        "description": "Quiet 120mm tower cooler with trusted thermal performance.",
        "image_search": "Noctua CPU cooler",
    },
    {
        "code": "COOL-CORSAIR-H100I",
        "name": "Corsair iCUE H100i RGB 240mm AIO Cooler",
        "brand": "Corsair",
        "category": "Cooling",
        "price": "139.90",
        "stock": 5,
        "description": "RGB 240mm liquid cooler with software-controlled lighting and fan curves.",
        "image_search": "RGB liquid CPU cooler",
    },
    {
        "code": "MON-DELL-G2724D",
        "name": "Dell G2724D 27-inch QHD Gaming Monitor",
        "brand": "Dell",
        "category": "Monitors",
        "price": "269.90",
        "stock": 9,
        "description": "27-inch QHD high-refresh gaming monitor for sharp, responsive play.",
        "image_search": "gaming computer monitor",
    },
    {
        "code": "MON-LG-27GP850",
        "name": "LG UltraGear 27GP850-B 27-inch Gaming Monitor",
        "brand": "LG",
        "category": "Monitors",
        "price": "329.90",
        "stock": 7,
        "description": "Fast Nano IPS gaming monitor with smooth motion and vivid color.",
        "image_search": "LG gaming monitor",
    },
    {
        "code": "MON-SAMSUNG-G5-32",
        "name": "Samsung Odyssey G5 32-inch Curved Monitor",
        "brand": "Samsung",
        "category": "Monitors",
        "price": "299.90",
        "stock": 6,
        "description": "Immersive curved QHD monitor for gaming and media setups.",
        "image_search": "curved gaming monitor",
    },
    {
        "code": "MON-ASUS-PA278QV",
        "name": "ASUS ProArt PA278QV 27-inch Creator Monitor",
        "brand": "ASUS",
        "category": "Monitors",
        "price": "289.90",
        "stock": 5,
        "description": "Color-focused 27-inch display for photo editing, design, and productivity.",
        "image_search": "computer monitor display",
    },
    {
        "code": "KEY-KEYCHRON-K2",
        "name": "Keychron K2 Wireless Mechanical Keyboard",
        "brand": "Keychron",
        "category": "Keyboards",
        "price": "89.90",
        "stock": 16,
        "description": "Compact wireless mechanical keyboard for office and gaming setups.",
        "image_search": "mechanical keyboard",
    },
    {
        "code": "KEY-LOGI-GPROX-TKL",
        "name": "Logitech G Pro X TKL Gaming Keyboard",
        "brand": "Logitech",
        "category": "Keyboards",
        "price": "179.90",
        "stock": 8,
        "description": "Tournament-style tenkeyless keyboard with responsive switches.",
        "image_search": "gaming keyboard",
    },
    {
        "code": "MOU-LOGI-MX3S",
        "name": "Logitech MX Master 3S Wireless Mouse",
        "brand": "Logitech",
        "category": "Mice",
        "price": "104.90",
        "stock": 14,
        "description": "Ergonomic productivity mouse with quiet clicks and precise tracking.",
        "image_search": "wireless computer mouse",
    },
    {
        "code": "MOU-RAZER-DAV3",
        "name": "Razer DeathAdder V3 Gaming Mouse",
        "brand": "Razer",
        "category": "Mice",
        "price": "69.90",
        "stock": 17,
        "description": "Lightweight ergonomic gaming mouse for fast competitive play.",
        "image_search": "gaming mouse",
    },
    {
        "code": "HEAD-HYPERX-CLOUD3",
        "name": "HyperX Cloud III Gaming Headset",
        "brand": "HyperX",
        "category": "Headsets",
        "price": "99.90",
        "stock": 12,
        "description": "Comfortable wired gaming headset with clear microphone audio.",
        "image_search": "gaming headset",
    },
    {
        "code": "HEAD-STEELSERIES-NOVA3",
        "name": "SteelSeries Arctis Nova 3 Headset",
        "brand": "SteelSeries",
        "category": "Headsets",
        "price": "84.90",
        "stock": 10,
        "description": "Lightweight RGB gaming headset for PC and console chat.",
        "image_search": "computer gaming headphones",
    },
    {
        "code": "NET-TPLINK-AX55",
        "name": "TP-Link Archer AX55 WiFi 6 Router",
        "brand": "TP-Link",
        "category": "Networking",
        "price": "89.90",
        "stock": 15,
        "description": "WiFi 6 router for faster home networking and lower wireless congestion.",
        "image_search": "WiFi router",
    },
    {
        "code": "NET-UNIFI-U6PLUS",
        "name": "Ubiquiti UniFi U6+ Wireless Access Point",
        "brand": "Ubiquiti",
        "category": "Networking",
        "price": "119.90",
        "stock": 7,
        "description": "Ceiling-mount wireless access point for reliable home and office WiFi.",
        "image_search": "wireless access point",
    },
    {
        "code": "NET-NETGEAR-GS308",
        "name": "Netgear GS308 8-Port Gigabit Switch",
        "brand": "Netgear",
        "category": "Networking",
        "price": "29.90",
        "stock": 22,
        "description": "Compact unmanaged switch for expanding wired network connections.",
        "image_search": "ethernet network switch",
    },
    {
        "code": "LAP-ASUS-TUF-A15",
        "name": "ASUS TUF Gaming A15 15.6-inch Laptop",
        "brand": "ASUS",
        "category": "Laptops",
        "price": "999.90",
        "stock": 5,
        "description": "Durable gaming laptop with high-refresh display and dedicated graphics.",
        "image_search": "gaming laptop",
    },
    {
        "code": "LAP-LENOVO-IDEAPAD-G3",
        "name": "Lenovo IdeaPad Gaming 3 Laptop",
        "brand": "Lenovo",
        "category": "Laptops",
        "price": "849.90",
        "stock": 6,
        "description": "Value gaming laptop for study, work, and entry-level PC gaming.",
        "image_search": "Lenovo laptop computer",
    },
]


class Command(BaseCommand):
    help = "Seed the store with PCForce products and local product images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Create products without downloading images.",
        )
        parser.add_argument(
            "--refresh-images",
            action="store_true",
            help="Download images again even if a local file already exists.",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=0.75,
            help="Delay between image searches to be polite to remote services.",
        )
        parser.add_argument(
            "--image-provider",
            choices=["auto", "commons", "bing"],
            default="auto",
            help="Where to search for product images.",
        )

    def handle(self, *args, **options):
        products_dir = Path(settings.MEDIA_ROOT) / "products"
        products_dir.mkdir(parents=True, exist_ok=True)

        image_sources = {}
        if not options["skip_images"]:
            image_sources = self.load_existing_manifest(products_dir)

        created_count = 0
        updated_count = 0
        image_count = 0
        placeholder_count = 0

        for product_data in PRODUCTS:
            category, _ = Category.objects.get_or_create(
                name=product_data["category"]
            )

            image_name = ""
            source = None

            if not options["skip_images"]:
                image_name, source = self.get_product_image(
                    product_data,
                    products_dir,
                    options["refresh_images"],
                    options["image_provider"],
                )
                if source:
                    image_sources[product_data["code"]] = source
                    if source["kind"] == "placeholder":
                        placeholder_count += 1
                    else:
                        image_count += 1

                if options["sleep"]:
                    time.sleep(options["sleep"])

            product_values = {
                "name": product_data["name"],
                "brand": product_data["brand"],
                "category": category,
                "price": Decimal(product_data["price"]),
                "stock": product_data["stock"],
                "description": product_data["description"],
            }

            if image_name:
                product_values["image"] = image_name

            _, created = Product.objects.update_or_create(
                code=product_data["code"],
                defaults=product_values,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        if not options["skip_images"]:
            self.save_manifest(products_dir, image_sources)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(PRODUCTS)} products "
                f"({created_count} created, {updated_count} updated)."
            )
        )
        self.stdout.write(f"Categories: {Category.objects.count()}")
        self.stdout.write(f"Downloaded images: {image_count}")
        self.stdout.write(f"Generated fallback images: {placeholder_count}")
        self.stdout.write(f"Image folder: {products_dir}")

    def get_product_image(
        self,
        product_data,
        products_dir,
        refresh_images,
        image_provider,
    ):
        slug = slugify(product_data["code"]).lower()
        existing = self.find_existing_image(products_dir, slug)

        if existing and not refresh_images:
            return f"products/{existing.name}", None

        provider_map = {
            "commons": self.search_commons_images,
            "bing": self.search_bing_images,
        }
        provider_names = (
            ["commons", "bing"] if image_provider == "auto" else [image_provider]
        )
        failures = []

        for provider_name in provider_names:
            search_text = (
                product_data["name"]
                if provider_name == "bing"
                else product_data["image_search"]
            )

            try:
                candidates = provider_map[provider_name](search_text)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                failures.append(f"{provider_name} search: {exc}")
                continue

            for candidate in candidates:
                try:
                    image_path = self.download_image(
                        candidate["download_url"],
                        products_dir / slug,
                    )
                    self.remove_stale_placeholder(products_dir, slug, image_path)
                    return (
                        f"products/{image_path.name}",
                        {
                            "kind": provider_name,
                            "search": search_text,
                            "source_url": candidate["source_url"],
                            "download_url": candidate["download_url"],
                            "title": candidate.get("title", ""),
                        },
                    )
                except (
                    HTTPError,
                    URLError,
                    TimeoutError,
                    OSError,
                    ValueError,
                    InvalidURL,
                ) as exc:
                    failures.append(f"{provider_name} download: {exc}")

        if failures:
            self.stderr.write(
                f"Image download failed for {product_data['code']}: {failures[0]}"
            )

        image_path = products_dir / f"{slug}.svg"
        self.write_placeholder(product_data, image_path)
        return (
            f"products/{image_path.name}",
            {
                "kind": "placeholder",
                "search": product_data["image_search"],
                "source_url": "generated locally",
            },
        )

    def search_commons_images(self, search_text):
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": "6",
            "gsrlimit": "8",
            "gsrsearch": search_text,
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlwidth": "900",
            "format": "json",
            "origin": "*",
        }
        api_url = f"{COMMONS_API_URL}?{urlencode(params)}"
        request = Request(api_url, headers={"User-Agent": USER_AGENT})

        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        pages = payload.get("query", {}).get("pages", {})
        ordered_pages = sorted(
            pages.values(),
            key=lambda page: page.get("index", 999),
        )
        candidates = []

        for page in ordered_pages:
            image_info = page.get("imageinfo", [{}])[0]
            mime = image_info.get("mime")

            if mime not in ALLOWED_IMAGE_TYPES:
                continue

            image_url = image_info.get("thumburl") or image_info.get("url")
            description_url = image_info.get("descriptionurl")

            if image_url and description_url:
                candidates.append(
                    {
                        "download_url": image_url,
                        "source_url": description_url,
                        "title": page.get("title", ""),
                    }
                )

        return candidates

    def search_bing_images(self, search_text):
        params = {
            "q": f"{search_text} product image",
            "form": "HDRSC2",
            "first": "1",
            "qft": "+filterui:photo-photo",
        }
        search_url = f"{BING_IMAGE_URL}?{urlencode(params)}"
        request = Request(search_url, headers={"User-Agent": USER_AGENT})

        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")

        metadata_matches = re.findall(r'class="iusc"[^>]+m="([^"]+)"', html)
        candidates = []

        for metadata_match in metadata_matches[:10]:
            try:
                metadata = json.loads(unescape(metadata_match))
            except json.JSONDecodeError:
                continue

            source_url = unescape(metadata.get("purl") or metadata.get("murl") or "")
            title = metadata.get("t", "")

            for key in ["murl", "turl"]:
                image_url = unescape(metadata.get(key) or "").strip()

                if image_url and image_url.startswith("http"):
                    candidates.append(
                        {
                            "download_url": image_url,
                            "source_url": source_url,
                            "title": title,
                        }
                    )

        return candidates

    def download_image(self, source_url, destination_base):
        source_url = self.normalize_url(source_url)
        request = Request(source_url, headers={"User-Agent": USER_AGENT})

        with urlopen(request, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            mime = content_type.split(";")[0].strip().lower()
            content = response.read()

        if not content:
            raise ValueError("empty image response")

        image_ext = ALLOWED_IMAGE_TYPES.get(mime) or self.sniff_image_extension(
            content
        )
        if not image_ext:
            raise ValueError(f"response is not a supported image ({mime or 'unknown'})")

        destination = destination_base.with_suffix(image_ext)
        destination.write_bytes(content)
        return destination

    def normalize_url(self, source_url):
        source_url = unescape(source_url or "").strip()
        parts = urlsplit(source_url)

        if parts.scheme not in ["http", "https"] or not parts.netloc:
            raise ValueError(f"unsupported image URL: {source_url}")

        return urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                quote(parts.path, safe="/%"),
                quote(parts.query, safe="=&?/:+,%"),
                "",
            )
        )

    def sniff_image_extension(self, content):
        if content.startswith(b"\xff\xd8\xff"):
            return ".jpg"

        if content.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"

        if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
            return ".webp"

        return None

    def remove_stale_placeholder(self, products_dir, slug, image_path):
        placeholder_path = products_dir / f"{slug}.svg"
        if image_path.suffix != ".svg" and placeholder_path.exists():
            placeholder_path.unlink()

    def find_existing_image(self, products_dir, slug):
        for image_ext in [".jpg", ".jpeg", ".png", ".webp", ".svg"]:
            image_path = products_dir / f"{slug}{image_ext}"
            if image_path.exists() and image_path.stat().st_size > 0:
                return image_path

        return None

    def write_placeholder(self, product_data, image_path):
        title_lines = self.wrap_text(product_data["name"], 28)
        brand = escape(product_data["brand"])
        category = escape(product_data["category"])

        title_spans = []
        start_y = 292 - (len(title_lines) - 1) * 24
        for index, line in enumerate(title_lines):
            title_spans.append(
                f'<text x="450" y="{start_y + index * 52}" '
                f'font-size="38" font-weight="700" text-anchor="middle" '
                f'fill="#101828">{escape(line)}</text>'
            )

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="0 0 900 650">
<rect width="900" height="650" fill="#f4f7fb"/>
<rect x="70" y="70" width="760" height="510" rx="34" fill="#ffffff" stroke="#d6dde8" stroke-width="4"/>
<rect x="130" y="126" width="640" height="118" rx="24" fill="#0f172a"/>
<circle cx="205" cy="185" r="34" fill="#2dd4bf"/>
<circle cx="286" cy="185" r="34" fill="#60a5fa"/>
<circle cx="367" cy="185" r="34" fill="#f97316"/>
<text x="450" y="198" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="700" text-anchor="middle" fill="#ffffff">PCForce</text>
<g font-family="Arial, Helvetica, sans-serif">
{''.join(title_spans)}
<text x="450" y="426" font-size="26" font-weight="700" text-anchor="middle" fill="#475467">{brand}</text>
<text x="450" y="468" font-size="22" text-anchor="middle" fill="#667085">{category}</text>
<text x="450" y="528" font-size="20" text-anchor="middle" fill="#98a2b3">Product image placeholder</text>
</g>
</svg>
"""
        image_path.write_text(svg, encoding="utf-8")

    def wrap_text(self, text, max_length):
        words = re.split(r"\s+", text)
        lines = []
        current_line = []

        for word in words:
            next_line = " ".join([*current_line, word])
            if len(next_line) <= max_length:
                current_line.append(word)
                continue

            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines[:3]

    def load_existing_manifest(self, products_dir):
        manifest_path = products_dir / "image_sources.json"
        if not manifest_path.exists():
            return {}

        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def save_manifest(self, products_dir, image_sources):
        manifest_path = products_dir / "image_sources.json"
        manifest_path.write_text(
            json.dumps(image_sources, indent=2, sort_keys=True),
            encoding="utf-8",
        )
