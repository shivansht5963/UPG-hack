# CO2 Impact Calculator - How It Works

## The Concept: "Trash to Impact Calculator"
Transforms boring waste weight into exciting environmental impact scores.

## The Formula
```python
CO2 Saved (kg) = Weight of Waste (kg) × CO2 Saving Factor (kg CO2/kg)
```

## Example Calculation
- **Waste:** 10kg of Recycled Plastic
- **Factor:** Recycling plastic saves ~1.5kg CO2 vs making new plastic
- **Result:** 10kg × 1.5 = **15kg of CO2 Prevented** 🌍

## Realistic CO2 Saving Factors (kg CO2 saved per kg recycled)

### Metals (Highest Impact!)
- **Aluminum**: 9.0 kg CO2/kg - Most impactful!
- **Copper**: 2.5 kg CO2/kg
- **Steel**: 1.8 kg CO2/kg
- **Generic Metal**: 1.8 kg CO2/kg

### Plastics
- **PET Plastic**: 1.5 kg CO2/kg
- **HDPE Plastic**: 1.4 kg CO2/kg
- **PP Plastic**: 1.3 kg CO2/kg
- **Generic Plastic**: 1.5 kg CO2/kg

### Electronics
- **E-Waste**: 3.2 kg CO2/kg
- **Electronics**: 3.2 kg CO2/kg

### Textiles & Paper
- **Cotton Waste**: 0.8 kg CO2/kg
- **Textile**: 0.8 kg CO2/kg
- **Paper**: 0.9 kg CO2/kg
- **Cardboard**: 0.7 kg CO2/kg

### Other Materials
- **Rubber**: 1.0 kg CO2/kg
- **Glass**: 0.5 kg CO2/kg

## How to Set CO2 Values

### Option 1: Django Admin (Easy)
1. Go to http://127.0.0.1:8000/admin/marketplace/material/
2. Click on a material (e.g., "PET Plastic")
3. Set `co2_saved_per_kg` field (e.g., 1.5)
4. Click "Save"

### Option 2: Run Update Script
```bash
python update_co2_factors.py
```

### Option 3: Django Shell (Manual)
```python
python manage.py shell
from marketplace.models import Material

# Update specific material
plastic = Material.objects.get(name__icontains='plastic')
plastic.co2_saved_per_kg = 1.5
plastic.save()
```

## Auto-Calculation
The `WasteListing.save()` method automatically calculates CO2:

```python
def save(self, *args, **kwargs):
    # Calculate CO2 saved
    self.co2_saved = self.weight * self.material.co2_saved_per_kg
    # ... rest of save logic
    super().save(*args, **kwargs)
```

## Value Proposition

### For Sellers (Workers)
- **"Green Score" Gamification**: "I saved 1 ton of CO2 this year!"
- **Personal Achievement**: Track environmental impact
- **Motivation**: Visual proof of making a difference

### For Buyers (Factories)
- **Compliance Certificate**: Show government/investors
- **ESG Goals**: Track carbon footprint reduction
- **Reporting**: Quantifiable environmental impact data

## In Short
🗑️ **Waste Receipt** → 🌍 **Planet-Saving Certificate**

## Testing
1. Create a listing with 10kg of material
2. Ensure material has `co2_saved_per_kg` set (e.g., 1.5)
3. Submit listing
4. Expected result: `co2_saved = 10 × 1.5 = 15.0 kg`
5. Display shows: "15.0 kg CO₂ Emissions Saved"

## Current Status
✅ Formula implemented in `WasteListing.save()`
✅ Auto-calculation enabled
⚠️  Materials need CO2 factors set (use update script or admin)
✅ Display ready in templates
