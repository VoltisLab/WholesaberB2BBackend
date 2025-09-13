from django.core.management.base import BaseCommand
from products.models import Material


class Command(BaseCommand):
    help = "Create or update predefined materials from a list"

    def handle(self, *args, **kwargs):
        # List of materials names
        material_data = [
            "Acrylic",
            "Alpaca",
            "Angora",
            "Aramid",
            "Acetate",
            "Bamboo",
            "Batiste",
            "Broadcloth",
            "Bouclé",
            "Burlap",
            "Canvas",
            "Cashmere",
            "Chambray",
            "Chiffon",
            "Corduroy",
            "Cotton",
            "Denim",
            "Duck",
            "Dobby",
            "Elastane",
            "Embroidery fabric",
            "Eyelet",
            "Fleece",
            "Felt",
            "Flannel",
            "Georgette",
            "Gingham",
            "Gabardine",
            "Gore-Tex",
            "Hemp",
            "Herringbone",
            "Houndstooth",
            "Ikat",
            "Interlock knit",
            "Jersey",
            "Jute",
            "Knits",
            "Kevlar",
            "Lace",
            "Leather",
            "Linen",
            "Lyocell",
            "Merino wool",
            "Mesh",
            "Modal",
            "Mohair",
            "Nylon",
            "Neoprene",
            "Netting",
            "Organza",
            "Oxford cloth",
            "Polyester",
            "Poplin",
            "Piqué",
            "PVC",
            "Quilted fabric",
            "Rayon",
            "Ripstop",
            "Satin",
            "Silk",
            "Spandex",
            "Suede",
            "Seersucker",
            "Taffeta",
            "Tencel",
            "Terrycloth",
            "Tweed",
            "Twill",
            "Ultrasuede",
            "Velvet",
            "Viscose",
            "Wool",
            "Worsted",
            "Xanadu fabric",
            "Yarn",
            "Zibeline",
        ]

        # Fetch existing materials
        existing_materials = Material.objects.filter(name__in=material_data)
        existing_material_names = set(existing_materials.values_list("name", flat=True))

        # Prepare new materials for bulk creation
        new_materials = [
            Material(name=material_name)
            for material_name in material_data
            if material_name not in existing_material_names
        ]

        # Bulk create new materials (ignores updates for existing materials)
        if new_materials:
            Material.objects.bulk_create(
                new_materials, batch_size=5000
            )  # Adjust batch size if necessary
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(new_materials)} new materials")
            )

        # For bulk update, you need to manually update the existing ones if required
        # This can be done using a loop or manually if necessary.
        if existing_material_names:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Skipped {len(existing_material_names)} existing materials"
                )
            )
