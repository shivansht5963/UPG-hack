"""
Script to update Material CO2 saving factors with realistic values
Based on environmental research:
- Recycling plastic saves ~1.5kg CO2 per kg vs virgin production
- Recycling metal saves ~1.8kg CO2 per kg
- E-waste recycling saves ~3.2kg CO2 per kg
- Paper/Cotton saves ~0.9kg CO2 per kg
"""

from marketplace.models import Material

# Realistic CO2 saving factors (kg CO2 saved per kg of material recycled)
co2_factors = {
    'PET Plastic': 1.5,
    'HDPE Plastic': 1.4,
    'PP Plastic': 1.3,
    'Plastic': 1.5,  # Generic plastic
    'Aluminum': 9.0,  # Aluminum has highest savings!
    'Steel': 1.8,
    'Copper': 2.5,
    'Metal': 1.8,  # Generic metal
    'E-Waste': 3.2,
    'Electronics': 3.2,
    'Paper': 0.9,
    'Cardboard': 0.7,
    'Cotton Waste': 0.8,
    'Textile': 0.8,
    'Glass': 0.5,
    'Rubber': 1.0,
}

# Update all materials
updated = 0
for material in Material.objects.all():
    # Try exact match first
    if material.name in co2_factors:
        material.co2_saved_per_kg = co2_factors[material.name]
        material.save()
        print(f"✅ Updated {material.name}: {material.co2_saved_per_kg} kg CO2/kg")
        updated += 1
    else:
        # Try partial match
        found = False
        for key, value in co2_factors.items():
            if key.lower() in material.name.lower() or material.name.lower() in key.lower():
                material.co2_saved_per_kg = value
                material.save()
                print(f"✅ Updated {material.name}: {material.co2_saved_per_kg} kg CO2/kg (matched {key})")
                updated += 1
                found = True
                break
        
        if not found:
            # Default for unknown materials
            material.co2_saved_per_kg = 1.0
            material.save()
            print(f"⚠️  Updated {material.name}: 1.0 kg CO2/kg (default)")
            updated += 1

print(f"\n🎉 Updated {updated} materials with CO2 saving factors!")
print("\n📊 Summary:")
for material in Material.objects.all().order_by('-co2_saved_per_kg'):
    print(f"  {material.name}: {material.co2_saved_per_kg} kg CO2 saved per kg")
